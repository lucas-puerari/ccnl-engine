"""Minimum INPS base of a run: what the run pays of its month, and the result.

The rule is :class:`~ccnl_engine.tax.contribution.models_minimum_base.MinimumBaseRule`;
the reading of it is :mod:`~ccnl_engine.payroll.contribution.rules_minimum_base`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.provenance.source.models import SourceLocation

__all__ = ["UNDETERMINED", "MinimumBase", "MinimumBaseReason", "MonthPosition"]


class MinimumBaseReason(StrEnum):
    """How the minimum entered the INPS base of a run.

    Attributes:
        ABOVE_MINIMUM: The base reaches the minimum: it is kept.
        RAISED_TO_MINIMUM: The base was raised to the minimum.
        APPRENTICE: Art. 7 c. 5 excludes apprentices.
        EXEMPT_CATEGORY: Art. 7 c. 5 excludes the category in the sector.
        CATEGORY_UNKNOWN: The sector excludes a category and the worker's
            is not known.
        PARTIAL_MONTH: The run pays part of its month.
        ABSENCE_IN_MONTH: An absence or a sick leave reduced the pay.
        PAY_ADDED_TO_MONTH: The run adds pay to a month posted by another
            run (an extra month, an adjustment, a termination), or settles
            the extra-month ratei with the pay of its month.
        MONTHLY_DAYS_UNSOURCED: The sector has no sourced monthly day count.
        HOURLY_MINIMUM_UNSOURCED: No hourly minimum is published for the
            full-time weekly hours of the part-time worker.
    """

    ABOVE_MINIMUM = "above_minimum"
    RAISED_TO_MINIMUM = "raised_to_minimum"
    APPRENTICE = "apprentice_excluded"
    EXEMPT_CATEGORY = "category_excluded"
    CATEGORY_UNKNOWN = "category_unknown"
    PARTIAL_MONTH = "partial_month"
    ABSENCE_IN_MONTH = "absence_in_month"
    PAY_ADDED_TO_MONTH = "pay_added_to_month"
    MONTHLY_DAYS_UNSOURCED = "monthly_days_unsourced"
    HOURLY_MINIMUM_UNSOURCED = "hourly_minimum_unsourced"


#: Reasons whose minimum the bundle cannot determine.
UNDETERMINED = frozenset({
    MinimumBaseReason.CATEGORY_UNKNOWN,
    MinimumBaseReason.PARTIAL_MONTH,
    MinimumBaseReason.ABSENCE_IN_MONTH,
    MinimumBaseReason.PAY_ADDED_TO_MONTH,
    MinimumBaseReason.MONTHLY_DAYS_UNSOURCED,
    MinimumBaseReason.HOURLY_MINIMUM_UNSOURCED,
})


@dataclass(frozen=True)
class MonthPosition:
    """What the run pays of its month, as the minimum reads it.

    Attributes:
        month_pay: Monthly pay of a fully employed month of the worker,
            part time included: what a run adding pay to the month is
            compared on.
        adds_to_month: The run does not post the monthly pay of its month
            (an extra-month run, an adjustment, a termination run after the
            regular run), or adds to it the ratei of the extra months
            liquidated when the employment ends.
        span: First and last employed day of a partly employed month whose
            pay the run posts; ``None`` for a fully employed month.
        absence: An unpaid absence or a sick leave falls in the run.
        apprentice: The worker is an apprentice.
        category: Worker category, ``None`` when not known.
        weekly_hours: Contracted weekly hours, ``None`` for full time.
        full_time_weekly_hours: Full-time weekly hours of the CCNL, ``None``
            when not stated (the worker then counts as full time).
    """

    month_pay: Decimal
    adds_to_month: bool = False
    span: tuple[date, date] | None = None
    absence: bool = False
    apprentice: bool = False
    category: WorkerCategory | None = None
    weekly_hours: Decimal | None = None
    full_time_weekly_hours: Decimal | None = None

    @property
    def part_time(self) -> tuple[Decimal, Decimal] | None:
        """Contracted and full-time weekly hours of a part-time worker.

        Returns:
            Both hours when the contracted ones are below full time, as the
            pay chain scales them; ``None`` for full time.
        """
        hours, full = self.weekly_hours, self.full_time_weekly_hours
        if hours is None or full is None or hours >= full:
            return None
        return hours, full


@dataclass(frozen=True)
class MinimumBase:
    """The minimum the INPS base of a run is compared with.

    Attributes:
        actual: INPS base of the run before the minimum.
        bound: Highest minimum the month of the run can have.
        reason: How the minimum entered the base.
        minimum: Minimum of the month, ``None`` when not determined or not
            needed (the base reaches :attr:`bound`, or the worker is
            excluded).
        source: Location of the rule the minimum is read from.
    """

    actual: Decimal
    bound: Decimal
    reason: MinimumBaseReason
    minimum: Decimal | None = None
    source: SourceLocation | None = None

    @property
    def undetermined(self) -> bool:
        """Whether the base may be below a minimum the bundle cannot fix."""
        return self.reason in UNDETERMINED

    @property
    def base(self) -> Decimal:
        """INPS base of the run: the actual base raised to the minimum."""
        return self.raise_to_minimum(self.actual)

    def raise_to_minimum(self, amount: Decimal) -> Decimal:
        """Return ``amount`` raised to the minimum, when one is determined.

        Returns:
            The larger of ``amount`` and :attr:`minimum`; ``amount`` when the
            minimum is not determined.
        """
        return amount if self.minimum is None else max(amount, self.minimum)
