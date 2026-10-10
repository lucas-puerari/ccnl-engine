"""The contract page generator detects drift without touching the pages."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from scripts.documentation.generate_contract_pages import (
    DATA_DIR,
    ROOT,
    generate_page,
    main,
)

if TYPE_CHECKING:
    from pathlib import Path

_CCNL = "commercio-confcommercio"


def _tree(tmp_path: Path) -> tuple[Path, Path]:
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "pages"
    data_dir.mkdir()
    out_dir.mkdir()
    shutil.copy(DATA_DIR / f"{_CCNL}.json", data_dir)
    return data_dir, out_dir


def _check(data_dir: Path, out_dir: Path) -> int:
    return main(["--check"], data_dir=data_dir, out_dir=out_dir, root=ROOT)


def test_committed_pages_match_bundle() -> None:
    """Every bundled CCNL has a committed page equal to its generated content."""
    assert main(["--check"]) == 0


def test_stale_page_fails_and_is_left_untouched(tmp_path: Path) -> None:
    """A drifted page fails the check and keeps its bytes."""
    data_dir, out_dir = _tree(tmp_path)
    page = out_dir / f"{_CCNL}.md"
    page.write_text("stale\n", encoding="utf-8")

    assert _check(data_dir, out_dir) == 1
    assert page.read_text(encoding="utf-8") == "stale\n"


def test_missing_page_fails(tmp_path: Path) -> None:
    """A CCNL without a page fails the check and no page is created."""
    data_dir, out_dir = _tree(tmp_path)

    assert _check(data_dir, out_dir) == 1
    assert not any(out_dir.iterdir())


def test_write_mode_creates_pages_that_then_pass(tmp_path: Path) -> None:
    """Without ``--check`` the generator writes every page from the data."""
    data_dir, out_dir = _tree(tmp_path)

    assert main([], data_dir=data_dir, out_dir=out_dir, root=ROOT) == 0
    page = out_dir / f"{_CCNL}.md"
    assert page.read_text(encoding="utf-8") == generate_page(
        data_dir / f"{_CCNL}.json", ROOT
    )
    assert _check(data_dir, out_dir) == 0


def test_page_does_not_depend_on_the_current_date() -> None:
    """The freshness card quotes the latest recorded tranche, not a future one."""
    page = generate_page(DATA_DIR / f"{_CCNL}.json", ROOT)

    assert "Next salary event" not in page
    assert "| **Latest salary tranche** |" in page
