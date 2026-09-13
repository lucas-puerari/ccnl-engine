"""Layer 3 time-supplement computation service."""

from __future__ import annotations

from collections import defaultdict
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


def _slice_hours_for_band(
    band_index: int,
    sorted_bands: list[OvertimeBand],
    total_hours: Decimal,
) -> Decimal:
    """Return the slice of hours assigned to one band in a threshold-sorted list.

    Bands are partitioned by ``hour_threshold_per_week``: band *i* covers
    hours from its threshold up to band *i+1*'s threshold (or all remaining
    hours for the last band).

    Args:
        band_index: Index of the current band in ``sorted_bands``.
        sorted_bands: Bands sorted ascending by ``hour_threshold_per_week``.
        total_hours: Total hours available for this work kind.

    Returns:
        Hours in the half-open interval assigned to this band.
    """
    lo = Decimal(sorted_bands[band_index].hour_threshold_per_week or 0)
    if band_index + 1 < len(sorted_bands):
        hi = Decimal(sorted_bands[band_index + 1].hour_threshold_per_week or 0)
        return max(_ZERO, min(total_hours, hi) - lo)
    return max(_ZERO, total_hours - lo)


def _supplements_for_kind(
    kind: WorkKind,
    bands: list[OvertimeBand],
    total_hours: Decimal,
    hourly_base: Decimal,
    as_of: date,
) -> list[tuple[Decimal, str, str, str]]:
    """Compute (amount, bucket, label, detail) entries for one work kind.

    When ``bands`` contains multiple entries they are sorted by
    ``hour_threshold_per_week`` and the total hours are partitioned among them.

    Args:
        kind: The :class:`WorkKind` being processed.
        bands: Bands that list ``kind`` in their ``applies_to_kinds``.
        total_hours: Hours declared for this kind in the pay period.
        hourly_base: Full-time hourly rate (base / divisor).
        as_of: Reference date for time-series rate lookups.

    Returns:
        List of ``(amount, bucket_key, label, detail)`` tuples for non-zero
        contributions.
    """
    sorted_bands = sorted(bands, key=lambda b: b.hour_threshold_per_week or 0)
    results: list[tuple[Decimal, str, str, str]] = []
    for i, band in enumerate(sorted_bands):
        band_hours = _slice_hours_for_band(i, sorted_bands, total_hours)
        if band_hours <= _ZERO:
            continue
        raw = _supplement_for_band(band, band_hours, hourly_base, as_of)
        if raw <= _ZERO:
            continue
        results.append((
            money(raw),
            _KIND_BUCKET[kind],
            band.description,
            f"{band.code}/{kind.value}",
        ))
    return results


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

    When multiple bands share the same ``applies_to_kinds`` entry they are
    partitioned by ``hour_threshold_per_week``: bands are sorted by threshold
    (ascending, ``None`` treated as 0) and each band receives the slice of
    hours between its threshold and the next band's threshold.  A single band
    per kind accumulates all hours as before.

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

    # Group bands by kind; preserve schema order within each kind.
    kind_bands: dict[WorkKind, list[OvertimeBand]] = defaultdict(list)
    for band in supplements_schema.overtime_bands:
        for kind in band.applies_to_kinds:
            kind_bands[kind].append(band)

    buckets: dict[str, Decimal] = {"overtime": _ZERO, "night": _ZERO, "holiday": _ZERO}
    trace: list[TraceStep] = []

    for kind, bands in kind_bands.items():
        total_hours = kind_to_hours.get(kind, _ZERO)
        if total_hours <= _ZERO:
            continue
        for amount, bucket, label, detail in _supplements_for_kind(
            kind, bands, total_hours, hourly_base, as_of
        ):
            buckets[bucket] += amount
            trace.append(
                TraceStep(
                    category=TraceCategory.TIME_SUPPLEMENT,
                    label=label,
                    amount=amount,
                    detail=detail,
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
