"""Internal helpers for sick-leave computation."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import SicknessRules, SicknessTier
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates, SickPayBand

_ZERO = Decimal(0)
_CALENDAR_DAYS = Decimal(30)
_DAYS_PER_MONTH = Decimal(30)


def _effective_integration_rate(
    sickness_rules: SicknessRules,
    cumulative_sick_days: Decimal | None,
) -> Decimal:
    """Return the integration rate for the current episode position.

    When ``tiers`` is non-empty and ``cumulative_sick_days`` is provided,
    selects the tier with the highest ``month_from`` that the cumulative
    position has reached.  Falls back to ``full_pay_integration_rate``
    when tiers are absent or cumulative context is unavailable.

    Args:
        sickness_rules: CCNL sickness rules with optional tiers.
        cumulative_sick_days: Total sick days elapsed before this period,
            or ``None`` to use the flat rate.

    Returns:
        The effective integration rate as a Decimal.
    """
    if not sickness_rules.tiers or cumulative_sick_days is None:
        return sickness_rules.full_pay_integration_rate

    current_month = int(cumulative_sick_days / _DAYS_PER_MONTH) + 1
    best: SicknessTier | None = None
    for tier in sickness_rules.tiers:
        within_until = tier.month_until is None or current_month < tier.month_until
        qualifies = current_month >= tier.month_from and within_until
        if qualifies and (best is None or tier.month_from > best.month_from):
            best = tier
    if best is not None:
        return best.integration_rate
    return sickness_rules.full_pay_integration_rate


def _bucket_days(
    sick_days: Decimal,
    carenza_days: int,
    bands: list[tuple[int, int]],
    cumulative_offset: Decimal = _ZERO,
) -> tuple[Decimal, list[Decimal]]:
    """Split *sick_days* into the carenza bucket and per-band buckets.

    When ``cumulative_offset`` > 0 the current period covers episode days
    ``[offset+1, offset+sick_days]`` (1-indexed), so carenza days and INPS
    bands that precede the offset are excluded.  This ensures that splitting
    the same illness episode across multiple calls returns the same totals as
    a single call.

    Args:
        sick_days: Total sick days in the period.
        carenza_days: Number of waiting days before INPS pays.
        bands: List of ``(day_from, day_to)`` tuples (1-indexed, inclusive)
            for INPS-covered day ranges.  Must be non-overlapping and start
            immediately after the carenza period.
        cumulative_offset: Episode days already elapsed before this period
            as a ``Decimal`` (preserves fractional days).  Defaults to zero
            (period starts at the beginning of the episode).

    Returns:
        A 2-tuple of (carenza, [days_in_band_1, days_in_band_2, ...]).
    """
    # Episode position uses 0-based half-open intervals: [ep_start, ep_end).
    # Episode day N (1-indexed) maps to half-open [N-1, N).
    ep_start = cumulative_offset
    ep_end = ep_start + sick_days

    # Carenza covers episode days 1..carenza_days, i.e. [0, carenza_days).
    carenza_end = Decimal(carenza_days)
    carenza = max(_ZERO, min(carenza_end, ep_end) - max(_ZERO, ep_start))

    band_days: list[Decimal] = []
    for day_from, day_to in bands:
        # Band covers episode days [day_from, day_to] inclusive
        # i.e. half-open [day_from-1, day_to).
        start = Decimal(day_from - 1)
        end = Decimal(day_to)
        days_in_band = max(_ZERO, min(end, ep_end) - max(start, ep_start))
        band_days.append(days_in_band)
    return carenza, band_days


def _ccnl_tier_boundaries_in_period(
    sickness_rules: SicknessRules,
    period_start: Decimal,
    period_end: Decimal,
) -> set[Decimal]:
    """Return CCNL tier boundary day-positions that fall strictly inside the period.

    Args:
        sickness_rules: CCNL rules with optional tiers.
        period_start: Episode day at which the period begins (0-based).
        period_end: Episode day at which the period ends (exclusive).

    Returns:
        Set of day positions where the CCNL integration rate changes.
    """
    boundaries: set[Decimal] = set()
    for tier in sickness_rules.tiers:
        for month in (tier.month_from, tier.month_until):
            if month is not None:
                day = Decimal(month - 1) * _DAYS_PER_MONTH
                if period_start < day < period_end:
                    boundaries.add(day)
    return boundaries


def _inps_boundaries_in_period(
    bands: list[SickPayBand],
    period_start: Decimal,
    period_end: Decimal,
) -> set[Decimal]:
    """Return INPS band boundary day-positions that fall strictly inside the period.

    Each band boundary is at the start of the band (``day_from - 1`` in
    0-based episode-day space).  Splitting at these points ensures every
    segment lies entirely within one INPS rate band.

    Args:
        bands: Statutory INPS rate bands from the bundled rates file.
        period_start: Episode day at which the period begins (0-based).
        period_end: Episode day at which the period ends (exclusive).

    Returns:
        Set of day positions where the INPS rate changes.
    """
    boundaries: set[Decimal] = set()
    for band in bands:
        for day in (Decimal(band.day_from - 1), Decimal(band.day_to)):
            if period_start < day < period_end:
                boundaries.add(day)
    return boundaries


def _tier_rate_segments(
    sick_days: Decimal,
    cumulative_sick_days: Decimal,
    sickness_rules: SicknessRules,
    sick_pay_rates: InpsSickPayRates | None = None,
) -> list[tuple[Decimal, Decimal]]:
    """Compute (days, rate) segments for company integration across tier boundaries.

    When the current period spans a CCNL tier boundary (measured in 30-day
    months) or an INPS band boundary, the days are split at the boundary and
    each segment receives the rate for its tier.  When tiers are absent or
    cumulative context is unavailable, a single segment covering all sick days
    is returned.

    Args:
        sick_days: Sick days in this period.
        cumulative_sick_days: Episode days elapsed before this period.
        sickness_rules: CCNL rules with optional tiers.
        sick_pay_rates: Statutory INPS rate bands; when provided, INPS band
            boundaries are also used as split points so that each segment
            lies entirely within one INPS rate band.

    Returns:
        List of ``(days, integration_rate)`` tuples covering the full period.
    """
    if not sickness_rules.tiers:  # pragma: no cover
        return [(sick_days, sickness_rules.full_pay_integration_rate)]

    period_start = cumulative_sick_days
    period_end = cumulative_sick_days + sick_days

    boundary_set: set[Decimal] = {period_start, period_end}
    boundary_set |= _ccnl_tier_boundaries_in_period(
        sickness_rules, period_start, period_end
    )
    if sick_pay_rates is not None:
        boundary_set |= _inps_boundaries_in_period(
            sick_pay_rates.bands, period_start, period_end
        )

    boundaries = sorted(boundary_set)

    segments: list[tuple[Decimal, Decimal]] = []
    for i in range(len(boundaries) - 1):
        seg_start = boundaries[i]
        seg_end = boundaries[i + 1]
        seg_days = seg_end - seg_start
        if seg_days <= _ZERO:  # pragma: no cover
            continue
        rate = _effective_integration_rate(sickness_rules, seg_start)
        segments.append((seg_days, rate))

    return segments or [(sick_days, sickness_rules.full_pay_integration_rate)]


def _inps_rate_at_offset(
    sick_pay_rates: InpsSickPayRates,
    seg_start: Decimal,
    seg_end: Decimal,
) -> Decimal:
    """Return the INPS band rate that overlaps [seg_start, seg_end), or zero.

    Args:
        sick_pay_rates: Statutory INPS rate bands.
        seg_start: Start of the segment in episode-day space (0-based).
        seg_end: End of the segment in episode-day space (exclusive).

    Returns:
        The INPS rate for the first overlapping band, or zero.
    """
    for band_obj in sick_pay_rates.bands:
        band_start = Decimal(band_obj.day_from - 1)
        band_end = Decimal(band_obj.day_to)
        overlap = max(_ZERO, min(band_end, seg_end) - max(band_start, seg_start))
        if overlap > _ZERO:
            return band_obj.rate
    return _ZERO


def _post_carenza_tier(
    post_carenza_days: Decimal,
    post_carenza_offset: Decimal,
    sickness_rules: SicknessRules,
    sick_pay_rates: InpsSickPayRates,
    daily_rate: Decimal,
) -> Decimal:
    """Company integration for post-carenza days using tier-aware segmentation.

    Splits the post-carenza period at CCNL tier boundaries and applies the
    correct rate per segment, offsetting the INPS indemnity for each band.

    Args:
        post_carenza_days: Sick days after the carenza period.
        post_carenza_offset: Episode position at the start of the post-carenza.
        sickness_rules: CCNL rules with tiers.
        sick_pay_rates: Statutory INPS rate bands.
        daily_rate: Daily gross pay rate.

    Returns:
        Total company integration contribution for the post-carenza portion.
    """
    segments = _tier_rate_segments(
        post_carenza_days, post_carenza_offset, sickness_rules, sick_pay_rates
    )
    total = _ZERO
    offset = post_carenza_offset
    for seg_days, eff_rate in segments:
        seg_end = offset + seg_days
        seg_inps_rate = _inps_rate_at_offset(sick_pay_rates, offset, seg_end)
        gap = max(_ZERO, eff_rate - seg_inps_rate)
        total += seg_days * gap * daily_rate
        offset = seg_end
    return total
