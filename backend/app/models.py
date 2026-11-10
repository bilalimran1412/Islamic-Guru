"""Database tables.

`sources` is the verified library: every Quran ayah, hadith and approved fatwa
the AI is allowed to cite. A citation is only shown to a user if its `ref_key`
exists here and the quoted text matches what is stored.
"""

import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import get_settings
from app.db import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")
EmbeddingType = Vector(get_settings().embedding_dim).with_variant(JSON(), "sqlite")


def _uuid() -> str:
    return str(uuid.uuid4())


class SourceKind(str, enum.Enum):
    quran = "quran"
    hadith = "hadith"
    fatwa = "fatwa"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Stable citation key, e.g. "quran:2:183", "bukhari:1903", "fatwa:<publisher>:<id>"
    ref_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    kind: Mapped[SourceKind] = mapped_column(Enum(SourceKind), index=True)
    collection: Mapped[str] = mapped_column(String(60))  # "quran", "bukhari", "muslim", publisher slug
    # Human-readable label, e.g. "Sahih al-Bukhari 1903" or "Surah Al-Baqarah 2:183"
    label: Mapped[str] = mapped_column(String(200))
    arabic: Mapped[str | None] = mapped_column(Text)
    # {"en": {"text": ..., "translator": ...}, "ur": {...}}
    translations: Mapped[dict] = mapped_column(JsonType, default=dict)
    grade: Mapped[str | None] = mapped_column(String(60))  # hadith grading, e.g. "Sahih"
    attribution: Mapped[str] = mapped_column(String(300))  # licence / credit line shown in the app
    source_url: Mapped[str | None] = mapped_column(String(500))
    embedding = mapped_column(EmbeddingType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FatwaStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Fatwa(Base):
    """Fatawa pulled from partner sites. Only approved ones are copied into `sources`."""

    __tablename__ = "fatwas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    publisher: Mapped[str] = mapped_column(String(120))  # Darul Ifta / website
    scholar: Mapped[str | None] = mapped_column(String(200))
    madhhab: Mapped[str | None] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(500))
    question: Mapped[str | None] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)  # original text, never edited
    language: Mapped[str] = mapped_column(String(10))
    original_url: Mapped[str] = mapped_column(String(500), unique=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[FatwaStatus] = mapped_column(Enum(FatwaStatus), default=FatwaStatus.pending)
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    madhhab: Mapped[str | None] = mapped_column(String(40))  # Phase 2 setting
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat", order_by="Message.created_at", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chat_id: Mapped[str] = mapped_column(ForeignKey("chats.id"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    # For assistant messages: status, citations, language, flags
    meta: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chat: Mapped[Chat] = relationship(back_populates="messages")


class ReportStatus(str, enum.Enum):
    open = "open"
    confirmed_wrong = "confirmed_wrong"
    dismissed = "dismissed"


class Report(Base):
    """A user flagged an answer as wrong. Feeds the scholar review queue."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    reason: Mapped[str] = mapped_column(String(40))
    details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyUsage(Base):
    __tablename__ = "daily_usage"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)  # YYYY-MM-DD
    questions: Mapped[int] = mapped_column(Integer, default=0)
