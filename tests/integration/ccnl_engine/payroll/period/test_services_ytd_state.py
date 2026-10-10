"""Year-to-date counters closed by a period and their use in the conguaglio.

A period adds to the YTD counters only what belongs to them: the full
taxable of a bonus, no bilateral-fund amount in the INPS counter.  The
December conguaglio reads them: a different taxable YTD changes the IRPEF,
an excess withheld becomes a refund, and the trattamento integrativo
recognised in one month is recovered in a later one.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine.payroll.event.facade import BilateralFundEvent, BonusEvent
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.models_run import PayrollRun
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState
from ccnl_engine.payroll.state.models_tax_cash import TaxCashState
from ccnl_engine.payroll.state.models_ytd_account import EarningsYtd, TaxYtd
from tests.fixtures.period_requests import account_total, period_request
from tests.fixtures.withholding import identified, paid_before

_YEAR = 2026
_ZERO = Decimal(0)
_CCNL_TRATT = "portieri-fabbricati-confedilizia.json"
_LEVEL_TRATT = "B5"  # 1,264.51 EUR/month (terziario sector, trattamento integrativo)


# ---------------------------------------------------------------------------
# taxable_ytd diluted by additional_months divisor
#
# _compute_amounts() sets period_taxable = taxable / additional_months and
# increments closing.taxable_ytd by that fraction.  A 1,000 EUR bonus whose
# INPS-net taxable is ~905.10 EUR therefore adds only ~69.62 EUR (905.10/13)
# to taxable_ytd instead of the full ~905.10.
# ---------------------------------------------------------------------------


def test_taxable_ytd_not_diluted_by_extra_months() -> None:
    """closing_state.taxable_ytd must increase by exactly 905.10 for a 1,000 EUR bonus.

    1,000 EUR bonus, employee INPS contribution 94.90 EUR (9.49%):
    event_taxable = 1,000.00 - 94.90 = 905.10.
    The current engine produces 810.20 due to a double-deduction of INPS
    inside event_taxable + actual_total_inps.
    """
    bonus = BonusEvent(event_date=date(_YEAR, 1, 15), amount=Decimal("1000.00"))

    result_base = calculate_period(period_request(month=1))
    result_with = calculate_period(period_request(month=1, events=(bonus,)))

    ytd_diff = (
        result_with.closing_state.cash.earnings.taxable
        - result_base.closing_state.cash.earnings.taxable
    )
    assert ytd_diff == Decimal("905.10"), (
        f"taxable_ytd increase from a 1,000 EUR bonus must be exactly 905.10 "
        f"(gross 1000 minus INPS 94.90); got {ytd_diff}."
    )


# ---------------------------------------------------------------------------
# Bilateral-fund employee amount added to inps_employee_ytd
#
# BilateralFundEvent is posted to EMPLOYEE_CONTRIBUTIONS, which is also the
# account whose running total drives inps_employee_ytd.  The fund contribution
# is not an INPS amount and must not affect the INPS YTD counter.
# ---------------------------------------------------------------------------


def test_bilateral_fund_excluded_from_inps_employee_ytd() -> None:
    """BilateralFundEvent must not change inps_employee_ytd.

    A 100 EUR bilateral fund contribution must not
    alter closing_state.inps_employee_ytd relative to the no-fund baseline.
    """
    fund = BilateralFundEvent(
        event_date=date(_YEAR, 1, 15),
        employee_amount=Decimal("100.00"),
        employer_amount=Decimal("100.00"),
    )

    result_base = calculate_period(period_request(month=1))
    result_with = calculate_period(period_request(month=1, events=(fund,)))

    base_ytd = result_base.closing_state.cash.earnings.inps_employee
    with_ytd = result_with.closing_state.cash.earnings.inps_employee
    assert with_ytd == base_ytd, (
        f"inps_employee_ytd with bilateral fund ({with_ytd}) must equal "
        f"baseline ({base_ytd}).  Fund employee amount currently posted to "
        "EMPLOYEE_CONTRIBUTIONS and counted toward inps_employee_ytd."
    )


# ---------------------------------------------------------------------------
# taxable_ytd in PeriodState not used in IRPEF conguaglio
#
# The conguaglio (IRPEF settling) in the final period depends on the actual
# YTD taxable income, not only on the projected annual figure.  When
# taxable_ytd differs between two otherwise identical December requests the
# resulting IRPEF must differ.
# Source: art. 23 c. 3 DPR 600/1973, ritenuta per conguaglio
# ---------------------------------------------------------------------------


def test_taxable_ytd_affects_conguaglio() -> None:
    """Different taxable_ytd must produce different IRPEF in the conguaglio.

    Source: art. 23 c. 3 DPR 600/1973.  Two December calculations, one with
    taxable_ytd=0 and one with taxable_ytd=15,000, must produce different
    ordinary_tax.
    """
    paid = paid_before(PayrollRun.regular(_YEAR, 12), day=28)
    opening_zero = identified(PeriodState(cash=TaxCashState()), paid)
    opening_high = identified(
        PeriodState(
            cash=TaxCashState(earnings=EarningsYtd(taxable=Decimal("15000.00")))
        ),
        paid,
    )
    # December is the last payment of the year: it settles the conguaglio.
    result_zero = calculate_period(
        replace(period_request(month=12, opening=opening_zero), planned_payments=())
    )
    result_high = calculate_period(
        replace(period_request(month=12, opening=opening_high), planned_payments=())
    )
    assert result_zero.closing_state.cash.conguaglio is not None

    tax_zero = result_zero.tax_computation.ordinary_tax
    tax_high = result_high.tax_computation.ordinary_tax
    assert tax_zero != tax_high, (
        "December IRPEF must differ when taxable_ytd differs: "
        f"taxable_ytd=0 -> {tax_zero}, "
        f"taxable_ytd=15000 -> {tax_high}.  "
        "taxable_ytd is ignored in the current projection (_compute_amounts.py)."
    )


# ---------------------------------------------------------------------------
# pregresso superiore al debito → rimborso 0.00
# ---------------------------------------------------------------------------


def test_excess_ytd_produces_refund() -> None:
    """When YTD already withheld exceeds annual liability a refund must appear.

    A December calculation with irpef_withheld_ytd=5000 and annual IRPEF
    liability well below 5000 must post a TaxRefundItem in TAX_REFUNDS rather than
    a negative ORDINARY_TAX entry (refunds now use the explicit TaxRefundItem
    representation instead of a signed withholding entry).
    """
    high_ytd = PeriodState(
        cash=TaxCashState(
            tax=TaxYtd(irpef=Decimal("5000.00")),
        )
    )
    # No payment planned after December: it settles the conguaglio.
    result = calculate_period(
        replace(period_request(month=12, opening=high_ytd), planned_payments=())
    )

    # Refund appears as a positive TAX_REFUNDS entry (tax_refund_item), not as
    # negative ORDINARY_TAX.
    refund = sum(
        e.amount
        for e in result.ledger_entries
        if e.account == AccountKind.TAX_REFUNDS and e.pay_item_kind == "tax_refund_item"
    )
    assert refund > _ZERO, (
        f"No TaxRefundItem in TAX_REFUNDS when 5000 YTD withheld exceeds liability; "
        f"ORDINARY_TAX = {account_total(result, AccountKind.ORDINARY_TAX)}"
    )


def test_credit_recognized_in_january_recovered_in_february() -> None:
    """Gate: credit_recognized_ytd and credit_recovered_ytd both advance correctly.

    Period 1 (January): B5 portieri salary (~15k EUR annual, terziario sector)
    → trattamento integrativo given → credit_recognized_ytd > 0.
    Period 2 (February): same salary + 25,000 EUR bonus → annual projection
    far above 28k EUR → annual trattamento = 0 → period_tratt < 0 (recovery)
    → credit_recovered_ytd > 0, credit_recognized_ytd unchanged.
    """
    # Period 1: January — B5 portieri baseline, no events
    result1 = calculate_period(
        period_request(month=1, ccnl=_CCNL_TRATT, level=_LEVEL_TRATT)
    )
    state1 = result1.closing_state
    assert state1.cash.trattamento.recognized > _ZERO, (
        "Trattamento integrativo must be recognized in January for B5 portieri "
        "income level (~15k EUR annual, terziario sector)"
    )
    assert state1.cash.trattamento.recovered == _ZERO

    # Period 2: February — large bonus pushes projected annual income above 28k EUR
    bonus = BonusEvent(event_date=date(_YEAR, 2, 15), amount=Decimal("25000.00"))
    result2 = calculate_period(
        period_request(
            month=2,
            opening=state1,
            events=(bonus,),
            ccnl=_CCNL_TRATT,
            level=_LEVEL_TRATT,
        )
    )
    state2 = result2.closing_state

    assert state2.cash.trattamento.recognized == state1.cash.trattamento.recognized, (
        "credit_recognized_ytd must not grow when period_tratt <= 0"
    )
    assert state2.cash.trattamento.recovered > _ZERO, (
        "Trattamento integrativo must be partially recovered in February "
        "when a 25,000 EUR bonus projects annual income far above 28k EUR"
    )
