"""The staleness report: what goes stale without a deadline in the data."""

from __future__ import annotations

import json
from datetime import date
from typing import TYPE_CHECKING

from scripts.provenance.staleness.report import Finding, main, render, staleness

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

_TODAY = date(2026, 10, 15)


def _write(root: Path, file: str, data: object) -> None:
    path = root / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def _agreement(periods: list[object], **verification: object) -> object:
    return {
        "levels": [{"base_salary": {"periods": periods}}],
        "verification": {"readiness": "production"} | verification,
    }


def test_an_agreement_shows_its_review_tranche_and_end(tmp_path: Path) -> None:
    """A review due, a tranche starting and closed tables are reported."""
    periods: list[object] = [
        {"valid_from": "2026-01-01", "valid_until": "2026-11-01"},
        {"valid_from": "2026-11-01", "valid_until": "2026-12-01"},
    ]
    _write(tmp_path, "agreement/x.json", _agreement(periods, review_due="2026-11-30"))

    assert staleness(tmp_path, _TODAY, within=60) == [
        Finding("agreement/x.json", "production: new tranche on 2026-11-01"),
        Finding("agreement/x.json", "production: pay tables run out on 2026-12-01"),
        Finding("agreement/x.json", "production: review due on 2026-11-30"),
    ]


def test_open_tables_and_far_dates_are_not_stale(tmp_path: Path) -> None:
    """An open last period and a review beyond the horizon report nothing."""
    periods = [{"valid_from": "2026-01-01", "valid_until": None}, {"valid_from": "bad"}]
    _write(tmp_path, "agreement/x.json", _agreement(periods, review_due="2027-06-01"))
    _write(tmp_path, "agreement/y.json", {"levels": "none"})
    _write(tmp_path, "list.json", [1, 2])

    assert staleness(tmp_path, _TODAY, within=60) == []


def test_a_ruleset_ending_or_provisional_is_reported(tmp_path: Path) -> None:
    """An ending ruleset and a provisional one in force are stale."""
    _write(tmp_path, "a.json", {"ruleset": {"effective_until": "2026-12-31"}})
    _write(
        tmp_path,
        "b.json",
        {"ruleset": {"effective_from": "2026-01-01", "provisional": True}},
    )
    _write(
        tmp_path,
        "c.json",
        {"ruleset": {"effective_from": "2027-06-01", "provisional": True}},
    )
    _write(tmp_path, "d.json", {"ruleset": "none"})

    assert staleness(tmp_path, _TODAY, within=90) == [
        Finding("a.json", "ruleset effective until 2026-12-31"),
        Finding("b.json", "provisional ruleset in force"),
    ]


def test_a_yearly_directory_without_the_coming_year_is_reported(
    tmp_path: Path,
) -> None:
    """The horizon reaches 2027: a directory holding only 2026 misses it."""
    _write(tmp_path, "contribution/2026/industria.json", {})
    _write(tmp_path, "sector/2026/industria.json", {})
    _write(tmp_path, "sector/2027/industria.json", {})

    assert staleness(tmp_path, _TODAY, within=90) == [
        Finding("contribution", "no data for 2027")
    ]


def test_a_municipal_surtax_older_than_a_month_is_stale(tmp_path: Path) -> None:
    """The MEF republishes the rates monthly; the year file must follow."""
    surtax = {"ruleset": {"published_at": "2026-09-13"}}
    _write(tmp_path, "surtax/municipal/2026.json", surtax)

    assert staleness(tmp_path, _TODAY, within=0) == [
        Finding(
            "surtax/municipal/2026.json",
            "municipal surtax published on 2026-09-13, over a month ago",
        )
    ]
    surtax["ruleset"]["published_at"] = "2026-09-14"
    _write(tmp_path, "surtax/municipal/2026.json", surtax)
    assert staleness(tmp_path, _TODAY, within=0) == []


def test_the_report_renders_a_table_or_says_nothing_is_stale() -> None:
    """The Markdown lists each finding by file."""
    assert "Nothing stale." in render([], _TODAY, 60)
    page = render([Finding("a.json", "ruleset effective until 2026-12-31")], _TODAY, 60)
    assert "| `a.json` | ruleset effective until 2026-12-31 |" in page


def test_the_bundle_report_runs(capsys: pytest.CaptureFixture[str]) -> None:
    """The script prints the report of the bundle and never fails."""
    assert main(["--within", "30"]) == 0
    assert "## Staleness on" in capsys.readouterr().out
