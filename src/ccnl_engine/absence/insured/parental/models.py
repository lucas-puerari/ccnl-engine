"""The INPS indemnity of a parental leave (art. 34 D.Lgs. 151/2001)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.provenance.source.rule.models import RuleProvenance

__all__ = ["EnhancedCohort", "ParentalRates"]

type _Share = Annotated[Decimal, Field(gt=Decimal(0), le=Decimal(1))]


class EnhancedCohort(BaseModel):
    """The months of the couple paid at the enhanced rate from a day.

    Attributes:
        from_date: First day of leave the months are paid at the enhanced
            rate on; the maternity or paternity leave must end on or after
            it, or the child be born on or after it.
        months: Months of the couple paid at the enhanced rate.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    from_date: date
    months: int = Field(ge=1)


class ParentalRates(BaseModel):
    """INPS indemnity of the parental leave of an employee.

    Attributes:
        indemnity_rate: Share of the daily pay INPS pays, 30%.
        enhanced_rate: Share of the enhanced months, 80%.
        daily_divisor: Days the pay of the month before is divided by, 30
            (art. 23, which art. 34 c. 1 applies).
        month_days: Days of leave that make a month of shorter spans, 30.
        own_months: Months of a parent not transferable to the other, 3.
        shared_months: Further months of the couple, 3.
        single_parent_months: Months of a sole parent, 9.
        child_age_years: Age of the child the leave ends at, 14.
        enhanced_age_years: Age of the child the enhanced rate ends at, 6.
        enhanced: The cohorts of the enhanced months, by first day.
        provenance: Source of the measures.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    indemnity_rate: _Share
    enhanced_rate: _Share
    daily_divisor: int = Field(ge=1)
    month_days: int = Field(ge=1)
    own_months: int = Field(ge=1)
    shared_months: int = Field(ge=0)
    single_parent_months: int = Field(ge=1)
    child_age_years: int = Field(ge=1)
    enhanced_age_years: int = Field(ge=1)
    enhanced: tuple[EnhancedCohort, ...]
    provenance: RuleProvenance

    @model_validator(mode="after")
    def _check_cohorts(self) -> Self:
        days = [c.from_date for c in self.enhanced]
        months = [c.months for c in self.enhanced]
        if days != sorted(set(days)) or months != sorted(set(months)):
            msg = "enhanced cohorts must grow in date and months"
            raise ValueError(msg)
        if months and months[-1] > self.own_months:
            msg = "enhanced months must fit in the months of a parent"
            raise ValueError(msg)
        return self

    def enhanced_months(self, day: date, protection_end: date, born_on: date) -> int:
        """Return the enhanced months of the couple on a day of leave.

        Args:
            day: The day of leave.
            protection_end: Last day of the maternity or paternity leave
                that ended last.
            born_on: Birth day of the child.

        Returns:
            The months of the last cohort in force on ``day`` the leave
            belongs to, 0 when none.
        """
        return max(
            (
                c.months
                for c in self.enhanced
                if c.from_date <= day
                and (protection_end >= c.from_date or born_on >= c.from_date)
            ),
            default=0,
        )
