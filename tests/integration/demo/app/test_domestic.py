"""The demo shows no tax lines for a household employer."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    import types

_APP_PY = Path(__file__).resolve().parents[4] / "demo" / "app.py"


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_app_domestic", _APP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_app_domestic"] = module
    spec.loader.exec_module(module)
    return module


def _year(demo_app: types.ModuleType, **params: object) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(demo_app.compute_salary(json.dumps(params)))
    assert "error" not in payload, payload
    return payload


def test_household_employer_shows_no_tax(demo_app: types.ModuleType) -> None:
    """A household employer withholds nothing: no IRPEF and no credit."""
    payload = _year(
        demo_app,
        ccnl="lavoro-domestico-convivente",
        level="A",
        contract="permanent",
        headcount=1,
    )
    accounts = payload["accounts"]

    assert payload["withholding_agent"] is False
    assert payload["irpef"] == {}
    assert isinstance(accounts, dict)
    assert accounts["ordinary_tax"] == 0
    assert accounts["credits"] == 0
    assert payload["annual_net"] < payload["annual_gross"]


def test_company_employer_withholds(demo_app: types.ModuleType) -> None:
    """A company is a withholding agent: IRPEF is withheld over the year."""
    payload = _year(
        demo_app,
        ccnl="commercio-confcommercio",
        level="4",
        contract="permanent",
        headcount=1,
    )
    accounts = payload["accounts"]

    assert payload["withholding_agent"] is True
    assert isinstance(accounts, dict)
    assert accounts["ordinary_tax"] > 0


def test_domestic_part_time_states_the_hours(demo_app: types.ModuleType) -> None:
    """A domestic worker at 63% of 40 hours works 25 hours a week."""
    code = json.loads(
        demo_app.scenario_snippet(
            json.dumps({
                "ccnl": "lavoro-domestico-non-convivente",
                "level": "B",
                "contract": "permanent",
                "headcount": 1,
                "part_time_pct": 63,
            })
        )
    )["code"]

    assert "weekly_hours=WeeklyHours(25)" in code
    assert "full_time_weekly_hours=WeeklyHours(40)" in code
