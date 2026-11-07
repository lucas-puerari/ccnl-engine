"""The salaries rise and the apprentices step down along each sub-sector ladder."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.facade import CCNL
from tests.unit.ccnl_engine.builders import _level, _series_with_prov, make_ccnl_dict


def _with_levels(*extra: dict[str, Any], app_type: str = "none") -> dict[str, Any]:
    data = make_ccnl_dict(app_type=app_type)
    data["levels"].extend(extra)
    return data


def _sub_level(code: str, order: int, salary: str, *subsectors: str) -> dict[str, Any]:
    return {**_level(code, order, salary), "subsectors": list(subsectors)}


def test_a_subsector_level_may_earn_more_than_a_higher_ordinary_one() -> None:
    """3s (order 5, 1200) sits above 4 (1000) only on its own ladder."""
    data = _with_levels(_sub_level("3s", 5, "1200.00", "pelli"))
    data["levels"][2]["base_salary_by_subsector"] = {
        "pelli": _series_with_prov("1100.00")
    }
    assert [lv.code for lv in CCNL.model_validate(data).levels][-1] == "3s"


def test_a_subsector_ladder_must_not_decrease() -> None:
    """On the pelli ladder 2 pays 1300, above the pelli level 3s (1200): rejected."""
    data = _with_levels(_sub_level("3s", 5, "1200.00", "pelli"))
    data["levels"][0]["base_salary_by_subsector"] = {
        "pelli": _series_with_prov("1300.00")
    }
    with pytest.raises(ValidationError, match="salary ordering violated"):
        CCNL.model_validate(data)


def test_an_apprentice_steps_down_its_subsector_ladder() -> None:
    """The pelli ladder of 9s is 2, 3, 4, 9s: the occhiali 3s is not on it."""
    data = _with_levels(
        _sub_level("3s", 5, "1200.00", "occhiali"),
        _sub_level("9s", 9, "1500.00", "pelli"),
        app_type="under_classification",
    )
    data["apprenticeship"][0]["destination_levels"] = ["4", "9s"]
    assert CCNL.model_validate(data).apprenticeship[0].destination_levels == ("4", "9s")
    data["apprenticeship"][0]["periods"][0]["levels_below"] = 4
    data["apprenticeship"][0]["destination_levels"] = ["9s"]
    with pytest.raises(ValidationError, match="no level 4 below '9s'"):
        CCNL.model_validate(data)
