import pytest
from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.deps import get_pipeline
from app.main import app
from app.models import Source, SourceKind
from app.rag.pipeline import AnswerPipeline
from tests.conftest import FakeGenerator, FakeRetriever, good_answer


@pytest.fixture
async def client(passages):
    await init_db()
    async with SessionLocal() as s:
        if not await s.get(Source, 1):
            s.add(Source(id=1, ref_key="quran:2:183", kind=SourceKind.quran, collection="quran",
                         label="Surah Al-Baqarah 2:183", arabic=passages[0].arabic,
                         translations=passages[0].translations, attribution="Tanzil (CC BY 3.0)"))
            await s.commit()
    app.dependency_overrides[get_pipeline] = lambda: AnswerPipeline(
        FakeRetriever(passages), FakeGenerator([good_answer()] * 50), get_settings())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        token = (await c.post("/v1/auth/guest")).json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"
        yield c
    app.dependency_overrides.clear()


async def test_ask_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        assert (await c.post("/v1/ask", json={"question": "hi there"})).status_code == 401


async def test_ask_history_and_report(client):
    r = await client.post("/v1/ask", json={"question": "Is fasting obligatory?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "answered"
    assert body["citations"][0]["ref_key"] == "quran:2:183"

    r2 = await client.post("/v1/ask", json={"question": "And for travellers?", "chat_id": body["chat_id"]})
    assert r2.json()["chat_id"] == body["chat_id"]

    chats = (await client.get("/v1/chats")).json()
    assert len(chats) == 1
    detail = (await client.get(f"/v1/chats/{body['chat_id']}")).json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant", "user", "assistant"]
    assert "problems" not in detail["messages"][1]["meta"]

    rep = await client.post("/v1/reports", json={"message_id": body["message_id"], "reason": "wrong_reference"})
    assert rep.status_code == 201


async def test_reference_lookup(client):
    r = await client.get("/v1/references/quran:2:183")
    assert r.status_code == 200
    assert r.json()["attribution"].startswith("Tanzil")
    assert (await client.get("/v1/references/bukhari:0")).status_code == 404


async def test_daily_limit(client):
    limit = get_settings().daily_free_questions
    for _ in range(limit):
        assert (await client.post("/v1/ask", json={"question": "Is fasting obligatory?"})).status_code == 200
    assert (await client.post("/v1/ask", json={"question": "Is fasting obligatory?"})).status_code == 429
