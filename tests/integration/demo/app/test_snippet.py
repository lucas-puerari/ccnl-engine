"""The Python snippet of the demo reproduces the scenario it shows."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    import types

_APP_PY = Path(__file__).resolve().parents[4] / "demo" / "app.py"
_SCENARIOS = [
    {
        "ccnl": "metalmeccanico-federmeccanica",
        "level": "C1",
        "contract": "permanent",
        "headcount": 200,
        "seniority_months": 0,
        "regione": "IT-25",
        "comune": "F205",
    },
    {
        "ccnl": "commercio-confcommercio",
        "level": "4",
        "contract": "fixed_term",
        "headcount": 50,
        "part_time_pct": 60,
        "seniority_months": 72,
        "first_enrolled_after_1995": True,
    },
    {
        "ccnl": "metalmeccanico-federmeccanica",
        "level": "C1",
        "contract": "apprentice",
        "apprentice_months": 18,
        "track": "professionalizzante_36",
        "headcount": 200,
    },
    {
        "ccnl": "lavoro-domestico-non-convivente",
        "level": "B",
        "contract": "permanent",
        "headcount": 1,
        "part_time_pct": 63,
    },
]


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_app_snippet", _APP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_app_snippet"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("params", _SCENARIOS, ids=lambda p: str(p["contract"]))
def test_snippet_prints_the_figures_of_the_demo(
    demo_app: types.ModuleType, params: dict[str, object]
) -> None:
    """Run as a script, the snippet prints the gross, net and cost shown."""
    encoded = json.dumps(params)
    code = json.loads(demo_app.scenario_snippet(encoded))["code"]
    shown = json.loads(demo_app.compute_salary(encoded))
    printed = io.StringIO()

    with contextlib.redirect_stdout(printed):
        exec(compile(code, "<snippet>", "exec"), {})

    lines = dict(line.split(": ") for line in printed.getvalue().splitlines())
    assert float(lines["Gross"]) == pytest.approx(shown["annual_gross"])
    assert float(lines["Net"]) == pytest.approx(shown["annual_net"])
    assert float(lines["Employer cost"]) == pytest.approx(shown["annual_employer_cost"])
    assert lines["Payable"] == str(shown["payability"] == "payable")


def test_snippet_imports_the_public_api_only(demo_app: types.ModuleType) -> None:
    """The snippet is code a caller copies: no internal module."""
    code = json.loads(demo_app.scenario_snippet(json.dumps(_SCENARIOS[3])))["code"]
    modules = {
        line.split()[1] for line in code.splitlines() if line.startswith("from ccnl")
    }

    assert modules == {"ccnl_engine", "ccnl_engine.inputs"}
