# Architecture

```
Flutter app ──HTTPS──> FastAPI ──> answer pipeline ──> Claude API
                          │              │
                          │              └── Postgres + pgvector (`sources`)
                          └── users, chats, messages, reports, daily_usage, fatwas
```

## Backend layout (`backend/app`)

| File | Role |
|---|---|
| `api/routes.py` | `/v1/auth/guest`, `/v1/ask`, `/v1/references/{ref_key}`, `/v1/chats`, `/v1/reports`, `/v1/about` |
| `api/account.py` | `/v1/auth/google`, `/v1/auth/apple` (+ Android callback), `/v1/me` (language, maslak) |
| `api/library.py` | `/v1/fatwas`: approved fatawa only |
| `api/scholar.py` | `/v1/scholar-questions`: Ask a Scholar |
| `api/admin.py` | `/v1/admin/*` for the review page (`static/admin.html`, served at `/admin`) |
| `oauth.py` | Verifies Google / Apple ID tokens against their public keys |
| `rag/language.py` | Offline language guess (en / ur / roman_ur / ar) |
| `rag/generator.py` | Claude calls: query rewrite and grounded answer, both with structured output |
| `rag/retriever.py` | pgvector search (with Voyage embeddings) or Postgres full-text fallback |
| `rag/verifier.py` | Reference checker, the last gate before an answer is shown |
| `rag/pipeline.py` | Ties the steps together; retries once on a failed check; never returns an unchecked answer |
| `rag/prompts.py` | System prompts, disclaimers and "no answer" texts per language |
| `models.py` | Tables. `sources.ref_key` (e.g. `quran:2:183`, `bukhari:1903`) is the citation key |

## Data scripts (`backend/scripts`)

| Script | Purpose |
|---|---|
| `import_quran.py` | Tanzil Arabic text + translation files |
| `import_hadith.py` | Bukhari and Muslim from the open hadith-api dataset |
| `embed_sources.py` | Fill `sources.embedding` (Voyage) |
| `import_fatwa_feed.py` | Partner RSS/Atom feed into the fatwa review queue |

## Database migrations

Schema changes: edit `app/models.py`, then from `backend/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

The Docker image runs `alembic upgrade head` on start.

## Before production

- Rate limiting per IP on `/v1/auth/guest` (e.g. at the reverse proxy).
- Individual scholar accounts instead of one shared admin key once the panel grows.
- Store billing (Google Play / App Store) for premium and Ask a Scholar.
- Build the ~300-question scholar test set and run it before every release.
