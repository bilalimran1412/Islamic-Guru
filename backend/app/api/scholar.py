"""Ask a Scholar (Phase 3): personal answers from the scholar panel."""

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import is_premium
from app.config import get_settings
from app.db import get_session
from app.models import ScholarQuestion, ScholarQuestionStatus, User
from app.schemas import Language
from app.security import current_user

router = APIRouter(prefix="/v1/scholar-questions")


class ScholarQuestionIn(BaseModel):
    question: str = Field(min_length=10, max_length=4000)
    language: Language = Language.en


class ScholarQuestionOut(BaseModel):
    id: str
    question: str
    status: ScholarQuestionStatus
    answer: str | None
    scholar_name: str | None
    answered_at: datetime | None
    created_at: datetime


def _out(q: ScholarQuestion) -> ScholarQuestionOut:
    return ScholarQuestionOut(id=q.id, question=q.question, status=q.status, answer=q.answer,
                              scholar_name=q.scholar_name, answered_at=q.answered_at, created_at=q.created_at)


@router.post("", response_model=ScholarQuestionOut, status_code=status.HTTP_201_CREATED)
async def ask_scholar(
    req: ScholarQuestionIn, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> ScholarQuestionOut:
    # Premium users and free deployments skip payment; otherwise the question waits until a
    # store purchase is verified (Google Play / App Store products still to be set up).
    needs_payment = get_settings().ask_scholar_requires_payment and not is_premium(user)
    q = ScholarQuestion(
        user_id=user.id, question=req.question, language=req.language.value,
        madhhab=user.madhhab.value if user.madhhab else None,
        status=ScholarQuestionStatus.awaiting_payment if needs_payment else ScholarQuestionStatus.pending,
        paid=not needs_payment,
    )
    session.add(q)
    await session.commit()
    await session.refresh(q)
    return _out(q)


@router.get("", response_model=list[ScholarQuestionOut])
async def my_questions(
    user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> list[ScholarQuestionOut]:
    rows = await session.execute(
        select(ScholarQuestion).where(ScholarQuestion.user_id == user.id)
        .order_by(ScholarQuestion.created_at.desc()).limit(100)
    )
    return [_out(q) for q in rows.scalars()]
