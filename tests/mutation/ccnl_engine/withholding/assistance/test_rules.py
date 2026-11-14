"""What the payslips settle of a 730-4 statement."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.withholding.assistance.inputs import (
    Form730Kind,
    Form730Line,
    Form730Settlement,
)
from ccnl_engine.withholding.assistance.rules import first_month, schedule

_K = Form730Kind


def _statement(
    received: date, installments: int = 1, **amounts: str
) -> Form730Settlement:
    lines = tuple(Form730Line(_K(k), Decimal(v)) for k, v in amounts.items())
    return Form730Settlement(received, lines, installments)


def test_the_month_after_the_receipt_settles() -> None:
    """Received in June: the July pay; in December: January of the next year."""
    assert first_month(_statement(date(2026, 6, 20))) == (2026, 7)
    assert first_month(_statement(date(2026, 12, 3))) == (2027, 1)


def test_a_refund_and_a_single_debt_on_the_first_pay() -> None:
    """A credit is refunded whole; a debt without installments is withheld whole."""
    plan = schedule(
        _statement(date(2026, 6, 20), irpef_balance="-300.00", regional_surtax="80.00")
    )
    assert [(i.kind, i.month, i.amount, i.interest) for i in plan] == [
        (_K.IRPEF_BALANCE, 7, Decimal("-300.00"), Decimal(0)),
        (_K.REGIONAL_SURTAX, 7, Decimal("80.00"), Decimal(0)),
    ]


def test_twelve_euro_or_less_is_neither_withheld_nor_refunded() -> None:
    """Per tax: 12.00 and -12.00 drop, 12.01 stays."""
    plan = schedule(
        _statement(
            date(2026, 6, 20),
            irpef_balance="12.00",
            regional_surtax="-12.00",
            municipal_surtax="12.01",
        )
    )
    assert [(i.kind, i.amount) for i in plan] == [
        (_K.MUNICIPAL_SURTAX, Decimal("12.01"))
    ]


def test_installments_with_the_interest_of_each_month() -> None:
    """300.00 in 3: 100.00 each, 0.33% for each month after the first."""
    plan = schedule(_statement(date(2026, 6, 20), 3, irpef_balance="300.00"))
    assert [(i.month, i.amount, i.interest) for i in plan] == [
        (7, Decimal("100.00"), Decimal("0.00")),
        (8, Decimal("100.00"), Decimal("0.33")),
        (9, Decimal("100.00"), Decimal("0.66")),
    ]


def test_installments_end_in_november_and_keep_the_cents() -> None:
    """Received in September: 6 asked, 2 possible (October, November)."""
    plan = schedule(_statement(date(2026, 9, 10), 6, irpef_first_advance="100.01"))
    assert [(i.month, i.amount) for i in plan] == [
        (10, Decimal("50.01")),
        (11, Decimal("50.00")),
    ]


def test_the_second_acconto_in_november_never_in_installments() -> None:
    """Withheld whole in November whatever the installments asked."""
    plan = schedule(_statement(date(2026, 6, 20), 5, irpef_second_advance="400.00"))
    assert [(i.month, i.amount, i.interest) for i in plan] == [
        (11, Decimal("400.00"), Decimal(0))
    ]


@pytest.mark.parametrize("installments", [0, 7])
def test_installments_between_one_and_six(installments: int) -> None:
    """DM 164/1999: up to six monthly installments."""
    with pytest.raises(InvalidInputError):
        _statement(date(2026, 6, 20), installments, irpef_balance="10")


def test_a_kind_once() -> None:
    """Each line of the statement once."""
    line = Form730Line(_K.IRPEF_BALANCE, Decimal(1))
    with pytest.raises(InvalidInputError):
        Form730Settlement(date(2026, 6, 20), (line, line))
