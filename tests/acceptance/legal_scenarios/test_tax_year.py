"""Tax year attribution and obligations that survive the year change."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import PayrollState
from ccnl_engine.engine.errors import InvalidInputError, UnsupportedTaxYearError
from ccnl_engine.payroll.domain.employment_context import TemporalContext
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


def test_december_paid_by_ten_january_stays_in_previous_year() -> None:
    """Art. 51 c. 1 TUIR: December 2026 paid on 10 January 2027 is 2026 income."""
    result = regular_period(month=12, payment_date=date(2027, 1, 10))

    assert result.closing_state.tax_year == 2026


def test_december_paid_after_twelve_january_moves_to_next_year() -> None:
    """Art. 51 c. 1 TUIR: pay received after 12 January is taxed by cash in 2027."""
    temporal = TemporalContext.from_period(2026, 12, date(2027, 1, 13))

    assert temporal.competence == date(2026, 12, 1)
    assert temporal.fiscal_year == 2027


@pytest.mark.parametrize(
    ("payment_date", "tax_year"),
    [(date(2027, 1, 13), 2027), (date(2028, 6, 28), 2028)],
)
def test_run_of_unbundled_tax_year_raises_domain_error(
    payment_date: date, tax_year: int
) -> None:
    """The engine computes the run with the payment year's tables.

    Those tables are not bundled, so the run fails with a domain error that
    names the attributed tax year instead of computing it with 2026 rules.
    """
    with pytest.raises(UnsupportedTaxYearError) as info:
        regular_period(month=12, payment_date=payment_date)

    assert info.value.year == tax_year


def test_run_of_next_tax_year_is_not_added_to_current_year_state() -> None:
    """December 2026 paid on 13 January 2027 cannot close into the 2026 state."""
    opening = PayrollState(
        tax_year=2026, regular_periods_closed=11, tax_withholding_periods_closed=11
    )

    with pytest.raises(InvalidInputError, match="belongs to tax year 2027"):
        regular_period(month=12, payment_date=date(2027, 1, 13), opening_state=opening)


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
