import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256"
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

import pytest

from app.rag.generator import AnswerOut, CitationDraft, RewriteOut
from app.rag.retriever import Passage

FASTING_AYAH = Passage(
    ref_key="quran:2:183",
    kind="quran",
    label="Surah Al-Baqarah 2:183",
    arabic="يَا أَيُّهَا الَّذِينَ آمَنُوا كُتِبَ عَلَيْكُمُ الصِّيَامُ كَمَا كُتِبَ عَلَى الَّذِينَ مِن قَبْلِكُمْ لَعَلَّكُمْ تَتَّقُونَ",
    translations={"en": {"text": "O you who have believed, decreed upon you is fasting as it was decreed "
                               "upon those before you that you may become righteous.",
                         "translator": "Sahih International"}},
)
FASTING_HADITH = Passage(
    ref_key="bukhari:1903",
    kind="hadith",
    label="Sahih al-Bukhari 1903",
    arabic=None,
    translations={"en": {"text": "Whoever does not give up false statements and evil deeds, Allah is "
                               "not in need of his leaving his food and drink."}},
    grade="Sahih",
)


class FakeRetriever:
    def __init__(self, passages):
        self.passages = passages
        self.queries = None

    async def search(self, queries, top_k):
        self.queries = queries
        return self.passages


class FakeGenerator:
    """Returns queued answers in order; records feedback it was given."""

    def __init__(self, answers, rewrite=None):
        self.answers = list(answers)
        self.rewrite_out = rewrite
        self.feedback = []

    async def rewrite(self, question):
        return self.rewrite_out

    async def answer(self, question, language, passages, feedback=None):
        self.feedback.append(feedback)
        return self.answers.pop(0) if self.answers else None


def good_answer() -> AnswerOut:
    return AnswerOut(
        status="answered",
        answer="Fasting in Ramadan is obligatory [1]. Avoid false speech while fasting [2].",
        citations=[
            CitationDraft(ref_key="quran:2:183", quote="decreed upon you is fasting"),
            CitationDraft(ref_key="bukhari:1903"),
        ],
        consult_scholar=False,
    )


@pytest.fixture
def passages():
    return [FASTING_AYAH, FASTING_HADITH]


__all__ = ["FakeGenerator", "FakeRetriever", "RewriteOut", "good_answer"]
