"""The permit buckets of a CCNL: ROL and ex festività hours, and the new-hire ramp."""

from __future__ import annotations

from datetime import date  # noqa: TC003
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ccnl_engine.leave.types import LeaveBucket, MonthCredit
from ccnl_engine.provenance.source.rule.models import RuleProvenance  # noqa: TC001

__all__ = ["NewHireRamp", "PermitHours", "PermitRules", "RampStep"]

_ZERO = Decimal(0)
_ONE = Decimal(1)


class PermitHours(BaseModel):
    """Hours of a permit bucket a year, for the employers above a size.

    Attributes:
        hours: Hours a year of a full-time worker.
        headcount_above: The hours apply to an employer with more than this
            many employees; ``None`` for the hours of any employer.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hours: Decimal = Field(gt=_ZERO)
    headcount_above: int | None = Field(default=None, ge=1)


class RampStep(BaseModel):
    """Share of the hours a new hire accrues from a seniority on.

    Attributes:
        service_months_min: Months since the hire from which the share
            applies.
        share: Share of the yearly hours accrued, from 0 to 1.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    service_months_min: int = Field(ge=0)
    share: Decimal = Field(ge=_ZERO, le=_ONE)


class NewHireRamp(BaseModel):
    """Reduced hours of the workers hired after a date, by months of service.

    Attributes:
        hired_after: The ramp applies to the workers hired after this day.
        hired_until: The ramp applies to the workers hired up to this day
            included (Studi Art. 91 c.3: the hires within the term of the
            contract); ``None`` for every later hire.
        headcount_max: The ramp applies to an employer with at most this
            many employees (Farmacie Art. 24: "fino a 40 dipendenti");
            ``None`` for any employer.
        steps: Shares by months since the hire; the first starts at 0.
        provenance: Source of the ramp.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hired_after: date
    hired_until: date | None = None
    headcount_max: int | None = Field(default=None, ge=1)
    steps: tuple[RampStep, ...] = Field(min_length=1)
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        months = [s.service_months_min for s in self.steps]
        if months[0] != 0 or months != sorted(set(months)):
            msg = f"ramp steps must start at 0 months, in order; got {months}"
            raise ValueError(msg)
        return self

    def covers(self, headcount: int) -> bool:
        """Return whether the ramp applies to an employer of ``headcount``.

        Returns:
            ``False`` above :attr:`headcount_max`.
        """
        return self.headcount_max is None or headcount <= self.headcount_max

    def share(self, hired_on: date, service_months: int) -> Decimal:
        """Return the share of the hours a worker hired on ``hired_on`` accrues.

        Returns:
            1 for a worker hired on or before :attr:`hired_after` or after
            :attr:`hired_until`, else the share of the last step
            ``service_months`` reached.
        """
        until = self.hired_until
        if hired_on <= self.hired_after or (until is not None and hired_on > until):
            return _ONE
        reached = [s for s in self.steps if s.service_months_min <= service_months]
        return reached[-1].share


class WeekAbsorption(BaseModel):
    """Permit hours a shorter full-time week absorbs.

    Terziario Art. 133: "b) 39 ore settimanali. Si realizza attraverso
    l'assorbimento di 36 ore di permesso retribuito".

    Attributes:
        weekly_hours: Full-time week of the employment.
        hours: Yearly hours of the bucket the week absorbs.
        subsectors: Sub-sectors of the employer (``EmployerProfile.subsector``)
            whose week absorbs these hours instead of those of the entries
            without one (Commercio Art. 134: the supermercati on a 38-hour
            average); empty for every employer.
        provenance: Source of the absorption.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    weekly_hours: Decimal = Field(gt=_ZERO)
    hours: Decimal = Field(ge=_ZERO)
    subsectors: tuple[str, ...] = ()
    provenance: RuleProvenance | None = None


class PermitRules(BaseModel):
    """Yearly hours of a permit bucket and how they accrue.

    Attributes:
        bucket: The bucket: :attr:`~LeaveBucket.ROL` or
            :attr:`~LeaveBucket.EX_FESTIVITA`.
        annual_hours: Hours a year by employer size; the tier of the
            largest ``headcount_above`` the employer exceeds applies, else
            the tier without one.
        includes_ex_festivita: Whether the hours hold those of the abolished
            festivities (a single pool): the CCNL then has no separate
            :attr:`~LeaveBucket.EX_FESTIVITA` bucket.
        month_credit: Which months accrue a twelfth of the hours; ``None``
            when the text does not say how a month fraction counts.
        ramp: Reduced hours of the workers hired after a date.
        day_hours: Hours that make one day when the text pays the hours left
            by the day (Studi Art. 98: the retribuzione normale giornaliera
            of each of the four festività of 8 hours): at the end of the
            employment every ``day_hours`` hours are paid at the daily quota,
            the monthly pay over the ferie divisor; ``None`` when they are
            paid by the hour.
        week_absorption: Hours a shorter full-time week absorbs, by week.
        provenance: Source of the hours.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bucket: LeaveBucket
    annual_hours: tuple[PermitHours, ...] = Field(min_length=1)
    includes_ex_festivita: bool = False
    month_credit: MonthCredit | None = None
    ramp: NewHireRamp | None = None
    day_hours: Decimal | None = Field(default=None, gt=_ZERO)
    week_absorption: tuple[WeekAbsorption, ...] = ()
    provenance: RuleProvenance | None = None

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if self.bucket is LeaveBucket.FERIE:
            msg = "ferie are not a permit bucket: state them in LeaveRules"
            raise ValueError(msg)
        if self.includes_ex_festivita and self.bucket is not LeaveBucket.ROL:
            msg = "only the rol bucket can include the ex festività hours"
            raise ValueError(msg)
        sizes = [h.headcount_above for h in self.annual_hours]
        if sizes.count(None) != 1 or len(set(sizes)) != len(sizes):
            msg = (
                "annual_hours needs one tier without headcount_above and distinct "
                f"sizes; got {sizes}"
            )
            raise ValueError(msg)
        return self

    def hours_for(
        self,
        headcount: int,
        week: Decimal | None = None,
        subsector: str | None = None,
    ) -> Decimal:
        """Return the yearly hours of a full-time worker of an employer.

        Returns:
            The hours of the largest size ``headcount`` exceeds, else those
            of the tier without a size, less those the full-time ``week``
            absorbs (the entries of the ``subsector`` when it has some),
            never below zero.
        """
        above = [
            h
            for h in self.annual_hours
            if h.headcount_above is not None and headcount > h.headcount_above
        ]
        if above:
            hours = max(above, key=lambda h: h.headcount_above or 0).hours
        else:
            hours = next(
                h.hours for h in self.annual_hours if h.headcount_above is None
            )
        same_week = [a for a in self.week_absorption if a.weekly_hours == week]
        chosen = [a for a in same_week if subsector in a.subsectors] or [
            a for a in same_week if not a.subsectors
        ]
        absorbed = sum((a.hours for a in chosen), _ZERO)
        return max(hours - absorbed, _ZERO)
