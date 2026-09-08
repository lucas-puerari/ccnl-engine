"""Data tests: CCNL knowledge values must match the case files exactly.

Level 2 of the three-level test architecture.  Each case file in
``tests/data/cases/`` is a JSON document that records the expected values
for one CCNL's salary table, seniority increments, and apprenticeship
percentages.  Tests here load the *real* bundled files via ``load_ccnl()``
and compare field values directly — no ``compute()``, no tax logic.

The checks are independent so a regression in, say, a salary table entry
fails here (data layer) rather than only in the reference tests where the
signal is buried inside a full payroll computation.
"""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.engine.contract.domain.apprenticeship import (
    ApprenticeshipPercentage,
    ApprenticeshipUnderClassification,
)
from ccnl_engine.engine.contract.service.loaders import load_ccnl

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL

_CASES_DIR = Path(__file__).parent / "cases"
_CASE_FILES = sorted(_CASES_DIR.glob("*.json"))


def _check_salary(ccnl: CCNL, fname: str, sc: dict[str, Any]) -> None:
    """Assert one salary table entry matches its expected value."""
    as_of = date.fromisoformat(sc["as_of"])
    level = ccnl.level_by_code(sc["level_code"])
    actual = level.base_salary.value_at(as_of)
    assert actual == Decimal(sc["expected_monthly"]), (
        f"{fname} level {sc['level_code']!r} "
        f"base_salary on {as_of}: expected {sc['expected_monthly']!r}, "
        f"got {actual!r}"
    )


def _check_seniority(ccnl: CCNL, fname: str, sc: dict[str, Any]) -> None:
    """Assert one seniority increment matches its expected value."""
    as_of = date.fromisoformat(sc["as_of"])
    si = ccnl.parameters.seniority_increments
    assert si is not None, (
        f"{fname}: seniority_checks declared but "
        "parameters.seniority_increments is None"
    )
    ts = si.amount_by_level.get(sc["level_code"])
    assert ts is not None, (
        f"{fname}: seniority level {sc['level_code']!r} not found in amount_by_level"
    )
    actual = ts.value_at(as_of)
    assert actual == Decimal(sc["expected_amount"]), (
        f"{fname} seniority level {sc['level_code']!r} "
        f"on {as_of}: expected {sc['expected_amount']!r}, got {actual!r}"
    )


def _check_apprenticeship_pct(ccnl: CCNL, fname: str, ac: dict[str, Any]) -> None:
    """Assert one apprenticeship percentage period matches its expected value."""
    months = int(ac["months_elapsed"])
    track_name: str | None = ac.get("track_name")
    tracks = [
        t
        for t in ccnl.apprenticeship_tracks_for(ac["level_code"])
        if isinstance(t, ApprenticeshipPercentage)
        and (track_name is None or t.name == track_name)
    ]
    for track in tracks:
        for period in track.periods:
            if period.months_from <= months and (
                period.months_until is None or months < period.months_until
            ):
                assert period.percentage == Decimal(ac["expected_pct"]), (
                    f"{fname} apprenticeship pct "
                    f"level {ac['level_code']!r} track {track_name!r} "
                    f"months_elapsed={months}: "
                    f"expected {ac['expected_pct']!r}, got {period.percentage!r}"
                )
                return
    pytest.fail(
        f"{fname}: no percentage period covers "
        f"level {ac['level_code']!r} track {track_name!r} "
        f"months_elapsed={months}"
    )


def _check_apprenticeship_uc(ccnl: CCNL, fname: str, ac: dict[str, Any]) -> None:
    """Assert one under-classification period matches its expected value."""
    months = int(ac["months_elapsed"])
    track_name: str | None = ac.get("track_name")
    tracks = [
        t
        for t in ccnl.apprenticeship_tracks_for(ac["level_code"])
        if isinstance(t, ApprenticeshipUnderClassification)
        and (track_name is None or t.name == track_name)
    ]
    for track in tracks:
        for period in track.periods:
            if period.months_from <= months and (
                period.months_until is None or months < period.months_until
            ):
                assert period.levels_below == int(ac["expected_levels_below"]), (
                    f"{fname} apprenticeship UC "
                    f"level {ac['level_code']!r} track {track_name!r} "
                    f"months_elapsed={months}: "
                    f"expected levels_below={ac['expected_levels_below']!r}, "
                    f"got {period.levels_below!r}"
                )
                return
    pytest.fail(
        f"{fname}: no under-classification period covers "
        f"level {ac['level_code']!r} track {track_name!r} "
        f"months_elapsed={months}"
    )


class TestDataCases:
    """Each data case JSON must match the loaded CCNL values exactly."""

    @pytest.mark.parametrize("case_file", _CASE_FILES, ids=lambda p: p.stem)
    def test_case_matches(self, case_file: Path) -> None:
        """Load the CCNL and assert every declared check passes."""
        case = json.loads(case_file.read_text(encoding="utf-8"))
        fname: str = case["ccnl_file"]
        ccnl = load_ccnl(fname)

        for sc in case.get("salary_checks", []):
            _check_salary(ccnl, fname, sc)

        for sc in case.get("seniority_checks", []):
            _check_seniority(ccnl, fname, sc)

        for ac in case.get("apprenticeship_pct_checks", []):
            _check_apprenticeship_pct(ccnl, fname, ac)

        for ac in case.get("apprenticeship_uc_checks", []):
            _check_apprenticeship_uc(ccnl, fname, ac)
