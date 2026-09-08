"""Layer 3 time-supplement computation service."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import TimeSupplementKind, WorkKind
from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import OvertimeBand, TimeSupplements
    from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours

_ZERO = Decimal(0)

# WorkKind → which accumulator bucket it targets.
# SUPPLEMENTARE counts toward overtime (lavoro supplementare for part-timers).
# NIGHT_HOLIDAY (festivo-notturno) counts toward the holiday bucket.
_KIND_BUCKET: dict[WorkKind, str] = {
    WorkKind.WEEKDAY: "overtime",
    WorkKind.SUPPLEMENTARE: "overtime",
    WorkKind.NIGHT: "night",
    WorkKind.HOLIDAY: "holiday",
    WorkKind.NIGHT_HOLIDAY: "holiday",
}


def _band_rate(band: OvertimeBand, as_of: date) -> Decimal:
    """Return the rate value for the band on ``as_of``.

    Returns:
        The resolved rate as a Decimal.
    """
    return band.rate.value_at(as_of)


def _supplement_for_band(
    band: OvertimeBand,
    hours: Decimal,
    hourly_base: Decimal,
    as_of: date,
) -> Decimal:
    """Compute the supplement amount for one band and one hours bucket.

    Returns:
        Supplement amount for the given band, not yet rounded.
    """
    if hours <= _ZERO:
        return _ZERO
    rate = _band_rate(band, as_of)
    if band.kind == TimeSupplementKind.PERCENTAGE:
        return hours * rate * hourly_base
    # INDENNITA_PER_HOUR or INDENNITA_PER_SHIFT: rate is per hour/shift
    return hours * rate


def compute_time_supplements(
    supps_input: OvertimeHours,
    supplements_schema: TimeSupplements,
    base_monthly_full_time: Decimal,
    hourly_divisor: Decimal,
    as_of: date,
) -> tuple[Decimal, Decimal, Decimal, tuple[TraceStep, ...]]:
    """Compute overtime, night-work, and holiday-work supplements.

    The hourly base is ``base_monthly_full_time / hourly_divisor``, per the
    CCNL convention that maggiorazioni apply to the *minimo tabellare* only
    (or the gross, if ``hourly_base_method="gross_incl_allowances"``).

    The function accumulates *all* bands whose ``applies_to_kinds`` matches
    the caller's input: all matching bands are summed (not first-match-wins).

    Args:
        supps_input: Caller-declared supplement hours for the pay period.
        supplements_schema: CCNL time-supplement rules.
        base_monthly_full_time: Full-time base salary (minimo tabellare).
        hourly_divisor: CCNL monthly hours divisor (e.g. 173).
        as_of: Reference date for time-series rate lookups.

    Returns:
        A 4-tuple of:
        - ``overtime_supplement_monthly``: weekday overtime supplement.
        - ``night_supplement_monthly``: night-work supplement.
        - ``holiday_supplement_monthly``: holiday-work supplement.
        - ``supplement_steps``: ordered :class:`TraceStep` entries for the
          supplement trace.
    """
    hourly_base = base_monthly_full_time / hourly_divisor

    kind_to_hours: dict[WorkKind, Decimal] = {
        WorkKind.WEEKDAY: supps_input.weekday_hours,
        WorkKind.NIGHT: supps_input.night_hours,
        WorkKind.HOLIDAY: supps_input.holiday_hours,
        WorkKind.NIGHT_HOLIDAY: supps_input.night_holiday_hours,
        WorkKind.SUPPLEMENTARE: supps_input.supplementare_hours,
    }

    buckets: dict[str, Decimal] = {"overtime": _ZERO, "night": _ZERO, "holiday": _ZERO}
    trace: list[TraceStep] = []

    for band in supplements_schema.overtime_bands:
        for kind in band.applies_to_kinds:
            hours = kind_to_hours.get(kind, _ZERO)
            if hours <= _ZERO:
                continue
            raw = _supplement_for_band(band, hours, hourly_base, as_of)
            if raw <= _ZERO:
                continue
            amount = money(raw)
            buckets[_KIND_BUCKET[kind]] += amount
            trace.append(
                TraceStep(
                    category=TraceCategory.TIME_SUPPLEMENT,
                    label=band.description,
                    amount=amount,
                    detail=f"{band.code}/{kind.value}",
                )
            )

    overtime_supplement = money(buckets["overtime"])
    night_supplement = money(buckets["night"])
    holiday_supplement = money(buckets["holiday"])
    total = money(overtime_supplement + night_supplement + holiday_supplement)

    if trace:
        trace.append(
            TraceStep(
                category=TraceCategory.SUPPLEMENT_TOTAL,
                label="Totale maggiorazioni",
                amount=total,
            )
        )

    return overtime_supplement, night_supplement, holiday_supplement, tuple(trace)
