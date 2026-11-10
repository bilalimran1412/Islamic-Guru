from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.rag.generator import ClaudeGenerator
from app.rag.pipeline import AnswerPipeline
from app.rag.retriever import PostgresRetriever, VoyageEmbedder

_generator: ClaudeGenerator | None = None


def get_generator() -> ClaudeGenerator:
    global _generator
    if _generator is None:
        _generator = ClaudeGenerator(get_settings())
    return _generator


def get_pipeline(
    session: AsyncSession = Depends(get_session),
    generator: ClaudeGenerator = Depends(get_generator),
) -> AnswerPipeline:
    s = get_settings()
    embedder = VoyageEmbedder(s.voyage_api_key, s.embedding_model) if s.voyage_api_key else None
    return AnswerPipeline(PostgresRetriever(session, s, embedder), generator, s)
