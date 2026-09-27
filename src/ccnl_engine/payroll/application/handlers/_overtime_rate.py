"""Overtime multiplier of an event: the caller's value or the CCNL band.

D.Lgs. 66/2003 art. 5 c. 5 leaves the overtime supplement to the CCNL and
sets no statutory rate, so the engine has no default multiplier:

- an explicit ``OvertimeEvent.multiplier`` prevails.  When it differs from
  every CCNL percentage band of the event's kind, the run is provisional
  with issue ``caller_multiplier_differs_from_ccnl`` reporting both values;
- without a multiplier the CCNL band of the event's kind gives it as
  ``1 + band``;
- without a multiplier and without such a band the run is rejected with
  :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.

The band of a kind is the single percentage overtime band (code ``OT_*``)
that applies to it with no hour threshold and no context condition: the
first tier of overtime.  Bands that start beyond a daily or weekly hour
threshold depend on hours of the week an event does not carry; when a
derived multiplier leaves them out, the run is provisional with issue
``overtime_tier_not_applied``.  A band paid per hour or per shift, or not
in force on the event date, gives no multiplier.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.working_time import TimeSupplementKind, WorkKind
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.contract.domain.working_time import OvertimeBand
    from ccnl_engine.payroll.domain.events import OvertimeEvent

__all__ = [
    "CALLER_MULTIPLIER_DIFFERS",
    "CCNL_BAND_APPLIED",
    "TIER_NOT_APPLIED",
    "CCNLOvertimeBands",
    "OvertimeRate",
    "resolve_overtime_rate",
]

CALLER_MULTIPLIER_DIFFERS = "caller_multiplier_differs_from_ccnl"
CCNL_BAND_APPLIED = "ccnl_overtime_band_applied"
TIER_NOT_APPLIED = "overtime_tier_not_applied"
_OVERTIME_PREFIX = "OT_"


@dataclass(frozen=True)
class CCNLOvertimeBands:
    """The overtime bands of a CCNL and the rule identity they are cited by.

    Attributes:
        bands: Time-supplement bands of the CCNL, empty when it has none.
        ruleset: Ruleset identifier of the CCNL.
        version: Ruleset version.
    """

    bands: tuple[OvertimeBand, ...] = ()
    ruleset: str = "ccnl"
    version: str = "none"

    @classmethod
    def of(cls, ccnl: CCNL, year: int) -> CCNLOvertimeBands:
        """Return the bands of ``ccnl``.

        Returns:
            The bands with the CCNL ruleset, or its slug and ``year``.
        """
        rules = ccnl.work_rules
        supplements = None if rules is None else rules.time_supplements
        bands = () if supplements is None else supplements.overtime_bands
        if ccnl.ruleset is not None:
            return cls(bands, ccnl.ruleset.id, ccnl.ruleset.version)
        return cls(bands, f"ccnl/{ccnl.meta.ccnl_id}", str(year))

    def rule_of(self, band: OvertimeBand) -> str:
        """Return the rule identifier of ``band``.

        Returns:
            ``<ruleset>:work_rules.time_supplements.overtime_bands[<code>]``.
        """
        return f"{self.ruleset}:work_rules.time_supplements.overtime_bands[{band.code}]"


@dataclass(frozen=True)
class OvertimeRate:
    """The multiplier an overtime event is paid with, and where it comes from.

    Attributes:
        multiplier: Multiplier applied to the hourly rate.
        derived: ``True`` when it comes from the CCNL band, ``False`` when
            the caller supplied it.
        band: The first-tier CCNL band of the event's kind, if any.
        supplement: Supplement of ``band`` on the event date (``0.25``).
        tiers: Percentage bands of the kind that start beyond an hour
            threshold, in force on the event date, with their supplement.
    """

    multiplier: Decimal
    derived: bool
    band: OvertimeBand | None = None
    supplement: Decimal | None = None
    tiers: tuple[tuple[OvertimeBand, Decimal], ...] = ()

    @property
    def derived_band(self) -> OvertimeBand | None:
        """The CCNL band the multiplier comes from, ``None`` for the caller's."""
        return self.band if self.derived else None

    def paid(self, event: OvertimeEvent) -> OvertimeEvent:
        """Return ``event`` with the multiplier it is paid with.

        Returns:
            A copy of ``event`` whose ``multiplier`` is :attr:`multiplier`.
        """
        return replace(event, multiplier=self.multiplier)


def _in_force(band: OvertimeBand, event: OvertimeEvent) -> Decimal | None:
    period = band.rate.period_at(event.event_date)
    return None if period is None else period.value


def _kind_bands(
    bands: CCNLOvertimeBands, event: OvertimeEvent
) -> list[tuple[OvertimeBand, Decimal]]:
    """Return the unconditional percentage overtime bands of the event's kind.

    Returns:
        ``(band, supplement)`` for each band in force on the event date.
    """
    kind = WorkKind(event.kind.value)
    found: list[tuple[OvertimeBand, Decimal]] = []
    for band in bands.bands:
        rate = _in_force(band, event)
        if (
            band.code.startswith(_OVERTIME_PREFIX)
            and band.kind is TimeSupplementKind.PERCENTAGE
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
        The caller's multiplier, or ``1 + band`` of the CCNL first tier.

    Raises:
        InvalidInputError: When the event has no multiplier and the CCNL
            has no first-tier percentage band of its kind in force.
    """
    matching = _kind_bands(bands, event)
    tiers = tuple((b, rate) for b, rate in matching if _has_threshold(b))
    base = next(((b, rate) for b, rate in matching if not _has_threshold(b)), None)
    band, supplement = (None, None) if base is None else base
    if event.multiplier is not None:
        return OvertimeRate(event.multiplier, False, band, supplement, tiers)
    if band is None or supplement is None:
        msg = (
            f"OvertimeEvent on {event.event_date.isoformat()} has no multiplier "
            f"and the CCNL ({bands.ruleset}) has no first-tier percentage "
            f"overtime band for {event.kind.value!r} work in force on that "
            "date; D.Lgs. 66/2003 art. 5 leaves the rate to the CCNL, so pass "
            "an explicit multiplier"
        )
        raise InvalidInputError(msg, feature="overtime")
    return OvertimeRate(Decimal(1) + supplement, True, band, supplement, tiers)


def overtime_issues(
    event: OvertimeEvent, rate: OvertimeRate
) -> tuple[CalculationIssue, ...]:
    """Return the issues the multiplier of ``event`` raises.

    Returns:
        ``caller_multiplier_differs_from_ccnl`` for a caller multiplier
        matching no CCNL band of the kind, ``overtime_tier_not_applied``
        for a derived multiplier that leaves out higher tiers, else none.
    """
    day = event.event_date.isoformat()
    if rate.derived:
        if not rate.tiers:
            return ()
        codes = ", ".join(f"{b.code} ({1 + r})" for b, r in rate.tiers)
        message = (
            f"overtime on {day}: the CCNL first-tier multiplier {rate.multiplier} "
            f"is applied to every hour; the bands {codes} start beyond an hour "
            "threshold the event does not carry: pass an explicit multiplier "
            "for the hours beyond it"
        )
        return (CalculationIssue(TIER_NOT_APPLIED, message, _PROVISIONAL),)
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
    return (CalculationIssue(CALLER_MULTIPLIER_DIFFERS, message, _PROVISIONAL),)


_PROVISIONAL = CalculationStatus.PROVISIONAL


def band_decision(
    event: OvertimeEvent, rate: OvertimeRate, bands: CCNLOvertimeBands, amount: Decimal
) -> CalculationDecision | None:
    """Return the decision of a multiplier derived from the CCNL band.

    Returns:
        An ``overtime`` decision citing the band, provisional when higher
        tiers were left out; ``None`` for a caller multiplier.
    """
    band = rate.band
    if not rate.derived or band is None or rate.supplement is None:
        return None
    provenance = band.provenance
    return CalculationDecision(
        capability="overtime",
        status=CalculationStatus.PROVISIONAL if rate.tiers else CalculationStatus.FINAL,
        reason_code=CCNL_BAND_APPLIED,
        rule=bands.rule_of(band),
        rule_version=bands.version,
        inputs={
            "kind": event.kind.value,
            "band_code": band.code,
            "band_supplement": rate.supplement,
            "multiplier": rate.multiplier,
            "hours": event.hours,
            "hourly_rate": event.hourly_rate,
        },
        source=None if provenance is None else provenance.location,
        amount=amount,
    )
