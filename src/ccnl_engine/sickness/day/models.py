"""INPS and CCNL rules a sick day is classified with.

The CCNL treatment of a day comes from one of two models of
:class:`~ccnl_engine.sickness.integration.models.SicknessRules`:

- per episode: the index of the day in its episode and the relapses it
  continues selects the tier (months of 30 days) and ends the comporto
  past ``max_duration_days``;
- cumulated: the sick days of several episodes are counted
  (:mod:`~ccnl_engine.sickness.cumulation.rules`).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.sickness.cumulation.rules import (
    CcnlDay,
    CumulativeTreatment,
    SicknessWorker,
)
from ccnl_engine.sickness.cumulation.year.rules import YearTreatment

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date

    from ccnl_engine.sickness.indemnity.models import InpsSickPayRates
    from ccnl_engine.sickness.integration.models import SicknessRules
    from ccnl_engine.sickness.models import SicknessEpisode, SicknessHistory

__all__ = ["DayTreatment", "SickPayRules"]

_TIER_MONTH_DAYS = 30

#: CCNL treatment of a sick day of an episode, from its relapse-chain index
#: and its date.
type DayTreatment = Callable[[int, date], CcnlDay]


@dataclass(frozen=True)
class SickPayRules:
    """INPS and CCNL rules a sick day is classified with.

    Attributes:
        inps: Statutory INPS waiting period, bands and annual maximum.
        inps_cover: Whether INPS pays the indemnity to the worker; ``None``
            when the bundle does not say.  Without cover INPS pays nothing.
        ccnl: CCNL integration rates, tiers and comporto.
        worker: Seniority, hire date and known sickness history, read by
            a cumulated CCNL treatment.
        fixed_term: Whether the contract is fixed-term, whose sickness pay
            is limited by D.L. 463/1983 art. 5.
        holidays: The national holidays the CCNL holiday target applies on
            (``SicknessRules.holiday``), Sundays not included.
    """

    inps: InpsSickPayRates
    inps_cover: bool | None
    ccnl: SicknessRules
    worker: SicknessWorker = field(default_factory=SicknessWorker)
    fixed_term: bool = False
    holidays: frozenset[date] = frozenset()

    @property
    def paid_directly(self) -> bool:
        """Whether INPS pays every day of the fixed-term contract directly."""
        statute = self.inps.fixed_term
        return self.fixed_term and statute is not None and statute.paid_directly

    def target_rate(self, index: int) -> Decimal:
        """Return the CCNL integration target of episode day ``index``.

        Returns:
            The rate of the day band ``index`` falls in, else of the tier of
            its month of sickness, the flat rate when none matches.
        """
        band = next((b for b in self.ccnl.day_bands if b.holds(index)), None)
        if band is not None:
            return band.integration_rate
        month = (index - 1) // _TIER_MONTH_DAYS + 1
        tiers = sorted(self.ccnl.tiers, key=lambda t: t.month_from, reverse=True)
        tier = next(
            (
                t
                for t in tiers
                if t.month_from <= month
                and (t.month_until is None or month < t.month_until)
            ),
            None,
        )
        return (
            self.ccnl.full_pay_integration_rate
            if tier is None
            else tier.integration_rate
        )

    def _per_episode(self, index: int, day: date) -> CcnlDay:
        """Return the treatment of episode day ``index`` of the per-episode model.

        Returns:
            The day past ``max_duration_days`` is past the comporto; the
            rate is the one of its tier.
        """
        del day
        return CcnlDay(
            beyond_comporto=index > self.ccnl.max_duration_days,
            rate=self.target_rate(index),
            carenza_rate=self.ccnl.carenza_integration_rate,
        )

    def cumulative(
        self, episode: SicknessEpisode, history: SicknessHistory
    ) -> CumulativeTreatment | None:
        """Return the cumulated treatment of ``episode``, if the CCNL has one.

        Returns:
            The treatment after the recorded episodes that started before
            it, ``None`` for a per-episode CCNL.
        """
        cumulation = self.ccnl.cumulation
        if cumulation is None:
            return None
        return CumulativeTreatment(
            self.ccnl, cumulation, episode, history.earlier(episode), self.worker
        )

    def year(
        self, episode: SicknessEpisode, history: SicknessHistory
    ) -> YearTreatment | None:
        """Return the per-episode treatment counted over several episodes.

        Returns:
            The treatment, ``None`` unless the CCNL counts its comporto over
            the calendar year or windows, or by seniority, or lowers the
            carenza by event.
        """
        ccnl = self.ccnl
        counted = (
            ccnl.comporto_calendar_year or ccnl.comporto_windows or ccnl.comporto_bands
        )
        if not counted and ccnl.carenza_by_event is None:
            return None
        return YearTreatment(
            ccnl,
            episode,
            history.earlier(episode),
            self.worker,
            self.target_rate,
            history.offset(episode),
        )

    def treatment(
        self, episode: SicknessEpisode, history: SicknessHistory
    ) -> DayTreatment:
        """Return the CCNL treatment of the days of ``episode``.

        A CCNL that pays the carenza only past a minimum length of the
        sickness (``carenza_min_days``) pays no waiting day of a shorter
        episode, one that pays the first waiting day only past a minimum
        (``carenza_first_day_min_days``) does not pay that day; the length
        is the one of the certificates the run knows.

        Returns:
            A function of the relapse-chain index and the date of a day.
        """
        treatment = self._with_holidays(self._treatment(episode, history))
        length = (episode.ended_on - episode.started_on).days
        unpaid_from = _unpaid_carenza_from(self.ccnl, length)
        if unpaid_from is None:
            return treatment

        def unpaid_carenza(index: int, day: date) -> CcnlDay:
            ccnl_day = treatment(index, day)
            if index > unpaid_from:
                return ccnl_day
            return replace(ccnl_day, carenza_rate=Decimal(0))

        return unpaid_carenza

    def _with_holidays(self, treatment: DayTreatment) -> DayTreatment:
        """Return ``treatment`` with the holiday target on the holidays.

        Returns:
            The treatment, the target of a holiday within the comporto
            raised to the CCNL holiday rate.
        """
        holiday = self.ccnl.holiday
        if holiday is None or not self.holidays:
            return treatment
        rate = holiday.rate

        def on_holiday(index: int, day: date) -> CcnlDay:
            ccnl_day = treatment(index, day)
            if day not in self.holidays or ccnl_day.beyond_comporto:
                return ccnl_day
            return replace(
                ccnl_day,
                rate=max(ccnl_day.rate, rate),
                carenza_rate=max(ccnl_day.carenza_rate, rate),
            )

        return on_holiday

    def _treatment(
        self, episode: SicknessEpisode, history: SicknessHistory
    ) -> DayTreatment:
        """Return the treatment of the model of the CCNL, before the carenza.

        Returns:
            The cumulated, calendar-year or per-episode treatment.
        """
        cumulative = self.cumulative(episode, history)
        if cumulative is not None:
            return cumulative.day
        year = self.year(episode, history)
        return self._per_episode if year is None else year.day


#: Episode index past every waiting day: the whole carenza is unpaid.
_EVERY_DAY = sys.maxsize


def _unpaid_carenza_from(ccnl: SicknessRules, length: int) -> int | None:
    """Return the last waiting day the CCNL leaves unpaid for ``length``.

    Args:
        ccnl: The sickness rules of the CCNL.
        length: Calendar days of the episode past its first day.

    Returns:
        The episode index up to which the carenza is unpaid: every waiting
        day under ``carenza_min_days``, the first under
        ``carenza_first_day_min_days``; ``None`` when all are paid.
    """
    if ccnl.carenza_min_days is not None and length < ccnl.carenza_min_days:
        return _EVERY_DAY
    first = ccnl.carenza_first_day_min_days
    if first is not None and length < first:
        return 1
    return None
