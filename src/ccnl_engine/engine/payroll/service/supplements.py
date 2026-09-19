"""Layer 3 time-supplement computation service."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import TimeSupplementKind, WorkKind
from ccnl_engine.engine.payroll.domain.calculation import TraceCategory, TraceStep
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from collections.abc import Sequence
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

    Thresholds are normalised relative to the first band's threshold so that
    a leading non-zero value (e.g. 40 = standard weekly hours) is treated as
    the origin.  ``total_hours`` represents overtime hours already in excess of
    the ordinary schedule, so subtracting the base threshold before partitioning
    gives the correct slice for each band.

    Args:
        band_index: Index of the current band in ``sorted_bands``.
        sorted_bands: Bands sorted ascending by ``hour_threshold_per_week``.
        total_hours: Overtime hours for this work kind (already in excess of
            the ordinary schedule).

    Returns:
        Hours in the half-open interval assigned to this band.
    """
    base = Decimal(sorted_bands[0].hour_threshold_per_week or 0)
    lo = Decimal(sorted_bands[band_index].hour_threshold_per_week or 0) - base
    if band_index + 1 < len(sorted_bands):
        hi = Decimal(sorted_bands[band_index + 1].hour_threshold_per_week or 0) - base
        return max(_ZERO, min(total_hours, hi) - lo)
    return max(_ZERO, total_hours - lo)


def _supplements_for_kind(
    kind: WorkKind,
    bands: list[OvertimeBand],
    total_hours: Decimal,
    hourly_base: Decimal,
    as_of: date,
    weekly_hours: Sequence[Decimal] | None = None,
    kind_to_hours: dict[WorkKind, Decimal] | None = None,
) -> list[tuple[Decimal, str, str, str]]:
    """Compute (amount, bucket, label, detail) entries for one work kind.

    When ``bands`` contains multiple entries they are sorted by
    ``hour_threshold_per_week`` and hours are partitioned among them.

    When ``weekly_hours`` is provided, each entry represents one calendar
    week.  Band-hours are accumulated across all weeks before computing
    money, so the rounding behaviour is identical to the single-period
    path and trace step counts remain the same.

    When ``weekly_hours`` is ``None`` (default), ``total_hours`` is
    treated as a single period (the whole month as one week).  This is
    correct for single-band CCNLs but overstates the higher bands for
    CCNLs with per-week hour caps; prefer supplying ``weekly_hours`` for
    those contracts.

    Bands with non-empty ``required_context_kinds`` are skipped unless all
    of those kinds have non-zero hours in ``kind_to_hours``.

    Args:
        kind: The :class:`WorkKind` being processed.
        bands: Bands that list ``kind`` in their ``applies_to_kinds``.
        total_hours: Monthly hours declared for this kind (used when
            ``weekly_hours`` is ``None`` or as the skip guard otherwise).
        hourly_base: Full-time hourly rate (base / divisor).
        as_of: Reference date for time-series rate lookups.
        weekly_hours: Per-week hour list, or ``None`` for the monthly path.
        kind_to_hours: Full map of declared hours per kind, for conditional
            band evaluation.

    Returns:
        List of ``(amount, bucket_key, label, detail)`` tuples for non-zero
        contributions.
    """
    ctx = kind_to_hours or {}
    eligible = [
        b for b in bands
        if not b.required_context_kinds
        or all(ctx.get(rk, _ZERO) > _ZERO for rk in b.required_context_kinds)
    ]
    sorted_bands = sorted(eligible, key=lambda b: b.hour_threshold_per_week or 0)
    hours_periods: Sequence[Decimal] = (
        weekly_hours if weekly_hours is not None else [total_hours]
    )
    results: list[tuple[Decimal, str, str, str]] = []
    for i, band in enumerate(sorted_bands):
        # Accumulate band-hours across all periods, then round once.
        band_hours: Decimal = _ZERO
        for h in hours_periods:
            band_hours += _slice_hours_for_band(i, sorted_bands, h)
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


def _build_weekly_kind_hours(
    supps_input: OvertimeHours,
) -> dict[WorkKind, list[Decimal]] | None:
    """Return per-kind weekly-hour lists, or ``None`` when no weeks supplied.

    Returns:
        Mapping of :class:`WorkKind` to per-week hour lists, or ``None`` when
        :attr:`OvertimeHours.weeks` is empty.
    """
    if not supps_input.weeks:
        return None
    return {
        WorkKind.WEEKDAY: [w.weekday_hours for w in supps_input.weeks],
        WorkKind.NIGHT: [w.night_hours for w in supps_input.weeks],
        WorkKind.HOLIDAY: [w.holiday_hours for w in supps_input.weeks],
        WorkKind.NIGHT_HOLIDAY: [w.night_holiday_hours for w in supps_input.weeks],
        WorkKind.SUPPLEMENTARE: [w.supplementare_hours for w in supps_input.weeks],
    }


def _group_bands_by_kind(
    supplements_schema: TimeSupplements,
) -> dict[WorkKind, list[OvertimeBand]]:
    """Group overtime bands by their applicable :class:`WorkKind`.

    Preserves schema order within each kind so that per-CCNL band order is
    stable before the threshold sort inside :func:`_supplements_for_kind`.

    Returns:
        Mapping of :class:`WorkKind` to the list of bands that apply to it.
    """
    kind_bands: dict[WorkKind, list[OvertimeBand]] = defaultdict(list)
    for band in supplements_schema.overtime_bands:
        for kind in band.applies_to_kinds:
            kind_bands[kind].append(band)
    return kind_bands


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

    **Per-week mode**: when :attr:`~OvertimeHours.weeks` is non-empty each
    week is processed through the band thresholds independently.
    Band-hours are accumulated across all weeks before money is computed,
    keeping rounding identical to the single-period path.

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

    weekly_kind_hours = _build_weekly_kind_hours(supps_input)
    kind_bands = _group_bands_by_kind(supplements_schema)

    buckets: dict[str, Decimal] = {"overtime": _ZERO, "night": _ZERO, "holiday": _ZERO}
    trace: list[TraceStep] = []

    for kind, bands in kind_bands.items():
        total_hours = kind_to_hours.get(kind, _ZERO)
        if total_hours <= _ZERO:
            continue
        weekly = weekly_kind_hours[kind] if weekly_kind_hours is not None else None
        for amount, bucket, label, detail in _supplements_for_kind(
            kind, bands, total_hours, hourly_base, as_of, weekly, kind_to_hours
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
