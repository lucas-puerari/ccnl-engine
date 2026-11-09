"""Employer sick-pay coefficients on an independent hourly remuneration base."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.sickness.day.rules import SickDayKind

if TYPE_CHECKING:
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.sickness.day.rules import SickDaySegment


class HourlyWaitingTier(BaseModel):
    """Employer coefficient for the first waiting days of a longer episode.

    Attributes:
        more_than_days: Minimum episode length, exclusive.
        coefficient: Multiplier of the hourly contractual base and daily hours.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    more_than_days: int = Field(ge=0)
    coefficient: Decimal = Field(ge=0)


class HourlySicknessBand(BaseModel):
    """Employer coefficient for episode days in a half-open interval.

    Attributes:
        day_from: First episode day covered.
        day_until: First day no longer covered, exclusive.
        coefficient: Multiplier of the hourly contractual base and daily hours.
        requires_inps: Pay only for days indemnified by INPS.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    day_from: int = Field(ge=1)
    day_until: int = Field(ge=2)
    coefficient: Decimal = Field(ge=0)
    requires_inps: bool = False


class HourlyEmployerIntegration(BaseModel):
    """Direct employer pay independent of the INPS indemnity and daily quota.

    The base comprises contractual minimum and only the named allowances,
    divided by ``hourly_divisor``. Each payable day takes one ``weekly_days``
    share of the contracted weekly hours; Sundays and national holidays are
    excluded. The first matching waiting tier in descending length applies.

    Attributes:
        base_allowances: Codes of contractual allowances entering the base.
        weekly_days: Days of a normal payable week.
        standard_weekly_hours: Full-time contracted hours if none are stated.
        waiting_days: Number of waiting days with an episode-length tier.
        waiting_tiers: Coefficients conditional on the complete episode length.
        day_bands: Employer coefficients for subsequent days.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_allowances: tuple[str, ...] = ()
    weekly_days: int = Field(ge=1, le=7)
    standard_weekly_hours: Decimal = Field(gt=0)
    waiting_days: int = Field(ge=1)
    waiting_tiers: tuple[HourlyWaitingTier, ...] = ()
    day_bands: tuple[HourlySicknessBand, ...] = ()

    def coefficient(self, index: int, length: int, inps_rate: Decimal) -> Decimal:
        """Return the direct employer multiplier for this episode day.

        Returns:
            Zero when the episode is too short or INPS does not indemnify
            a band requiring INPS cover.
        """
        if index <= self.waiting_days:
            eligible = (t for t in self.waiting_tiers if length > t.more_than_days)
            return max((t.coefficient for t in eligible), default=Decimal(0))
        return _band_coefficient(self.day_bands, index, inps_rate)


def _band_coefficient(
    bands: tuple[HourlySicknessBand, ...], index: int, inps_rate: Decimal
) -> Decimal:
    """Return the first band requiring this day's INPS status, else zero.

    Returns:
        The direct employer coefficient, never an INPS-inclusive target.
    """
    for band in bands:
        if band.day_from <= index < band.day_until:
            if band.requires_inps != (inps_rate > 0):
                return Decimal(0)
            return band.coefficient
    return Decimal(0)


def hourly_employer_pay(
    spec: HourlyEmployerIntegration,
    segment: SickDaySegment,
    chain: MonthlyPayChain,
    divisor: Decimal,
    weekly_hours: Decimal,
    holidays: frozenset[date],
    episode_length: int,
) -> Decimal:
    """Pay qualifying days of a segment using the independent hourly base.

    Returns:
        The employer's direct cash payment, rounded once for this segment.
    """
    if segment.kind in {SickDayKind.BEYOND_COMPORTO, SickDayKind.FIXED_TERM_LIMIT}:
        return Decimal(0)
    base = chain.base + sum(
        (
            value
            for allowance, value in chain.allowances
            if allowance.code in spec.base_allowances
        ),
        Decimal(0),
    )
    hourly = base / divisor
    daily_hours = weekly_hours / spec.weekly_days
    length = episode_length
    total = Decimal(0)
    day = segment.first
    while day <= segment.last:
        if day.weekday() != 6 and day not in holidays:
            index = segment.first_index + (day - segment.first).days
            total += (
                hourly
                * daily_hours
                * spec.coefficient(index, length, segment.inps_rate)
            )
        day += timedelta(days=1)
    return money(total)
