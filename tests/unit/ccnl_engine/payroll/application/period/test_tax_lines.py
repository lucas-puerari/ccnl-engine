"""Tax and credit base lines: non-negative amounts, account and code by flow."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application.amounts._surtax import RunSurtax
from ccnl_engine.payroll.application.amounts._types import _PeriodAmounts
from ccnl_engine.payroll.application.period._tax_lines import tax_lines
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.surtax_obligations import SurtaxComponent, SurtaxPart

_ZERO = Decimal(0)


def _amounts(
    *,
    irpef: Decimal = _ZERO,
    tratt: Decimal = _ZERO,
    surtax: Decimal | None = None,
    run_surtax: RunSurtax | None = None,
) -> _PeriodAmounts:
    run = run_surtax if run_surtax is not None else RunSurtax()
    return _PeriodAmounts(
        monthly_gross=Decimal(2000),
        inps_employee=_ZERO,
        inps_employer=_ZERO,
        tfr=_ZERO,
        period_irpef=irpef,
        period_tratt=tratt,
        period_surtax=run.due if surtax is None else surtax,
        period_taxable=_ZERO,
        period_substitute_tax=_ZERO,
        pdr_eligible=_ZERO,
        surtax=run,
    )


def _shape(
    amounts: _PeriodAmounts,
) -> list[tuple[str, AccountKind, Decimal, str | None]]:
    return [
        (line.entry_stem or line.stem, line.account, line.amount, line.remittance_code)
        for line in tax_lines(amounts)
    ]


_PARTS = (
    SurtaxPart(SurtaxComponent.REGIONAL_BALANCE, 2025, Decimal(20)),
    SurtaxPart(SurtaxComponent.MUNICIPAL_BALANCE, 2025, Decimal(8)),
    SurtaxPart(SurtaxComponent.MUNICIPAL_ADVANCE, 2026, Decimal(5)),
)


def test_surtax_parts_post_one_coded_line_each() -> None:
    """Regional 3802, municipal saldo 3848 and acconto 3847 (Allegato 1)."""
    assert _shape(_amounts(run_surtax=RunSurtax(parts=_PARTS))) == [
        ("surtax_regional_balance_2025", AccountKind.SURTAX, Decimal(20), "3802"),
        ("surtax_municipal_balance_2025", AccountKind.SURTAX, Decimal(8), "3848"),
        ("surtax_municipal_advance_2026", AccountKind.SURTAX, Decimal(5), "3847"),
    ]


def test_surtax_carried_in_is_withheld_first_on_an_uncoded_line() -> None:
    """10 carried in and 33 due, 25 withheld: 10 carried, 15 regional.

    The pay covers 25 of the 43 due: the carried surtax first, then the
    parts in order; the municipal parts wait for the next run.
    """
    run = RunSurtax(parts=_PARTS, carried_in=Decimal(10))

    assert _shape(_amounts(surtax=Decimal(25), run_surtax=run)) == [
        ("surtax", AccountKind.SURTAX, Decimal(10), None),
        ("surtax_regional_balance_2025", AccountKind.SURTAX, Decimal(15), "3802"),
    ]
    assert run.advance_withheld(Decimal(25), 2026) == _ZERO
    assert run.advance_withheld(Decimal(43), 2026) == Decimal(5)


def test_municipal_advance_refund_is_a_surtax_refund_line() -> None:
    """An acconto given back posts a positive uncoded SURTAX_REFUNDS line."""
    run = RunSurtax(refund=Decimal("12.50"))

    assert _shape(_amounts(run_surtax=run)) == [
        ("surtax_refund", AccountKind.SURTAX_REFUNDS, Decimal("12.50"), None)
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
