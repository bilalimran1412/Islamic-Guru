from app.config import get_settings
from app.rag.generator import AnswerOut, CitationDraft, RewriteOut
from app.rag.pipeline import AnswerPipeline
from app.schemas import AnswerStatus, Language
from tests.conftest import FakeGenerator, FakeRetriever, good_answer


def make(passages, answers, rewrite=None):
    gen = FakeGenerator(answers, rewrite)
    return AnswerPipeline(FakeRetriever(passages), gen, get_settings()), gen


async def test_verified_answer_is_returned(passages):
    p, _ = make(passages, [good_answer()])
    r = await p.run("Is fasting obligatory?")
    assert r.status == AnswerStatus.answered
    assert [c.label for c in r.citations] == ["Surah Al-Baqarah 2:183", "Sahih al-Bukhari 1903"]
    assert r.disclaimer


async def test_no_passages_means_no_answer():
    p, gen = make([], [good_answer()])
    r = await p.run("Something obscure")
    assert r.status == AnswerStatus.no_answer
    assert r.consult_scholar
    assert gen.feedback == []  # generator never called


async def test_failed_check_is_retried_with_feedback(passages):
    bad = AnswerOut(status="answered", answer="Claim [1].",
                    citations=[CitationDraft(ref_key="bukhari:5555")], consult_scholar=False)
    p, gen = make(passages, [bad, good_answer()])
    r = await p.run("Is fasting obligatory?")
    assert r.status == AnswerStatus.answered
    assert gen.feedback[0] is None
    assert "not one of the provided sources" in gen.feedback[1][0]


async def test_two_failed_checks_never_show_unverified_answer(passages):
    bad = AnswerOut(status="answered", answer="Claim [1].",
                    citations=[CitationDraft(ref_key="bukhari:5555")], consult_scholar=False)
    p, _ = make(passages, [bad, bad])
    r = await p.run("Is fasting obligatory?")
    assert r.status == AnswerStatus.no_answer
    assert "bukhari:5555" not in r.answer
    assert r.problems


async def test_rewrite_sets_language_and_queries(passages):
    rw = RewriteOut(language="roman_ur", search_queries=["obligation of fasting"], in_scope=True,
                    sensitive=False)
    retriever = FakeRetriever(passages)
    p = AnswerPipeline(retriever, FakeGenerator([good_answer()], rw), get_settings())
    r = await p.run("roza farz hai kya?")
    assert r.language == Language.roman_ur
    assert "obligation of fasting" in retriever.queries
    assert r.disclaimer.startswith("Yeh")


async def test_sensitive_topic_always_recommends_scholar(passages):
    p, _ = make(passages, [good_answer()])
    r = await p.run("What happens after talaq while fasting?")
    assert r.consult_scholar


async def test_out_of_scope(passages):
    oos = AnswerOut(status="out_of_scope", answer="This app covers Sunni guidance only.", citations=[],
                    consult_scholar=False)
    p, _ = make(passages, [oos])
    r = await p.run("Tell me why group X is wrong")
    assert r.status == AnswerStatus.out_of_scope


async def test_ai_outage_is_reported_as_service_error(passages):
    p, _ = make(passages, [])  # generator returns None
    r = await p.run("Is fasting obligatory?")
    assert r.service_error
