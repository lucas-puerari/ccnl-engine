"""A fixed-term worker's sickness on the payslip (D.L. 463/1983 art. 5).

Metalmeccanico C3 operaio, an episode from Monday 9 to Friday 20 March 2026,
hired on 1 January 2026: 67 days with this employer before 9 March.
- 200 days of work before it: every day paid, INPS advanced (the same as
  an open-ended contract);
- 20 days of work: 30 days of 2026 at most, all within the episode, and
  INPS pays its share directly (c. 3): nothing advanced on the payslip;
- an episode of all March with 20 days of work: 31 March is the 31st day
  of 2026, past the 30 days, unpaid and deducted.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.fact.inputs import EmploymentPeriod
from ccnl_engine.employment.fixed_term.inputs import FixedTerm, NaspiExclusion
from ccnl_engine.events import SicknessEpisode
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import calculate_period
from ccnl_engine.run.types import PeriodId
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult


def _run(worked: int | None, first: int = 9, last: int = 20) -> PeriodResult:
    episode = SicknessEpisode(
        "FT", date(2026, 3, first), date(2026, 3, last), prior_worked_days=worked
    )
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            seniority=new_hire(),
            opening_state=PeriodState.zero(),
            events=(episode,),
            category=WorkerCategory.OPERAIO,
            contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
            employment_period=EmploymentPeriod(date(2026, 1, 1)),
        )
    )


def _amount(result: PeriodResult, kind: str) -> Decimal:
    return sum((i.amount for i in result.pay_items if i.kind == kind), Decimal(0))


def test_inps_paid_directly_is_not_advanced() -> None:
    """With 20 days of work INPS pays directly: no INPS share on the payslip."""
    advanced = _run(200)
    direct = _run(20)

    assert _amount(advanced, "sickness_inps_item") > 0
    assert _amount(direct, "sickness_inps_item") == 0
    # The employer still pays its integration on top of what INPS pays.
    assert _amount(direct, "sickness_item") == _amount(advanced, "sickness_item")


def test_unstated_days_of_work_are_reported() -> None:
    """Without prior_worked_days the limit is not applied, with an issue."""
    result = _run(None)

    assert "sickness_fixed_term_prior_work_unknown" in {i.code for i in result.issues}
    assert _amount(result, "sickness_inps_item") == _amount(
        _run(200), "sickness_inps_item"
    )


def test_days_past_the_limit_are_deducted_unpaid() -> None:
    """All of March with 20 days of work: 31 March is unpaid sickness."""
    limited = _run(20, 1, 31)
    segments = {
        d.inputs.get("segments")
        for d in limited.decisions
        if d.capability == "sickness"
    }

    assert any("fixed_term_limit" in str(s) for s in segments)
