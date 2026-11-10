from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Language(str, Enum):
    en = "en"
    ur = "ur"  # Urdu script
    roman_ur = "roman_ur"  # Urdu written in Latin letters
    ar = "ar"


class AnswerStatus(str, Enum):
    answered = "answered"
    no_answer = "no_answer"  # nothing reliable in our library
    out_of_scope = "out_of_scope"  # e.g. Shia fiqh, non-religious, abusive


class CitationOut(BaseModel):
    index: int  # matches [n] markers in the answer text
    ref_key: str
    label: str
    kind: str
    quote: str | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)
    chat_id: str | None = None
    language: Language | None = None  # None = detect from the question


class AskResponse(BaseModel):
    chat_id: str
    message_id: str
    status: AnswerStatus
    language: Language
    answer: str
    citations: list[CitationOut]
    consult_scholar: bool
    disclaimer: str


class SourceOut(BaseModel):
    ref_key: str
    kind: str
    label: str
    arabic: str | None
    translations: dict
    grade: str | None
    attribution: str
    source_url: str | None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    meta: dict
    created_at: datetime


class ChatSummary(BaseModel):
    id: str
    title: str
    created_at: datetime


class ChatDetail(ChatSummary):
    messages: list[MessageOut]


class ReportReason(str, Enum):
    wrong_reference = "wrong_reference"
    wrong_answer = "wrong_answer"
    sectarian = "sectarian"
    other = "other"


class ReportRequest(BaseModel):
    message_id: str
    reason: ReportReason
    details: str | None = Field(default=None, max_length=2000)


class TokenResponse(BaseModel):
    access_token: str
    user_id: str
