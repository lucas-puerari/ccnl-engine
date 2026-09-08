"""Sick-leave (malattia ordinaria) computation service.

Computes the INPS statutory indemnity and the CCNL company integration
top-up for a single pay period.  All outputs are *informational*:
``gross_annual``, ``taxable_income``, and ``net_annual`` are never mutated.

The daily reference base is ``gross_monthly / 30`` (conventional calendar
month, consistent with Italian payroll practice for sick-leave deductions).

INPS rate structure (statutory — D.Lgs. 151/2001, artt. 68-71):
- Days 1-*carenza_days*: no INPS indemnity; CCNL determines coverage.
- Days *carenza_days+1* onward: INPS rate bands defined in the bundled
  ``sick-pay-rates.json`` file (50 % for days 4-20, 66.67 % for days 21-180).

Company integration:
- During carenza: company pays ``carenza_integration_rate * daily_rate``.
- During INPS-covered days: company pays the gap between
  ``full_pay_integration_rate * daily_rate`` and the INPS indemnity for
  that band (floored at zero so the integration never goes negative).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import SicknessRules
    from ccnl_engine.engine.payroll.domain.supplements import SickInput
    from ccnl_engine.engine.tax.domain.sick_pay import InpsSickPayRates

_ZERO = Decimal(0)
_CALENDAR_DAYS = Decimal(30)


def _bucket_days(
    sick_days: Decimal,
    carenza_days: int,
    bands: list[tuple[int, int]],
) -> tuple[Decimal, list[Decimal]]:
    """Split *sick_days* into the carenza bucket and per-band buckets.

    Args:
        sick_days: Total sick days in the period.
        carenza_days: Number of waiting days before INPS pays.
        bands: List of ``(day_from, day_to)`` tuples (1-indexed, inclusive)
            for INPS-covered day ranges.  Must be non-overlapping and start
            immediately after the carenza period.

    Returns:
        A 2-tuple of (carenza, [days_in_band_1, days_in_band_2, ...]).
    """
    carenza = min(sick_days, Decimal(carenza_days))
    band_days: list[Decimal] = []
    for day_from, day_to in bands:
        # Count days that fall within [day_from, day_to] and within sick_days,
        # excluding days already counted in the carenza bucket.
        start = Decimal(day_from)
        end = Decimal(day_to)
        days_in_band = max(_ZERO, min(end, sick_days) - max(start - 1, carenza))
        band_days.append(days_in_band)
    return carenza, band_days


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
        - ``carenza_days``: days in the waiting period.
        - ``inps_indemnity``: total INPS indemnity for the period.
        - ``company_integration``: company supplement above INPS.
    """
    sick_days = sick_input.sick_days
    if sick_days <= _ZERO:
        return _ZERO, _ZERO, _ZERO, _ZERO

    daily_rate = money(gross_monthly / _CALENDAR_DAYS)
    carenza_limit = sick_pay_rates.carenza_days
    bands = [(b.day_from, b.day_to) for b in sick_pay_rates.bands]
    carenza, band_buckets = _bucket_days(sick_days, carenza_limit, bands)

    # INPS indemnity (only post-carenza bands)
    inps_indemnity = _ZERO
    for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets, strict=True):
        inps_indemnity += bucket * band_obj.rate * daily_rate

    # Company integration
    carenza_pay = carenza * sickness_rules.carenza_integration_rate * daily_rate
    post_carenza_company = _ZERO
    for band_obj, bucket in zip(sick_pay_rates.bands, band_buckets, strict=True):
        gap = max(
            _ZERO,
            sickness_rules.full_pay_integration_rate - band_obj.rate,
        )
        post_carenza_company += bucket * gap * daily_rate

    company_integration = money(carenza_pay + post_carenza_company)

    return (
        sick_days,
        money(carenza),
        money(inps_indemnity),
        company_integration,
    )
