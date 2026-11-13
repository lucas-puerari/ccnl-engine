"""Overtime multiplier of an event: the caller's value or the CCNL band.

D.Lgs. 66/2003 art. 5 c. 5 leaves the overtime supplement to the CCNL and
sets no statutory rate, so the engine has no default multiplier:

- an explicit ``OvertimeEvent.multiplier`` prevails.  When it differs from
  every CCNL percentage band of the event's kind, the run is provisional
  with issue ``caller_multiplier_differs_from_ccnl`` reporting both values;
- without a multiplier, known ``weekly_hours_before`` splits the event
  across the weekly bands of its kind and pays their weighted rate; otherwise
  the unthresholded first-tier CCNL band gives ``1 + band``;
- without a multiplier and without such a band the run is rejected with
  :class:`~ccnl_engine.errors.MissingRuleError`.

The band of a kind is the single percentage overtime band (code ``OT_*``)
that applies to it with no hour threshold and no context condition: the
first tier of overtime. Weekly thresholds can be applied when the event
states its preceding weekly hours; otherwise higher tiers, and daily tiers
without a daily hour position, remain unapplied and the run is provisional
with issue ``overtime_tier_not_applied``.  A band paid per shift, or not in force on
the event date, gives no multiplier.  A kind without a percentage band but
with a band in EUR per hour (the PA tables of fixed hourly amounts) is paid
that amount for each hour, in place of the hourly rate, with multiplier 1.
A band that names levels applies only to them.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.working_time.models import TimeSupplementKind, WorkKind
from ccnl_engine.working_time.overtime.decisions import CCNL_BAND_APPLIED, band_decision
from ccnl_engine.working_time.overtime.models import CCNLOvertimeBands
from ccnl_engine.working_time.overtime.weekly import weekly_rate

if TYPE_CHECKING:
    from ccnl_engine.event.facade import OvertimeEvent
    from ccnl_engine.working_time.models import OvertimeBand

__all__ = [
    "CALLER_MULTIPLIER_DIFFERS",
    "CCNL_BAND_APPLIED",
    "TIER_NOT_APPLIED",
    "CCNLOvertimeBands",
    "OvertimeRate",
    "band_decision",
    "resolve_overtime_rate",
]

CALLER_MULTIPLIER_DIFFERS = "caller_multiplier_differs_from_ccnl"
TIER_NOT_APPLIED = "overtime_tier_not_applied"
_OVERTIME_PREFIX = "OT_"
_FALLBACK = {
    WorkKind.REST_DAY: WorkKind.HOLIDAY,
    WorkKind.SATURDAY: WorkKind.WEEKDAY,
    WorkKind.SUNDAY: WorkKind.WEEKDAY,
}


@dataclass(frozen=True)
class OvertimeRate:
    """The multiplier an overtime event is paid with, and where it comes from.

    Attributes:
        multiplier: Multiplier applied to the hourly rate.
        derived: ``True`` when it comes from the CCNL band, ``False`` when
            the caller supplied it.
        band: The first-tier or first applied CCNL band of the event's kind,
            if any.
        supplement: Supplement of ``band`` on the event date (``0.25``).
        tiers: Percentage bands of the kind that start beyond an hour
            threshold, in force on the event date, with their supplement.
        hourly_amount: Amount in EUR of each hour when ``band`` is paid per
            hour; it replaces the hourly rate of the event.
        weekly_slices: Band, supplement and hours for each resolved weekly tier.
    """

    multiplier: Decimal
    derived: bool
    band: OvertimeBand | None = None
    supplement: Decimal | None = None
    tiers: tuple[tuple[OvertimeBand, Decimal], ...] = ()
    hourly_amount: Decimal | None = None
    weekly_slices: tuple[tuple[OvertimeBand, Decimal, Decimal], ...] = ()

    @property
    def derived_band(self) -> OvertimeBand | None:
        """The CCNL band the multiplier comes from, ``None`` for the caller's."""
        return self.band if self.derived else None

    def paid(self, event: OvertimeEvent) -> OvertimeEvent:
        """Return ``event`` with the multiplier it is paid with.

        Returns:
            A copy of ``event`` whose ``multiplier`` is :attr:`multiplier`
            and, for a band paid per hour, whose ``hourly_rate`` is its
            amount.
        """
        if self.hourly_amount is not None:
            return replace(
                event, multiplier=self.multiplier, hourly_rate=self.hourly_amount
            )
        return replace(event, multiplier=self.multiplier)


def _in_force(band: OvertimeBand, event: OvertimeEvent) -> Decimal | None:
    period = band.rate.period_at(event.event_date)
    return None if period is None else period.value


def _kind_bands(
    bands: CCNLOvertimeBands, event: OvertimeEvent
) -> list[tuple[OvertimeBand, Decimal]]:
    """Return the unconditional percentage overtime bands of the event's kind.

    Rest-day overtime takes the holiday bands, Saturday and Sunday overtime
    the weekday ones, when the CCNL has none of their own (``_FALLBACK``).

    Returns:
        ``(band, supplement)`` for each band in force on the event date.
    """
    kind = WorkKind(event.kind.value)
    found = _bands_of(bands, event, kind)
    if not found and kind in _FALLBACK:
        return _bands_of(bands, event, _FALLBACK[kind])
    return found


def _hourly_band(
    bands: CCNLOvertimeBands, event: OvertimeEvent
) -> tuple[OvertimeBand, Decimal] | None:
    """Return the band in EUR per hour of the event's kind, if any.

    Returns:
        ``(band, amount)`` of the first unthresholded such band in force,
        the holiday one for rest-day overtime without its own.
    """
    hourly = TimeSupplementKind.INDENNITA_PER_HOUR
    kind = WorkKind(event.kind.value)
    found = _bands_of(bands, event, kind, hourly)
    if not found and kind in _FALLBACK:
        found = _bands_of(bands, event, _FALLBACK[kind], hourly)
    return next(((b, r) for b, r in found if not _has_threshold(b)), None)


def _bands_of(
    bands: CCNLOvertimeBands,
    event: OvertimeEvent,
    kind: WorkKind,
    paid_as: TimeSupplementKind = TimeSupplementKind.PERCENTAGE,
) -> list[tuple[OvertimeBand, Decimal]]:
    found: list[tuple[OvertimeBand, Decimal]] = []
    for band in bands.bands:
        rate = _in_force(band, event)
        if (
            band.code.startswith(_OVERTIME_PREFIX)
            and band.kind is paid_as
            and kind in band.applies_to_kinds
            and not band.required_context_kinds
            and rate is not None
        ):
            found.append((band, rate))
    return found


def _has_threshold(band: OvertimeBand) -> bool:
    return (
        band.hour_threshold_per_day is not None
        or band.hour_threshold_per_week is not None
    )


def resolve_overtime_rate(
    event: OvertimeEvent, bands: CCNLOvertimeBands
) -> OvertimeRate:
    """Return the multiplier ``event`` is paid with.

    Returns:
        The caller's multiplier, a weighted weekly-tier multiplier when
        preceding weekly hours are stated, or ``1 + band`` of the first tier.

    Raises:
        MissingRuleError: When the event has no multiplier and the CCNL
            has no first-tier percentage band of its kind in force.
    """
    matching = _kind_bands(bands, event)
    tiers = tuple((b, rate) for b, rate in matching if _has_threshold(b))
    base = next(((b, rate) for b, rate in matching if not _has_threshold(b)), None)
    band, supplement = (None, None) if base is None else base
    if event.multiplier is not None:
        return OvertimeRate(event.multiplier, False, band, supplement, tiers)
    if event.weekly_hours_before is not None and matching:
        multiplier, slices = weekly_rate(event, matching)
        daily = tuple((b, r) for b, r in tiers if b.hour_threshold_per_day is not None)
        return OvertimeRate(
            multiplier,
            True,
            slices[0][0],
            slices[0][1],
            daily,
            weekly_slices=slices,
        )
    hourly = _hourly_band(bands, event) if band is None else None
    if hourly is not None:
        return OvertimeRate(Decimal(1), True, hourly[0], hourly_amount=hourly[1])
    if band is None or supplement is None:
        msg = (
            f"OvertimeEvent on {event.event_date.isoformat()} has no multiplier "
            f"and the CCNL ({bands.ruleset}) has no first-tier percentage "
            f"overtime band for {event.kind.value!r} work in force on that "
            "date; D.Lgs. 66/2003 art. 5 leaves the rate to the CCNL"
        )
        raise MissingRuleError(
            msg, as_of=event.event_date, feature=_OT, remediation=_MULTIPLIER
        )
    return OvertimeRate(Decimal(1) + supplement, True, band, supplement, tiers)


def overtime_issues(
    event: OvertimeEvent, rate: OvertimeRate
) -> tuple[CalculationIssue, ...]:
    """Return the issues the multiplier of ``event`` raises.

    Returns:
        ``caller_multiplier_differs_from_ccnl`` for a caller multiplier
        matching no CCNL band of the kind, ``overtime_tier_not_applied``
        for a derived multiplier that leaves out unresolved tiers, else none.
    """
    day = event.event_date.isoformat()
    if rate.derived:
        if not rate.tiers:
            return ()
        codes = ", ".join(f"{b.code} ({1 + r})" for b, r in rate.tiers)
        message = (
            f"overtime on {day}: the CCNL multiplier {rate.multiplier} "
            f"leaves out the bands {codes} beyond an hour threshold "
            "the event does not carry: pass an explicit multiplier "
            "for the hours beyond it"
        )
        return _issue(TIER_NOT_APPLIED, message, IssueCause.RULE)
    ccnl = [(rate.band, rate.supplement)] if rate.band is not None else []
    known = [(b, r) for b, r in (*ccnl, *rate.tiers) if r is not None]
    if not known or any(rate.multiplier == 1 + r for _, r in known):
        return ()
    values = ", ".join(f"{b.code} {1 + r}" for b, r in known)
    message = (
        f"overtime on {day}: caller multiplier {rate.multiplier} differs from "
        f"the CCNL bands for {event.kind.value!r} work ({values}); the caller "
        "value is applied"
    )
    return _issue(CALLER_MULTIPLIER_DIFFERS, message, IssueCause.CONDITION)


def _issue(code: str, message: str, cause: IssueCause) -> tuple[CalculationIssue]:
    return (CalculationIssue(code, message, _PROVISIONAL, capability=_OT, cause=cause),)


_PROVISIONAL = CalculationStatus.PROVISIONAL
_OT, _MULTIPLIER = "overtime", "Pass OvertimeEvent.multiplier."
