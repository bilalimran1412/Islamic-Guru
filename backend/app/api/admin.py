"""Scholar review API, used by the /admin web page.

Protected by a shared key (ADMIN_API_KEY) plus the reviewer's name, which is
recorded on every decision. Replace with individual scholar accounts before
the panel grows beyond a few people.
"""

import html
import re
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.models import (
    Fatwa,
    FatwaStatus,
    Madhhab,
    Message,
    Plan,
    Report,
    ReportStatus,
    ScholarQuestion,
    ScholarQuestionStatus,
    Source,
    SourceKind,
    User,
)


async def reviewer_name(
    x_admin_key: str = Header(default=""), x_reviewer: str = Header(default="")
) -> str:
    key = get_settings().admin_api_key
    if not key or not secrets.compare_digest(x_admin_key, key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid admin key")
    if not x_reviewer.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Reviewer name required")
    return x_reviewer.strip()[:120]


router = APIRouter(prefix="/v1/admin", dependencies=[Depends(reviewer_name)])

_TAGS = re.compile(r"<[^>]+>")
_BLOCK_TAGS = re.compile(r"</?(p|br|div|li|h\d)[^>]*>", re.IGNORECASE)


def html_to_text(raw: str) -> str:
    text = _BLOCK_TAGS.sub("\n", raw)
    text = html.unescape(_TAGS.sub("", text))
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


# ---------- overview ----------

@router.get("/stats")
async def stats(session: AsyncSession = Depends(get_session)) -> dict:
    async def count(stmt) -> int:
        return (await session.execute(stmt)).scalar_one()

    return {
        "open_reports": await count(select(func.count()).select_from(Report).where(
            Report.status == ReportStatus.open)),
        "pending_fatwas": await count(select(func.count()).select_from(Fatwa).where(
            Fatwa.status == FatwaStatus.pending)),
        "pending_scholar_questions": await count(select(func.count()).select_from(ScholarQuestion).where(
            ScholarQuestion.status == ScholarQuestionStatus.pending)),
        "users": await count(select(func.count()).select_from(User)),
    }


# ---------- reported answers ----------

class ReportDecision(BaseModel):
    status: ReportStatus
    note: str | None = Field(default=None, max_length=4000)


@router.get("/reports")
async def list_reports(status_: ReportStatus = Query(default=ReportStatus.open, alias="status"), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(Report, Message).join(Message, Message.id == Report.message_id)
        .where(Report.status == status_).order_by(Report.created_at).limit(100)
    )).all()
    out = []
    for report, answer in rows:
        question = (await session.execute(
            select(Message.content).where(Message.chat_id == answer.chat_id, Message.role == "user",
                                          Message.created_at <= answer.created_at)
            .order_by(Message.created_at.desc()).limit(1)
        )).scalar_one_or_none()
        out.append({
            "id": report.id, "reason": report.reason, "details": report.details,
            "status": report.status.value, "created_at": report.created_at,
            "question": question, "answer": answer.content,
            "citations": answer.meta.get("citations", []), "language": answer.meta.get("language"),
        })
    return out


@router.patch("/reports/{report_id}")
async def decide_report(report_id: str, req: ReportDecision, reviewer: str = Depends(reviewer_name),
                        session: AsyncSession = Depends(get_session)) -> dict:
    report = await session.get(Report, report_id)
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    report.status, report.reviewer, report.reviewer_note = req.status, reviewer, req.note
    await session.commit()
    return {"id": report.id, "status": report.status.value}


# ---------- fatawa review queue ----------

class FatwaApproval(BaseModel):
    madhhab: Madhhab | None = None
    scholar: str | None = Field(default=None, max_length=200)


@router.get("/fatwas")
async def list_fatwas(status_: FatwaStatus = Query(default=FatwaStatus.pending, alias="status"), session: AsyncSession = Depends(get_session)):
    rows = await session.execute(select(Fatwa).where(Fatwa.status == status_).order_by(Fatwa.created_at).limit(100))
    return [{
        "id": f.id, "publisher": f.publisher, "scholar": f.scholar, "madhhab": f.madhhab, "title": f.title,
        "question": f.question, "answer": html_to_text(f.answer), "language": f.language,
        "original_url": f.original_url, "published_at": f.published_at,
    } for f in rows.scalars()]


@router.post("/fatwas/{fatwa_id}/approve")
async def approve_fatwa(fatwa_id: str, req: FatwaApproval, reviewer: str = Depends(reviewer_name),
                        session: AsyncSession = Depends(get_session)) -> dict:
    f = await session.get(Fatwa, fatwa_id)
    if f is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fatwa not found")
    if req.madhhab:
        f.madhhab = req.madhhab.value
    if req.scholar:
        f.scholar = req.scholar
    f.status, f.reviewed_by = FatwaStatus.approved, reviewer

    # Copy into the library the AI searches. Text is kept as published (HTML tags removed).
    ref_key = f"fatwa:{f.id}"
    body = html_to_text(f.answer)
    if f.question:
        body = f"{f.question}\n\n{body}"
    src = (await session.execute(select(Source).where(Source.ref_key == ref_key))).scalar_one_or_none()
    if src is None:
        src = Source(ref_key=ref_key, kind=SourceKind.fatwa, collection=f.publisher[:60])
        session.add(src)
    src.label = f"{f.publisher}: {f.title}"[:200]
    src.arabic = body if f.language == "ar" else None
    src.translations = {} if f.language == "ar" else {f.language: {"text": body}}
    src.madhhab = f.madhhab
    src.attribution = f"{f.publisher}" + (f", {f.scholar}" if f.scholar else "") + " (used with permission)"
    src.source_url = f.original_url
    src.embedding = None  # picked up by scripts.embed_sources
    await session.commit()
    return {"id": f.id, "status": f.status.value, "ref_key": ref_key}


@router.post("/fatwas/{fatwa_id}/reject")
async def reject_fatwa(fatwa_id: str, reviewer: str = Depends(reviewer_name),
                       session: AsyncSession = Depends(get_session)) -> dict:
    f = await session.get(Fatwa, fatwa_id)
    if f is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fatwa not found")
    f.status, f.reviewed_by = FatwaStatus.rejected, reviewer
    src = (await session.execute(select(Source).where(Source.ref_key == f"fatwa:{f.id}"))).scalar_one_or_none()
    if src is not None:
        await session.delete(src)
    await session.commit()
    return {"id": f.id, "status": f.status.value}


# ---------- Ask a Scholar ----------

class ScholarAnswer(BaseModel):
    answer: str = Field(min_length=5, max_length=20000)


@router.get("/scholar-questions")
async def list_scholar_questions(status_: ScholarQuestionStatus = Query(default=ScholarQuestionStatus.pending, alias="status"),
                                 session: AsyncSession = Depends(get_session)):
    rows = await session.execute(
        select(ScholarQuestion).where(ScholarQuestion.status == status_).order_by(ScholarQuestion.created_at)
        .limit(100)
    )
    return [{"id": q.id, "question": q.question, "language": q.language, "madhhab": q.madhhab,
             "status": q.status.value, "answer": q.answer, "created_at": q.created_at} for q in rows.scalars()]


@router.post("/scholar-questions/{question_id}/answer")
async def answer_scholar_question(question_id: str, req: ScholarAnswer, reviewer: str = Depends(reviewer_name),
                                  session: AsyncSession = Depends(get_session)) -> dict:
    q = await session.get(ScholarQuestion, question_id)
    if q is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")
    q.answer, q.scholar_name = req.answer, reviewer
    q.status, q.answered_at = ScholarQuestionStatus.answered, datetime.now(UTC)
    await session.commit()
    return {"id": q.id, "status": q.status.value}


@router.post("/scholar-questions/{question_id}/decline")
async def decline_scholar_question(question_id: str, reviewer: str = Depends(reviewer_name),
                                   session: AsyncSession = Depends(get_session)) -> dict:
    q = await session.get(ScholarQuestion, question_id)
    if q is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")
    q.status, q.scholar_name = ScholarQuestionStatus.declined, reviewer
    await session.commit()
    return {"id": q.id, "status": q.status.value}


# ---------- plans (manual grants: testers, sponsored / sadaqah access) ----------

class PlanGrant(BaseModel):
    plan: Plan
    days: int | None = Field(default=None, ge=1, le=3660)  # None = no expiry


@router.post("/users/{user_id}/plan")
async def set_plan(user_id: str, req: PlanGrant, session: AsyncSession = Depends(get_session)) -> dict:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.plan = req.plan
    user.plan_expires_at = datetime.now(UTC) + timedelta(days=req.days) if req.days else None
    await session.commit()
    return {"id": user.id, "plan": user.plan.value, "expires_at": user.plan_expires_at}
