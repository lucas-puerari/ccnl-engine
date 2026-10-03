"""A tax year accepts every payment made in it, late competences included.

Art. 51 c. 1 TUIR (cassa allargata): pay of December 2026 paid after 12
January 2027 is 2027 income.  That year then also pays its own twelve
months, the quattordicesima and the tredicesima: fifteen payments, thirteen
of them regular runs, over two competence years.  The tax cash state counts
the payments of the tax year; the accrual state counts the months of each
competence year.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import cache

from ccnl_engine import Employment, PayrollRun
from tests.fixtures.payment_sequence import Payment, PaymentSequence

_COMMERCIO_L4 = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")


def _late_december_then_2027() -> list[Payment]:
    """Return December 2026 paid on 13 January 2027, then the 2027 year.

    Commercio pays the quattordicesima with the July pay and the
    tredicesima with the December pay, each after its regular run.

    Returns:
        Fifteen payments, in payment order, all of tax year 2027: 1 late
        December + 12 regular months + quattordicesima + tredicesima.
    """
    payments = [Payment(PayrollRun.regular(2026, 12), date(2027, 1, 13))]
    for month in range(1, 13):
        payments.append(Payment(PayrollRun.regular(2027, month), date(2027, month, 27)))
        if month == 7:
            payments.append(Payment(PayrollRun.fourteenth(2027, 7), date(2027, 7, 27)))
    payments.append(Payment(PayrollRun.thirteenth(2027, 12), date(2027, 12, 18)))
    return payments


@cache
def _paid_2027() -> PaymentSequence:
    """Pay every payment of tax year 2027 once per test session.

    Returns:
        The sequence after the fifteen payments.
    """
    sequence = PaymentSequence(employment=_COMMERCIO_L4)
    sequence.pay_all(_late_december_then_2027())
    return sequence


def test_late_december_payment_leaves_room_for_the_next_year() -> None:
    """December 2027 and the tredicesima are computed after a late December.

    The 2027 tax year holds 15 payments and closes complete: the
    withholding schedule of each run has 15 slots (the late December first),
    so the conguaglio falls on the tredicesima, the last payment.
    """
    sequence = _paid_2027()
    results = sequence.results

    assert len(results) == 15
    assert {result.closing_state.tax_year for result in results} == {2027}
    slots = {
        d.inputs["withholding_slots"]
        for r in results
        for d in r.decisions
        if d.capability == "irpef"
    }
    assert slots == {"15"}
    closing = sequence.state
    assert closing.accrual.regular_months(2026) == 1
    assert closing.accrual.regular_months(2027) == 12
    assert len(closing.accrual.extra_months_paid(2027)) == 2
    assert closing.cash.withholding_payments_closed == 15
    assert closing.cash.withholding_slots == 15
    assert closing.cash.is_complete
    assert [str(p) for p in closing.cash.prior_competence_payments] == [
        "2026-12-regular@2027-01-13"
    ]


def test_late_december_is_counted_once_in_the_cash_totals() -> None:
    """The YTD gross of 2027 is the sum of its 15 payments, December included."""
    sequence = _paid_2027()
    results = sequence.results

    gross = sequence.state.cash.earnings.gross
    assert gross == sum((r.period_gross for r in results), Decimal(0))
    assert results[0].period_gross > 0
