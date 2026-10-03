"""A tax year accepts every payment made in it, late competences included.

Art. 51 c. 1 TUIR (cassa allargata): pay of December 2026 paid after 12
January 2027 is 2027 income.  That year then also pays its own twelve
months and the quattordicesima: fourteen payments, thirteen of them regular
runs.  The year state must count payments of the tax year, not months of
competence.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine import DataIntegrityError, Employment, PayrollRun
from tests.fixtures.payment_sequence import Payment, PaymentSequence

_COMMERCIO_L4 = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")


def _late_december_then_2027() -> list[Payment]:
    """Return December 2026 paid on 13 January 2027, then the 2027 year.

    The quattordicesima is paid with the July pay, after the July run.

    Returns:
        Fifteen payments, in payment order, all of tax year 2027.
    """
    payments = [Payment(PayrollRun.regular(2026, 12), date(2027, 1, 13))]
    for month in range(1, 13):
        payments.append(Payment(PayrollRun.regular(2027, month), date(2027, month, 27)))
        if month == 7:
            payments.append(Payment(PayrollRun.fourteenth(2027, 7), date(2027, 7, 27)))
    return payments


@pytest.mark.xfail(
    strict=True,
    raises=DataIntegrityError,
    reason="the year state caps regular runs at twelve per tax year",
)
def test_late_december_payment_leaves_room_for_the_next_year() -> None:
    """December 2027 is computed after a late December 2026 payment.

    Today December 2026 paid on 13 January 2027 opens 2027 with one regular
    run closed; January to November and the quattordicesima bring it to 12
    regular and 13 withholding runs, and December 2027 fails with
    ``DataIntegrityError``: ``regular_periods_closed`` would be 13.
    """
    sequence = PaymentSequence(employment=_COMMERCIO_L4)

    results = sequence.pay_all(_late_december_then_2027())

    assert len(results) == 15
    assert {result.closing_state.tax_year for result in results} == {2027}
