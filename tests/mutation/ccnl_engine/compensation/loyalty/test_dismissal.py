"""Art. 65 CNA closing runs: EUR 2,763.57 x 5/12 = EUR 1,151.49.

The 15 April anniversary through 14 October contains five completed months;
the sixth month is incomplete. Before this change the termination award was zero.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.decision.models import CalculationStatus
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.period.inputs import EmploymentPeriod, TerminationCause
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.models import PayrollRun, RunKind
from ccnl_engine.run.types import PeriodId


def _run(
    cause: TerminationCause | None = TerminationCause.DISMISSAL,
    disciplinary: bool | None = False,
    *,
    ended: date = date(2026, 10, 14),
    started: date = date(2000, 4, 15),
    run_month: int | None = None,
    open_employment: bool = False,
) -> PeriodResult:
    month = ended.month if run_month is None else run_month
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(20)),
            period_id=PeriodId(ended.year, month),
            payment_date=date(ended.year, month, 27),
            ccnl_id="edilizia-artigianato-cna",
            level_code="7",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=(),
            employment_period=EmploymentPeriod(
                started_on=started,
                ended_on=None if open_employment else ended,
                ended_by=cause,
                disciplinary_dismissal=disciplinary,
            ),
            run=PayrollRun(run_kind=RunKind.TERMINATION, year=ended.year, month=month),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _awards(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if i.kind == "loyalty_premium_earning"]


def test_dismissal_pays_five_whole_twelfths_not_six() -> None:
    """EUR 2,763.57 normal monthly pay x 5 / 12 = EUR 1,151.49, not zero."""
    result = _run()
    assert _awards(result) == [Decimal("1151.49")]
    (decision,) = (
        d for d in result.decisions if d.reason_code == "loyalty_dismissal_twelfths"
    )
    assert decision.inputs["whole_months"] == "5"
    assert decision.inputs["annual_award"] == Decimal("2763.57")
    assert decision.amount == Decimal("1151.49")
    assert decision.source is not None
    assert decision.source.section is not None
    assert "Art. 65" in decision.source.section


def test_resignation_and_disciplinary_dismissal_pay_zero() -> None:
    """Same EUR 2,763.57 base: resignation and disciplinary dismissal owe EUR 0."""
    assert _awards(_run(TerminationCause.RESIGNATION, None)) == []
    assert _awards(_run(disciplinary=True)) == []


@pytest.mark.parametrize(
    ("cause", "disciplinary", "fact"),
    [
        (None, None, "ended_by"),
        (TerminationCause.DISMISSAL, None, "disciplinary_dismissal"),
    ],
)
def test_missing_closing_fact_blocks_award(
    cause: TerminationCause | None, disciplinary: bool | None, fact: str
) -> None:
    """Potential EUR 1,151.49 is blocked, never assumed to be payable."""
    result = _run(cause, disciplinary)
    assert _awards(result) == []
    (issue,) = (i for i in result.issues if i.code == f"loyalty_{fact}_unknown")
    assert issue.fact == fact
    assert issue.status is CalculationStatus.INCOMPLETE


def test_previous_anniversary_must_have_vested_and_month_must_complete() -> None:
    """Without a previous qualifying award, or a full month, pay EUR 0."""
    assert _awards(_run(started=date(2007, 4, 15))) == []
    assert _awards(_run(ended=date(2026, 4, 30))) == []


def test_previous_year_anniversary_and_only_closing_month() -> None:
    """A March end counts whole months since last April, not the next April."""
    march = _run(ended=date(2026, 3, 14))
    assert len(_awards(march)) == 1
    assert _awards(_run(run_month=9)) == []


def test_no_last_day_does_not_invent_a_dismissal_award() -> None:
    """An employment without an end date owes no termination twelfths."""
    assert _awards(_run(None, None, open_employment=True)) == []


def test_unknown_monthly_wage_does_not_invent_twelfths() -> None:
    """An unpriced annual award cannot imply a pro-rated monetary amount."""
    with patch(
        "ccnl_engine.compensation.loyalty.termination._award_amount", return_value=None
    ):
        assert _awards(_run()) == []


def test_disciplinary_fact_is_only_valid_on_dismissal() -> None:
    """A resignation cannot supply a disciplinary dismissal indicator."""
    with pytest.raises(InvalidInputError, match="applies only to a dismissal"):
        EmploymentPeriod(
            started_on=date(2000, 4, 15),
            ended_on=date(2026, 10, 14),
            ended_by=TerminationCause.RESIGNATION,
            disciplinary_dismissal=False,
        )
