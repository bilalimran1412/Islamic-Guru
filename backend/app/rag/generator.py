"""Claude calls: query rewriting and grounded answer generation."""

import logging
from typing import Literal, Protocol

import anthropic
from pydantic import BaseModel

from app.config import Settings
from app.rag.prompts import ANSWER_SYSTEM, REWRITE_SYSTEM
from app.rag.retriever import Passage

log = logging.getLogger(__name__)

# Server-side fallback: if the model declines a request, the API retries it on a
# fallback model chosen by refusal category, inside the same call.
_BETAS = ["server-side-fallback-2026-07-01"]


class RewriteOut(BaseModel):
    language: Literal["en", "ur", "roman_ur", "ar"]
    search_queries: list[str]
    in_scope: bool
    sensitive: bool


class CitationDraft(BaseModel):
    ref_key: str
    quote: str | None = None


class AnswerOut(BaseModel):
    status: Literal["answered", "no_answer", "out_of_scope"]
    answer: str
    citations: list[CitationDraft]
    consult_scholar: bool


class Generator(Protocol):
    async def rewrite(self, question: str) -> RewriteOut | None: ...

    async def answer(
        self, question: str, language: str, passages: list[Passage], feedback: list[str] | None = None,
        madhhab: str | None = None,
    ) -> AnswerOut | None: ...


def format_sources(passages: list[Passage]) -> str:
    parts = ["<sources>"]
    for p in passages:
        parts.append(f'<source ref_key="{p.ref_key}" label="{p.label}" kind="{p.kind}"'
                     + (f' grade="{p.grade}"' if p.grade else "")
                     + (f' madhhab="{p.madhhab}"' if p.madhhab else "") + ">")
        if p.arabic:
            parts.append(f"<arabic>{p.arabic}</arabic>")
        for lang, t in p.translations.items():
            body = t.get("text") if isinstance(t, dict) else t
            if body:
                parts.append(f'<translation lang="{lang}">{body}</translation>')
        parts.append("</source>")
    parts.append("</sources>")
    return "\n".join(parts)


class ClaudeGenerator:
    def __init__(self, settings: Settings, client: anthropic.AsyncAnthropic | None = None):
        self._s = settings
        self._client = client or anthropic.AsyncAnthropic()

    async def _parse(self, *, system: str, content: str, output_format, effort: str, max_tokens: int):
        try:
            resp = await self._client.beta.messages.parse(
                model=self._s.answer_model,
                max_tokens=max_tokens,
                betas=_BETAS,
                fallbacks="default",
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": content}],
                output_config={"effort": effort},
                output_format=output_format,
            )
        except anthropic.RateLimitError:
            log.warning("Claude rate limited")
            raise
        except anthropic.APIStatusError as e:
            log.error("Claude API error %s: %s", e.status_code, e.message)
            return None
        except anthropic.APIConnectionError:
            log.error("Could not reach the Claude API")
            return None
        if resp.stop_reason == "refusal":
            log.warning("Claude declined the request (all fallbacks)")
            return None
        if resp.stop_reason == "max_tokens":
            log.warning("Claude output hit max_tokens")
            return None
        return resp.parsed_output

    async def rewrite(self, question: str) -> RewriteOut | None:
        return await self._parse(
            system=REWRITE_SYSTEM,
            content=f"<question>{question}</question>",
            output_format=RewriteOut,
            effort=self._s.rewrite_effort,
            max_tokens=4000,
        )

    async def answer(
        self, question: str, language: str, passages: list[Passage], feedback: list[str] | None = None,
        madhhab: str | None = None,
    ) -> AnswerOut | None:
        content = f"{format_sources(passages)}\n\n<reply_language>{language}</reply_language>\n"
        if madhhab:
            content += f"<user_school>{madhhab}</user_school>\n"
        content += f"<question>{question}</question>"
        if feedback:
            problems = "\n".join(f"- {p}" for p in feedback)
            content += (
                "\n\nA previous draft failed the reference check for these reasons:\n"
                f"{problems}\nWrite a corrected answer that follows the rules exactly."
            )
        return await self._parse(
            system=ANSWER_SYSTEM,
            content=content,
            output_format=AnswerOut,
            effort=self._s.answer_effort,
            max_tokens=16000,
        )
