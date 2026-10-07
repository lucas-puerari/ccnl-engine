"""The counts quoted in docs/trust/ are generated from the bundle."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.service.loaders import load_ccnl
from scripts.docs.gen_trust_counts import (
    TRUST_DIR,
    bundle_counts,
    main,
    render,
)

if TYPE_CHECKING:
    from pathlib import Path

_READINESS = "<!-- trust:readiness-production -->{}<!-- /trust:readiness-production -->"


@pytest.fixture
def trust_copy(tmp_path: Path) -> Path:
    """Return a writable copy of the committed trust pages.

    Returns:
        The directory holding the copy.
    """
    target = tmp_path / "trust"
    shutil.copytree(TRUST_DIR, target)
    return target


def _page_with(trust_dir: Path, marker: str) -> Path:
    return next(p for p in sorted(trust_dir.glob("*.md")) if marker in p.read_text())


def test_committed_trust_pages_match_bundle() -> None:
    """Every count quoted in docs/trust/ equals the one rendered from the data."""
    assert main(["--check"]) == 0


def test_render_fills_known_markers_and_keeps_unknown_ones() -> None:
    """A known marker gets its count; an unknown one is reported, not changed."""
    text = "a <!-- trust:x -->old<!-- /trust:x --> b <!-- trust:y -->?<!-- /trust:y -->"

    filled, names = render(text, {"x": "42"})

    assert filled == "a <!-- trust:x -->42<!-- /trust:x --> b " + text.split("b ")[1]
    assert names == {"x", "y"}


def test_stale_count_fails_check_and_is_rewritten(trust_copy: Path) -> None:
    """A drifted count fails the check untouched; write mode restores it."""
    page = _page_with(trust_copy, "trust:readiness-production")
    original = page.read_text(encoding="utf-8")
    current = bundle_counts()["readiness-production"]
    stale = original.replace(_READINESS.format(current), _READINESS.format(999))
    page.write_text(stale, encoding="utf-8")

    assert main(["--check"], trust_dir=trust_copy) == 1
    assert page.read_text(encoding="utf-8") == stale
    assert main([], trust_dir=trust_copy) == 0
    assert page.read_text(encoding="utf-8") == original


def test_unknown_marker_fails(trust_copy: Path) -> None:
    """A marker naming no count is an error, in both modes."""
    page = trust_copy / "extra.md"
    page.write_text("<!-- trust:nope -->1<!-- /trust:nope -->\n", encoding="utf-8")

    assert main(["--check"], trust_dir=trust_copy) == 1
    assert main([], trust_dir=trust_copy) == 1


def test_count_quoted_by_no_page_fails(trust_copy: Path) -> None:
    """Deleting the page that quotes a count cannot hide a stale number."""
    _page_with(trust_copy, "trust:readiness-table").unlink()

    assert main(["--check"], trust_dir=trust_copy) == 1


def test_readiness_counts_follow_the_loader_default() -> None:
    """Files without a readiness key count as the model default."""
    counts = bundle_counts()
    listed = counts["readiness-reviewed-list"]
    reviewed = [] if listed == "none" else listed.split(", ")

    assert len(reviewed) == int(counts["readiness-reviewed"])
    for ccnl_id in reviewed:
        ccnl = load_ccnl(f"{ccnl_id.strip('`')}.json")
        assert ccnl.verification.readiness.value == "reviewed"
