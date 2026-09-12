"""Unit tests for the documentation generator helpers (R24).

Targets the field-name bugs corrected in R24: ``_latest_value`` and
``_latest_date`` previously sorted and read by ``"from"`` instead of
``"valid_from"``; ``_track_params_line`` read ``"under_level"`` instead of
``"levels_below"``.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Import gen_contract_pages via importlib to avoid sys.path manipulation that
# would cause mypy to see the file under two different module names.
# ---------------------------------------------------------------------------
_MOD_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "scripts"
    / "docs"
    / "gen_contract_pages.py"
)
_spec = importlib.util.spec_from_file_location("gen_contract_pages", _MOD_PATH)
assert _spec is not None
assert _spec.loader is not None
_gen = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("gen_contract_pages", _gen)
_spec.loader.exec_module(_gen)
_latest_value = _gen._latest_value
_latest_date = _gen._latest_date
_track_params_line = _gen._track_params_line


def _period(valid_from: str, amount: str) -> dict[str, Any]:
    return {"valid_from": valid_from, "valid_until": None, "amount": amount}


# ---------------------------------------------------------------------------
# _latest_value
# ---------------------------------------------------------------------------


class TestLatestValue:
    """_latest_value returns the amount from the chronologically last period."""

    def test_empty_periods_returns_none(self) -> None:
        """Empty list returns None."""
        assert _latest_value([]) is None

    def test_single_period_returns_its_amount(self) -> None:
        """Single-period list returns that period's amount."""
        assert _latest_value([_period("2024-01-01", "1000.00")]) == "1000.00"

    def test_sorts_by_valid_from(self) -> None:
        """Two periods: the later valid_from period is chosen."""
        periods = [
            _period("2025-01-01", "1100.00"),
            _period("2024-01-01", "1000.00"),
        ]
        assert _latest_value(periods) == "1100.00"

    def test_falls_back_to_value_key(self) -> None:
        """Periods with 'value' instead of 'amount' are handled."""
        p = {"valid_from": "2024-01-01", "valid_until": None, "value": "42.00"}
        assert _latest_value([p]) == "42.00"


# ---------------------------------------------------------------------------
# _latest_date
# ---------------------------------------------------------------------------


class TestLatestDate:
    """_latest_date returns the valid_from of the chronologically last period."""

    def test_empty_periods_returns_none(self) -> None:
        """Empty list returns None."""
        assert _latest_date([]) is None

    def test_single_period_returns_its_valid_from(self) -> None:
        """Single period: returns its valid_from."""
        assert _latest_date([_period("2024-01-01", "1000")]) == "2024-01-01"

    def test_chooses_latest_valid_from(self) -> None:
        """Two periods: the later valid_from is returned."""
        periods = [
            _period("2025-01-01", "1100"),
            _period("2024-01-01", "1000"),
        ]
        assert _latest_date(periods) == "2025-01-01"


# ---------------------------------------------------------------------------
# _track_params_line
# ---------------------------------------------------------------------------


class TestTrackParamsLine:
    """_track_params_line reads 'levels_below', not 'under_level'."""

    def test_empty_periods_returns_empty_string(self) -> None:
        """Empty periods list returns empty string."""
        assert not _track_params_line([])

    def test_levels_below_is_included(self) -> None:
        """levels_below key is read and included in the output."""
        periods = [{"percentage": "80", "levels_below": "2"}]
        result = _track_params_line(periods)
        assert "under-level: `2`" in result

    def test_old_under_level_key_ignored(self) -> None:
        """Legacy 'under_level' key is not picked up."""
        periods = [{"under_level": "2"}]
        result = _track_params_line(periods)
        assert "under-level" not in result

    def test_percentage_is_included(self) -> None:
        """Percentage key is included in the output."""
        periods = [{"percentage": "80"}]
        result = _track_params_line(periods)
        assert "percentage: 80" in result

    def test_both_fields_present(self) -> None:
        """Both percentage and levels_below are included when present."""
        periods = [{"percentage": "75", "levels_below": "1"}]
        result = _track_params_line(periods)
        assert "percentage: 75" in result
        assert "under-level: `1`" in result
