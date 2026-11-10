"""Mutation coverage for the 2012 multiservizi apprenticeship annex."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.rules import _apprentice_chain
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.inputs import Apprentice

_AS_OF = date(2024, 8, 1)


@pytest.mark.parametrize(
    ("destination", "month", "pay_level", "expected"),
    [
        ("2", 23, "1", Decimal("1228.74")),
        ("2", 24, "2", Decimal("1293.50")),
        ("3", 14, "1", Decimal("1228.74")),
        ("3", 15, "2", Decimal("1293.50")),
        ("4", 14, "2", Decimal("1293.50")),
        ("4", 15, "3", Decimal("1358.47")),
        ("5", 17, "3", Decimal("1358.47")),
        ("5", 18, "4", Decimal("1431.11")),
        ("5", 30, "4", Decimal("1431.11")),
        ("5", 36, "5", Decimal("1516.82")),
        ("6", 17, "4", Decimal("1431.11")),
        ("6", 18, "5", Decimal("1516.82")),
        ("7", 17, "5", Decimal("1516.82")),
        ("7", 18, "6", Decimal("1763.00")),
    ],
)
def test_maximum_term_grade_progression(
    destination: str, month: int, pay_level: str, expected: Decimal
) -> None:
    """Check pay grades at both half-term boundaries and after completion.

    At August 2024, destination III month 15 pays II: 769.21 tabellare
    + 513.96 contingenza + 10.33 EDR = EUR 1,293.50. Destination V
    month 30 still pays IV: 903.28 + 517.50 + 10.33 = EUR 1,431.11;
    the old track paid V (987.96 + 518.53 + 10.33 = EUR 1,516.82).
    """
    ccnl = load_ccnl("multiservizi-anip")
    chain, percentage, actual_level = _apprentice_chain(
        ccnl,
        ccnl.level_by_code(destination),
        Apprentice(month),
        1,
        frozenset(),
        _AS_OF,
    )
    assert percentage is None
    assert actual_level == pay_level
    assert (
        chain.base + sum((value for _, value in chain.allowances), Decimal(0))
        == expected
    )


def test_annex_maximum_months_and_provenance() -> None:
    """The six maximum terms are 24/30/30/36/36/36 months, not Article 12's table."""
    ccnl = load_ccnl("multiservizi-anip")
    for destination, months in (
        ("2", 24),
        ("3", 30),
        ("4", 30),
        ("5", 36),
        ("6", 36),
        ("7", 36),
    ):
        (track,) = ccnl.apprenticeship_tracks_for(destination)
        assert track.periods[-1].months_from == months
        assert track.provenance is not None
        assert track.provenance.extraction is not None
        assert track.provenance.extraction.effective_from == date(2012, 7, 20)
