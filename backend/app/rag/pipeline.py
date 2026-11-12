"""Question -> verified answer.

    detect language -> rewrite query -> search library -> generate -> verify
                                             |                          |
                                       nothing found            fails twice
                                             v                          v
                                         "no answer"               "no answer"
"""

import logging
from dataclasses import dataclass, field

from app.config import Settings
from app.rag.generator import Generator
from app.rag.language import detect_language
from app.rag.prompts import DISCLAIMERS, NO_ANSWER
from app.rag.retriever import Passage, Retriever
from app.rag.verifier import DraftCitation, verify
from app.schemas import AnswerStatus, CitationOut, Language

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

# Backup for the model's `sensitive` flag: these topics always recommend a scholar.
_SENSITIVE_TERMS = (
    "talaq", "divorce", "طلاق", "khula", "inherit", "wirasat", "virasat", "وراثت", "میراث",
    "takfir", "kafir", "کافر", "apostasy", "murtad", "custody", "halala", "حلالہ",
)


@dataclass
class PipelineResult:
    status: AnswerStatus
    language: Language
    answer: str
    citations: list[CitationOut] = field(default_factory=list)
    consult_scholar: bool = False
    disclaimer: str = ""
    problems: list[str] = field(default_factory=list)  # for logs / review, not shown to users
    service_error: bool = False  # the AI service failed; nothing was answered


class AnswerPipeline:
    def __init__(self, retriever: Retriever, generator: Generator, settings: Settings):
        self._retriever = retriever
        self._generator = generator
        self._settings = settings

    def _result(self, status: AnswerStatus, lang: Language, answer: str, **kw) -> PipelineResult:
        return PipelineResult(status=status, language=lang, answer=answer,
                              disclaimer=DISCLAIMERS[lang.value], **kw)

    async def run(
        self, question: str, language: Language | None = None, madhhab: str | None = None
    ) -> PipelineResult:
        lang = language or detect_language(question)
        sensitive = any(t in question.lower() for t in _SENSITIVE_TERMS)

        rewrite = await self._generator.rewrite(question)
        queries = [question]
        if rewrite:
            if language is None:
                lang = Language(rewrite.language)
            sensitive = sensitive or rewrite.sensitive
            queries += rewrite.search_queries

        passages: list[Passage] = await self._retriever.search(queries, self._settings.retrieval_top_k)
        if not passages:
            return self._result(AnswerStatus.no_answer, lang, NO_ANSWER[lang.value],
                                consult_scholar=True, problems=["no passages retrieved"])

        feedback: list[str] | None = None
        problems: list[str] = []
        for attempt in range(1, MAX_ATTEMPTS + 1):
            draft = await self._generator.answer(question, lang.value, passages, feedback, madhhab=madhhab)
            if draft is None:
                if attempt == 1:
                    return self._result(AnswerStatus.no_answer, lang, NO_ANSWER[lang.value],
                                        service_error=True, problems=["generation failed"])
                problems.append(f"attempt {attempt}: generation failed")
                break

            if draft.status == "out_of_scope":
                return self._result(AnswerStatus.out_of_scope, lang, draft.answer)
            if draft.status == "no_answer":
                return self._result(AnswerStatus.no_answer, lang, draft.answer or NO_ANSWER[lang.value],
                                    consult_scholar=True)

            cites = [DraftCitation(c.ref_key, c.quote) for c in draft.citations]
            check = verify(draft.answer, cites, passages)
            if check.ok:
                by_key = {p.ref_key: p for p in passages}
                return self._result(
                    AnswerStatus.answered, lang, draft.answer,
                    citations=[
                        CitationOut(index=i, ref_key=c.ref_key, label=by_key[c.ref_key].label,
                                    kind=by_key[c.ref_key].kind, quote=c.quote)
                        for i, c in enumerate(cites, start=1)
                    ],
                    consult_scholar=draft.consult_scholar or sensitive,
                )
            log.warning("Reference check failed (attempt %d): %s", attempt, check.problems)
            problems += [f"attempt {attempt}: {p}" for p in check.problems]
            feedback = check.problems

        # Never show an unverified answer.
        return self._result(AnswerStatus.no_answer, lang, NO_ANSWER[lang.value],
                            consult_scholar=True, problems=problems)
