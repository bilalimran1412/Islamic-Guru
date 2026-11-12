# Decisions

Defaults chosen when the project was set up (Nov 2026). Change them here when they change.

| Topic | Decision |
|---|---|
| App name | "Islamic Guru" is a placeholder until branding is decided. |
| Maslak | Sunni-only, all four schools. Shia fiqh questions get a polite out-of-scope reply. |
| Disputed fiqh in the MVP | The MVP library has only Quran + Bukhari + Muslim, which can't support each school's position. On disputed matters (raf' al-yadayn, Witr, Taraweeh) the app shows the relevant hadith, says the schools differ, and recommends a scholar. Per-school answers come with the fiqh/fatawa library in Phase 2. |
| Urdu translations | No licensed Urdu translation yet. Quoted text is shown in Arabic + English; the explanation is written in the user's language. Add a licensed Urdu translation before calling Urdu support complete. |
| Reference check | Every cited ref must be among the retrieved passages, and every quote must match the stored text after normalisation (diacritics, punctuation, letter variants). |
| Fatawa from partner sites | Pulled by RSS/API only with written permission, stored unchanged with publisher, scholar, date and original URL. They wait in a review queue (`fatwas.status = pending`) until a scholar approves them. |
| Hadith source | Open hadith-api dataset (public domain) until the Sunnah.com API key arrives. Numbering must be checked against Sunnah.com before launch. |
| Quran source | Tanzil text (CC BY 3.0, unchanged, attributed). Translations via Tanzil files now; Quran Foundation API once developer credentials are issued. |
| AI model | Claude via the Anthropic API with server-side refusal fallback. Model and effort are settings (`ANSWER_MODEL`, `ANSWER_EFFORT`). |
| Sign-in | Guest account with a token on first launch; Google / Apple sign-in to be linked to the same account later (Apple requires Sign in with Apple once Google sign-in ships on iOS). |
| Free tier | 10 questions per day per user (`DAILY_FREE_QUESTIONS`). Premium has no daily limit. |
| Maslak setting | Optional. With a school chosen, that school's view comes first where sources state school positions (fatawa carry a madhhab tag); others still shown. With none chosen, views side by side. |
| Voice | On-device speech recognition (Android / iOS built-in): no server cost, Urdu supported where the phone has the Urdu (Pakistan) language pack. |
| Ask a Scholar payment | Until store billing is live, free-plan questions wait as "awaiting payment" and scholars don't see them; premium users' questions go straight to the panel. Premium can be granted manually from `/admin` (testers, sponsored / sadaqah access). |
| Scholar review access | One shared admin key plus the reviewer's name on every decision. Move to individual accounts when the panel grows. |
| Fonts | Amiri (Arabic) and Noto Nastaliq Urdu bundled in the app (SIL Open Font License), shown on the Licences screen. |
