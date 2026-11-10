from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.db import get_session
from app.deps import get_pipeline
from app.models import Chat, DailyUsage, Message, Report, Source, User
from app.rag.pipeline import AnswerPipeline
from app.schemas import (
    AnswerStatus,
    AskRequest,
    AskResponse,
    ChatDetail,
    ChatSummary,
    MessageOut,
    ReportRequest,
    SourceOut,
    TokenResponse,
)
from app.security import create_token, current_user

router = APIRouter(prefix="/v1")


@router.post("/auth/guest", response_model=TokenResponse)
async def guest_login(session: AsyncSession = Depends(get_session)) -> TokenResponse:
    user = User()
    session.add(user)
    await session.commit()
    return TokenResponse(access_token=create_token(user.id), user_id=user.id)


async def _consume_daily_quota(session: AsyncSession, user: User) -> None:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    usage = await session.get(DailyUsage, (user.id, day))
    if usage is None:
        usage = DailyUsage(user_id=user.id, day=day, questions=0)
        session.add(usage)
    if usage.questions >= get_settings().daily_free_questions:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Daily free question limit reached")
    usage.questions += 1


@router.post("/ask", response_model=AskResponse)
async def ask(
    req: AskRequest,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_session),
    pipeline: AnswerPipeline = Depends(get_pipeline),
) -> AskResponse:
    if req.chat_id:
        chat = await session.get(Chat, req.chat_id)
        if chat is None or chat.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    else:
        chat = Chat(user_id=user.id, title=req.question[:80])
        session.add(chat)

    await _consume_daily_quota(session, user)
    session.add(Message(chat=chat, role="user", content=req.question))
    await session.flush()

    result = await pipeline.run(req.question, req.language)
    if result.service_error:
        await session.rollback()  # don't store the question or use up the free quota
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Answer service unavailable, try again")

    reply = Message(
        chat=chat,
        role="assistant",
        content=result.answer,
        meta={
            "status": result.status.value,
            "language": result.language.value,
            "citations": [c.model_dump() for c in result.citations],
            "consult_scholar": result.consult_scholar,
            "disclaimer": result.disclaimer,
            "problems": result.problems,
        },
    )
    session.add(reply)
    await session.commit()

    return AskResponse(
        chat_id=chat.id,
        message_id=reply.id,
        status=result.status,
        language=result.language,
        answer=result.answer,
        citations=result.citations,
        consult_scholar=result.consult_scholar,
        disclaimer=result.disclaimer,
    )


@router.get("/references/{ref_key}", response_model=SourceOut)
async def get_reference(ref_key: str, session: AsyncSession = Depends(get_session)) -> SourceOut:
    src = (await session.execute(select(Source).where(Source.ref_key == ref_key))).scalar_one_or_none()
    if src is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reference not found")
    return SourceOut(
        ref_key=src.ref_key, kind=src.kind.value, label=src.label, arabic=src.arabic,
        translations=src.translations, grade=src.grade, attribution=src.attribution,
        source_url=src.source_url,
    )


@router.get("/chats", response_model=list[ChatSummary])
async def list_chats(
    user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> list[ChatSummary]:
    rows = await session.execute(
        select(Chat).where(Chat.user_id == user.id).order_by(Chat.created_at.desc()).limit(100)
    )
    return [ChatSummary(id=c.id, title=c.title, created_at=c.created_at) for c in rows.scalars()]


def _public_meta(meta: dict) -> dict:
    return {k: v for k, v in meta.items() if k != "problems"}


@router.get("/chats/{chat_id}", response_model=ChatDetail)
async def get_chat(
    chat_id: str, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> ChatDetail:
    chat = (
        await session.execute(
            select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.messages))
        )
    ).scalar_one_or_none()
    if chat is None or chat.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    return ChatDetail(
        id=chat.id, title=chat.title, created_at=chat.created_at,
        messages=[
            MessageOut(id=m.id, role=m.role, content=m.content, meta=_public_meta(m.meta),
                       created_at=m.created_at)
            for m in chat.messages
        ],
    )


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def report_answer(
    req: ReportRequest, user: User = Depends(current_user), session: AsyncSession = Depends(get_session)
) -> dict:
    msg = await session.get(Message, req.message_id)
    if msg is None or msg.role != "assistant":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Answer not found")
    chat = await session.get(Chat, msg.chat_id)
    if chat is None or chat.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Answer not found")
    report = Report(message_id=msg.id, user_id=user.id, reason=req.reason.value, details=req.details)
    session.add(report)
    await session.commit()
    return {"id": report.id, "status": "received"}


@router.get("/about")
async def about() -> dict:
    return {
        "scope": "Sunni guidance from the Quran and Sahih hadith, covering all four schools "
                 "(Hanafi, Shafi'i, Maliki, Hanbali). Shia fiqh is not covered.",
        "sources": ["Quran (Tanzil / Quran Foundation)", "Sahih al-Bukhari", "Sahih Muslim"],
        "answer_statuses": [s.value for s in AnswerStatus],
    }
