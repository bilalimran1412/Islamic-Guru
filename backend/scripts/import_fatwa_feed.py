"""Pull new fatawa from a partner site's RSS/Atom feed into the review queue.

Only use with WRITTEN PERMISSION from the publisher. Items land in `fatwas` with
status "pending"; nothing reaches the AI until a scholar approves it (Phase 2
admin screen copies approved items into `sources`).

Usage (from backend/):
  python -m scripts.import_fatwa_feed --publisher "Example Darul Ifta" \
      --feed https://example.org/fatwa/feed --language ur
"""

import argparse
import asyncio
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import httpx
from sqlalchemy import select

from app.db import SessionLocal, init_db
from app.models import Fatwa

_ATOM = "{http://www.w3.org/2005/Atom}"


def parse_feed(xml: str) -> list[dict]:
    root = ET.fromstring(xml)
    items = []
    for it in root.iter("item"):  # RSS 2.0
        pub = it.findtext("pubDate")
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "url": (it.findtext("link") or "").strip(),
            "body": it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
                    or it.findtext("description") or "",
            "published": parsedate_to_datetime(pub) if pub else None,
        })
    for e in root.iter(f"{_ATOM}entry"):  # Atom
        link = e.find(f"{_ATOM}link")
        items.append({
            "title": (e.findtext(f"{_ATOM}title") or "").strip(),
            "url": link.get("href", "") if link is not None else "",
            "body": e.findtext(f"{_ATOM}content") or e.findtext(f"{_ATOM}summary") or "",
            "published": None,
        })
    return [i for i in items if i["url"] and i["body"]]


async def main(publisher: str, feed: str, language: str) -> None:
    await init_db()
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(feed)
        resp.raise_for_status()
    items = parse_feed(resp.text)
    added = 0
    async with SessionLocal() as s:
        for i in items:
            exists = await s.scalar(select(Fatwa.id).where(Fatwa.original_url == i["url"]))
            if exists:
                continue
            s.add(Fatwa(publisher=publisher, title=i["title"][:500], answer=i["body"], language=language,
                        original_url=i["url"], published_at=i["published"]))
            added += 1
        await s.commit()
    print(f"{added} new fatawa queued for review ({len(items)} in feed)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--publisher", required=True)
    ap.add_argument("--feed", required=True)
    ap.add_argument("--language", default="ur")
    a = ap.parse_args()
    asyncio.run(main(a.publisher, a.feed, a.language))
