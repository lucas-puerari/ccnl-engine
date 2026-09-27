"""Tax and credit base lines: non-negative amounts, account and code by flow."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.period._tax_lines import surtax_split, tax_lines
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome

_ZERO = Decimal(0)


def _amounts(
    *,
    irpef: Decimal = _ZERO,
    tratt: Decimal = _ZERO,
    surtax: Decimal = _ZERO,
    annual: SurtaxOutcome | None = None,
) -> _PeriodAmounts:
    return _PeriodAmounts(
        monthly_gross=Decimal(2000),
        inps_employee=_ZERO,
        inps_employer=_ZERO,
        tfr=_ZERO,
        period_irpef=irpef,
        period_tratt=tratt,
        period_surtax=surtax,
        period_taxable=_ZERO,
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
        surtax=annual if annual is not None else SurtaxOutcome(),
    )


def _shape(
    amounts: _PeriodAmounts,
) -> list[tuple[str, AccountKind, Decimal, str | None]]:
    return [
        (line.entry_stem or line.stem, line.account, line.amount, line.remittance_code)
        for line in tax_lines(amounts)
    ]


def test_surtax_split_follows_the_annual_ratio() -> None:
    """Annual 300 regional and 100 municipal: 33.34 of a run is 25.01 + 8.33.

    33.34 * 300 / 400 = 25.005, rounded half up to 25.01; the municipal
    part is the residual 33.34 - 25.01 = 8.33.
    """
    annual = SurtaxOutcome(regional=Decimal(300), municipal=Decimal(100))

    assert surtax_split(Decimal("33.34"), annual) == (Decimal("25.01"), Decimal("8.33"))


def test_surtax_split_without_annual_surtax_is_zero() -> None:
    """No annual surtax: nothing to split on."""
    assert surtax_split(Decimal(10), SurtaxOutcome()) == (_ZERO, _ZERO)


def test_surtax_carried_in_without_annual_surtax_is_one_uncoded_line() -> None:
    """10 EUR carried in, no annual surtax left: one uncoded ``surtax`` line."""
    assert _shape(_amounts(surtax=Decimal(10))) == [
        ("surtax", AccountKind.SURTAX, Decimal(10), None)
    ]


def test_regional_only_surtax_posts_no_municipal_line() -> None:
    """A municipality without surtax: the whole run goes to 3802."""
    annual = SurtaxOutcome(regional=Decimal(240))

    assert _shape(_amounts(surtax=Decimal(20), annual=annual)) == [
        ("surtax_regional", AccountKind.SURTAX, Decimal(20), "3802")
    ]


def test_refund_and_recovery_are_positive_on_their_accounts() -> None:
    """IRPEF refunded and trattamento recovered post positive amounts."""
    assert _shape(_amounts(irpef=Decimal(-50), tratt=Decimal(-30))) == [
        ("irpef_refund", AccountKind.TAX_REFUNDS, Decimal(50), None),
        ("tratt_integ_recovery", AccountKind.CREDIT_RECOVERIES, Decimal(30), None),
    ]


def test_trattamento_recovery_keeps_a_negative_pay_item() -> None:
    """The pay item of a recovery keeps the signed amount of the payslip."""
    (line,) = tax_lines(_amounts(tratt=Decimal(-30)))

    assert (line.stem, line.item_amount) == ("tratt_integ", Decimal(-30))


def test_withholding_and_credit_paid_are_coded() -> None:
    """IRPEF withheld under 1001, trattamento paid under 1701."""
    assert _shape(_amounts(irpef=Decimal(200), tratt=Decimal(100))) == [
        ("irpef", AccountKind.ORDINARY_TAX, Decimal(200), "1001"),
        ("tratt_integ", AccountKind.CREDITS, Decimal(100), "1701"),
    ]
