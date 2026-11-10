"""Cheap, offline language detection for routing and for the reply language.

The query-rewrite step (see `generator.rewrite_query`) refines this, but we
need a guess before any model call and as a fallback when that call fails.
"""

import re

from app.schemas import Language

_ARABIC_SCRIPT = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
# Letters used in Urdu but not in Arabic.
_URDU_ONLY = re.compile(r"[ٹڈڑںھہےۓگچپژک]")

# Roman Urdu function words. Religious terms (namaz, haram, zakat...) are left out on
# purpose: English-speaking Muslims use them too, so they say nothing about language.
_ROMAN_URDU_WORDS = {
    "kya", "kia", "hai", "hain", "hy", "ka", "ki", "ke", "ko", "se", "mein", "mai",
    "kaise", "kaisay", "kese", "kyun", "kyon", "nahi", "nahin", "nai", "karna", "karte",
    "krna", "krte", "karein", "chahiye", "chahye", "agar", "aur", "bhi", "wala", "wali",
    "sakte", "sakta", "sakti", "tha", "thi", "hota", "hoti", "hum", "ham", "aap", "ap",
    "mujhe", "mera", "meri", "hamein", "tareeqa", "tarika", "masla", "hukum", "batain",
    "bataen", "btayen", "kitni", "kitne", "kab", "kahan", "jab", "phir", "lekin",
}


def detect_language(text: str) -> Language:
    if _ARABIC_SCRIPT.search(text):
        return Language.ur if _URDU_ONLY.search(text) else Language.ar
    words = re.findall(r"[a-zA-Z]+", text.lower())
    if not words:
        return Language.en
    hits = sum(1 for w in words if w in _ROMAN_URDU_WORDS)
    # Two hits, or a high share of short texts, is a strong Roman Urdu signal.
    if hits >= 2 or (hits >= 1 and len(words) <= 4):
        return Language.roman_ur
    return Language.en
