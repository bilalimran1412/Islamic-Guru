"""Import the Quran from Tanzil text files into `sources`.

Download from https://tanzil.net/download/ (accept the terms):
  - Quran text: "Uthmani" (or "Simple Clean"), format "Text (with aya numbers)" -> quran-uthmani.txt
  - Translations: https://tanzil.net/trans/ , format "Text (with aya numbers)"
Each line is `sura|aya|text`.

Tanzil's Quran text is CC BY 3.0: it must not be changed and the attribution must be kept.
Each translation has its own licence; check it before shipping.

Usage (from backend/):
  python -m scripts.import_quran --arabic data/raw/quran-uthmani.txt \
      --translation "en|Saheeh International|data/raw/en.sahih.txt"
"""

import argparse
import asyncio

from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal, init_db
from app.models import Source, SourceKind
from scripts.surahs import SURAH_NAMES

ATTRIBUTION = "Quran text: Tanzil Project (tanzil.net), CC BY 3.0"


def read_tanzil(path: str) -> dict[tuple[int, int], str]:
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            sura, aya, text = line.split("|", 2)
            out[(int(sura), int(aya))] = text
    return out


async def main(arabic_path: str, translations: list[str]) -> None:
    await init_db()
    arabic = read_tanzil(arabic_path)
    trans = []
    for spec in translations:
        lang, translator, path = spec.split("|", 2)
        trans.append((lang, translator, read_tanzil(path)))

    rows = []
    for (sura, aya), text in arabic.items():
        rows.append({
            "ref_key": f"quran:{sura}:{aya}",
            "kind": SourceKind.quran,
            "collection": "quran",
            "label": f"Surah {SURAH_NAMES[sura - 1]} {sura}:{aya}",
            "arabic": text,
            "translations": {lang: {"text": t[(sura, aya)], "translator": who}
                             for lang, who, t in trans if (sura, aya) in t},
            "grade": None,
            "attribution": ATTRIBUTION,
            "source_url": f"https://quran.com/{sura}/{aya}",
        })

    async with SessionLocal() as s:
        for i in range(0, len(rows), 1000):
            stmt = insert(Source).values(rows[i:i + 1000])
            stmt = stmt.on_conflict_do_update(
                index_elements=["ref_key"],
                set_={"arabic": stmt.excluded.arabic, "translations": stmt.excluded.translations,
                      "label": stmt.excluded.label, "embedding": None},
            )
            await s.execute(stmt)
        await s.commit()
    print(f"Imported {len(rows)} ayahs")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arabic", required=True)
    ap.add_argument("--translation", action="append", default=[], help="lang|translator|path")
    a = ap.parse_args()
    asyncio.run(main(a.arabic, a.translation))
