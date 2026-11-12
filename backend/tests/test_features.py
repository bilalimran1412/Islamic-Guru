"""Sign-in linking, profile/maslak, fatawa review + library, Ask a Scholar, premium plan, admin auth."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api import account
from app.api.admin import html_to_text
from app.config import get_settings
from app.db import SessionLocal, init_db
from app.deps import get_pipeline
from app.main import app
from app.models import Fatwa
from app.oauth import VerifiedIdentity
from app.rag.pipeline import AnswerPipeline
from tests.conftest import FakeGenerator, FakeRetriever, good_answer

ADMIN = {"X-Admin-Key": "test-admin-key", "X-Reviewer": "Mufti Test"}


@pytest.fixture
async def ctx(passages):
    await init_db()
    gen = FakeGenerator([good_answer()] * 50)
    app.dependency_overrides[get_pipeline] = lambda: AnswerPipeline(FakeRetriever(passages), gen, get_settings())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = (await c.post("/v1/auth/guest")).json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"
        yield c, gen
    app.dependency_overrides.clear()


async def test_sign_in_links_guest_and_keeps_history(ctx, monkeypatch):
    c, _ = ctx
    monkeypatch.setattr(account, "verify_id_token",
                        lambda p, t, s: VerifiedIdentity(p, "google-sub-1", "a@example.com", "Ali"))
    await c.post("/v1/ask", json={"question": "Is fasting obligatory?"})
    guest_id = (await c.get("/v1/me")).json()["user_id"]

    r = await c.post("/v1/auth/google", json={"id_token": "x"})
    assert r.status_code == 200
    assert r.json()["user_id"] == guest_id  # guest account upgraded in place

    # A second device: new guest signs in with the same Google account -> its chats move over.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c2:
        t2 = (await c2.post("/v1/auth/guest")).json()["access_token"]
        c2.headers["Authorization"] = f"Bearer {t2}"
        await c2.post("/v1/ask", json={"question": "And for travellers?"})
        r2 = await c2.post("/v1/auth/google", json={"id_token": "x"})
        assert r2.json()["user_id"] == guest_id
        c2.headers["Authorization"] = f"Bearer {r2.json()['access_token']}"
        assert len((await c2.get("/v1/chats")).json()) == 2


async def test_sign_in_not_configured_returns_503(ctx):
    c, _ = ctx
    r = await c.post("/v1/auth/apple", json={"id_token": "x"})
    assert r.status_code == 503


async def test_maslak_setting_reaches_the_answer_prompt(ctx):
    c, gen = ctx
    r = await c.patch("/v1/me", json={"madhhab": "hanafi", "preferred_language": "ur"})
    assert r.json()["madhhab"] == "hanafi"
    await c.post("/v1/ask", json={"question": "Witr kaise parhein?"})
    assert gen.madhhab == "hanafi"
    r = await c.patch("/v1/me", json={"clear_madhhab": True})
    assert r.json()["madhhab"] is None


async def test_admin_requires_key(ctx):
    c, _ = ctx
    assert (await c.get("/v1/admin/stats")).status_code == 401
    assert (await c.get("/v1/admin/stats", headers={"X-Admin-Key": "test-admin-key"})).status_code == 400
    assert (await c.get("/v1/admin/stats", headers=ADMIN)).status_code == 200
    assert (await c.get("/admin")).status_code == 200


async def test_fatwa_review_flow(ctx):
    c, _ = ctx
    async with SessionLocal() as s:
        f = Fatwa(publisher="Test Darul Ifta", title="Zakat on gold", question="Is zakat due on jewellery?",
                  answer="<p>Yes, when it reaches nisab.</p>", language="en",
                  original_url="https://example.org/fatwa/zakat-gold")
        s.add(f)
        await s.commit()
        fid = f.id

    assert (await c.get(f"/v1/fatwas/{fid}")).status_code == 404  # pending: not public
    pending = (await c.get("/v1/admin/fatwas", headers=ADMIN)).json()
    assert any(p["id"] == fid and p["answer"] == "Yes, when it reaches nisab." for p in pending)

    r = await c.post(f"/v1/admin/fatwas/{fid}/approve", headers=ADMIN, json={"madhhab": "hanafi"})
    assert r.json()["ref_key"] == f"fatwa:{fid}"

    lib = (await c.get("/v1/fatwas", params={"q": "zakat"})).json()
    assert lib[0]["madhhab"] == "hanafi"
    ref = (await c.get(f"/v1/references/fatwa:{fid}")).json()
    assert ref["kind"] == "fatwa" and ref["source_url"] == "https://example.org/fatwa/zakat-gold"
    assert "used with permission" in ref["attribution"]

    await c.post(f"/v1/admin/fatwas/{fid}/reject", headers=ADMIN)
    assert (await c.get(f"/v1/references/fatwa:{fid}")).status_code == 404


async def test_ask_a_scholar_and_premium(ctx):
    c, _ = ctx
    me = (await c.get("/v1/me")).json()
    q = (await c.post("/v1/scholar-questions", json={"question": "A personal question about my inheritance."})).json()
    assert q["status"] == "awaiting_payment"  # free plan

    await c.post(f"/v1/admin/users/{me['user_id']}/plan", headers=ADMIN, json={"plan": "premium", "days": 30})
    assert (await c.get("/v1/me")).json()["premium_active"]

    q2 = (await c.post("/v1/scholar-questions", json={"question": "Another personal question for a scholar."})).json()
    assert q2["status"] == "pending"
    pending = (await c.get("/v1/admin/scholar-questions", headers=ADMIN)).json()
    assert any(p["id"] == q2["id"] for p in pending)

    await c.post(f"/v1/admin/scholar-questions/{q2['id']}/answer", headers=ADMIN, json={"answer": "Wa alaikum..."})
    mine = {x["id"]: x for x in (await c.get("/v1/scholar-questions")).json()}
    assert mine[q2["id"]]["status"] == "answered"
    assert mine[q2["id"]]["scholar_name"] == "Mufti Test"

    # Premium: no daily limit
    for _ in range(get_settings().daily_free_questions + 2):
        assert (await c.post("/v1/ask", json={"question": "Is fasting obligatory?"})).status_code == 200


async def test_report_review(ctx):
    c, _ = ctx
    ans = (await c.post("/v1/ask", json={"question": "Is fasting obligatory?"})).json()
    await c.post("/v1/reports", json={"message_id": ans["message_id"], "reason": "wrong_answer"})
    reports = (await c.get("/v1/admin/reports", headers=ADMIN)).json()
    mine = [r for r in reports if r["answer"] == ans["answer"] and r["question"] == "Is fasting obligatory?"]
    assert mine
    r = await c.patch(f"/v1/admin/reports/{mine[0]['id']}", headers=ADMIN, json={"status": "dismissed"})
    assert r.json()["status"] == "dismissed"


def test_html_to_text():
    assert html_to_text("<p>One &amp; two</p><p>Three</p>") == "One & two\n\nThree"


async def test_apple_android_callback_redirects_to_app(ctx):
    c, _ = ctx
    r = await c.post("/v1/auth/apple/callback", data={"code": "abc", "id_token": "tok"})
    assert r.status_code == 307
    loc = r.headers["location"]
    assert loc.startswith("intent://callback?code=abc&id_token=tok")
    assert "package=com.islamicguru.islamic_guru" in loc
