"""One sample payslip of each tax sector, January 2026, by contract type.

For each of the eight sectors a CCNL of the sector is run as a permanent,
part-time, fixed-term and apprentice employment where the sector has them,
for an employer of 50 (5 for the apprentice of a small firm).  The expected
employee and employer contributions are computed here from the rates of
``knowledge/contribution/2026/<sector>.json`` and from the statutes, not
from the engine:

- the fixed-term surcharge of L. 92/2012 art. 2 c. 28, 1.4% of the employer,
  except the public administrations (c. 29 lett. d) and the operai agricoli
  (c. 3), whose fixed-term rate is the OTD column of INPS circ. 43/2026;
- the apprentice rates of L. 296/2006 art. 1 c. 773 and L. 92/2012 art. 2
  c. 36, cut by 8.5 points in the first year up to nine employees, plus
  the wage-integration shares of the employer they owe since 2022 (INPS
  circ. 76/2022), by headcount;
- the solidarity fund of the credito CCNL on a permanent contract (INPS
  circ. 90/2015: "tutti i lavoratori dipendenti con contratto a tempo
  indeterminato");
- the part-time pay scaled on the weekly hours (D.Lgs. 81/2015 art. 7);
- the domestic hourly contributions of INPS circ. 9/2026 on the band of
  the effective hourly pay.

Each side is the IVS share plus the rest, each taken to cents, on the base
of the run: the gross to the whole euro (INPS circ. 208/2001), to the cent
in the public administrations.
"""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

import pytest

from ccnl_engine import Employment, Headcount, PeriodResult
from ccnl_engine.inputs import (
    Apprentice,
    ContributableHours,
    FixedTerm,
    Permanent,
    WeeklyHours,
    WorkerCategory,
)
from scripts.provenance.rules import KNOWLEDGE_DIR
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import EMPLOYER, regular_period

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")
_SURCHARGE = Decimal("0.014")
_HEADCOUNT = 50
_SMALL_FIRM = 5


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _inps(sector: str) -> dict[str, Any]:
    path = KNOWLEDGE_DIR / "contribution" / "2026" / f"{sector}.json"
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _tier(tiers: list[dict[str, Any]], headcount: int) -> dict[str, Any]:
    return next(
        t
        for t in tiers
        if t["max_employees"] is None or headcount <= t["max_employees"]
    )


def _side(base: Decimal, rate: Decimal, ivs: Decimal) -> Decimal:
    return _cents(base * ivs) + _cents(base * (rate - ivs))


def _base(result: PeriodResult, sector: str) -> Decimal:
    whole = _inps(sector)["inps"].get("base_whole_euro", True)
    gross = result.period_gross
    return gross.quantize(Decimal(1), rounding=ROUND_HALF_UP) if whole else gross


def _expected(
    sector: str,
    base: Decimal,
    category: str,
    *,
    fixed_term: bool = False,
    headcount: int = _HEADCOUNT,
) -> tuple[Decimal, Decimal]:
    inps = _inps(sector)["inps"]
    employee = _tier(inps["employee_tiers"], headcount)
    employer = _tier(inps["employer_tiers"], headcount)
    rate = Decimal(employer.get("rate_by_category", {}).get(category, employer["rate"]))
    if fixed_term:
        by_category = employer.get("fixed_term_rate_by_category", {})
        exempt = sector == "pubblica-amministrazione" or category in by_category
        rate = Decimal(by_category[category]) if category in by_category else rate
        rate += Decimal(0) if exempt else _SURCHARGE
    credit = Decimal(inps.get("public_credit", {}).get("employee_rate", "0"))
    employee_side = _side(
        base, Decimal(employee["rate"]), Decimal(employee["ivs_rate"])
    ) + _cents(base * credit)
    return employee_side, _side(base, rate, Decimal(employer["ivs_rate"]))


def _solidarity(slug: str, base: Decimal) -> tuple[Decimal, Decimal]:
    path = KNOWLEDGE_DIR / "agreement" / f"{slug}.json"
    fund = json.loads(path.read_text(encoding="utf-8"))["parameters"].get(
        "solidarity_fund"
    )
    if fund is None:
        return Decimal(0), Decimal(0)
    return (
        _cents(base * Decimal(fund["employee_rate"])),
        _cents(base * Decimal(fund["employer_rate"])),
    )


def _run(
    slug: str,
    level: str,
    category: WorkerCategory | None,
    contract_type: Permanent | FixedTerm | Apprentice,
    headcount: int = _HEADCOUNT,
    **employment: object,
) -> PeriodResult:
    return regular_period(
        employment=Employment(
            ccnl_id=slug,
            level_code=level,
            category=category,
            seniority=new_hire(),
            contract_type=contract_type,
            **employment,  # type: ignore[arg-type]
        ),
        employer=replace(EMPLOYER, headcount=Headcount(headcount)),
    )


def _actual(result: PeriodResult) -> tuple[Decimal, Decimal]:
    breakdown = result.contribution_breakdown
    return breakdown.employee, breakdown.employer


#: Sector, CCNL, level and the category of the level.
_SAMPLES = (
    ("industria", "metalmeccanico-federmeccanica", "C3", "operaio"),
    ("terziario", "commercio-confcommercio", "4", "impiegato"),
    ("edilizia", "edilizia-ance-impiegati", "4", "impiegato"),
    ("artigianato", "metalmeccanico-artigianato", "2bis", "operaio"),
    ("credito", "bancari-abi", "3A4", "impiegato"),
    ("agricoltura", "operai-agricoli-florovivaisti", "Area2", "operaio"),
    (
        "pubblica-amministrazione",
        "funzioni-centrali-aran",
        "FUNZIONARI",
        "impiegato",
    ),
)


@pytest.mark.parametrize(("sector", "slug", "level", "category"), _SAMPLES)
@pytest.mark.parametrize("fixed_term", [False, True], ids=["permanent", "fixed_term"])
def test_permanent_and_fixed_term_contributions(
    sector: str, slug: str, level: str, category: str, fixed_term: bool
) -> None:
    """The sector rates, plus the surcharge where the statute charges it."""
    contract = FixedTerm() if fixed_term else Permanent()
    result = _run(slug, level, WorkerCategory(category), contract)
    base = _base(result, sector)
    employee, employer = _expected(sector, base, category, fixed_term=fixed_term)
    fund = (Decimal(0), Decimal(0)) if fixed_term else _solidarity(slug, base)

    assert _actual(result) == (employee + fund[0], employer + fund[1])


def test_part_time_scales_the_pay_and_keeps_the_rates() -> None:
    """20 of 40 hours: half the pay, the same rates on it."""
    full = _run(
        "metalmeccanico-federmeccanica", "C3", WorkerCategory.OPERAIO, Permanent()
    )
    half = _run(
        "metalmeccanico-federmeccanica",
        "C3",
        WorkerCategory.OPERAIO,
        Permanent(),
        weekly_hours=WeeklyHours(Decimal(20)),
        full_time_weekly_hours=WeeklyHours(Decimal(40)),
    )

    assert half.period_gross == _cents(full.period_gross / 2)
    assert _actual(half) == _expected("industria", _base(half, "industria"), "operaio")


@pytest.mark.parametrize(
    ("headcount", "employer_rate", "employer_ivs"),
    [
        (_HEADCOUNT, "employer_rate", "employer_ivs_rate"),
        (
            _SMALL_FIRM,
            "small_firm_employer_rate_months_0_11",
            "small_firm_employer_ivs_rate_months_0_11",
        ),
    ],
    ids=["firm_of_50", "firm_of_5"],
)
def test_apprentice_rates(
    headcount: int, employer_rate: str, employer_ivs: str
) -> None:
    """11.61% of the employer, 3.11% in the first year up to nine employees.

    Both plus the FIS and CIGS shares of the employer's headcount.
    """
    result = _run(
        "commercio-confcommercio",
        "4",
        WorkerCategory.IMPIEGATO,
        Apprentice(months_elapsed=6),
        headcount,
    )
    rates = _inps("terziario")["apprentice"]
    share = _tier(rates["headcount_shares"], headcount)
    base = _base(result, "terziario")
    employee = Decimal(rates["employee_rate"]) + Decimal(share["employee_rate"])
    employer = Decimal(rates[employer_rate]) + Decimal(share["employer_rate"])

    assert _actual(result) == (
        _side(base, employee, Decimal(rates["employee_ivs_rate"])),
        _side(base, employer, Decimal(rates[employer_ivs])),
    )


def test_domestic_hourly_contributions() -> None:
    """Over 11.70 an hour of effective pay: 0.59 and 1.75 an hour."""
    hours = Decimal(86)
    result = regular_period(
        employment=Employment(
            ccnl_id="lavoro-domestico-non-convivente",
            level_code="B",
            seniority=new_hire(),
            contract_type=Permanent(),
            weekly_hours=WeeklyHours(Decimal(20)),
        ),
        contributable_hours=ContributableHours(hours),
    )
    bands = _inps("lavoro-domestico")["domestic_contributions"]["wage_brackets"]
    (top,) = [b for b in bands if b["hourly_rate_up_to"] is None]

    assert _actual(result) == (
        _cents(hours * Decimal(top["employee_per_hour"])),
        _cents(hours * Decimal(top["employer_per_hour"])),
    )
