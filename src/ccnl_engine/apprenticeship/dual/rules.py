"""Monthly pay of a first- or third-level apprentice.

Each pay element of the level the hours are paid at is weighed by the
hours of the month: the school hours are unpaid, the training at the
employer takes the training share, the work the rate of the period.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ccnl_engine.apprenticeship.dual.models import BASE, SENIORITY
from ccnl_engine.compensation.element.rules import _level_chain
from ccnl_engine.compensation.ladder.rules import level_below
from ccnl_engine.errors import MissingRequiredFactError, OutOfScopeError
from ccnl_engine.pay_item.rounding.policies import money

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.apprenticeship.dual.models import DualPeriod, DualTrack
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.employment.apprentice.inputs import Apprentice, DualHours
    from ccnl_engine.employment.category.models import WorkerCategory

__all__ = ["dual_chain"]

_FEATURE = "apprenticeship"


def _track(ccnl: CCNL, level: Level, apprentice: Apprentice) -> DualTrack:
    """Return the dual track of the apprentice.

    Returns:
        The one track of the programme for the destination level, or the
        one ``Apprentice.track`` names.

    Raises:
        OutOfScopeError: When no track, or more than one, applies.
    """
    tracks = [
        t
        for t in ccnl.dual_apprenticeship
        if t.programme is apprentice.programme
        and level.code in t.destination_levels
        and apprentice.track in {None, t.name}
    ]
    if len(tracks) == 1:
        return tracks[0]
    names = [t.name for t in tracks]
    reason = "ambiguous_track" if tracks else "no_track"
    msg = (
        f"{len(tracks)} {apprentice.programme.value} apprenticeship tracks of "
        f"'{ccnl.meta.ccnl_id}' cover level {level.code!r}: {names}"
    )
    raise OutOfScopeError(
        msg,
        reason=reason,
        feature=_FEATURE,
        ruleset=ccnl.meta.ccnl_id,
        remediation="Set Apprentice.track to one of the tracks listed."
        if tracks
        else "The CCNL sets no pay for this apprenticeship and level.",
    )


def _required(value: int | None, name: str, ccnl: CCNL) -> int:
    """Return ``value``, a fact the period of the track needs.

    Returns:
        ``value``.

    Raises:
        MissingRequiredFactError: When it is ``None``.
    """
    if value is None:
        msg = f"the apprenticeship pay of '{ccnl.meta.ccnl_id}' needs {name}"
        raise MissingRequiredFactError(
            msg,
            feature=_FEATURE,
            ruleset=ccnl.meta.ccnl_id,
            remediation=f"State {name}.",
        )
    return value


def _within_months(period: DualPeriod, months: int) -> bool:
    """Whether month ``months`` of the contract falls in ``period``.

    Returns:
        ``True`` from :attr:`DualPeriod.months_from` up to
        :attr:`DualPeriod.months_until` (exclusive), each when set.
    """
    start, end = period.months_from, period.months_until
    return (start is None or months >= start) and (end is None or months < end)


def _holds(period: DualPeriod, apprentice: Apprentice, ccnl: CCNL) -> bool:
    """Whether ``period`` pays the apprentice now.

    Returns:
        ``True`` when every selector the period sets matches.
    """
    if not _within_months(period, apprentice.months_elapsed):
        return False
    if period.school_year is not None and period.school_year != _required(
        apprentice.school_year, "Apprentice.school_year", ccnl
    ):
        return False
    up_to, over = period.programme_months_up_to, period.programme_months_over
    if period.half is None and up_to is None and over is None:
        return True
    length = _required(apprentice.programme_months, "Apprentice.programme_months", ccnl)
    half = 1 if 2 * apprentice.months_elapsed < length else 2
    if period.half is not None and period.half != half:
        return False
    if up_to is not None and length > up_to:
        return False
    return over is None or length > over


def _period(track: DualTrack, apprentice: Apprentice, ccnl: CCNL) -> DualPeriod:
    """Return the period of ``track`` that pays the apprentice now.

    Returns:
        The first period that holds.

    Raises:
        OutOfScopeError: When none does (a school year the CCNL leaves out).
    """
    for period in track.periods:
        if _holds(period, apprentice, ccnl):
            return period
    msg = (
        f"track {track.name!r} of '{ccnl.meta.ccnl_id}' sets no pay for school "
        f"year {apprentice.school_year}, programme of "
        f"{apprentice.programme_months} months, month {apprentice.months_elapsed}"
    )
    raise OutOfScopeError(
        msg,
        reason="no_period",
        feature=_FEATURE,
        ruleset=ccnl.meta.ccnl_id,
        remediation="The CCNL pays no apprentice in this stretch of the track.",
    )


def _weighed(
    value: Decimal,
    code: str,
    track: DualTrack,
    period: DualPeriod,
    hours: DualHours,
) -> Decimal:
    """Return the monthly ``value`` of element ``code`` for the hours.

    Returns:
        ``value`` times the paid share of the hours, rounded to the cent.
    """
    work = track.work_elements
    work_rate = period.work_rate if work is None or code in work else 0
    training = track.company_training_elements
    paid = training is None or code in training
    on = work_rate if track.company_training_on == "work" else 1
    training_rate = track.company_training_rate * on if paid else 0
    share = hours.work * work_rate + hours.company_training * training_rate
    return money(value * share / hours.total)


def dual_chain(
    ccnl: CCNL,
    level: Level,
    apprentice: Apprentice,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
    seniority_months: int | None,
) -> MonthlyPayChain:
    """Return the monthly pay of a first- or third-level apprentice.

    Returns:
        The chain of the level the period pays at, each element weighed
        by the hours of :attr:`Apprentice.hours`.

    Raises:
        MissingRequiredFactError: When the hours, or a fact the period
            needs, are not stated.
    """
    track = _track(ccnl, level, apprentice)
    period = _period(track, apprentice, ccnl)
    hours = apprentice.hours
    if hours is None:
        msg = f"the {apprentice.programme.value} apprenticeship pay needs the hours"
        raise MissingRequiredFactError(
            msg,
            feature=_FEATURE,
            ruleset=ccnl.meta.ccnl_id,
            remediation="State Apprentice.hours: school, company training, work.",
        )
    reference = (
        level
        if track.reference_level is None
        else ccnl.level_by_code(track.reference_level)
    )
    chain = _level_chain(
        ccnl,
        level_below(ccnl.levels, reference, period.levels_below),
        count,
        roles,
        as_of,
        worker_category=worker_category,
        is_apprentice=True,
        seniority_months=seniority_months,
    )
    return replace(
        chain,
        base=_weighed(chain.base, BASE, track, period, hours),
        seniority=_weighed(chain.seniority, SENIORITY, track, period, hours),
        allowances=tuple(
            (a, _weighed(v, a.code, track, period, hours)) for a, v in chain.allowances
        ),
    )
