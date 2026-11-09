"""Caller-stated paid holiday count for a payroll period."""

from __future__ import annotations

from dataclasses import dataclass

from ccnl_engine.validators import require_int


@dataclass(frozen=True, slots=True)
class PaidHolidayDays:
    """Number of eligible paid holidays, including those on rest days.

    The caller resolves employment span, local patron saint and any suspension;
    this count does not replace hours actually worked.

    Attributes:
        value: Nonnegative whole number of eligible holidays.
    """

    value: int

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.value, "PaidHolidayDays.value", feature="period_facts", minimum=0
        )
