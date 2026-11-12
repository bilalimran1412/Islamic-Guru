"""Search over the verified library (`sources` table).

Two strategies:
- Vector search with pgvector when an embedding provider is configured.
- Postgres full-text search on the English translation otherwise (works with no
  extra API key, good enough for development).
"""

from dataclasses import dataclass, field
from typing import Protocol

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings


@dataclass
class Passage:
    ref_key: str
    kind: str
    label: str
    arabic: str | None
    translations: dict = field(default_factory=dict)
    grade: str | None = None
    madhhab: str | None = None
    score: float = 0.0

    def translation(self, lang: str) -> str | None:
        t = self.translations.get(lang)
        return t.get("text") if isinstance(t, dict) else t

    def all_texts(self) -> list[str]:
        texts = [self.arabic] if self.arabic else []
        texts += [self.translation(lang) or "" for lang in self.translations]
        return [t for t in texts if t]


class Retriever(Protocol):
    async def search(self, queries: list[str], top_k: int) -> list[Passage]: ...


class Embedder(Protocol):
    async def embed(self, texts: list[str], input_type: str) -> list[list[float]]: ...


class VoyageEmbedder:
    """Multilingual embeddings via the Voyage AI REST API."""

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model

    async def embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.voyageai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"input": texts, "model": self._model, "input_type": input_type},
            )
            resp.raise_for_status()
            return [item["embedding"] for item in resp.json()["data"]]


def _row_to_passage(row, score: float) -> Passage:
    return Passage(
        ref_key=row.ref_key,
        kind=row.kind.value if hasattr(row.kind, "value") else str(row.kind),
        label=row.label,
        arabic=row.arabic,
        translations=row.translations or {},
        grade=row.grade,
        madhhab=row.madhhab,
        score=score,
    )


class PostgresRetriever:
    def __init__(self, session: AsyncSession, settings: Settings, embedder: Embedder | None):
        self._session = session
        self._settings = settings
        self._embedder = embedder

    async def search(self, queries: list[str], top_k: int) -> list[Passage]:
        queries = [q for q in queries if q.strip()]
        if not queries:
            return []
        if self._embedder:
            found = await self._vector_search(queries, top_k)
        else:
            found = await self._keyword_search(queries, top_k)
        # Merge results across query variants, keeping the best score per ref.
        best: dict[str, Passage] = {}
        for p in found:
            if p.ref_key not in best or p.score > best[p.ref_key].score:
                best[p.ref_key] = p
        return sorted(best.values(), key=lambda p: p.score, reverse=True)[:top_k]

    async def _vector_search(self, queries: list[str], top_k: int) -> list[Passage]:
        vectors = await self._embedder.embed(queries, input_type="query")
        results: list[Passage] = []
        for vec in vectors:
            rows = await self._session.execute(
                text(
                    """
                    SELECT ref_key, kind, label, arabic, translations, grade, madhhab,
                           1 - (embedding <=> CAST(:vec AS vector)) AS score
                    FROM sources
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:vec AS vector)
                    LIMIT :k
                    """
                ),
                {"vec": str(vec), "k": top_k},
            )
            results += [
                _row_to_passage(r, float(r.score))
                for r in rows
                if float(r.score) >= self._settings.min_relevance
            ]
        return results

    async def _keyword_search(self, queries: list[str], top_k: int) -> list[Passage]:
        results: list[Passage] = []
        for q in queries:
            rows = await self._session.execute(
                text(
                    """
                    SELECT ref_key, kind, label, arabic, translations, grade, madhhab,
                           ts_rank(to_tsvector('english', coalesce(translations->'en'->>'text', translations->'ur'->>'text', '')),
                                   websearch_to_tsquery('english', :q)) AS score
                    FROM sources
                    WHERE to_tsvector('english', coalesce(translations->'en'->>'text', translations->'ur'->>'text', ''))
                          @@ websearch_to_tsquery('english', :q)
                    ORDER BY score DESC
                    LIMIT :k
                    """
                ),
                {"q": q, "k": top_k},
            )
            results += [_row_to_passage(r, float(r.score)) for r in rows]
        return results
