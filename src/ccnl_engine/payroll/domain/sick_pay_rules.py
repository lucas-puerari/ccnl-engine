"""INPS and CCNL rules a sick day is classified with.

The CCNL treatment of a day comes from one of two models of
:class:`~ccnl_engine.contract.domain.sickness.SicknessRules`:

- per episode: the index of the day in its episode and the relapses it
  continues selects the tier (months of 30 days) and ends the comporto
  past ``max_duration_days``;
- cumulated: the sick days of several episodes are counted
  (:mod:`~ccnl_engine.payroll.domain.sick_cumulation`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.sick_cumulation import (
    CcnlDay,
    CumulativeTreatment,
    SicknessWorker,
)
from ccnl_engine.payroll.domain.sick_year import YearTreatment

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.contract.domain.sickness import SicknessRules
    from ccnl_engine.payroll.domain.sickness import SicknessEpisode, SicknessHistory
    from ccnl_engine.tax.domain.sick_pay import InpsSickPayRates

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
    """

    inps: InpsSickPayRates
    inps_cover: bool | None
    ccnl: SicknessRules
    worker: SicknessWorker = field(default_factory=SicknessWorker)

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
        """Return the per-episode treatment counted over the calendar year.

        Returns:
            The treatment, ``None`` unless the CCNL counts its comporto over
            the calendar year or lowers the carenza by event.
        """
        ccnl = self.ccnl
        if not ccnl.comporto_calendar_year and ccnl.carenza_by_event is None:
            return None
        return YearTreatment(
            ccnl,
            episode,
            history.earlier(episode),
            self.worker.known_from,
            self.target_rate,
        )

    def treatment(
        self, episode: SicknessEpisode, history: SicknessHistory
    ) -> DayTreatment:
        """Return the CCNL treatment of the days of ``episode``.

        Returns:
            A function of the relapse-chain index and the date of a day.
        """
        cumulative = self.cumulative(episode, history)
        if cumulative is not None:
            return cumulative.day
        year = self.year(episode, history)
        return self._per_episode if year is None else year.day
