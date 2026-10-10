"""What a run pays of its month, and the base its minimum gives."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.contribution.models_minimum_base import (
    MinimumBase,
    MinimumBaseReason,
    MonthPosition,
)

_D = Decimal


@pytest.mark.parametrize(
    ("hours", "full_time", "part_time"),
    [
        (None, None, None),
        (_D(20), None, None),
        (None, _D(40), None),
        (_D(40), _D(40), None),
        (_D(20), _D(40), (_D(20), _D(40))),
    ],
)
def test_part_time_only_below_the_full_time_hours(
    hours: Decimal | None,
    full_time: Decimal | None,
    part_time: tuple[Decimal, Decimal] | None,
) -> None:
    """As the pay chain scales: both hours stated, contracted below full."""
    position = MonthPosition(
        month_pay=_D(1000), weekly_hours=hours, full_time_weekly_hours=full_time
    )

    assert position.part_time == part_time


def test_minimum_raises_every_amount_below_it() -> None:
    """A minimum of 1,511.38 raises 1,437.20 and the recurring 1,400.00."""
    minimum = MinimumBase(
        _D("1437.20"),
        _D("1511.38"),
        MinimumBaseReason.RAISED_TO_MINIMUM,
        _D("1511.38"),
    )

    assert minimum.base == _D("1511.38")
    assert minimum.raise_to_minimum(_D("1400.00")) == _D("1511.38")
    assert minimum.raise_to_minimum(_D("1600.00")) == _D("1600.00")


def test_undetermined_minimum_raises_nothing() -> None:
    """Without a minimum the actual base stays."""
    minimum = MinimumBase(_D("900"), _D("1511.38"), MinimumBaseReason.PARTIAL_MONTH)

    assert minimum.undetermined
    assert minimum.base == _D("900")
