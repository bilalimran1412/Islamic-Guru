from app.rag.verifier import DraftCitation, verify


def test_valid_answer_passes(passages):
    r = verify("Fasting is prescribed [1].",
               [DraftCitation("quran:2:183", "decreed upon you is fasting")], passages)
    assert r.ok, r.problems


def test_arabic_quote_without_diacritics_passes(passages):
    r = verify("Fasting is prescribed [1].", [DraftCitation("quran:2:183", "كتب عليكم الصيام")], passages)
    assert r.ok, r.problems


def test_unknown_reference_fails(passages):
    r = verify("A claim [1].", [DraftCitation("bukhari:99999")], passages)
    assert not r.ok
    assert "not one of the provided sources" in r.problems[0]


def test_real_reference_with_invented_wording_fails(passages):
    r = verify("A claim [1].", [DraftCitation("bukhari:1903", "Whoever fasts will enter paradise directly")],
               passages)
    assert not r.ok
    assert "does not match" in r.problems[0]


def test_no_citations_fails(passages):
    assert not verify("Some answer.", [], passages).ok


def test_dangling_marker_fails(passages):
    r = verify("Claim [1] and [2].", [DraftCitation("quran:2:183")], passages)
    assert not r.ok
    assert any("[2]" in p for p in r.problems)


def test_missing_markers_fails(passages):
    assert not verify("Claim without markers.", [DraftCitation("quran:2:183")], passages).ok
