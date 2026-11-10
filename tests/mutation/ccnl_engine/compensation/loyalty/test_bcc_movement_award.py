"""Art. 102: EUR 1,800 salary + EUR 200 increments = EUR 2,000.

At the 25-year movement milestone, 0.9066 x 2,000 = EUR 1,813.20;
24 years or an ineligible professional-area level pays EUR 0. The monthly
chain is only an approximation of the enumerated Art. 102 pay components.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.compensation.loyalty.rules import loyalty_premium
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource

from .test_rules import _context

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext


def test_movement_milestone_only_in_qualifying_month_and_levels() -> None:
    """EUR 2,000 x 90.66% = EUR 1,813.20 in April, zero at 24 years."""
    ctx = cast("SimpleNamespace", _context(start=date(2010, 7, 15)))
    ctx.contract.ccnl.parameters.loyalty_premium = SimpleNamespace(
        service_years=25,
        months=Decimal("0.9066"),
        recurrence="once",
        categories=(WorkerCategory.QUADRO,),
        subsectors=(),
        levels=("QD3", "QD4"),
        service_basis="recognised",
        manual_hours=None,
        provenance=SimpleNamespace(location=SimpleNamespace(section="Art. 102")),
    )
    ctx.request.level_code = "QD3"
    ctx.worker_category = WorkerCategory.QUADRO
    ctx.request.seniority = SeniorityFact.since(
        date(2001, 4, 15), SenioritySource.PAYSLIP
    )
    assert loyalty_premium(cast("RunContext", ctx)).amount == Decimal("1813.20")
    ctx.request.level_code = "3AP3"
    ctx.worker_category = WorkerCategory.IMPIEGATO
    assert loyalty_premium(cast("RunContext", ctx)).amount == 0
    ctx.request.level_code = "QD3"
    ctx.worker_category = WorkerCategory.QUADRO
    ctx.request.seniority = SeniorityFact.since(
        date(2002, 4, 15), SenioritySource.PAYSLIP
    )
    assert loyalty_premium(cast("RunContext", ctx)).amount == 0
    ctx.request.seniority = SeniorityFact.since(
        date(2001, 4, 15), SenioritySource.PAYSLIP
    )
    ctx.request.period_id.month = 5
    assert loyalty_premium(cast("RunContext", ctx)).amount == 0


def test_bundled_bcc_qd3_movement_award() -> None:
    """EUR 4,396.88 + 7 x EUR 95.31 = EUR 5,064.05.

    The QD3 award is 0.9066 x 5,064.05 = EUR 4,591.07 in April;
    an area worker, or a QD3 with only 24 years, receives EUR 0.
    This excludes unprovided individual allowances.
    """

    def run(level: str, service_from: date) -> list[Decimal]:
        result = calculate_period(
            PeriodCalculationRequest(
                employer=EmployerProfile(headcount=Headcount(20)),
                period_id=PeriodId(2026, 4),
                payment_date=date(2026, 4, 27),
                ccnl_id="bcc-credito-cooperativo",
                level_code=level,
                opening_state=PeriodState.zero(),
                roles=frozenset(),
                events=(),
                employment_period=EmploymentPeriod(started_on=date(2010, 7, 15)),
                seniority=SeniorityFact.since(service_from, SenioritySource.PAYSLIP),
            ),
            repo=bundled_repository(),
            resolver=bundled_policies(),
        )
        return [
            item.amount for item in result.pay_items if item.kind == "bonus_earning"
        ]

    assert run("QD3", date(2001, 4, 15)) == [Decimal("4591.07")]
    assert run("3AP3", date(2001, 4, 15)) == []
    assert run("QD3", date(2002, 4, 15)) == []


@pytest.mark.parametrize(
    "case", ["missing", "annual", "recent", "ended_prior", "ended_early", "ended_late"]
)
def test_recognised_service_requires_active_milestone(case: str) -> None:
    """EUR 2,000 x 90.66% pays EUR 1,813.20 only while employed."""
    ctx = cast("SimpleNamespace", _context(start=date(2010, 7, 15)))
    ctx.contract.ccnl.parameters.loyalty_premium = SimpleNamespace(
        service_years=25,
        months=Decimal("0.9066"),
        recurrence="annual" if case == "annual" else "once",
        categories=(WorkerCategory.QUADRO,),
        subsectors=(),
        levels=("QD3",),
        service_basis="recognised",
        manual_hours=None,
        provenance=SimpleNamespace(location=SimpleNamespace(section="Art. 102")),
    )
    ctx.request.level_code = "QD3"
    ctx.worker_category = WorkerCategory.QUADRO
    ctx.request.seniority = (
        None
        if case == "missing"
        else SeniorityFact.since(
            date(2026, 4, 15) if case == "recent" else date(2001, 4, 15),
            SenioritySource.PAYSLIP,
        )
    )
    if case in {"ended_prior", "ended_early", "ended_late"}:
        ctx.request.employment_period = EmploymentPeriod(
            started_on=date(2010, 7, 15),
            ended_on={
                "ended_prior": date(2026, 3, 31),
                "ended_early": date(2026, 4, 14),
                "ended_late": date(2026, 4, 20),
            }[case],
        )
    expected = Decimal("1813.20") if case == "ended_late" else Decimal(0)
    assert loyalty_premium(cast("RunContext", ctx)).amount == expected


def test_annual_award_requires_employment_through_anniversary() -> None:
    """Employment ending April 14 cannot earn the April 15 EUR 2,000 award."""
    ctx = cast("SimpleNamespace", _context())
    ctx.request.employment_period = EmploymentPeriod(
        started_on=date(2006, 4, 15), ended_on=date(2026, 4, 14)
    )
    assert loyalty_premium(cast("RunContext", ctx)).amount == 0
