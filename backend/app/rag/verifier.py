"""Reference checker: the last gate before an answer reaches a user.

An answer passes only if:
1. it cites at least one source (no source, no answer),
2. every cited ref_key is one of the passages we retrieved from our library
   (so the model can't cite something it was never shown),
3. every quote matches the stored text of that source after normalisation
   (so a real hadith number can't carry made-up wording), and
4. every [n] marker in the answer text points at an existing citation.
"""

import re
from dataclasses import dataclass, field

from app.rag.retriever import Passage
from app.rag.text import quote_matches

_MARKER = re.compile(r"\[(\d+)\]")


@dataclass
class DraftCitation:
    ref_key: str
    quote: str | None = None


@dataclass
class VerificationResult:
    ok: bool
    problems: list[str] = field(default_factory=list)


def verify(answer: str, citations: list[DraftCitation], passages: list[Passage]) -> VerificationResult:
    problems: list[str] = []
    by_key = {p.ref_key: p for p in passages}

    if not citations:
        problems.append("The answer cites no sources.")

    for i, c in enumerate(citations, start=1):
        passage = by_key.get(c.ref_key)
        if passage is None:
            problems.append(f"Citation [{i}] '{c.ref_key}' is not one of the provided sources.")
            continue
        if c.quote and not quote_matches(c.quote, *passage.all_texts()):
            problems.append(
                f"Citation [{i}] quote does not match the stored text of {passage.label}. "
                "Quote the source text exactly or omit the quote."
            )

    markers = {int(m) for m in _MARKER.findall(answer)}
    for m in sorted(markers):
        if m < 1 or m > len(citations):
            problems.append(f"Marker [{m}] in the answer has no matching citation.")
    if citations and not markers:
        problems.append("The answer text has no [n] markers linking statements to citations.")

    return VerificationResult(ok=not problems, problems=problems)
