"""Apprenticeship track selection and pay chain construction."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.apprenticeship import ApprenticeshipPercentage
from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.service.chain import _allowance_active, _level_chain
from ccnl_engine.shared.domain.errors import OutOfScopeError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.contract.domain.apprenticeship import (
        ApprenticeshipTrack,
        ApprenticeshipUnderClassification,
    )
    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import Level
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.employment import Apprentice
    from ccnl_engine.payroll.service.types import MonthlyPayChain, MonthPeriod

_TWO = Decimal(2)

#: Engine limitation of a midpoint period that leaves an allowance unaveraged.
MIDPOINT_ALLOWANCES = "apprenticeship_midpoint_allowances"


def _find_period_index(periods: Sequence[MonthPeriod], months_elapsed: int) -> int:
    for i, period in enumerate(periods):
        if period.months_from <= months_elapsed and (
            period.months_until is None or months_elapsed < period.months_until
        ):
            return i
    msg = f"no apprenticeship period covers months_elapsed={months_elapsed}"
    remediation = "Verify that months_elapsed is within the range covered by the track."
    raise OutOfScopeError(
        msg,
        reason="no_period",
        feature="apprenticeship",
        remediation=remediation,
    )


def _eligible_destination_levels(ccnl: CCNL) -> list[str]:
    """Return sorted destination-level codes across all apprenticeship tracks.

    Returns:
        Sorted list of level codes covered by at least one apprenticeship track.
    """
    return sorted({c for t in ccnl.apprenticeship for c in t.destination_levels})


def _select_track(
    ccnl: CCNL, level: Level, employment: Apprentice
) -> ApprenticeshipTrack:
    if employment.track is not None:
        track = ccnl.apprenticeship_track_named(employment.track)
        if level.code not in track.destination_levels:
            msg = (
                f"apprenticeship track {track.name!r} does not cover destination "
                f"level {level.code!r} (covers {track.destination_levels})"
            )
            remediation = (
                f"Choose a track whose destination_levels includes {level.code!r}."
            )
            raise OutOfScopeError(
                msg,
                reason="no_track",
                feature="apprenticeship",
                ruleset=ccnl.meta.ccnl_id,
                remediation=remediation,
            )
        return track
    candidates = ccnl.apprenticeship_tracks_for(level.code)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        eligible = _eligible_destination_levels(ccnl)
        msg = (
            f"CCNL '{ccnl.meta.ccnl_id}' has no apprenticeship track for destination "
            f"level {level.code!r} (eligible destination levels: {eligible})"
        )
        raise OutOfScopeError(
            msg,
            reason="no_track",
            feature="apprenticeship",
            ruleset=ccnl.meta.ccnl_id,
            remediation=(
                "Use a level code listed in eligible_destination_levels, "
                "or use a standard (non-apprenticeship) contract type."
            ),
        )
    names = [t.name for t in candidates]
    msg = (
        f"destination level {level.code!r} is covered by several apprenticeship "
        f"tracks {names}; set Apprentice.track to choose one"
    )
    remediation = f"Set Apprentice.track to one of: {names}."
    raise OutOfScopeError(
        msg,
        reason="ambiguous_track",
        feature="apprenticeship",
        ruleset=ccnl.meta.ccnl_id,
        remediation=remediation,
    )


def _percentage_track_chain(
    ccnl: CCNL,
    level: Level,
    track: ApprenticeshipPercentage,
    period_index: int,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
    seniority_months: int | None,
) -> tuple[MonthlyPayChain, Decimal, None]:
    """Build the pay chain for a percentage-based apprenticeship track.

    Returns:
        A tuple of (chain, apprenticeship_pct, None).
    """
    reference = (
        ccnl.level_by_code(track.reference_level)
        if track.reference_level is not None
        else level
    )
    chain = _level_chain(
        ccnl,
        reference,
        count,
        roles,
        as_of,
        worker_category=worker_category,
        is_apprentice=True,
        seniority_months=seniority_months,
    )
    return chain, track.periods[period_index].percentage, None


def _underclass_track_chain(
    ccnl: CCNL,
    level: Level,
    track: ApprenticeshipUnderClassification,
    period_index: int,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: WorkerCategory | None,
    seniority_months: int | None,
) -> tuple[MonthlyPayChain, None, str]:
    """Build the pay chain for an under-classification apprenticeship track.

    Returns:
        A tuple of (chain, None, pay_level_code).
    """
    period = track.periods[period_index]
    pay_level = ccnl.level_by_order(level.order - period.levels_below)
    chain = _level_chain(
        ccnl,
        pay_level,
        count,
        roles,
        as_of,
        worker_category=worker_category,
        is_apprentice=True,
        seniority_months=seniority_months,
    )
    if period.midpoint_to_destination:
        chain = _midpoint_chain(chain, level, roles, as_of, seniority_months)
    return chain, None, pay_level.code


def _midpoint_chain(
    chain: MonthlyPayChain,
    destination: Level,
    roles: frozenset[str],
    as_of: date,
    seniority_months: int | None,
) -> MonthlyPayChain:
    """Average the base salary of *chain* with that of the destination level.

    The midpoint applies to the base salary only; the allowances stay those
    of the pay level.  When they differ from the destination allowances the
    chain records the ``apprenticeship_midpoint_allowances`` limitation.

    Returns:
        The chain with the averaged base salary.
    """
    with rule_scope(feature="base_salary"):
        dest_base = destination.base_salary.value_at(as_of)
        destination_allowances = money(
            sum(
                (
                    a.monthly.value_at(as_of)
                    for a in destination.fixed_allowances
                    if _allowance_active(a, roles, seniority_months, as_of)
                ),
                Decimal(0),
            )
        )
    limitations = chain.limitations
    if destination_allowances != chain.allowances_total:
        limitations = (*limitations, MIDPOINT_ALLOWANCES)
    return replace(
        chain, base=money((chain.base + dest_base) / _TWO), limitations=limitations
    )


def _apprentice_chain(
    ccnl: CCNL,
    level: Level,
    employment: Apprentice,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    worker_category: WorkerCategory | None = None,
    seniority_months: int | None = None,
) -> tuple[MonthlyPayChain, Decimal | None, str | None]:
    track = _select_track(ccnl, level, employment)
    period_index = _find_period_index(
        track.periods,  # type: ignore[arg-type]
        employment.months_elapsed,
    )
    if isinstance(track, ApprenticeshipPercentage):
        return _percentage_track_chain(
            ccnl,
            level,
            track,
            period_index,
            count,
            roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months,
        )
    chain, pct, code = _underclass_track_chain(
        ccnl,
        level,
        track,
        period_index,
        count,
        roles,
        as_of,
        worker_category=worker_category,
        seniority_months=seniority_months,
    )
    return chain, pct, code
