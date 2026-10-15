"""First-round CCNLs against the cost tables of the Ministry of Labour.

The Ministry of Labour sets the cost of labour of a CCNL in tables
(D.Lgs. 36/2023 art. 41 c. 13), an example the engine is not built from:

- Metalmeccanica industria, impiegati, June 2026 (DD 82 of 5 October 2026,
  sha256 4fc6ef9789a1708128cfddfcfa9860d9321a81997a3ba1fd425d50eeb33eae6b):
  level C3 with 3 scatti, tabellare 26.537,16 and scatti 1.067,04 a year,
  INPS 29.36%, TFR on tabellare and scatti over 13.5.
- Edilizia, operai, May 2025 (DD 40 of 13 May 2026, sha256
  0e6a8b8da4217b9a1fe31f35924428c5c33ddcd726d05135b185b39149afed72): level 1,
  minimo 6,17, contingenza 2,96 and EDR 0,06 an hour, riposi annui 4,95%,
  Cassa Edile 18,50%, INPS 34,28% for 15-50 employees.

The deviations the tables show (INAIL, the health funds, the provincial
elements, the elemento perequativo) are declared in the CCNL files.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from ccnl_engine import Employment, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.inputs import (
    ContributableHours,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.pay_item.models import (
    BaseSalaryEarning,
    FixedAllowanceEarning,
    HourlyPercentageEarning,
    SeniorityEarning,
    TfrAccrualItem,
)
from tests.knowledge.ccnl_engine.support import EMPLOYER, regular_period

if TYPE_CHECKING:
    from ccnl_engine.contribution.results import ContributionComponent

_CENT = Decimal("0.01")


def _employer_rate(components: tuple[ContributionComponent, ...]) -> Decimal:
    return sum((c.rate for c in components if c.name.endswith("_employer")), Decimal(0))


def test_metalmeccanica_impiegato_c3_june_2026() -> None:
    """Tabellare, scatti, INPS rate and TFR of the table."""
    employment = Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        seniority=SeniorityFact.since(
            date(2020, 1, 1), SenioritySource.EMPLOYER_RECORDS
        ),
        pension_fund=NoPensionFund(),
        contract_type=Permanent(),
        category=WorkerCategory.IMPIEGATO,
    )
    result = regular_period(
        employment=employment,
        employer=replace(EMPLOYER, headcount=Headcount(51)),
        month=6,
    )
    items = result.pay_items
    (base,) = [i.amount for i in items if isinstance(i, BaseSalaryEarning)]
    (scatti,) = [i.amount for i in items if isinstance(i, SeniorityEarning)]
    (tfr,) = [i.amount for i in items if isinstance(i, TfrAccrualItem)]
    components = result.contribution_breakdown.components
    inps_base = components[0].base

    assert base == (Decimal("26537.16") / 12).quantize(_CENT, ROUND_HALF_UP)
    assert scatti == (Decimal("1067.04") / 12).quantize(_CENT, ROUND_HALF_UP)
    assert _employer_rate(components) == Decimal("0.2936")
    gross_tfr = ((base + scatti) / Decimal("13.5")).quantize(_CENT, ROUND_HALF_UP)
    assert tfr == gross_tfr - (inps_base * Decimal("0.005")).quantize(_CENT)


def test_edilizia_operaio_level_1() -> None:
    """Hourly elements, riposi annui, Cassa Edile accrual and INPS rate."""
    result = regular_period(
        ccnl_slug="edilizia-ance.json",
        level_code="1",
        month=1,
        employer=replace(EMPLOYER, headcount=Headcount(30)),
        ordinary_hours_worked=ContributableHours(Decimal(173)),
    )
    items = result.pay_items
    (base,) = [i.amount for i in items if isinstance(i, BaseSalaryEarning)]
    allowances = sorted(i.amount for i in items if isinstance(i, FixedAllowanceEarning))
    percentages = sorted(
        i.amount for i in items if isinstance(i, HourlyPercentageEarning)
    )
    contingenza = allowances[-1]
    hourly = [
        (v / 173).quantize(_CENT, ROUND_HALF_UP)
        for v in (base, contingenza, allowances[0])
    ]

    assert hourly == [Decimal("6.17"), Decimal("2.96"), Decimal("0.06")]
    assert percentages == [
        ((base + contingenza) * Decimal(r)).quantize(_CENT, ROUND_HALF_UP)
        for r in ("0.0495", "0.185")
    ]
    assert _employer_rate(result.contribution_breakdown.components) == Decimal("0.3428")
