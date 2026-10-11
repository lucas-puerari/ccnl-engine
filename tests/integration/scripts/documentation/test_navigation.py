"""Every hand-written page of the site is reachable from the navigation.

The contract pages are generated and reached from the contracts index and
the search, so the navigation lists only the index and the matrix.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

_ROOT = Path(__file__).parents[4]
_DOCS = _ROOT / "docs"


def _nav_pages() -> set[str]:
    """Return every page the navigation of ``zensical.toml`` lists.

    Returns:
        Paths relative to ``docs/``.
    """
    config = tomllib.loads((_ROOT / "zensical.toml").read_text(encoding="utf-8"))
    return set(re.findall(r"'([\w./-]+\.md)'", repr(config["nav"])))


def _manual_pages() -> set[str]:
    """Return the hand-written pages: the contract pages are generated.

    Returns:
        Paths relative to ``docs/``.
    """
    return {
        path.relative_to(_DOCS).as_posix()
        for path in _DOCS.rglob("*.md")
        if path.relative_to(_DOCS).parts[0] not in {"_build", "contracts"}
    }


def test_every_manual_page_is_in_the_navigation() -> None:
    """A page missing from the navigation is reachable only by search."""
    assert _manual_pages() - _nav_pages() == set()


def test_the_navigation_lists_existing_pages_only() -> None:
    """A navigation entry names a page of ``docs/``."""
    missing = {page for page in _nav_pages() if not (_DOCS / page).is_file()}
    assert missing == set()


def test_contract_pages_stay_out_of_the_navigation() -> None:
    """Only the contracts index and the capability matrix are listed."""
    contracts = {page for page in _nav_pages() if page.startswith("contracts/")}
    assert contracts == {"contracts/index.md", "contracts/capability-matrix.md"}
