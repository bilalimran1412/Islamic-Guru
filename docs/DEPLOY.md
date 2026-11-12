# Deploying the backend

The API ships as one Docker image. On start it runs database migrations
(`alembic upgrade head`) and then serves on port 8000.

## 1. Server

Any small VPS works for the MVP (2 vCPU / 4 GB RAM), e.g. DigitalOcean, AWS Lightsail or
Google Cloud. Use a managed Postgres **with the pgvector extension** if you can
(DigitalOcean, AWS RDS, Google Cloud SQL and Supabase all support it); otherwise run the
`pgvector/pgvector:pg17` image from `docker-compose.yml`.

## 2. Configure

Copy `backend/.env.example` to `backend/.env` on the server and fill in:

| Setting | Where it comes from |
|---|---|
| `DATABASE_URL` | Your Postgres (`postgresql+asyncpg://user:pass@host:5432/db`) |
| `JWT_SECRET` | `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `ADMIN_API_KEY` | Another random string; give it only to panel scholars |
| `GOOGLE_CLIENT_IDS`, `APPLE_CLIENT_IDS` | See "Sign-in setup" below |

## 3. Run

```bash
docker compose up -d --build
```

Put HTTPS in front (Caddy is simplest: `your-domain { reverse_proxy localhost:8000 }`).
The app must use HTTPS in release builds.

## 4. Load the library (once, then when sources change)

```bash
docker compose exec api python -m scripts.import_hadith bukhari muslim
docker compose exec api python -m scripts.import_quran --arabic /data/quran-uthmani.txt \
    --translation "en|Saheeh International|/data/en.sahih.txt"
docker compose exec api python -m scripts.embed_sources   # if VOYAGE_API_KEY is set
```

(Mount the Tanzil files into the container at `/data`.)

Partner fatwa feeds, e.g. daily with cron:

```bash
docker compose exec api python -m scripts.import_fatwa_feed --publisher "Name" --feed https://... --language ur
```

## 5. Build the app against the server

```bash
cd mobile
flutter build appbundle --dart-define=API_BASE_URL=https://your-domain \
  --dart-define=GOOGLE_SERVER_CLIENT_ID=... --dart-define=APPLE_SERVICE_ID=... \
  --dart-define=APPLE_REDIRECT_URI=https://your-domain/v1/auth/apple/callback
```

## Sign-in setup

**Google**
1. Google Cloud Console → APIs & Services → Credentials.
2. Create an OAuth client of type **Web** (its ID is `GOOGLE_SERVER_CLIENT_ID` in the app).
3. Create an **Android** client with package `com.islamicguru.islamic_guru` and your signing key's SHA-1.
4. For iOS, create an **iOS** client, set `GOOGLE_IOS_CLIENT_ID`, and add its reversed client ID as a URL scheme in `ios/Runner/Info.plist`.
5. Put the Web (and iOS) client IDs in the backend's `GOOGLE_CLIENT_IDS`.

**Apple** (required on iOS once Google sign-in is offered there)
1. Apple Developer → Identifiers: enable "Sign in with Apple" on the app ID; add the capability in Xcode.
2. For Android, create a **Services ID**, set its return URL to `https://your-domain/v1/auth/apple/callback`.
3. Backend `APPLE_CLIENT_IDS` = `com.islamicguru.islamic_guru,<services id>`.

## Scholar review

Open `https://your-domain/admin`, enter your name and the admin key. Tabs:
reported answers, fatawa queue, Ask a Scholar questions, and plan grants
(premium for testers or sponsored users).
