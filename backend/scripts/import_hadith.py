"""Import hadith collections into `sources` from the open hadith-api dataset
(github.com/fawazahmed0/hadith-api, public domain / Unlicense).

This is the interim source while the Sunnah.com API key is pending. Before launch:
- spot-check text against a printed edition, and
- confirm the numbering matches Sunnah.com (citations show these numbers to users).

Usage (from backend/):
  python -m scripts.import_hadith bukhari muslim
"""

import argparse
import asyncio

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.db import SessionLocal
from app.models import Source, SourceKind

BASE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions"
COLLECTIONS = {
    "bukhari": ("Sahih al-Bukhari", "Sahih"),
    "muslim": ("Sahih Muslim", "Sahih"),
}
ATTRIBUTION = "Hadith text: hadith-api dataset (fawazahmed0), public domain"


def _num(n) -> str:
    """7.0 -> '7', 7.1 -> '7.1' (the dataset splits some hadith into parts)."""
    f = float(n)
    return str(int(f)) if f.is_integer() else str(f)


async def fetch(client: httpx.AsyncClient, edition: str) -> dict[str, str]:
    r = await client.get(f"{BASE}/{edition}.min.json")
    r.raise_for_status()
    return {_num(h["hadithnumber"]): h["text"] for h in r.json()["hadiths"] if h["text"].strip()}


async def main(names: list[str]) -> None:
    async with httpx.AsyncClient(timeout=120) as client:
        for name in names:
            title, grade = COLLECTIONS[name]
            ara = await fetch(client, f"ara-{name}")
            eng = await fetch(client, f"eng-{name}")
            rows = [{
                "ref_key": f"{name}:{num}",
                "kind": SourceKind.hadith,
                "collection": name,
                "label": f"{title} {num}",
                "arabic": ara.get(num),
                "translations": {"en": {"text": eng[num]}} if num in eng else {},
                "grade": grade,
                "attribution": ATTRIBUTION,
                "source_url": f"https://sunnah.com/{name}:{num}",
            } for num in sorted(set(ara) | set(eng), key=float)]

            async with SessionLocal() as s:
                for i in range(0, len(rows), 1000):
                    stmt = insert(Source).values(rows[i:i + 1000])
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["ref_key"],
                        set_={"arabic": stmt.excluded.arabic, "translations": stmt.excluded.translations,
                              "embedding": None},
                    )
                    await s.execute(stmt)
                await s.commit()
            print(f"Imported {len(rows)} hadith from {title}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("collections", nargs="+", choices=sorted(COLLECTIONS))
    asyncio.run(main(ap.parse_args().collections))
