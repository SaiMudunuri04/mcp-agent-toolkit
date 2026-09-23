import os

from mcp_toolkit.tools_impl import doc_search_impl, record_lookup_impl, text_stats_impl


def test_doc_search_finds_refund_doc():
    docs = doc_search_impl("refund policy", os.environ["DATA_DIR"], k=2)
    assert docs, "expected at least one hit"
    assert any("refund" in d["title"].lower() for d in docs)


def test_doc_search_no_match():
    assert doc_search_impl("xyzzy quantum platypus", os.environ["DATA_DIR"]) == []


def test_record_lookup_by_id():
    r = record_lookup_impl("R-2003", os.environ["DATA_DIR"])
    assert r is not None
    assert r["status"] == "investigating"


def test_record_lookup_case_insensitive():
    r = record_lookup_impl("r-2001", os.environ["DATA_DIR"])
    assert r is not None and r["record_id"] == "R-2001"


def test_record_lookup_unknown_returns_none():
    assert record_lookup_impl("R-9999", os.environ["DATA_DIR"]) is None


def test_text_stats_counts():
    stats = text_stats_impl("The quick brown fox jumps over the lazy dog.")
    assert stats["words"] == 9
    assert stats["sentences"] == 1
    assert stats["reading_time_minutes"] > 0
    assert stats["top_keywords"], "expected keywords"
