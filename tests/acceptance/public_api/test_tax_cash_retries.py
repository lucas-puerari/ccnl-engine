"""A payment closes once: retries never count competence or cash twice.

Each run closes its competence run in the accrual state and its payment in
the tax cash state.  Recomputing a payment on the state it opened with is
deterministic; recomputing it on a state that already closed it is
rejected before any amount is computed, and a year or tax-year plan
resumed on such a state skips the payments it already closed with the
same payment id.  The accrual state survives the
change of tax year, so a December already paid in its own year cannot be
paid again in the next one.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    TaxYearPlan,
)
from ccnl_engine.inputs import Permanent
from ccnl_engine.results import EvidenceStatus, ResultAssurance
from tests.fixtures.next_year_repository import NextYearRepository
from tests.fixtures.payment_sequence import Payment, PaymentSequence

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult
    from ccnl_engine.inputs import PeriodState

_COMMERCIO_L4 = Employment(
    ccnl_slug="commercio-confcommercio.json", level_code="4", contract_type=Permanent()
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_ENGINE = PayrollEngine(repository=NextYearRepository())
_LATE_DECEMBER = Payment(PayrollRun.regular(2026, 12), date(2027, 1, 13))
_JANUARY = Payment(PayrollRun.regular(2027, 1), date(2027, 1, 27))


def test_retry_on_the_same_opening_state_is_identical() -> None:
    """The same payment on the same opening state closes the same state."""
    first = PaymentSequence(employment=_COMMERCIO_L4).pay(_LATE_DECEMBER)
    retry = PaymentSequence(employment=_COMMERCIO_L4).pay(_LATE_DECEMBER)

    assert retry.closing_state == first.closing_state
    assert retry.period_net == first.period_net


@pytest.mark.parametrize(
    "retry",
    [_LATE_DECEMBER, Payment(_LATE_DECEMBER.run, date(2027, 1, 14))],
    ids=["same date", "other date"],
)
def test_retry_on_the_closed_state_is_rejected(retry: Payment) -> None:
    """A payment already closed is rejected, whatever its payment date."""
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay_all([_LATE_DECEMBER, _JANUARY])
    closed = sequence.state

    with pytest.raises(InvalidInputError, match="already closed") as info:
        sequence.pay(retry)

    assert info.value.feature == "accrual_state"
    assert sequence.state is closed
    assert closed.cash.withholding_payments_closed == 2
    assert closed.accrual.regular_months(2026) == 1


@cache
def _year_2026() -> PeriodState:
    """Close tax year 2026 paid on the 28th of every month.

    Returns:
        The state that opens tax year 2027.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_COMMERCIO_L4, employer=_EMPLOYER)
    )
    return _ENGINE.close_tax_year(year.closing_state)


def test_december_paid_in_its_year_cannot_be_paid_again_late() -> None:
    """December 2026 closed in 2026 is rejected on 13 January 2027."""
    sequence = PaymentSequence(employment=_COMMERCIO_L4, state=_year_2026())

    with pytest.raises(InvalidInputError, match="already closed"):
        sequence.pay(_LATE_DECEMBER)


def test_year_calculation_after_a_late_december() -> None:
    """The 2027 year runs on 15 slots: the late December, then its 14 runs.

    The commercio calendar pays twelve months, the quattordicesima and the
    tredicesima: fourteen runs computed by the year, one more payment
    already closed by the opening state.
    """
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay(_LATE_DECEMBER)

    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2027,
            employment=_COMMERCIO_L4,
            employer=_EMPLOYER,
            opening_state=sequence.state,
        )
    )

    assert len(year.period_results) == 14
    slots = {
        d.inputs["withholding_slots"]
        for r in year.period_results
        for d in r.decisions
        if d.capability == "irpef"
    }
    assert slots == {"15"}
    closing = year.closing_state
    assert closing.cash.withholding_payments_closed == 15
    assert _ENGINE.close_tax_year(closing).tax_year == 2028


def test_year_calculation_rejects_a_run_closed_with_another_payment() -> None:
    """January 2027 paid on the 27th cannot be planned again on the 28th."""
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay_all([_LATE_DECEMBER, _JANUARY])

    with pytest.raises(InvalidInputError, match="already closed with another") as info:
        _ENGINE.calculate_competence_year(
            CompetenceYearPlan(
                year=2027,
                employment=_COMMERCIO_L4,
                employer=_EMPLOYER,
                opening_state=sequence.state,
            )
        )

    assert info.value.feature == "accrual_state"


@cache
def _year_2026_result() -> CompetenceYearResult:
    """Compute the 2026 competence year once, paid on the 28th of each month.

    Returns:
        The fourteen runs of 2026.
    """
    return _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_COMMERCIO_L4, employer=_EMPLOYER)
    )


@pytest.mark.parametrize("stopped_after", [1, 7, 13])
def test_a_plan_resumed_on_an_interrupted_state_gives_the_same_year(
    stopped_after: int,
) -> None:
    """Resuming after k payments computes the rest once: same closing state.

    The payments the opening state already closed with the same payment id
    are skipped, so the resumed results are the tail of one pass.
    """
    whole = _year_2026_result()
    interrupted = whole.period_results[stopped_after - 1].closing_state

    resumed = _ENGINE.calculate_tax_year(
        TaxYearPlan(
            tax_year=2026,
            competence_years=(
                CompetenceYearPlan(
                    year=2026, employment=_COMMERCIO_L4, employer=_EMPLOYER
                ),
            ),
            opening_state=interrupted,
        )
    )

    assert resumed.closing_state == whole.closing_state
    assert resumed.period_results == whole.period_results[stopped_after:]
    assert resumed.payments == whole.closing_state.cash.payments
    computed = whole.closing_state.cash.payments[stopped_after:]
    assert resumed.assessed_payments == computed
    assert (
        resumed.blockers
        == ResultAssurance.combine(
            r.assurance for r in whole.period_results[stopped_after:]
        ).blockers
    )


def test_a_plan_retried_on_its_closing_state_computes_nothing() -> None:
    """A retry after the last payment adds no payment and changes no total."""
    whole = _year_2026_result()

    retried = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=_COMMERCIO_L4,
            employer=_EMPLOYER,
            opening_state=whole.closing_state,
        )
    )

    assert retried.period_results == ()
    assert retried.closing_state == whole.closing_state
    assert retried.annual_gross == 0
    assert retried.assessed_payments == ()
    assert not retried.is_payable
    assert retried.assurance.evidence is EvidenceStatus.MISSING


def test_close_tax_year_is_rejected_twice() -> None:
    """A closed year has no conguaglio left to close: no duplicate year."""
    opened = _ENGINE.close_tax_year(_year_2026_result().closing_state)

    with pytest.raises(InvalidInputError, match="not complete"):
        _ENGINE.close_tax_year(opened)


def test_monthly_payslips_close_2026_with_a_december_paid_on_13_january() -> None:
    """Payslip by payslip: the tredicesima states that nothing follows it.

    Without ``planned_payments`` the standard December salary would still be
    expected in 2026; with ``()`` the tredicesima settles the conguaglio, the
    year closes and the December salary opens 2027.
    """
    runs = [PayrollRun.regular(2026, m) for m in range(1, 12)]
    runs.insert(6, PayrollRun.fourteenth(2026, 6))
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay_all(Payment(run, date(2026, run.month, 27)) for run in runs)
    thirteenth = sequence.engine.calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12),
            payment_date=date(2026, 12, 15),
            employment=_COMMERCIO_L4,
            employer=_EMPLOYER,
            opening_state=sequence.state,
            planned_payments=(),
        )
    )

    opening_2027 = _ENGINE.close_tax_year(thirteenth.closing_state)
    late = PaymentSequence(employment=_COMMERCIO_L4, state=opening_2027)
    december = late.pay(_LATE_DECEMBER)

    assert thirteenth.closing_state.cash.conguaglio is not None
    assert december.closing_state.tax_year == 2027
    assert december.closing_state.accrual.regular_months(2026) == 12
