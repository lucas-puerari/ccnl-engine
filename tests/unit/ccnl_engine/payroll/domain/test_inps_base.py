"""The INPS base of a competence year, own and of other employers."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.shared.domain.errors import InvalidInputError


def test_total_counts_every_employment_and_runs_add_to_own() -> None:
    """Other employers count toward the massimale; runs add to this one."""
    base = InpsBaseYtd(2026, own=Decimal(100), other_employers=Decimal(50))

    after = base.plus(Decimal(10))

    assert base.total == Decimal(150)
    assert after == InpsBaseYtd(2026, own=Decimal(110), other_employers=Decimal(50))


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"year": 1969}, "InpsBaseYtd.year"),
        ({"own": Decimal(-1)}, "InpsBaseYtd.own"),
        ({"other_employers": 5}, "InpsBaseYtd.other_employers"),
    ],
)
def test_rejects_an_invalid_field(kwargs: dict[str, object], field: str) -> None:
    """A year from 1970, non-negative Decimal amounts."""
    with pytest.raises(InvalidInputError) as info:
        InpsBaseYtd(**({"year": 2026} | kwargs))  # type: ignore[arg-type]

    assert info.value.field == field
