"""Rule of the minimum INPS contribution base of one year (minimale).

D.L. 463/1983 art. 7 c. 1, second period (as amended by D.L. 338/1989 art.
1 c. 2): the daily pay contributions are computed on "non può essere
inferiore al 9,50%" of the monthly minimum FPLD pension in force on 1
January.  INPS publishes the amount each year (circ. 6/2026 par. 1: 58.13
EUR for 2026).  Art. 7 c. 5 excludes apprentices, operai agricoli and
domestic workers.  For part time, D.Lgs. 81/2015 art. 11 c. 1 turns it into
an hourly minimum: the daily minimum times the days of the normal working
week, over the full-time weekly hours of the CCNL (circ. 6/2026 par. 4:
"58,13 euro x 6/40 = 8,72 euro" for a 40-hour week).  The minimum of a
qualifica can be higher: Tabella A of the circular's allegato 1 lists it by
sector and qualifica, raised to the 9.50% amount when below it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.primitives import PositiveCeiling
from ccnl_engine.provenance.source.models_chain import RuleProvenance

__all__ = ["HourlyMinimum", "MinimumBaseRule"]


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
        daily_by_category: Higher daily minimums of the qualifiche of the
            sector, from Tabella A of the INPS circular (the dirigenti of
            industria, for instance); the other categories take ``daily``.
        week_days: Days of the normal working week the hourly minimum is
            published for (six in the private sector, circ. 6/2026 par. 4).
        monthly_days: Days of a fully paid month of a monthly-paid worker
            the daily minimum is counted on; ``None`` when the bundle has
            no source for the sector, and a run below the minimum is then
            undetermined.
        hourly: Published hourly minimums of part-time workers, by the
            full-time weekly hours of the CCNL.
        exempt_categories: Worker categories of the sector art. 7 c. 5
            excludes (the operai agricoli).
        provenance: Source of the amounts and the day counts.

    Raises:
        ValueError: When ``monthly_days`` is not between the days of four
            and of five normal weeks, two hourly minimums share their
            full-time weekly hours, or an exempt category has a minimum.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    daily: PositiveCeiling
    daily_by_category: dict[WorkerCategory, PositiveCeiling] = {}
    week_days: int = Field(ge=1, le=6)
    monthly_days: int | None = Field(default=None, ge=1, le=31)
    hourly: tuple[HourlyMinimum, ...] = ()
    exempt_categories: frozenset[WorkerCategory] = frozenset()
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
        exempt = self.exempt_categories & self.daily_by_category.keys()
        if exempt:
            msg = f"exempt categories cannot have a minimum: {sorted(exempt)}"
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

        INPS publishes them for the general daily minimum only.

        Returns:
            False for a category with its own daily minimum.
        """
        return category is None or category not in self.daily_by_category

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
