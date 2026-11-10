from app.rag.language import detect_language
from app.rag.text import normalize, quote_matches
from app.schemas import Language


def test_normalize_strips_arabic_diacritics_and_variants():
    assert normalize("كُتِبَ عَلَيْكُمُ الصِّيَامُ") == normalize("كتب عليكم الصيام")
    assert normalize("إِنَّ") == normalize("ان")


def test_quote_matches_ignores_punctuation_and_case():
    src = "O you who have believed, decreed upon you is fasting."
    assert quote_matches("decreed upon you is FASTING", src)
    assert not quote_matches("decreed upon you is prayer", src)


def test_quote_matches_rejects_tiny_quotes():
    assert not quote_matches("you", "O you who have believed")


def test_detect_language():
    assert detect_language("How do I perform wudu?") == Language.en
    assert detect_language("Is music haram or halal?") == Language.en
    assert detect_language("namaz ka tareeqa kya hai") == Language.roman_ur
    assert detect_language("روزے کی نیت کیسے کریں؟") == Language.ur
    assert detect_language("ما حكم صيام يوم عرفة؟") == Language.ar
