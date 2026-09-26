"""Tax year attribution and obligations that survive the year change."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import PayrollState
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.ytd_accounts import TrattamentoAccount
from tests.acceptance.legal_scenarios._support import regular_period

pytestmark = pytest.mark.legal_scenario


def test_december_paid_by_twelve_january_stays_in_previous_year() -> None:
    """Cassa allargata: pay paid by 12 January belongs to the previous year.

    Art. 51 c. 1 TUIR: December 2026 pay paid on 12 January 2027 is 2026 income.
    """
    result = regular_period(month=12, payment_date=date(2027, 1, 12))

    assert result.closing_state.tax_year == 2026


@pytest.mark.xfail(
    strict=True,
    reason="tax year follows the competence period instead of the payment date",
)
def test_december_paid_after_twelve_january_moves_to_next_year() -> None:
    """Art. 51 c. 1 TUIR: pay received after 12 January is taxed by cash in 2027.

    A fix also needs the 2027 tax tables, which are not bundled yet.

    Observed on 26 September 2026: tax year 2026, the same result as for a
    payment on 27 December 2026 or in June 2028.
    """
    result = regular_period(month=12, payment_date=date(2027, 1, 13))

    assert result.closing_state.tax_year == 2027


@pytest.mark.xfail(
    strict=True,
    reason="starting a new tax year drops an active installment recovery plan",
)
def test_installment_recovery_survives_the_year_change() -> None:
    """D.L. 3/2020 art. 1 c. 3: recovery above 60 EUR runs in 8 installments.

    A plan of 160.00 EUR in 8 installments of 20.00 with 2 posted before
    December posts the third in December, leaving 5 installments (100.00) for
    2027.  The state that opens 2027 must still carry them.

    Observed on 26 September 2026: December posts -20.00 and keeps the plan,
    but ``zero()`` returns a state without it.
    """
    plan = RecoveryPlan(
        kind="trattamento_integrativo",
        original_amount=Decimal(160),
        installment_amount=Decimal(20),
        installments_total=8,
        installments_posted=2,
    )
    opening = PayrollState(
        tax_year=2026,
        regular_periods_closed=11,
        tax_withholding_periods_closed=11,
        trattamento=TrattamentoAccount(
            recognized=Decimal(160), recovered=Decimal(40), plan=plan
        ),
    )
    december = regular_period(month=12, opening_state=opening)
    carried = december.closing_state.trattamento.plan
    assert carried is not None
    assert carried.residual == Decimal("100.00")

    next_year = december.closing_state.zero()

    assert next_year.trattamento.plan == carried
