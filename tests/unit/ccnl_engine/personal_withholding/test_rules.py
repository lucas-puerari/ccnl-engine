"""Limits of garnishments and salary assignments, computed by hand.

Art. 545 c. 3-5 c.p.c., art. 72-ter DPR 602/1973 (art. 171 D.Lgs. 33/2025
from 2027) and art. 5, 68-70 DPR 180/1950; each limit is rounded down to
the cent.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.personal_withholding.inputs import PersonalWithholdingKind as Kind
from ccnl_engine.personal_withholding.rules import DueWithholding, allocate

_OPEN = Decimal(100_000)


def _due(
    kind: Kind, installment: str | None = None, residual: Decimal = _OPEN
) -> DueWithholding:
    return DueWithholding(
        kind, None if installment is None else Decimal(installment), residual
    )


@pytest.mark.parametrize(
    ("base", "dues", "expected", "rules"),
    [
        # Art. 545 c. 4: a fifth of 1,500.00.
        ("1500.00", [_due(Kind.ORDINARY)], ["300.00"], ["cpc-art545-c4"]),
        # Agente della riscossione: 1/10 up to 2,500, 1/7 up to 5,000, 1/5 above.
        ("2000.00", [_due(Kind.TAX_COLLECTION)], ["200.00"], ["dpr602-1973-art72ter"]),
        ("2500.00", [_due(Kind.TAX_COLLECTION)], ["250.00"], ["dpr602-1973-art72ter"]),
        ("3000.00", [_due(Kind.TAX_COLLECTION)], ["428.57"], ["dpr602-1973-art72ter"]),
        ("6000.00", [_due(Kind.TAX_COLLECTION)], ["1200.00"], ["dpr602-1973-art72ter"]),
        # Maintenance 400 first: the cessione gets 2/5 x 1,500 - 400 = 200 (art. 68).
        (
            "1500.00",
            [_due(Kind.MAINTENANCE, "400"), _due(Kind.SALARY_ASSIGNMENT, "250")],
            ["400", "200.00"],
            ["cpc-art545-c3", "dpr180-1950-art68-c1"],
        ),
        # Cessione 250 first, then a garnishment (its fifth, 300) and maintenance
        # 400, which gets what the half leaves: 750 - 250 - 300 = 200.
        (
            "1500.00",
            [
                _due(Kind.SALARY_ASSIGNMENT, "250"),
                _due(Kind.ORDINARY),
                _due(Kind.MAINTENANCE, "400"),
            ],
            ["250", "300.00", "200.00"],
            ["dpr180-1950-art5", "cpc-art545-c4", "dpr180-1950-art68-c2"],
        ),
        # Two ordinary garnishments share the fifth: the first, with 100 left
        # to pay, leaves 200 to the second.
        (
            "1500.00",
            [_due(Kind.ORDINARY, residual=Decimal(100)), _due(Kind.ORDINARY)],
            ["100", "200.00"],
            ["cpc-art545-c4", "cpc-art545-c4"],
        ),
        # A maintenance order alone takes its measure, never more than the net.
        ("500.00", [_due(Kind.MAINTENANCE, "800")], ["500.00"], ["cpc-art545-c3"]),
        # A delegation after a garnishment: half of 1,500 less 300 (art. 69).
        (
            "1500.00",
            [_due(Kind.ORDINARY), _due(Kind.PAYMENT_DELEGATION, "600")],
            ["300.00", "450.00"],
            ["cpc-art545-c4", "dpr180-1950-art69"],
        ),
        # A cessione and a delegation stop at half of 1,500 together (art. 70).
        (
            "1500.00",
            [_due(Kind.SALARY_ASSIGNMENT, "250"), _due(Kind.PAYMENT_DELEGATION, "600")],
            ["250", "500.00"],
            ["dpr180-1950-art5", "dpr180-1950-art70"],
        ),
        # After a delegation of 600, a cessione and a garnishment share the
        # 150 the half leaves.
        (
            "1500.00",
            [
                _due(Kind.PAYMENT_DELEGATION, "600"),
                _due(Kind.SALARY_ASSIGNMENT, "250"),
                _due(Kind.TAX),
            ],
            ["600", "150.00", "0.00"],
            ["dpr180-1950-art70", "dpr180-1950-art70", "dpr180-1950-art68-c2"],
        ),
        (
            "1500.00",
            [_due(Kind.PAYMENT_DELEGATION, "700"), _due(Kind.TAX)],
            ["700", "50.00"],
            ["dpr180-1950-art70", "dpr180-1950-art69"],
        ),
    ],
)
def test_amount_withheld(
    base: str, dues: list[DueWithholding], expected: list[str], rules: list[str]
) -> None:
    """Each deduction takes what its limit and the earlier ones leave."""
    withheld = allocate(Decimal(base), dues, 2026)

    assert [w.amount for w in withheld] == [Decimal(e) for e in expected]
    assert [w.rule.rule for w in withheld] == rules


def test_tax_collection_cites_the_testo_unico_from_2027() -> None:
    """Art. 72-ter DPR 602/1973 ends on 31 December 2026; art. 171 follows."""
    (withheld,) = allocate(Decimal(2000), [_due(Kind.TAX_COLLECTION)], 2027)

    assert (withheld.amount, withheld.rule.rule) == (
        Decimal("200.00"),
        "dlgs33-2025-art171",
    )


def test_nothing_is_withheld_from_a_net_below_zero() -> None:
    """A run whose net is negative leaves nothing to garnish."""
    (withheld,) = allocate(Decimal(-10), [_due(Kind.MAINTENANCE, "100")], 2026)

    assert withheld.amount == Decimal(0)
