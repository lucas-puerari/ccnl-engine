"""A payment closes once: retries never count competence or cash twice.

Each run closes its competence run in the accrual state and its payment in
the tax cash state.  Recomputing a payment on the state it opened with is
deterministic; recomputing it on a state that already closed it is
rejected before any amount is computed.  The accrual state survives the
change of tax year, so a December already paid in its own year cannot be
paid again in the next one.
"""

from __future__ import annotations

from datetime import date
from functools import cache

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodState,
    YearInput,
)
from tests.fixtures.next_year_repository import NextYearRepository
from tests.fixtures.payment_sequence import Payment, PaymentSequence

_COMMERCIO_L4 = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
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
    year = _ENGINE.calculate_year(
        YearInput(year=2026, employment=_COMMERCIO_L4, employer=_EMPLOYER)
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

    year = _ENGINE.calculate_year(
        YearInput(
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


def test_year_calculation_rejects_a_run_of_the_year_already_closed() -> None:
    """January 2027 already paid cannot open a 2027 year calculation."""
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay_all([_LATE_DECEMBER, _JANUARY])

    with pytest.raises(InvalidInputError, match="must close no run") as info:
        _ENGINE.calculate_year(
            YearInput(
                year=2027,
                employment=_COMMERCIO_L4,
                employer=_EMPLOYER,
                opening_state=sequence.state,
            )
        )

    assert info.value.field == "YearInput.opening_state"
