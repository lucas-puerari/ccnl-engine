"""The municipal surtax of the year at the delibera of the next year."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.surtax.rules import next_year_municipal
from ccnl_engine.surtax.table.models import ComunaleEntry, SurtaxBracket

_ENTRY = ComunaleEntry(
    nome="Comune",
    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
    exemption_threshold=Decimal(12000),
)


def test_without_a_delibera_of_the_next_year_nothing_changes() -> None:
    """No row of the next year: the acconto keeps the rate of the year."""
    assert next_year_municipal(Decimal(30000), None, Decimal(5000)) is None


def test_the_next_year_rate_applies_above_its_threshold() -> None:
    """30,000.00 at 0.8%: 240.00."""
    assert next_year_municipal(Decimal(30000), _ENTRY, Decimal(5000)) == Decimal(
        "240.00"
    )


def test_no_surtax_within_the_threshold_or_without_irpef() -> None:
    """Within 12,000.00, or with no IRPEF due, the base is zero."""
    assert next_year_municipal(Decimal(11000), _ENTRY, Decimal(500)) == 0
    assert next_year_municipal(Decimal(30000), _ENTRY, Decimal(0)) == 0
