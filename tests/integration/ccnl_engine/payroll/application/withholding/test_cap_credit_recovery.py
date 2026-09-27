"""Credit recoveries the pay cannot cover are carried as a shortfall.

AdE circ. 29/E/2020 par. 6 and 4/E/2025 par. 1.2: a recovery the
conguaglio di fine rapporto cannot make "per incapienza della retribuzione"
falls under art. 23 c. 3 DPR 600/1973 and is communicated to the worker.
The cap takes the credit recoveries first, then IRPEF, then surtax.

Every case is built by hand: 1,000 EUR of cash earnings less 100 EUR of
employee INPS leave 900 EUR of pay before tax and recoveries.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.withholding._cap import (
    cap_withholding,
    run_net,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.pay_items import CompetencePeriod
from ccnl_engine.payroll.domain.ytd_accounts import WithholdingShortfall
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules

_YEAR = 2026
_ZERO = Decimal(0)
_RULES = load_year_rules(_YEAR, TaxSector.INDUSTRIA, 50)
_IRPEF = Decimal(200)


def _amounts() -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=Decimal(1000),
        inps_employee=Decimal(100),
        inps_employer=_ZERO,
        tfr=_ZERO,
        period_irpef=_IRPEF,
        period_tratt=_ZERO,
        period_surtax=_ZERO,
        period_taxable=_ZERO,
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
    )


def _entry(account: AccountKind, amount: Decimal) -> LedgerEntry:
    return LedgerEntry(
        entry_id=f"{account}_x",
        competence_period=CompetencePeriod(year=_YEAR, month=3),
        payment_date=date(_YEAR, 3, 27),
        pay_item_id="x",
        pay_item_kind="x",
        account=account,
        amount=amount,
    )


def _entries(*extra: LedgerEntry) -> tuple[LedgerEntry, ...]:
    return (
        _entry(AccountKind.CASH_EARNINGS, Decimal(1000)),
        _entry(AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal(100)),
        _entry(AccountKind.ORDINARY_TAX, _IRPEF),
        *extra,
    )


def test_recovery_above_the_pay_is_carried() -> None:
    """A 1,500 EUR recovery on 900 EUR of pay.

    The recovery takes the 900 EUR and IRPEF nothing: 600 EUR of recovery
    and the 200 EUR of IRPEF are carried, and the run posts a +600 EUR
    line so that its net is 1,000 - 100 - 1,500 + 600 = 0.
    """
    entries = _entries(_entry(AccountKind.CREDITS, Decimal(-1500)))
    capped = cap_withholding(
        _amounts(), entries, WithholdingShortfall(), last_slot=True, rules=_RULES
    )
    assert capped.amounts.period_irpef == _ZERO
    assert capped.shortfall == WithholdingShortfall(
        irpef=Decimal(200), credit_recovery=Decimal(600)
    )
    assert capped.recovery_adjustment == Decimal(600)
    (decision,) = capped.decisions
    assert decision.reason_code == "withholding_capped"
    assert decision.inputs["pay_available"] == Decimal(900)
    assert decision.inputs["credit_recovery_due"] == Decimal(1500)
    assert decision.amount == Decimal(800)
    (issue,) = capped.issues
    assert issue.code == "withholding_shortfall_unrecovered"
    assert "600 credit recovery" in issue.message
    net = run_net((
        _entry(AccountKind.CASH_EARNINGS, Decimal(1000)),
        _entry(AccountKind.EMPLOYEE_CONTRIBUTIONS, Decimal(100)),
        _entry(AccountKind.CREDITS, Decimal(-1500)),
        _entry(AccountKind.CREDITS, capped.recovery_adjustment),
    ))
    assert net == _ZERO


def test_carried_recovery_is_withheld_on_the_next_run() -> None:
    """600 EUR carried in, 900 EUR of pay, 200 EUR of IRPEF.

    The run withholds the 600 EUR first (a -600 EUR line), then the 200 EUR
    of IRPEF from the 300 EUR left: nothing is carried out.
    """
    capped = cap_withholding(
        _amounts(),
        _entries(),
        WithholdingShortfall(credit_recovery=Decimal(600)),
        last_slot=False,
        rules=_RULES,
    )
    assert capped.amounts.period_irpef == _IRPEF
    assert capped.shortfall == WithholdingShortfall()
    assert capped.recovery_adjustment == Decimal(-600)
    (decision,) = capped.decisions
    assert decision.reason_code == "shortfall_withheld"
    assert capped.issues == ()
