"""Working-time and leave rule models for CCNL contracts."""

from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ccnl_engine.engine.contract.domain.validity import TimeSeries
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance


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
    not overlap with ``night_hours`` or ``holiday_hours``.
    """

    WEEKDAY = "weekday"
    NIGHT = "night"
    HOLIDAY = "holiday"
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
    provenance: RuleProvenance | None = None


class TimeSupplements(BaseModel):
    """Layer 3 time-supplement rules (overtime, night work, holiday work).

    ``hourly_base_method`` controls which base is used:

    * ``minimo_tabellare``: the CCNL table minimum only (no allowances).
    * ``gross_incl_allowances``: the full gross including fixed allowances.

    ``overtime_bands`` is an ordered list of :class:`OvertimeBand` entries.
    All applicable bands accumulate (no "first match wins" truncation) unless
    a CCNL-specific note says otherwise.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hourly_base_method: Literal["minimo_tabellare", "gross_incl_allowances"] = (
        "minimo_tabellare"
    )
    overtime_bands: tuple[OvertimeBand, ...] = Field(default=())

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
        unconditional: dict[str, list[str]] = {}
        for band in bands:
            is_conditional = bool(band.required_context_kinds)
            has_threshold = (
                band.hour_threshold_per_week is not None
                or band.hour_threshold_per_day is not None
            )
            if not is_conditional and not has_threshold:
                for k in band.applies_to_kinds:
                    unconditional.setdefault(k, []).append(band.code)
        collisions = {k: codes for k, codes in unconditional.items() if len(codes) > 1}
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


class LeaveEntitlementTier(BaseModel):
    """One seniority-gated leave entitlement tier.

    When ``service_months_min`` months of service have elapsed, the worker
    is entitled to ``annual_days`` paid leave days per year. Tiers are
    evaluated in descending order of ``service_months_min``; the first
    matching tier wins. Use :class:`LeaveRules.default_annual_days` as
    the fallback when no tier matches or seniority is unknown.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    service_months_min: int = Field(default=0, ge=0)
    annual_days: Decimal = Field(gt=Decimal(0))


class LeaveRules(BaseModel):
    """Layer 3 rules for paid leave (ferie / permessi) accrual.

    ``default_annual_days`` is the contractual entitlement when no
    seniority-gated tier matches or when seniority is unknown.
    ``entitlement_tiers`` (optional) list tiers in any order; the engine
    selects the one with the highest ``service_months_min`` that the
    worker has satisfied.

    ``provenance`` links this rule to its CCNL article.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    default_annual_days: Decimal = Field(gt=Decimal(0))
    entitlement_tiers: tuple[LeaveEntitlementTier, ...] = Field(default=())
    provenance: RuleProvenance | None = None
