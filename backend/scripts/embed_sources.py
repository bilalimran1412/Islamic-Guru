"""Compute embeddings for sources that don't have one yet (needs VOYAGE_API_KEY).

Usage (from backend/):  python -m scripts.embed_sources
"""

import asyncio

from sqlalchemy import select, update

from app.config import get_settings
from app.db import SessionLocal
from app.models import Source
from app.rag.retriever import VoyageEmbedder

BATCH = 64


def document_text(src: Source) -> str:
    parts = [src.label]
    en = (src.translations or {}).get("en")
    if en:
        parts.append(en["text"] if isinstance(en, dict) else en)
    if src.arabic:
        parts.append(src.arabic)
    return "\n".join(parts)


async def main() -> None:
    s = get_settings()
    if not s.voyage_api_key:
        raise SystemExit("Set VOYAGE_API_KEY first")
    embedder = VoyageEmbedder(s.voyage_api_key, s.embedding_model)
    total = 0
    async with SessionLocal() as session:
        while True:
            rows = (await session.execute(
                select(Source).where(Source.embedding.is_(None)).limit(BATCH)
            )).scalars().all()
            if not rows:
                break
            vectors = await embedder.embed([document_text(r) for r in rows], input_type="document")
            for r, v in zip(rows, vectors, strict=True):
                await session.execute(update(Source).where(Source.id == r.id).values(embedding=v))
            await session.commit()
            total += len(rows)
            print(f"embedded {total}")


if __name__ == "__main__":
    asyncio.run(main())
