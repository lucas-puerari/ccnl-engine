"""Working-time and leave rule models for CCNL contracts."""

from collections.abc import Sequence
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ccnl_engine.agreement.validity.rules import TimeSeries
from ccnl_engine.provenance.source.rule.models import RuleProvenance
from ccnl_engine.working_time.supplement.models import (
    HourlyBaseMethod,
    SupplementBand,
    SupplementWork,
)


class TimeSupplementKind(StrEnum):
    """How the overtime band rate is applied."""

    PERCENTAGE = "percentage"
    INDENNITA_PER_SHIFT = "indennita_per_shift"
    INDENNITA_PER_HOUR = "indennita_per_hour"


class WorkKind(StrEnum):
    """Kind of working time for overtime band matching.

    ``NIGHT_HOLIDAY`` represents hours worked at night *on* a public holiday
    (lavoro straordinario festivo-notturno).  The caller must declare these
    hours separately in :attr:`OvertimeHours.night_holiday_hours`; they do
    not overlap with ``night_hours`` or ``holiday_hours``.  ``REST_DAY``
    is overtime on the weekly rest day for the CCNLs that pay it apart from
    the public holidays.
    """

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
    REST_DAY = "rest_day"
    NIGHT_HOLIDAY = "night_holiday"
    SUPPLEMENTARE = "supplementare"


class OvertimeBand(BaseModel):
    """One overtime/supplement band: a rate applied to a specific work kind.

    ``kind`` controls how ``rate`` is interpreted:

    * ``percentage``: supplement = rate * full-time hourly base * hours.
    * ``indennita_per_hour``: supplement = rate * hours (fixed EUR/hour).
    * ``indennita_per_shift``: supplement = rate * shift count (fixed EUR/shift).

    ``applies_to_kinds`` lists the :class:`WorkKind` values this band covers.
    ``hour_threshold_per_day`` / ``hour_threshold_per_week`` optionally restrict
    the band to hours *beyond* that threshold (straordinario, not supplementare).
    ``required_context_kinds``, when non-empty, makes this a conditional band:
    it is only applied when ALL listed kinds also have non-zero declared hours.
    ``levels``, when non-empty, restricts the band to those level codes (a
    PA table of hourly amounts by area); empty, it applies to every level.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    description: str
    kind: TimeSupplementKind
    rate: TimeSeries
    hour_threshold_per_day: int | None = None
    hour_threshold_per_week: int | None = None
    applies_to_kinds: tuple[WorkKind, ...]
    required_context_kinds: tuple[WorkKind, ...] = ()
    levels: tuple[str, ...] = ()
    provenance: RuleProvenance | None = None


class TimeSupplements(BaseModel):
    """Layer 3 time-supplement rules (overtime, night work, holiday work).

    ``hourly_base_method`` names the monthly pay elements divided by
    ``parameters.hourly_divisor`` for the hourly rate of the CCNL
    (:class:`HourlyBaseMethod`).  The engine derives an hourly rate from it
    only when ``hourly_base_provenance`` is verified; otherwise the caller
    states the rate.  ``hourly_divisor_weekly_hours``, when set, is the
    full-time week the divisor belongs to: an employment whose full-time
    week differs is not derived (the CCNL sets another divisor for it).

    ``overtime_bands`` is an ordered list of :class:`OvertimeBand` entries.
    All applicable bands accumulate (no "first match wins" truncation) unless
    a CCNL-specific note says otherwise.  ``supplement_bands`` are the
    supplements of ordinary night, holiday and shift work.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hourly_base_method: HourlyBaseMethod = HourlyBaseMethod.MINIMO_TABELLARE
    hourly_base_provenance: RuleProvenance | None = None
    hourly_divisor_weekly_hours: int | None = Field(default=None, ge=1)
    overtime_bands: tuple[OvertimeBand, ...] = Field(default=())
    supplement_bands: tuple[SupplementBand, ...] = Field(default=())

    @field_validator("overtime_bands")
    @classmethod
    def _no_ambiguous_collisions(
        cls, bands: tuple[OvertimeBand, ...]
    ) -> tuple[OvertimeBand, ...]:
        """Reject overlapping bands with no threshold or context predicate.

        Two or more bands for the same WorkKind are only allowed when they are
        disambiguated by ``hour_threshold_per_week``, ``hour_threshold_per_day``,
        or ``required_context_kinds``. Bands that overlap without any such
        predicate are ambiguous and cannot be applied deterministically.

        Returns:
            The validated bands tuple unchanged.

        Raises:
            ValueError: If two or more unconditional bands share a WorkKind
                with no threshold to distinguish them.
        """
        unconditional: dict[str, list[OvertimeBand]] = {}
        for band in bands:
            is_conditional = bool(band.required_context_kinds)
            has_threshold = (
                band.hour_threshold_per_week is not None
                or band.hour_threshold_per_day is not None
            )
            if not is_conditional and not has_threshold:
                for k in band.applies_to_kinds:
                    unconditional.setdefault(k, []).append(band)
        collisions = {
            k: [b.code for b in found]
            for k, found in unconditional.items()
            if _levels_overlap(found)
        }
        if collisions:
            details = "; ".join(
                f"{k}: {codes}" for k, codes in sorted(collisions.items())
            )
            msg = (
                "Ambiguous OvertimeBand collisions (missing threshold or predicate): "
                + details
            )
            raise ValueError(msg)
        return bands

    @field_validator("supplement_bands")
    @classmethod
    def _one_band_per_work(
        cls, bands: tuple[SupplementBand, ...]
    ) -> tuple[SupplementBand, ...]:
        """Reject two bands of the same work and role for a level.

        Returns:
            The validated bands unchanged.

        Raises:
            ValueError: When two bands of one work and role share a level.
        """
        groups: dict[tuple[SupplementWork, str | None], list[SupplementBand]] = {}
        for band in bands:
            groups.setdefault((band.work, band.role), []).append(band)
        clashes = [
            f"{work}/{role}: {[b.code for b in found]}"
            for (work, role), found in groups.items()
            if _levels_overlap(found)
        ]
        if clashes:
            msg = "Ambiguous SupplementBand collisions: " + "; ".join(sorted(clashes))
            raise ValueError(msg)
        return bands


def _levels_overlap(bands: Sequence[OvertimeBand | SupplementBand]) -> bool:
    """Return whether two of ``bands`` can apply to the same level.

    Returns:
        ``True`` when two bands share a level or one names no level.
    """
    for i, band in enumerate(bands):
        for other in bands[i + 1 :]:
            if not band.levels or not other.levels:
                return True
            if set(band.levels) & set(other.levels):
                return True
    return False


class TravelAllowanceBand(BaseModel):
    """Daily travel allowance of the CCNL for a span of hours away.

    Attributes:
        hours_from: First hour of the span (at least this many hours).
        hours_until: Hours the span stays below; ``None`` for no limit.
        italy: Daily amount of a trasferta in Italy.
        abroad: Daily amount of a trasferta abroad.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hours_from: Decimal = Field(ge=Decimal(0))
    hours_until: Decimal | None = None
    italy: TimeSeries
    abroad: TimeSeries

    def holds(self, hours: Decimal) -> bool:
        """Return whether ``hours`` away fall in the span.

        Returns:
            ``hours_from <= hours < hours_until``.
        """
        return hours >= self.hours_from and (
            self.hours_until is None or hours < self.hours_until
        )


class CcnlTravelAllowance(BaseModel):
    """CCNL amounts of the daily travel allowance (indennità di trasferta).

    Attributes:
        bands: Spans of hours away with their amounts; fewer hours than the
            first span give no allowance.
        tfr_base: What of the allowance enters the TFR base: ``"none"``,
            ``"whole"``, or ``"above_exempt"`` (the part above the IRPEF
            exemption, Logistica art. 62 c. 7).
        night_allowance: Amount for each day of at least
            :attr:`night_from_hours` away (Logistica art. 16: 0.93 per
            trasferta of 18 to 24 hours), pay of the period that enters the
            TFR base; ``None`` without one.
        night_from_hours: Hours away from which the night allowance is due.
        provenance: Source and status of the amounts.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    bands: tuple[TravelAllowanceBand, ...] = Field(min_length=1)
    tfr_base: Literal["none", "whole", "above_exempt"]
    night_allowance: TimeSeries | None = None
    night_from_hours: Decimal = Decimal(18)
    provenance: RuleProvenance | None = None

    def band_of(self, hours: Decimal) -> TravelAllowanceBand | None:
        """Return the span of ``hours`` away.

        Returns:
            The band holding ``hours``, ``None`` below the first.
        """
        return next((b for b in self.bands if b.holds(hours)), None)
