"""Months of a seniority freeze left out of the increments (ABI art. 103 c. 3)."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.seniority.freeze.models import SeniorityFreeze
from ccnl_engine.seniority.freeze.rules import months_without_freeze

_ABI = SeniorityFreeze(valid_from=date(2013, 1, 1), valid_until=date(2014, 8, 1))


@pytest.mark.parametrize(
    ("counted_on", "competence", "expected"),
    [
        (date(2012, 1, 1), date(2026, 1, 1), 100 - 19),
        (date(2013, 7, 1), date(2026, 1, 1), 100 - 13),
        (date(2015, 1, 1), date(2026, 1, 1), 100),
        (date(2012, 1, 1), date(2013, 6, 15), 100 - 5),
    ],
    ids=["whole_freeze", "half_freeze", "after_freeze", "inside_the_freeze"],
)
def test_aged_months_lose_their_overlap(
    counted_on: date, competence: date, expected: int
) -> None:
    """19 months frozen; only the months aged since the stated date count."""
    assert months_without_freeze(100, (_ABI,), counted_on, competence) == expected


def test_never_below_zero() -> None:
    """A few stated months cannot go negative."""
    assert months_without_freeze(3, (_ABI,), date(2012, 1, 1), date(2026, 1, 1)) == 0


def test_a_freeze_ends_after_it_starts() -> None:
    """The end is the first day after the period."""
    with pytest.raises(ValidationError, match="ends after it starts"):
        SeniorityFreeze(valid_from=date(2014, 8, 1), valid_until=date(2013, 1, 1))


def test_bancari_abi_declares_the_2013_2014_freeze() -> None:
    """Art. 103 c. 3: 1 January 2013 - 31 July 2014."""
    increments = load_ccnl("bancari-abi").parameters.seniority_increments

    assert increments.freezes == (_ABI,)
