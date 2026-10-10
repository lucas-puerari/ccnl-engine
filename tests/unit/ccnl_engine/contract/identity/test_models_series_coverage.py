"""Temporal coverage of the rule series a run reads with each level."""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.contract.identity.facade import CCNL
from ccnl_engine.contract.identity.models_series_coverage import required_series
from tests.helpers import TEST_PROV, make_ccnl_dict

_LATE = "2021-01-01"


def _late(value: str = "5.00") -> dict[str, Any]:
    """Return a series starting a year after the pay tables of the fixture.

    Returns:
        A one-period series from 2021-01-01.
    """
    return {"periods": [{"valid_from": _LATE, "valid_until": None, "value": value}]}


def _declared(kind: str = "missing") -> dict[str, Any]:
    """Return the late series with the year before declared as a gap.

    Returns:
        A gap from 2020-01-01 to 2021-01-01, then a value.
    """
    gap = {"valid_from": "2020-01-01", "valid_until": _LATE, "gap_kind": kind}
    return {"periods": [gap, *_late()["periods"]]}


def _allowance(monthly: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": "EDR",
        "description": "EDR",
        "monthly": monthly,
        "provenance": TEST_PROV,
    }


def _ccnl_with(**increments: Any) -> dict[str, Any]:  # noqa: ANN401
    data = make_ccnl_dict()
    data["parameters"]["seniority_increments"].update(increments)
    return data


class TestRejectsALateSeries:
    """A series a run reads must not start after its pay table."""

    def test_allowance(self) -> None:
        """An allowance starting after the base salary of its level."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [_allowance(_late())]
        with pytest.raises(ValidationError, match=r"fixed_allowances\[EDR\]"):
            CCNL.model_validate(data)

    def test_level_amount(self) -> None:
        """A seniority amount starting after the base salary of its level."""
        data = _ccnl_with(amount_by_level={"4": _late()})
        with pytest.raises(ValidationError, match=r"amount_by_level\[4\]"):
            CCNL.model_validate(data)

    def test_category_amount(self) -> None:
        """A category seniority amount starting after the pay table."""
        data = _ccnl_with(amount_by_level_by_category={"operaio": {"3": _late()}})
        with pytest.raises(ValidationError, match=r"\[operaio\]\[3\]"):
            CCNL.model_validate(data)

    def test_tier_amount(self) -> None:
        """A tier amount starting after the pay table."""
        tier = {
            "cadence_months": 24,
            "maximum_count": 2,
            "amount_by_level": {"4": _late()},
            "provenance": TEST_PROV,
        }
        data = _ccnl_with(amount_by_level={}, maximum_count=2, tiers=[tier])
        with pytest.raises(ValidationError, match=r"tiers\[0\]\.amount_by_level\[4\]"):
            CCNL.model_validate(data)

    def test_apprentice_amount(self) -> None:
        """The apprentice amount must cover the first pay table of the CCNL."""
        data = _ccnl_with(apprentice_amount=_late())
        with pytest.raises(ValidationError, match="apprentice_amount starts on"):
            CCNL.model_validate(data)


class TestAcceptsADeclaredGap:
    """The range before a late value is declared with a gap period."""

    @pytest.mark.parametrize("kind", ["missing", "not_applicable", "unknown"])
    def test_gap_kinds(self, kind: str) -> None:
        """Every gap kind declares the range before the value."""
        data = make_ccnl_dict()
        data["levels"][0]["fixed_allowances"] = [_allowance(_declared(kind))]
        CCNL.model_validate(data)


class TestRequiredSeries:
    """The series a run reads and the date each must cover from."""

    def test_paths_and_starts(self) -> None:
        """CCNL-wide series cover the first pay table, a level's its own."""
        data = _ccnl_with(apprentice_amount=_declared())
        data["levels"][2]["base_salary"]["periods"][0]["valid_from"] = "2020-06-01"
        ccnl = CCNL.model_validate(data)
        found = {
            path: start
            for path, start, _ in required_series(ccnl.levels, ccnl.parameters)
        }
        assert found == {
            "parameters.additional_months": date(2020, 1, 1),
            "parameters.seniority_increments.apprentice_amount": date(2020, 1, 1),
            "parameters.seniority_increments.amount_by_level[4]": date(2020, 6, 1),
        }

    def test_level_without_a_salary_value_is_skipped(self) -> None:
        """A level whose base salary is all gap reads no other series."""
        data = make_ccnl_dict()
        for level in data["levels"]:
            level["base_salary"] = {
                "periods": [
                    {
                        "valid_from": "2020-01-01",
                        "valid_until": None,
                        "gap_kind": "unknown",
                    }
                ]
            }
        ccnl = CCNL.model_validate(data)
        assert list(required_series(ccnl.levels, ccnl.parameters)) == []
        assert list(required_series(ccnl.levels[:1], ccnl.parameters)) == []
        mixed = (*ccnl.levels[:2], CCNL.model_validate(make_ccnl_dict()).levels[2])
        paths = [path for path, _, _ in required_series(mixed, ccnl.parameters)]
        assert "parameters.seniority_increments.amount_by_level[4]" in paths
