# Phase plan

Status key: ✅ built · 🟡 built, needs keys/accounts/store setup to go live · ⬜ not started

## Phase 1: Android MVP (target: early Feb 2027)

| Item | Status | Notes |
|---|---|---|
| Chat Q&A with citations | ✅ | Needs `ANTHROPIC_API_KEY` for real answers |
| Code check of every reference | ✅ | `backend/app/rag/verifier.py` |
| Tap a reference → Arabic + translation | ✅ | |
| English, Urdu, Roman Urdu | ✅ | Licensed Urdu translation of Quran/hadith still needed |
| Guest sign-in + chat history | ✅ | |
| Google / Apple sign-in | 🟡 | Needs Google OAuth client IDs and Apple Service ID |
| Report a wrong answer | ✅ | |
| Scholar review screen (reports, fatawa queue) | ✅ | Web page at `/admin`, protected by `ADMIN_API_KEY` |
| Fonts bundled in the app | ✅ | Amiri, Noto Nastaliq Urdu (OFL) |
| Database migrations | ✅ | Alembic |
| Server deployment | 🟡 | Docker image + guide; needs a server and domain |
| Sunnah.com / Quran Foundation data | ⬜ | Waiting for API access |
| ~300-question scholar test set | ⬜ | Needs the scholar panel |

**Gate before beta:** scholar panel reviews the test set and is satisfied with answer quality.

## Phase 2: iOS + depth (target: April 2027)

| Item | Status | Notes |
|---|---|---|
| iOS app | 🟡 | Same Flutter code; needs Apple developer account and a Mac to build |
| Arabic interface | ✅ | |
| Maslak setting (Hanafi, Shafi'i, Maliki, Hanbali, Ahl-e-Hadith) | ✅ | Chosen school's view shown first once fiqh sources exist |
| Fatawa and scholars' articles library | ✅ | Approved fatawa only, with "read original" link |
| Voice questions (speak in Urdu) | ✅ | On-device speech recognition, no extra cost |
| Partner fatwa feeds | 🟡 | Needs written permission from each site |

## Phase 3: Monetisation

| Item | Status | Notes |
|---|---|---|
| Ask a Scholar (human answer) | ✅ | Question queue + scholar answers in `/admin` |
| Payment for Ask a Scholar | 🟡 | Needs Google Play / App Store products |
| Premium subscription (no daily limit) | 🟡 | Backend plan + limit done; store billing needs products set up |
| Prayer times, Qibla, Quran reader | ⬜ | Optional: only if users ask |

## What only you can unblock

1. Anthropic API key.
2. Sunnah.com API key and Quran Foundation developer credentials.
3. Licensed Urdu translation (Quran and hadith).
4. Written permission from fatwa publishers.
5. Google Play ($25) and Apple ($99/yr) developer accounts, then store products for premium and Ask a Scholar.
6. Server + domain for the backend.
7. Scholar panel (2–3 ulema, incl. comparative fiqh).
