# Islamic Guru

A chat app where Muslims ask everyday questions about Islam and get answers drawn
only from the Quran and Sahih hadith, with every answer citing its source.

| Folder | What it is |
|---|---|
| `mobile/` | Flutter app (Android first, iOS from the same code) |
| `backend/` | Python FastAPI API: answer pipeline, reference checker, chats, reports |
| `docs/` | Phase plan, architecture, decisions, deployment |

## How an answer is made

1. **Detect language**: English, Urdu, Roman Urdu or Arabic.
2. **Rewrite the question** into English and Arabic search queries (Claude), so Roman Urdu
   questions still find the right texts.
3. **Search our library** (`sources` table: Quran ayahs, Bukhari, Muslim). No match means
   "no reliable answer, ask a scholar"; the AI is not called.
4. **Generate** an answer with Claude using only the passages found, with `[n]` markers and citations.
5. **Check every reference in code** (`backend/app/rag/verifier.py`): each cited source must be one
   we retrieved, and any quote must match the stored text. A failed check is retried once with
   the problems listed; if it fails again, the user gets "no reliable answer", never an unchecked one.

## Features

- **Chat** with citations you can tap to see the Arabic text, translation and grade.
- **Languages:** English, Urdu, Roman Urdu, Arabic. **Voice questions** (on-device speech recognition).
- **Maslak setting:** Hanafi, Shafi'i, Maliki, Hanbali or Ahl-e-Hadith first; or all side by side.
- **Fatawa library:** scholar-approved fatawa from partner sites, unchanged, with a link to the original.
- **Ask a Scholar:** personal questions answered by the panel.
- **Accounts:** guest by default; Google / Apple sign-in keeps history across devices.
- **Scholar review page** at `/admin`: reported answers, fatawa queue, scholar questions, premium grants.

See `docs/PHASES.md` for what is done and what is waiting on keys or accounts.

## Run locally

Needs Docker, Python 3.12+ and Flutter 3.47+.

```bash
cp backend/.env.example backend/.env   # then fill in ANTHROPIC_API_KEY, JWT_SECRET, ADMIN_API_KEY
docker compose up -d                   # Postgres + pgvector, and the API on :8000 (runs migrations)
```

Load the library (from `backend/`, with a local virtualenv and `pip install -r requirements-dev.txt`;
run `alembic upgrade head` first if the API hasn't started yet):

```bash
python -m scripts.import_quran --arabic data/raw/quran-uthmani.txt --translation "en|Saheeh International|data/raw/en.sahih.txt"
python -m scripts.import_hadith bukhari muslim
python -m scripts.embed_sources        # optional, needs VOYAGE_API_KEY; enables vector search
```

Run the app against the local API:

```bash
cd mobile && flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

## Tests

```bash
cd backend && pytest
cd mobile && flutter analyze && flutter test
```

Deployment: `docs/DEPLOY.md`.
