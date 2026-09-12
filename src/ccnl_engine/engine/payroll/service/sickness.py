"""Sick-leave (malattia ordinaria) computation service.

Computes the INPS statutory indemnity and the CCNL company integration
top-up for a single pay period.  All outputs are *informational*:
``gross_annual``, ``taxable_income``, and ``net_annual`` are never mutated.

The daily reference base is ``gross_monthly / 30`` (conventional calendar
month, consistent with Italian payroll practice for sick-leave deductions).

INPS rate structure (statutory -- D.Lgs. 151/2001, artt. 68-71):
- Days 1-*carenza_days*: no INPS indemnity; CCNL determines coverage.
- Days *carenza_days+1* onward: INPS rate bands defined in the bundled
  ``sick-pay-rates.json`` file (50 % for days 4-20, 66.67 % for days 21-180).

Cumulative offset (R5):
When ``SickInput.cumulative_sick_days`` is provided it represents the number
of sick days already elapsed in the same illness episode BEFORE this period.
The carenza and INPS band positions are computed relative to the episode
start, so splitting one episode across multiple periods gives the same totals
as computing it as a single period.

Company integration:
- During carenza: company pays ``carenza_integration_rate * daily_rate``.
- During INPS-covered days: company pays the gap between the effective
  integration rate and the INPS indemnity for that band (floored at zero).
- When ``SicknessRules.tiers`` is populated and ``cumulative_sick_days`` is
  provided, the integration rate is selected per 30-day tier month. Periods
  that cross a tier boundary are split at that boundary so each segment uses
  the correct rate (R6).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import SicknessRules, SicknessTier
    from ccnl_engine.engine.payroll.domain.supplements import SickInput
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

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
    cumulative_offset: int = 0,
) -> tuple[Decimal, list[Decimal]]:
    """Split *sick_days* into the carenza bucket and per-band buckets.

    When ``cumulative_offset`` > 0 the current period covers episode days
    ``[offset+1, offset+sick_days]`` (1-indexed), so carenza days and INPS
    bands that precede the offset are excluded.  This ensures that splitting
    the same illness episode across multiple calls returns the same totals as
    a single call (R5).

    Args:
        sick_days: Total sick days in the period.
        carenza_days: Number of waiting days before INPS pays.
        bands: List of ``(day_from, day_to)`` tuples (1-indexed, inclusive)
            for INPS-covered day ranges.  Must be non-overlapping and start
            immediately after the carenza period.
        cumulative_offset: Episode days already elapsed before this period.
            Defaults to 0 (period starts at the beginning of the episode).

    Returns:
        A 2-tuple of (carenza, [days_in_band_1, days_in_band_2, ...]).
    """
    # Episode position uses 0-based half-open intervals: [ep_start, ep_end).
    # Episode day N (1-indexed) maps to half-open [N-1, N).
    ep_start = Decimal(cumulative_offset)
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


def _tier_rate_segments(
    sick_days: Decimal,
    cumulative_sick_days: Decimal,
    sickness_rules: SicknessRules,
) -> list[tuple[Decimal, Decimal]]:
    """Compute (days, rate) segments for company integration across tier boundaries.

    When the current period spans a CCNL tier boundary (measured in 30-day
    months), the days are split at the boundary and each segment receives the
    rate for its tier (R6).  When tiers are absent or cumulative context is
    unavailable, a single segment covering all sick days is returned.

    Args:
        sick_days: Sick days in this period.
        cumulative_sick_days: Episode days elapsed before this period.
        sickness_rules: CCNL rules with optional tiers.

    Returns:
        List of ``(days, integration_rate)`` tuples covering the full period.
    """
    if not sickness_rules.tiers:  # pragma: no cover
        return [(sick_days, sickness_rules.full_pay_integration_rate)]

    # Collect all day-based tier boundary points within or around the period.
    period_start = cumulative_sick_days
    period_end = cumulative_sick_days + sick_days

    # Tier boundaries in days.
    # Month m starts at day (m-1)*30: int(day/30)+1 = m when day = (m-1)*30.
    boundary_set: set[Decimal] = {period_start, period_end}
    for tier in sickness_rules.tiers:
        for month in (tier.month_from, tier.month_until):
            if month is not None:
                day = Decimal(month - 1) * _DAYS_PER_MONTH
                if period_start < day < period_end:
                    boundary_set.add(day)

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
        post_carenza_days, post_carenza_offset, sickness_rules
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


def compute_sickness(
    sick_input: SickInput,
    sickness_rules: SicknessRules,
    sick_pay_rates: InpsSickPayRates,
    gross_monthly: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Compute sick-leave indemnity and CCNL integration for one pay period.

    Args:
        sick_input: Caller-declared sick days.
        sickness_rules: CCNL-specific integration parameters.
        sick_pay_rates: Statutory INPS rate bands loaded from the bundle.
        gross_monthly: Full-time gross pay for the month (``chain.gross``).

    Returns:
        A 4-tuple of:
        - ``sick_days``: total sick days (echo of input).
        - ``carenza_days``: days in the waiting period (this period only).
        - ``inps_indemnity``: total INPS indemnity for the period.
        - ``company_integration``: company supplement above INPS.
    """
    sick_days = sick_input.sick_days
    if sick_days <= _ZERO:
        return _ZERO, _ZERO, _ZERO, _ZERO

    cumulative = sick_input.cumulative_sick_days
    offset = int(cumulative) if cumulative is not None else 0

    daily_rate = money(gross_monthly / _CALENDAR_DAYS)
    carenza_limit = sick_pay_rates.carenza_days
    bands = [(b.day_from, b.day_to) for b in sick_pay_rates.bands]
    carenza, band_buckets = _bucket_days(
        sick_days, carenza_limit, bands, cumulative_offset=offset
    )

    # INPS indemnity (only post-carenza bands)
    inps_indemnity = _ZERO
    for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets, strict=True):
        inps_indemnity += bucket * band_obj.rate * daily_rate

    # Company integration -- split at CCNL tier boundaries when available (R6)
    carenza_pay = carenza * sickness_rules.carenza_integration_rate * daily_rate
    post_carenza_days = max(_ZERO, sick_days - carenza)

    if cumulative is not None and sickness_rules.tiers and post_carenza_days > _ZERO:
        post_carenza_offset = Decimal(max(offset, carenza_limit))
        post_carenza_company = _post_carenza_tier(
            post_carenza_days,
            post_carenza_offset,
            sickness_rules,
            sick_pay_rates,
            daily_rate,
        )
    else:
        # Simple single-rate integration (no tiers or no cumulative context)
        eff_rate = _effective_integration_rate(sickness_rules, cumulative)
        post_carenza_company = _ZERO
        for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets, strict=True):
            gap = max(_ZERO, eff_rate - band_obj.rate)
            post_carenza_company += bucket * gap * daily_rate

    company_integration = money(carenza_pay + post_carenza_company)

    return (
        sick_days,
        money(carenza),
        money(inps_indemnity),
        company_integration,
    )
