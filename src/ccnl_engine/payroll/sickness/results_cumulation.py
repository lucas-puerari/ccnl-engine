"""What the cumulated sick pay of the days a run pays rests on.

The treatment of :mod:`~ccnl_engine.payroll.sickness.rules_cumulation` reads
the episodes the state records.  It is certain only when nothing the engine
does not know could change it:

- the seniority: without it the first band applies, which is the treatment
  of every band until the counts pass the full-pay or comporto days of the
  first band;
- the history: with the recorded episodes complete only from
  :attr:`~ccnl_engine.payroll.sickness.rules_cumulation.SicknessWorker.known_from`,
  as many sick days as the calendar days before it (within the window and
  the employment) could add to the comporto, to a chain that could reach
  back past it, and to the short absences of the year;
- the exemption of a short absence, when its rank could reduce it.

The counts never decrease within an episode, so the last day paid holds the
highest.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.payroll.sickness.rules_cumulation import window_start

if TYPE_CHECKING:
    from ccnl_engine.contract.sickness.models import SicknessSeniorityBand
    from ccnl_engine.payroll.sickness.rules_cumulation import CumulativeTreatment

__all__ = ["CumulationReport", "cumulation_report"]


@dataclass(frozen=True)
class CumulationReport:
    """What the treatment of the days a run pays rests on.

    Attributes:
        band: Seniority band applied.
        chain_days: Days of the treatment chain on the last day paid.
        window_days: Sick days within the window on the last day paid.
        reduced: Whether a day paid within the comporto is past the
            full-pay days of the band.
        seniority_reach: Whether the seniority is unknown and a band with
            more days could change the treatment.
        band_changes: Whether the band changes within the days paid.
        history_reach: Whether sick days before the recorded history could
            change the treatment.
        exemption_reach: Whether an unstated short-absence exemption could
            change the treatment.
    """

    band: SicknessSeniorityBand
    chain_days: int
    window_days: int
    reduced: bool
    seniority_reach: bool
    band_changes: bool
    history_reach: bool
    exemption_reach: bool


def _unknown_days(treatment: CumulativeTreatment, day: date) -> int:
    """Return the most sick days before the known history in the window.

    Returns:
        The days from the start of the window, or of the employment if
        later, to the first known day; zero when the whole history is
        known.
    """
    known = treatment.worker.known_from
    if known is None:
        return 0
    first = window_start(day, treatment.cumulation.window_years)
    hired = treatment.worker.hired_on
    if hired is not None and hired > first:
        first = hired
    return max(0, (known - first).days)


def _history_reach(treatment: CumulativeTreatment, last: date) -> bool:
    """Return whether unknown sick days could change the treatment.

    Returns:
        Whether they could pass the comporto, the full-pay days of a chain
        that could reach back past the known history, or reduce a short
        absence of a year the history does not cover from its start.
    """
    unknown = _unknown_days(treatment, last)
    known = treatment.worker.known_from
    if unknown == 0 or known is None:
        return False
    band, cumulation, episode = treatment.band, treatment.cumulation, treatment.episode
    linked = (treatment.chain[1] - known).days < cumulation.reset_after_days
    short = cumulation.short_absences
    short_unknown = (
        short is not None
        and known > date(episode.started_on.year, 1, 1)
        and episode.days <= short.max_days
        and episode.short_absence_exempt is not True
    )
    return (
        treatment.window_days(last) + unknown > band.comporto_days
        or (linked and treatment.chain_days(last) + unknown > band.full_pay_days)
        or short_unknown
    )


def _reduced_paid(treatment: CumulativeTreatment, span: tuple[date, date]) -> bool:
    """Return whether a day of ``span`` within the comporto is reduced.

    Returns:
        Whether the first reduced day of the span, if any, is within the
        comporto.
    """
    first = max(span[0], treatment.first_reduced())
    return (
        first <= span[1]
        and treatment.window_days(first) <= treatment.band.comporto_days
    )


def cumulation_report(
    treatment: CumulativeTreatment, span: tuple[date, date]
) -> CumulationReport:
    """Return what the treatment of the days of ``span`` rests on.

    Returns:
        The band, the counts and what could change them.
    """
    last = span[1]
    band = treatment.band
    chain, window = treatment.chain_days(last), treatment.window_days(last)
    first_band = treatment.cumulation.bands[0]
    return CumulationReport(
        band=band,
        chain_days=chain,
        window_days=window,
        reduced=_reduced_paid(treatment, span),
        seniority_reach=treatment.worker.seniority is None
        and (chain > first_band.full_pay_days or window > first_band.comporto_days),
        band_changes=treatment.band_on(last) != band,
        history_reach=_history_reach(treatment, last),
        exemption_reach=treatment.short.unknown,
    )
