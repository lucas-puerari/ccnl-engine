"""Tests for scripts/ci/rules_diff_report.py comparison helpers."""

from __future__ import annotations

import importlib.resources
import importlib.util
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import ccnl_engine.knowledge.ccnl.data as ccnl_data_pkg
from ccnl_engine.contract.domain.identity import CCNL
from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod

if TYPE_CHECKING:
    import types

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT = _PROJECT_ROOT / "scripts" / "ci" / "rules_diff_report.py"


@pytest.fixture(scope="module")
def report_mod() -> types.ModuleType:
    """Load scripts/ci/rules_diff_report.py as a module.

    Returns:
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location("_test_rules_diff_report", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_rules_diff_report"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def metalmeccanico_ccnl() -> CCNL:
    """Load metalmeccanico-federmeccanica as a CCNL instance.

    Returns:
        Validated CCNL object.
    """
    files_pkg = importlib.resources.files(ccnl_data_pkg)
    raw = (files_pkg / "metalmeccanico-federmeccanica.json").read_text()
    return CCNL.model_validate(json.loads(raw))


def _ts(pairs: list[tuple[date, Decimal | None]]) -> TimeSeries:
    """Build a minimal TimeSeries from (valid_from, value) pairs.

    Returns:
        A TimeSeries with one period per pair.
    """
    periods = tuple(
        ValidityPeriod(valid_from=d, valid_until=None, value=v) for d, v in pairs
    )
    return TimeSeries(periods=periods)


# ---------------------------------------------------------------------------
# _compare_ts
# ---------------------------------------------------------------------------


class TestCompareTs:
    """_compare_ts detects value changes between two TimeSeries at ref dates."""

    def test_identical_series_no_changes(self, report_mod: types.ModuleType) -> None:
        """Two identical TimeSeries produce no change lines."""
        ts = _ts([(date(2026, 1, 1), Decimal("1000.00"))])
        lines = report_mod._compare_ts(ts, ts, {date(2026, 1, 1)}, "base salary")
        assert lines == []

    def test_value_change_detected(self, report_mod: types.ModuleType) -> None:
        """A value change between old and new TimeSeries is reported."""
        old = _ts([(date(2026, 1, 1), Decimal(168))])
        new = _ts([(date(2026, 1, 1), Decimal(999))])
        lines = report_mod._compare_ts(old, new, {date(2026, 1, 1)}, "hourly divisor")
        assert len(lines) == 1
        assert "hourly divisor" in lines[0]
        assert "168" in lines[0]
        assert "999" in lines[0]

    def test_old_none_shows_addition(self, report_mod: types.ModuleType) -> None:
        """When old_ts is None the new value appears as an addition."""
        new = _ts([(date(2026, 1, 1), Decimal("50.00"))])
        lines = report_mod._compare_ts(None, new, {date(2026, 1, 1)}, "allowance X")
        assert len(lines) == 1
        assert "(none)" in lines[0]


# ---------------------------------------------------------------------------
# _compare_ccnl_versions — hourly_divisor coverage
# ---------------------------------------------------------------------------


class TestCompareCcnlVersionsHourlyDivisor:
    """_compare_ccnl_versions detects hourly_divisor changes."""

    def test_hourly_divisor_change_detected(
        self,
        report_mod: types.ModuleType,
        metalmeccanico_ccnl: CCNL,
    ) -> None:
        """A CCNL differing only in hourly_divisor is reported under Parameters."""
        files_pkg = importlib.resources.files(ccnl_data_pkg)
        raw = (files_pkg / "metalmeccanico-federmeccanica.json").read_text()
        data_mod = json.loads(raw)
        data_mod["parameters"]["hourly_divisor"]["periods"][0]["value"] = "999"
        new_ccnl = CCNL.model_validate(data_mod)

        lines = list(report_mod._compare_ccnl_versions(metalmeccanico_ccnl, new_ccnl))
        combined = "\n".join(lines)
        assert "hourly divisor" in combined
        assert "_No computational changes detected._" not in combined

    def test_identical_ccnl_no_changes(
        self,
        report_mod: types.ModuleType,
        metalmeccanico_ccnl: CCNL,
    ) -> None:
        """Comparing a CCNL to itself yields the no-changes sentinel."""
        lines = list(
            report_mod._compare_ccnl_versions(metalmeccanico_ccnl, metalmeccanico_ccnl)
        )
        assert "_No computational changes detected._" in lines
