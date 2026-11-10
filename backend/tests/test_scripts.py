from scripts.import_fatwa_feed import parse_feed
from scripts.import_hadith import _num
from scripts.surahs import SURAH_NAMES


def test_surah_names():
    assert len(SURAH_NAMES) == 114
    assert SURAH_NAMES[1] == "Al-Baqarah"


def test_hadith_number_format():
    assert _num(7.0) == "7"
    assert _num(7.1) == "7.1"


def test_parse_rss_feed():
    xml = """<rss version="2.0"><channel><item><title>Zakat on gold</title>
    <link>https://example.org/f/1</link><description>Answer text</description>
    <pubDate>Mon, 09 Nov 2026 10:00:00 +0000</pubDate></item>
    <item><title>No link</title><description>x</description></item></channel></rss>"""
    items = parse_feed(xml)
    assert len(items) == 1
    assert items[0]["url"] == "https://example.org/f/1"
