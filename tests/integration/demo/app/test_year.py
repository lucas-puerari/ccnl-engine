"""The demo computes a whole competence year and shows what it computed."""

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
_STANDARD = {
    "ccnl": "metalmeccanico-federmeccanica",
    "level": "C1",
    "contract": "permanent",
    "headcount": 200,
    "seniority_months": 0,
}
_COMMERCIO = {
    "ccnl": "commercio-confcommercio",
    "level": "4",
    "contract": "permanent",
    "headcount": 50,
}


@pytest.fixture(scope="module")
def demo_app() -> types.ModuleType:
    """Load demo/app.py without adding demo/ to sys.path permanently.

    Returns:
        The loaded demo app module.
    """
    spec = importlib.util.spec_from_file_location("_test_demo_app_year", _APP_PY)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_test_demo_app_year"] = module
    spec.loader.exec_module(module)
    return module


def _year(demo_app: types.ModuleType, **params: object) -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(demo_app.compute_salary(json.dumps(params)))
    assert "error" not in payload, payload
    return payload


def test_annual_figures_are_the_sum_of_the_runs(demo_app: types.ModuleType) -> None:
    """Net and employer cost reconcile with the gross and the year's ledger.

    The annual gross is not a month times the number of monthly payments.
    """
    year = _year(demo_app, **_STANDARD)
    accounts = year["accounts"]

    assert year["runs"] == 13
    assert year["annual_gross"] != pytest.approx(year["monthly_gross"] * year["runs"])
    assert year["annual_net"] == pytest.approx(
        year["annual_gross"]
        - accounts["employee_contributions"]
        - accounts["bilateral_fund_employee"]
        - accounts["pension_fund_employee"]
        - accounts["ordinary_tax"]
        - accounts["surtax"]
        + accounts["credits"],
        abs=0.01,
    )
    assert year["annual_employer_cost"] == pytest.approx(
        year["annual_gross"]
        + accounts["employer_contributions"]
        + accounts["bilateral_fund_employer"]
        + accounts["pension_fund_employer"]
        + accounts["tfr_accrual"],
        abs=0.01,
    )
    assert year["net_average"] == pytest.approx(year["annual_net"] / 13)


def test_irpef_figures_come_from_the_engine(demo_app: types.ModuleType) -> None:
    """The taxable income and the IRPEF of the breakdown are not placeholders."""
    year = _year(demo_app, **_STANDARD)
    irpef = year["irpef"]

    assert irpef["taxable_income"] > 0
    assert irpef["irpef_gross"] - irpef["work_deduction"] - irpef[
        "ulteriore_detrazione"
    ] == pytest.approx(year["accounts"]["ordinary_tax"], abs=0.01)


def test_part_time_scales_the_pay(demo_app: types.ModuleType) -> None:
    """60% of full time pays 60% of the monthly gross."""
    full = _year(demo_app, **_COMMERCIO)
    part = _year(demo_app, **_COMMERCIO, part_time_pct=60)

    assert part["monthly_gross"] == pytest.approx(full["monthly_gross"] * 0.6, abs=0.05)


def test_stated_seniority_adds_increments(demo_app: types.ModuleType) -> None:
    """Months of service enter the pay and clear the missing seniority fact."""
    unknown = _year(demo_app, **_COMMERCIO)
    stated = _year(demo_app, **_COMMERCIO, seniority_months=72)

    assert stated["monthly_gross"] > unknown["monthly_gross"]
    assert {"category": "seniority"}.items() <= stated["trace"][1].items()
    details = {b["detail"] for b in unknown["blockers"] if b["code"] == "missing_fact"}
    assert "seniority" in details
    assert "seniority" not in {
        b["detail"] for b in stated["blockers"] if b["code"] == "missing_fact"
    }


def test_trace_adds_up_to_the_monthly_gross(demo_app: types.ModuleType) -> None:
    """The earnings of the reference month sum to its gross."""
    year = _year(demo_app, **_COMMERCIO, seniority_months=72)
    *earnings, gross = year["trace"]

    assert gross == {"category": "gross", "code": "", "amount": year["monthly_gross"]}
    assert sum(step["amount"] for step in earnings) == pytest.approx(gross["amount"])


@pytest.mark.parametrize(
    ("params", "readiness", "production"),
    [
        (_STANDARD, "production", True),
        (_COMMERCIO, "reviewed", False),
        (
            {
                **_COMMERCIO,
                "ccnl": "acconciatura-estetica-confartigianato",
                "level": "3",
            },
            "exploratory",
            False,
        ),
    ],
)
def test_readiness_is_the_ruleset_used(
    demo_app: types.ModuleType,
    params: dict[str, object],
    readiness: str,
    production: bool,
) -> None:
    """The reliability message reads the CCNL ruleset of the run."""
    ruleset = _year(demo_app, **params)["ruleset"]

    assert ruleset["readiness"] == readiness
    assert ruleset["production"] is production


def test_sources_link_only_public_addresses(demo_app: types.ModuleType) -> None:
    """A source without an HTTP address has no link."""
    for ccnl, level in (
        ("sistemazioni-idraulico-forestali-operai", None),
        ("pulizia-artigianato-confartigianato", None),
    ):
        level_code = level or json.loads(demo_app.load_ccnl_levels(ccnl))[0]["code"]
        sources = _year(
            demo_app, ccnl=ccnl, level=level_code, contract="permanent", headcount=10
        )["sources"]
        assert sources
        assert all(
            s["url"] is None or s["url"].startswith(("http://", "https://"))
            for s in sources
        )
        assert any(s["url"] is None for s in sources)


@pytest.mark.parametrize(
    "params",
    [
        {**_STANDARD, "contract": "freelance"},
        {**_STANDARD, "level": "ZZ"},
        {**_STANDARD, "ccnl": "no-such-ccnl"},
    ],
)
def test_an_invalid_scenario_returns_an_error(
    demo_app: types.ModuleType, params: dict[str, object]
) -> None:
    """compute_salary never raises across the Pyodide boundary."""
    assert "error" in json.loads(demo_app.compute_salary(json.dumps(params)))


def test_apprentice_tracks_of_a_level(demo_app: types.ModuleType) -> None:
    """Metalmeccanico C1 has two tracks: the scenario must name one."""
    tracks = json.loads(
        demo_app.load_level_tracks("metalmeccanico-federmeccanica", "C1")
    )
    apprentice = {**_STANDARD, "contract": "apprentice", "apprentice_months": 18}

    assert set(tracks) == {"professionalizzante_36", "professionalizzante_30"}
    assert "error" in json.loads(demo_app.compute_salary(json.dumps(apprentice)))
    assert _year(demo_app, **apprentice, track="professionalizzante_36")["runs"] == 13
