"""The una tantum of the agenti immobiliari FIAIP renewal of 19 May 2025.

Art. 163 (pp. 97-98, sha256
560d16410d3e41dc0bfb00bfe2a40ef65f2cd900234aeaee92018ed9fa21ead5): two
installments, from 1 September 2025 and 1 May 2026, level IV EUR 100.00
each; in full to a hire before 1 January 2024, "proporzionalmente ai mesi
lavorati tra la data di assunzione e il 1° maggio 2025" to a hire from 1
January 2024.  The covered period, January 2024 to April 2025, is 16
months: 12 of 2024 and 4 of 2025.

- May 2026, hired 2023: 100.00, all of earlier years, taxed apart.
- September 2025, hired 2023: 12/16 = 75.00 of 2024 apart, 25.00 of 2025
  with the run.
- Hired 1 October 2024: 7 of the 16 months, 43.75.
- Half time: 50.00.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.una_tantum.rules import UNA_TANTUM, una_tantum_events
from ccnl_engine.decision.models import DecisionOrigin
from ccnl_engine.inputs import (
    EmploymentPeriod,
    Permanent,
    PriorYearTaxFacts,
    WeeklyHours,
)
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_ENGINE = PayrollEngine.bundled()
_BIENNIO = (Decimal(30_000), Decimal(32_000))


def _run(
    year: int,
    month: int,
    hired: date | None = date(2023, 3, 1),
    hours: int = 40,
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=year, month=month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_id="agenti-immobiliari-fiaip",
                level_code="IV",
                seniority=new_hire(2023),
                roles=frozenset(),
                contract_type=Permanent(),
                employment_period=None if hired is None else EmploymentPeriod(hired),
                weekly_hours=WeeklyHours(Decimal(hours)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
            prior_year=PriorYearTaxFacts(net_income_biennio=_BIENNIO),
        )
    )


def _arrears(result: PeriodResult) -> list[tuple[str, str, Decimal]]:
    return sorted(
        (str(d.inputs["reference_period"]), d.reason_code, Decimal(d.inputs["amount"]))
        for d in result.decisions
        if d.capability == "contract_renewal_arrears"
        and d.origin is DecisionOrigin.ENGINE
    )


def test_may_2026_pays_the_whole_installment_apart() -> None:
    """Every covered month is of an earlier year."""
    result = _run(2026, 5)
    assert _arrears(result) == [("2025-04", "separate_taxation", Decimal("100.00"))]
    assert UNA_TANTUM in {lim.id for lim in result.limitations}


def test_september_2025_splits_2024_from_2025() -> None:
    """12 of the 16 covered months are of 2024 (the bundle has no 2025 tax)."""
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2025, month=9),
            payment_date=date(2025, 9, 27),
            level_code="IV",
            employment_period=EmploymentPeriod(date(2023, 3, 1)),
            weekly_hours=None,
            full_time_weekly_hours=None,
        ),
    )
    events, met = una_tantum_events(
        request, load_ccnl("agenti-immobiliari-fiaip"), RunKind.REGULAR
    )
    assert met
    assert [(e.reference_period, e.amount, e.event_date) for e in events] == [
        (PeriodId(2024, 12), Decimal("75.00"), date(2025, 9, 1)),
        (PeriodId(2025, 4), Decimal("25.00"), date(2025, 9, 1)),
    ]
    assert una_tantum_events(
        request, load_ccnl("agenti-immobiliari-fiaip"), RunKind.THIRTEENTH
    ) == ((), False)


def test_a_hire_within_the_vacancy_is_paid_its_months() -> None:
    """Hired 1 October 2024: October 2024 to April 2025, 7 of 16."""
    assert _arrears(_run(2026, 5, date(2024, 10, 1))) == [
        ("2025-04", "separate_taxation", Decimal("43.75"))
    ]


def test_a_half_time_is_paid_half() -> None:
    """20 of 40 hours."""
    assert _arrears(_run(2026, 5, hours=20)) == [
        ("2025-04", "separate_taxation", Decimal("50.00"))
    ]


@pytest.mark.parametrize("hired", [date(2025, 6, 1), None])
def test_no_payment_after_the_vacancy_or_without_the_period(
    hired: date | None,
) -> None:
    """Hired after April 2025, or not stated: nothing, the path reported."""
    result = _run(2026, 5, hired)
    assert _arrears(result) == []
    assert UNA_TANTUM in {lim.id for lim in result.limitations}


def test_a_month_without_an_installment_pays_none() -> None:
    """June 2026: no installment, no path."""
    result = _run(2026, 6)
    assert _arrears(result) == []
    assert UNA_TANTUM not in {lim.id for lim in result.limitations}
