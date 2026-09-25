"""Regression tests for substitute tax regime eligibility and credit recovery bugs.

All tests are marked xfail(strict=True): they document the normatively correct
behaviour.  When fixes land these turn XPASS, causing CI to fail and prompting
removal of the markers.

Bugs covered:

1. Substitute tax applied unconditionally regardless of prior-year income.
   Source: L. 199/2025 art. 1 co. 9 — productivity bonus tassazione sostitutiva
   1% up to 5,000 EUR applies only to workers with reddito da lavoro dipendente
   e assimilati of the previous year within the income ceiling (80,000 EUR).
   Current: no eligibility check; 1% is applied to every BonusEvent of kind
   "productivity_bonus", including workers above the ceiling.

2. Trattamento integrativo recovery does not use eight equal installments.
   Source: D.L. 3/2020, art. 1 comma 3 — if the amount to recover exceeds 60 EUR
   the recovery must occur in eight equal installments ("otto rate di pari
   ammontare") starting from the reconciliation payslip.
   Current: _resolve_trattamento divides the recovery by remaining periods,
   producing a rate proportional to calendar position rather than a fixed
   eight-installment plan.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.ledger import AccountKind
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.events import BonusEvent
from ccnl_engine.payroll.domain.period import PeriodCalculationRequest, PeriodState

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_ZERO = Decimal(0)


def _sum_account(result: object, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),  # type: ignore[attr-defined]
        _ZERO,
    )


# ---------------------------------------------------------------------------
# Bug 1 — substitute tax applied regardless of prior-year income ceiling
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BonusEvent has no prior_income field; substitute tax at 1% is applied "
        "unconditionally to every productivity_bonus. Workers above the 80,000 EUR "
        "income ceiling must not receive the agevolazione."
    ),
)
def test_productivity_bonus_ineligible_above_income_ceiling() -> None:
    """Productivity bonus above the income ceiling must be taxed at ordinary rates.

    Source: L. 199/2025 art. 1 co. 9 — tassazione sostitutiva 1% applies only
    for workers with prior-year reddito ≤ income_ceiling (variable-pay-rules.json
    income_ceiling=80000).  A worker with prior_income=90000 must have
    SUBSTITUTE_TAX = 0.00 and the bonus taxed at ordinary IRPEF rates.

    Current behaviour: SUBSTITUTE_TAX = 50.00 for a 5,000 EUR bonus regardless
    of prior income (BonusEvent carries no prior_income; eligibility is never
    checked).
    """
    bonus = BonusEvent(
        event_date=date(_YEAR, 1, 15),
        amount=Decimal("5000.00"),
        kind="productivity_bonus",
    )
    req = PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=1),
        payment_date=date(_YEAR, 1, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
        events=(bonus,),
        # prior_year_income not representable in current API — no such field exists
    )
    result = calculate_period(req)

    sub_tax = _sum_account(result, AccountKind.SUBSTITUTE_TAX)
    assert sub_tax == _ZERO, (
        f"A productivity_bonus for an ineligible worker must produce "
        f"SUBSTITUTE_TAX = 0.00; got {sub_tax}.  "
        "Fix: BonusEvent must carry prior_income and eligibility must be checked "
        "before applying the substitute rate."
    )


# ---------------------------------------------------------------------------
# Bug 2 — trattamento integrativo recovery not in eight equal installments
# ---------------------------------------------------------------------------


def test_trattamento_integrativo_recovery_uses_eight_installments() -> None:
    """Recovery of trattamento integrativo > 60 EUR must use eight equal installments.

    Source: D.L. 3/2020, art. 1 comma 3.

    Scenario: nine months of credit recognized at ~100/month = 900 EUR total.
    In October a large bonus (20,000 EUR) pushes annual taxable above the 28,000
    threshold, so the annual entitlement drops to 0 and the full 900 EUR must be
    recovered in 8 equal installments of 112.50 EUR.
    """
    opening = PeriodState(
        regular_periods_closed=9,
        tax_withholding_periods_closed=9,
        credit_recognized_ytd=Decimal("900.00"),
        credit_recovered_ytd=Decimal(0),
        gross_ytd=Decimal("20000.00"),
        taxable_ytd=Decimal("18000.00"),
        inps_base_ytd=Decimal("20000.00"),
        irpef_withheld_ytd=Decimal("2000.00"),
    )
    bonus = BonusEvent(
        event_date=date(_YEAR, 10, 15),
        amount=Decimal("20000.00"),
        kind="bonus",
    )
    req = PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=10),
        payment_date=date(_YEAR, 10, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening,
        events=(bonus,),
    )
    result = calculate_period(req)

    recovery = _sum_account(result, AccountKind.CREDITS)
    installment = Decimal("900.00") / 8
    assert recovery == -installment, (
        f"First recovery installment must be -900/8 = -{installment}; got {recovery}."
    )


def test_trattamento_integrativo_small_recovery_taken_in_one_period() -> None:
    """Recovery of trattamento integrativo <= 60 EUR must be taken in a single period.

    Source: D.L. 3/2020, art. 1 comma 3 — only amounts > 60 EUR trigger the
    eight-installment plan; smaller amounts must be recovered in one shot.

    Scenario: 50 EUR of credit recognized across 9 months, income rises above
    threshold in October.  Recovery = 50 EUR (<= 60): deducted fully in month 10.
    """
    opening = PeriodState(
        regular_periods_closed=9,
        tax_withholding_periods_closed=9,
        credit_recognized_ytd=Decimal("50.00"),
        credit_recovered_ytd=Decimal(0),
        gross_ytd=Decimal("20000.00"),
        taxable_ytd=Decimal("18000.00"),
        inps_base_ytd=Decimal("20000.00"),
        irpef_withheld_ytd=Decimal("2000.00"),
    )
    bonus = BonusEvent(
        event_date=date(_YEAR, 10, 15),
        amount=Decimal("20000.00"),
        kind="bonus",
    )
    req = PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=10),
        payment_date=date(_YEAR, 10, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=opening,
        events=(bonus,),
    )
    result = calculate_period(req)

    recovery = _sum_account(result, AccountKind.CREDITS)
    assert recovery == Decimal("-50.00"), (
        f"Recovery ≤ 60 EUR must be fully deducted in one period; got {recovery}."
    )
