"""Rule of the minimum INPS contribution base of one year (minimale).

D.L. 463/1983 art. 7 c. 1: the daily pay contributions are computed on is
not below 9.50% of the monthly minimum FPLD pension (circ. 6/2026 par. 1:
58.13 EUR for 2026); c. 5 excludes apprentices and keeps the operai
agricoli at their own amount.  Part time takes the hourly minimum of
D.Lgs. 81/2015 art. 11 c. 1 (par. 4: "58,13 euro x 6/40 = 8,72 euro").
Tabella A of allegato 1 lists the minimum of each qualifica by sector.  The
run side is what a run pays of its month and the result the contribution
step reads (:mod:`~ccnl_engine.contribution.minimum_base.rules`).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.types import PositiveCeiling

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.provenance.source.models import SourceLocation
__all__ = [
    "UNDETERMINED",
    "HourlyMinimum",
    "MinimumBase",
    "MinimumBaseReason",
    "MinimumBaseRule",
    "MonthPosition",
]


class HourlyMinimum(BaseModel):
    """Hourly minimum of a part-time worker for one full-time week.

    Attributes:
        full_time_weekly_hours: Full-time weekly hours of the CCNL the
            amount is published for.
        amount: Hourly minimum as INPS publishes it, rounded there.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    full_time_weekly_hours: PositiveCeiling
    amount: PositiveCeiling


class MinimumBaseRule(BaseModel):
    """Daily and hourly minimum INPS base of one year and sector.

    Attributes:
        daily: Minimum daily pay of art. 7 c. 1 D.L. 463/1983.
        daily_by_category: Tabella A minimums of the qualifiche other than
            ``daily``: higher (dirigenti) or lower (operai agricoli, 51.70).
        week_days: Days of the normal working week the hourly minimum is
            published for (six in the private sector, circ. 6/2026 par. 4).
        monthly_days: Days of a fully paid month the daily minimum is
            counted on; ``None`` when unsourced (a run below is undetermined).
        hourly: Published hourly minimums of part-time workers, by the
            full-time weekly hours of the CCNL.
        hourly_categories: Categories of ``daily_by_category`` whose part
            time takes the published hourly minimums (circ. 43/2026 par. 5).
        provenance: Source of the amounts and the day counts.

    Raises:
        ValueError: When ``monthly_days`` is not between the days of four
            and of five normal weeks, two hourly minimums share their
            full-time weekly hours, or an hourly category has no daily
            minimum of its own.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    daily: PositiveCeiling
    daily_by_category: dict[WorkerCategory, PositiveCeiling] = {}
    week_days: int = Field(ge=1, le=6)
    monthly_days: int | None = Field(default=None, ge=1, le=31)
    hourly: tuple[HourlyMinimum, ...] = ()
    hourly_categories: frozenset[WorkerCategory] = frozenset()
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _check(self) -> Self:
        days = self.monthly_days
        if days is not None and not 4 * self.week_days <= days <= 5 * self.week_days:
            msg = (
                f"monthly_days ({days}) must hold between four and five weeks "
                f"of {self.week_days} days"
            )
            raise ValueError(msg)
        hours = [h.full_time_weekly_hours for h in self.hourly]
        if len(set(hours)) != len(hours):
            msg = f"hourly minimums repeat full-time weekly hours: {hours}"
            raise ValueError(msg)
        stray = self.hourly_categories - self.daily_by_category.keys()
        if stray:
            msg = f"hourly categories need a daily minimum: {sorted(stray)}"
            raise ValueError(msg)
        return self

    def daily_for(self, category: WorkerCategory | None) -> Decimal:
        """Return the daily minimum of a worker of ``category``.

        Returns:
            The minimum of the qualifica when the sector gives one, else
            the general ``daily``.
        """
        if category is None:
            return self.daily
        return self.daily_by_category.get(category, self.daily)

    def publishes_hourly_for(self, category: WorkerCategory | None) -> bool:
        """Return whether the published hourly minimums apply to ``category``.

        INPS publishes them for the general daily minimum, and for the
        categories of ``hourly_categories``.

        Returns:
            False for any other category with its own daily minimum.
        """
        return (
            category is None
            or category not in self.daily_by_category
            or category in self.hourly_categories
        )

    @property
    def lowers_by_category(self) -> bool:
        """Whether ``daily`` may overstate the minimum of an unknown category.

        Returns:
            True when a category of ``daily_by_category`` is below ``daily``.
        """
        return any(amount < self.daily for amount in self.daily_by_category.values())

    def hourly_for(self, full_time_weekly_hours: Decimal) -> Decimal | None:
        """Return the published hourly minimum of a full-time week.

        Returns:
            The amount published for ``full_time_weekly_hours``, ``None``
            when INPS publishes none for it.
        """
        return next(
            (
                h.amount
                for h in self.hourly
                if h.full_time_weekly_hours == full_time_weekly_hours
            ),
            None,
        )


class MinimumBaseReason(StrEnum):
    """How the minimum entered the INPS base of a run.

    Attributes:
        ABOVE_MINIMUM: The base reaches the minimum: it is kept.
        RAISED_TO_MINIMUM: The base was raised to the minimum.
        APPRENTICE: Art. 7 c. 5 excludes apprentices.
        CATEGORY_UNKNOWN: A category of the sector has a lower daily
            minimum and the worker's is not known.
        PARTIAL_MONTH: The run pays part of its month.
        ABSENCE_IN_MONTH: An absence or a sick leave reduced the pay.
        PAY_ADDED_TO_MONTH: The run adds pay to a month posted by another
            run (an extra month, an adjustment, a termination), or settles
            the extra-month ratei with the pay of its month.
        MONTHLY_DAYS_UNSOURCED: The sector has no sourced monthly day count.
        HOURLY_MINIMUM_UNSOURCED: No hourly minimum is published for the
            full-time weekly hours of the part-time worker.
        MONTH_NOT_WORKED: The run would post the pay of a month the
            vertical part time does not work: no hour is paid, so the
            hourly minimum of D.Lgs. 81/2015 art. 11 c. 1 gives none.
        INDEMNIFIED_MONTH: Every employed day of the month is a maternity
            leave or a work-injury inability an insurer indemnifies: the
            days are credited with figurative contributions and the
            employer pays no day the daily minimum is counted on.
    """

    ABOVE_MINIMUM = "above_minimum"
    RAISED_TO_MINIMUM = "raised_to_minimum"
    APPRENTICE = "apprentice_excluded"
    CATEGORY_UNKNOWN = "category_unknown"
    PARTIAL_MONTH = "partial_month"
    ABSENCE_IN_MONTH = "absence_in_month"
    PAY_ADDED_TO_MONTH = "pay_added_to_month"
    MONTHLY_DAYS_UNSOURCED = "monthly_days_unsourced"
    HOURLY_MINIMUM_UNSOURCED = "hourly_minimum_unsourced"
    MONTH_NOT_WORKED = "month_not_worked"
    INDEMNIFIED_MONTH = "indemnified_month"


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
        worked: Whether the worker works in the month; ``False`` for a
            month outside the months of a vertical part time.
        indemnified: Every employed day of the month is a maternity leave
            or a work-injury inability after the injury day.
    """

    month_pay: Decimal
    adds_to_month: bool = False
    span: tuple[date, date] | None = None
    absence: bool = False
    apprentice: bool = False
    category: WorkerCategory | None = None
    weekly_hours: Decimal | None = None
    full_time_weekly_hours: Decimal | None = None
    worked: bool = True
    indemnified: bool = False

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
