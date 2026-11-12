"""Fatawa library (Phase 2): approved fatawa only, shown unchanged with a link to the original."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Fatwa, FatwaStatus

router = APIRouter(prefix="/v1/fatwas")


class FatwaSummary(BaseModel):
    id: str
    title: str
    publisher: str
    scholar: str | None
    madhhab: str | None
    language: str
    published_at: datetime | None


class FatwaDetail(FatwaSummary):
    question: str | None
    answer: str
    original_url: str


def _summary(f: Fatwa) -> dict:
    return {"id": f.id, "title": f.title, "publisher": f.publisher, "scholar": f.scholar,
            "madhhab": f.madhhab, "language": f.language, "published_at": f.published_at}


@router.get("", response_model=list[FatwaSummary])
async def list_fatwas(
    q: str | None = Query(default=None, max_length=200),
    madhhab: str | None = None,
    limit: int = Query(default=30, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[FatwaSummary]:
    stmt = select(Fatwa).where(Fatwa.status == FatwaStatus.approved)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Fatwa.title.ilike(like), Fatwa.question.ilike(like), Fatwa.answer.ilike(like)))
    if madhhab:
        stmt = stmt.where(Fatwa.madhhab == madhhab)
    stmt = stmt.order_by(Fatwa.published_at.desc().nulls_last(), Fatwa.created_at.desc())
    rows = await session.execute(stmt.limit(limit).offset(offset))
    return [FatwaSummary(**_summary(f)) for f in rows.scalars()]


@router.get("/{fatwa_id}", response_model=FatwaDetail)
async def get_fatwa(fatwa_id: str, session: AsyncSession = Depends(get_session)) -> FatwaDetail:
    f = await session.get(Fatwa, fatwa_id)
    if f is None or f.status != FatwaStatus.approved:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fatwa not found")
    return FatwaDetail(**_summary(f), question=f.question, answer=f.answer, original_url=f.original_url)
