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

## Before production

- Replace `init_db()` table creation with Alembic migrations.
- Admin screen for scholars: review queue for reports and pending fatawa.
- Rate limiting per IP on `/v1/auth/guest`.
- Bundle fonts (Amiri, Noto Nastaliq Urdu) in the app instead of fetching them at runtime.
- Build the ~300-question scholar test set and run it before every release.
