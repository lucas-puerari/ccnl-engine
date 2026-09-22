"""compute_sickness — the public entry point for sick-leave calculation."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.sickness._helpers import (
    _ZERO,
    _bucket_days,
    _effective_integration_rate,
    _post_carenza_tier,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import SicknessRules
    from ccnl_engine.engine.payroll.domain.supplements import SickInput
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

_CALENDAR_DAYS = Decimal(30)


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

    # Normalise once: None means "first episode, zero elapsed days"
    # and is documented as equivalent to Decimal(0) in SickInput.
    cumulative: Decimal = sick_input.cumulative_sick_days or _ZERO
    offset: Decimal = cumulative

    daily_rate = money(gross_monthly / _CALENDAR_DAYS)
    carenza_limit = sick_pay_rates.carenza_days
    bands = [(b.day_from, b.day_to) for b in sick_pay_rates.bands]
    carenza, band_buckets = _bucket_days(
        sick_days, carenza_limit, bands, cumulative_offset=offset
    )

    # INPS indemnity (only post-carenza bands; INPS has its own band ceiling)
    inps_indemnity = _ZERO
    for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets, strict=True):
        inps_indemnity += bucket * band_obj.rate * daily_rate

    # Company integration is limited to the comporto period (max_duration_days).
    # Days beyond the comporto are not covered by the CCNL.
    comporto_limit = Decimal(sickness_rules.max_duration_days)
    eligible = max(_ZERO, comporto_limit - offset)
    integration_days = min(sick_days, eligible)

    carenza_i, band_buckets_i = _bucket_days(
        integration_days, carenza_limit, bands, cumulative_offset=offset
    )

    # Company integration -- split at CCNL tier boundaries when available
    carenza_pay = carenza_i * sickness_rules.carenza_integration_rate * daily_rate
    post_carenza_days = max(_ZERO, integration_days - carenza_i)

    if sickness_rules.tiers and post_carenza_days > _ZERO:
        post_carenza_offset = max(offset, Decimal(carenza_limit))
        post_carenza_company = _post_carenza_tier(
            post_carenza_days,
            post_carenza_offset,
            sickness_rules,
            sick_pay_rates,
            daily_rate,
        )
    else:
        # Simple single-rate integration (no tiers, or only carenza days)
        eff_rate = _effective_integration_rate(sickness_rules, cumulative)
        post_carenza_company = _ZERO
        for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets_i, strict=True):
            gap = max(_ZERO, eff_rate - band_obj.rate)
            post_carenza_company += bucket * gap * daily_rate
        # Days within comporto but beyond the last INPS band have INPS rate = 0.
        days_in_bands = sum(band_buckets_i)
        beyond_band_days = post_carenza_days - days_in_bands
        if beyond_band_days > _ZERO:
            post_carenza_company += beyond_band_days * eff_rate * daily_rate

    company_integration = money(carenza_pay + post_carenza_company)

    return (
        sick_days,
        money(carenza),
        money(inps_indemnity),
        company_integration,
    )
