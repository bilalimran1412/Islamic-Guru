"""Text normalisation used to compare quotes with stored source text.

Quotes are compared after removing Arabic diacritics (tashkeel), tatweel,
punctuation and case, and unifying common letter variants, so a correctly
quoted passage still matches when the model drops harakat or punctuation.
"""

import re
import unicodedata

_ARABIC_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_LETTER_VARIANTS = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
        "ى": "ي",
        "ی": "ي",  # Urdu/Persian yeh
        "ے": "ي",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }
)
_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = _ARABIC_DIACRITICS.sub("", text)
    text = text.translate(_LETTER_VARIANTS)
    text = _NON_WORD.sub(" ", text.lower())
    return _SPACES.sub(" ", text).strip()


def quote_matches(quote: str, *candidates: str | None, min_chars: int = 12) -> bool:
    """True if `quote` appears (after normalisation) in any candidate text.

    Very short quotes are rejected because they would match almost anything.
    """
    q = normalize(quote)
    if len(q) < min_chars:
        return False
    return any(c and q in normalize(c) for c in candidates)
