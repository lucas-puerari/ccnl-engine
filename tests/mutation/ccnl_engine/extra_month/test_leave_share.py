"""The 13th of a compulsory maternity leave at the share of the CCNL.

ANASTE art. 45 c. 23 (2025 text, PDF p. 43): "la 13° mensilità limitatamente
all'aliquota corrispondente al 20% della retribuzione".  2026, a leave from 1
March to 31 July: 7 months accrue without it, 5 only with it.  The rateo is
7 + 5 x 0.20 = 8 months of 12: scale 8/12, fraction 0.6667 of a month.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.absence.insured.inputs import MaternityLeaveEvent
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.extra_month.leave_share import (
    LeaveShare,
    leave_share,
    maternity_share,
    with_leave_share,
)
from ccnl_engine.extra_month.models import ExtraMonthAccrual
from ccnl_engine.extra_month.schedule.models import ExtraMonthKind, ExtraMonthSchedule
from ccnl_engine.inputs import EmploymentPeriod, NoPensionFund, Permanent
from ccnl_engine.period.facts.inputs import PeriodFacts
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_SCHEDULE = ExtraMonthSchedule(
    kind=ExtraMonthKind.THIRTEENTH,
    name="thirteenth",
    payment_month=12,
    accrual_window_start_month=1,
)
_LEAVE = MaternityLeaveEvent(date(2026, 3, 1), date(2026, 7, 31))


def _accrual() -> ExtraMonthAccrual:
    return ExtraMonthAccrual.of(_SCHEDULE, 2026)


def test_the_leave_months_accrue_at_the_share() -> None:
    """Five leave months at 20%: 8 of 12 months paid."""
    share = leave_share(Decimal("0.20"), (_LEAVE,))
    assert share is not None
    paid = with_leave_share(_accrual(), frozenset(), share)
    assert paid.accrued == 12
    assert paid.scale == Decimal(8) / Decimal(12)
    assert round(paid.fraction, 4) == Decimal("0.6667")


def test_the_whole_rateo_without_a_share_or_a_leave() -> None:
    """A CCNL with no share, or a year with no leave, keeps the rateo."""
    assert leave_share(None, (_LEAVE,)) is None
    assert leave_share(Decimal("0.20"), ()) is None
    accrual = _accrual()
    assert with_leave_share(accrual, frozenset(), None) is accrual


def test_a_leave_outside_the_accrued_months_changes_nothing() -> None:
    """Months already suspended, or not accrued, are not the leave's."""
    accrual = ExtraMonthAccrual.of(
        _SCHEDULE, 2026, non_accruing_days=_days(date(2026, 3, 1), date(2026, 7, 31))
    )
    share = LeaveShare(_days(date(2026, 3, 1), date(2026, 7, 31)), Decimal("0.20"))
    suspended = _days(date(2026, 3, 1), date(2026, 7, 31))
    assert with_leave_share(accrual, suspended, share) is accrual


def test_anaste_states_its_share() -> None:
    """ANASTE pays 20%; a CCNL without the clause pays the whole rateo."""
    assert maternity_share(
        load_ccnl("istituzioni-servizi-socio-assistenziali-anaste")
    ) == (Decimal("0.20"))
    assert maternity_share(load_ccnl("commercio-confcommercio")) is None


def _days(first: date, last: date) -> frozenset[date]:
    return frozenset(
        date.fromordinal(d) for d in range(first.toordinal(), last.toordinal() + 1)
    )


def _thirteenth_at_termination(events: tuple[MaternityLeaveEvent, ...]) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 7),
            payment_date=date(2026, 7, 28),
            employment=Employment(
                ccnl_id="istituzioni-servizi-socio-assistenziali-anaste",
                level_code="4",
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2025, 1, 1), date(2026, 7, 31)),
                contract_type=Permanent(),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(events=events),
        )
    )
    (quantity,) = (
        i.quantity for i in result.pay_items if i.kind == "extra_month_earning"
    )
    return quantity


def test_the_termination_liquidates_the_leave_months_at_the_share() -> None:
    """ANASTE, ending 31 July 2026: 7/12 without the leave.

    With a leave from March, 2 months + 5 x 0.20 = 3 of 12.
    """
    assert _thirteenth_at_termination(()) == Decimal(7) / Decimal(12)
    assert _thirteenth_at_termination((_LEAVE,)) == Decimal(3) / Decimal(12)
