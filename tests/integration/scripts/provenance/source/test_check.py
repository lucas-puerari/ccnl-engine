"""The source check: each URL fetched once, its hash compared, nothing written."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from scripts.provenance.source.check import Result, check, fetch, render, sources

if TYPE_CHECKING:
    from pathlib import Path

_DOC = {"url": "https://example.org/a.pdf", "sha256": "aa"}


def _bundle(root: Path) -> Path:
    (root / "agreement").mkdir()
    payload = {"meta": {"sources": [_DOC]}, "levels": [{"source": _DOC | {"page": 3}}]}
    (root / "agreement" / "x.json").write_text(json.dumps(payload), encoding="utf-8")
    other = {
        "sources": [{"url": "https://example.org/b.htm", "sha256": "bb"}, {"url": 1}]
    }
    (root / "y.json").write_text(json.dumps(other), encoding="utf-8")
    return root


def test_each_url_is_collected_once_with_its_hashes_and_files(tmp_path: Path) -> None:
    """Nested source objects of every file are found and deduplicated."""
    assert sources(_bundle(tmp_path)) == {
        "https://example.org/a.pdf": ({"aa"}, {"agreement/x.json"}),
        "https://example.org/b.htm": ({"bb"}, {"y.json"}),
    }


def test_each_source_is_ok_changed_or_unreachable(tmp_path: Path) -> None:
    """The hash on record decides; a failed request is unreachable."""

    def get(url: str) -> str:
        if url.endswith(".htm"):
            raise OSError
        return "aa"

    results = check(_bundle(tmp_path), get)

    assert [r.status for r in results] == ["ok", "unreachable"]
    assert results[1].error == "OSError"
    changed = Result("u", frozenset({"aa"}), frozenset({"f.json"}), actual="cc")
    assert changed.status == "changed"


def test_the_report_lists_what_is_not_ok() -> None:
    """Counts first, then one row per changed or unreachable URL."""
    results = [
        Result("https://a", frozenset({"aa"}), frozenset({"x.json"}), actual="aa"),
        Result("https://b", frozenset({"bb"}), frozenset({"y.json"}), actual="cc"),
        Result("https://c", frozenset({"dd"}), frozenset({"z.json"}), error="timeout"),
    ]

    page = render(results)

    assert "3 URLs: 1 ok, 1 changed, 1 unreachable." in page
    assert "| changed | https://b | cc | `y.json` |" in page
    assert "| unreachable | https://c | timeout | `z.json` |" in page
    assert "https://a" not in page
    assert "|" not in render(results[:1])


def test_only_http_urls_are_fetched() -> None:
    """A file or ftp URL never reaches urlopen."""
    with pytest.raises(OSError, match="not an http"):
        fetch("file:///etc/passwd")
