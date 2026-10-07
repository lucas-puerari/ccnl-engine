"""The INPS base of a competence year, own and of other employers."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.shared.domain.errors import InvalidInputError


def test_total_counts_every_employment_and_runs_add_to_own() -> None:
    """Other employers count toward the massimale; runs add to this one."""
    base = InpsBaseYtd(2026, own=Decimal(100), other_employers=Decimal(50))

    after = base.plus(Decimal(10), 3)

    assert base.total == Decimal(150)
    assert after == InpsBaseYtd(
        2026,
        own=Decimal(110),
        other_employers=Decimal(50),
        month=3,
        month_base=Decimal(10),
    )


def test_runs_of_one_month_share_its_base() -> None:
    """A second run of March adds to March; April starts again from zero."""
    march = InpsBaseYtd(2026).plus(Decimal(100), 3, Decimal("1.00"))

    second = march.plus(Decimal(40), 3, Decimal("0.40"))
    april = second.plus(Decimal(7), 4)

    assert (second.month_base, second.base_of_month(3)) == (Decimal(140), Decimal(140))
    assert second.base_of_month(4) == Decimal(0)
    assert (april.month, april.month_base, april.own) == (4, Decimal(7), Decimal(147))
    assert april.additional_ivs == Decimal("1.40")


def test_withheld_counts_this_and_the_other_employers() -> None:
    """The 1% withheld on the year: own, possibly negative, and certified."""
    base = InpsBaseYtd(
        2026,
        additional_ivs=Decimal("-20.00"),
        other_employers_additional_ivs=Decimal("50.00"),
    )

    assert base.additional_ivs_withheld == Decimal("30.00")


@pytest.mark.parametrize(
    ("other_employers", "withheld", "unknown"),
    [
        pytest.param("0", None, False, id="no-other-employer"),
        pytest.param("1000", None, True, id="base-without-its-1pct"),
        pytest.param("1000", "0", False, id="stated-zero"),
    ],
)
def test_the_1pct_of_other_employers_is_unknown_only_with_their_base(
    other_employers: str, withheld: str | None, *, unknown: bool
) -> None:
    """An unstated 1% matters only when other employers have a base."""
    base = InpsBaseYtd(
        2026,
        other_employers=Decimal(other_employers),
        other_employers_additional_ivs=None if withheld is None else Decimal(withheld),
    )

    assert base.other_employers_withheld_unknown is unknown
    assert base.additional_ivs_withheld == Decimal(0)


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"year": 1969}, "InpsBaseYtd.year"),
        ({"own": Decimal(-1)}, "InpsBaseYtd.own"),
        ({"other_employers": 5}, "InpsBaseYtd.other_employers"),
        ({"additional_ivs": 5}, "InpsBaseYtd.additional_ivs"),
        (
            {"other_employers_additional_ivs": Decimal(-1)},
            "InpsBaseYtd.other_employers_additional_ivs",
        ),
        ({"month": 13}, "InpsBaseYtd.month"),
        ({"month": 1, "month_base": Decimal(-1)}, "InpsBaseYtd.month_base"),
        ({"month_base": Decimal(1)}, "InpsBaseYtd.month_base"),
    ],
)
def test_rejects_an_invalid_field(kwargs: dict[str, object], field: str) -> None:
    """A year from 1970, Decimal amounts, a month base only with a month."""
    with pytest.raises(InvalidInputError) as info:
        InpsBaseYtd(**({"year": 2026} | kwargs))  # type: ignore[arg-type]

    assert info.value.field == field
