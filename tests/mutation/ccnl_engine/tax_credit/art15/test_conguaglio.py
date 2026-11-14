"""The conguaglio deducts the art. 15 charges the employer withheld.

Chimica D1, hired 1 April 2026: 1000.00 of medical expenses through the
employer, 870.89 above the franchise, deduct 165.47 from the tax of the
conguaglio only.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.tax_credit.art15.inputs import Art15Expense, Art15Kind
from tests.mutation.ccnl_engine.irpef.prior import test_conguaglio as base

if TYPE_CHECKING:
    import pytest

_HEALTH = (Art15Expense(Art15Kind.HEALTH, Decimal(1000)),)


def test_the_conguaglio_deducts_the_charges(monkeypatch: pytest.MonkeyPatch) -> None:
    """165.47 less IRPEF due, a final art15_deductions decision."""
    plain = base._conguaglio(())
    original = base._facts
    monkeypatch.setattr(
        base, "_facts", lambda prior: replace(original(prior), art15_expenses=_HEALTH)
    )
    taken = base._conguaglio(())

    due = plain.tax_computation.withholding_due - taken.tax_computation.withholding_due
    assert due == Decimal("165.47")
    (decision,) = (d for d in taken.decisions if d.capability == "art15_deductions")
    assert decision.amount == Decimal("165.47")
    assert not [d for d in plain.decisions if d.capability == "art15_deductions"]
