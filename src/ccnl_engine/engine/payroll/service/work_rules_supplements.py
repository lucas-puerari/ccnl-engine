"""Supplements handler: overtime, night, and holiday time supplements."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.contract.domain.ccnl import WorkKind
from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.payroll.service.supplements import compute_time_supplements

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import CCNL, OvertimeBand
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.domain.calculation import TraceStep
    from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours

_ZERO = Decimal(0)


@dataclass(frozen=True)
class _SupplementsResult:
    overtime: Decimal
    night: Decimal
    holiday: Decimal
    trace: tuple[TraceStep, ...]
    overtime_supported: bool
    night_supported: bool
    holiday_supported: bool


def _kind_supported(bands: Sequence[OvertimeBand], *kinds: WorkKind) -> bool:
    """Return True when any band in *bands* applies to at least one of *kinds*.

    Returns:
        ``True`` if a matching band exists, ``False`` otherwise.
    """
    return any(k in b.applies_to_kinds for b in bands for k in kinds)


def _warn_missing_kind_bands(
    bands: Sequence[OvertimeBand],
    kind_hours: dict[WorkKind, Decimal],
    warnings: list[str],
) -> None:
    """Append a warning for each work kind that has positive hours but no band."""
    for kind, hours in kind_hours.items():
        if hours > _ZERO and not _kind_supported(bands, kind):
            warnings.append(f"{kind.value} hours declared but not covered by any band")


def _kinds_with_tiered_weekly_bands(
    bands: Sequence[OvertimeBand],
) -> set[WorkKind]:
    """Return kinds that have tiered weekly bands (threshold-partitioned).

    Returns:
        Set of :class:`WorkKind` values that have two or more tiered bands.
    """
    kinds_with_threshold: set[WorkKind] = set()
    for band in bands:
        if band.hour_threshold_per_week is not None:
            kinds_with_threshold.update(band.applies_to_kinds)
    return kinds_with_threshold


def _warn_tiered_bands_without_weeks(
    bands: Sequence[OvertimeBand],
    ts: OvertimeHours,
    kind_hours: dict[WorkKind, Decimal],
    wr_warnings: list[str],
) -> None:
    """Append a warning when tiered per-week bands exist but no weeks supplied."""
    if ts.weeks:
        return
    tiered = _kinds_with_tiered_weekly_bands(bands)
    active_tiered = {k for k in tiered if kind_hours.get(k, _ZERO) > _ZERO}
    if not active_tiered:
        return
    names = ", ".join(sorted(k.value for k in active_tiered))
    wr_warnings.append(
        f"CCNL defines tiered weekly thresholds for {names}; "
        "provide OvertimeHours.weeks for accurate per-week "
        "band partitioning"
    )


def _run_wr_supplements(
    scenario: _InternalScenario,
    ccnl: CCNL,
    base_monthly_full_time: Decimal,
    hourly_divisor: Decimal,
    as_of: date,
    wr_warnings: list[str],
) -> _SupplementsResult:
    """Run the work-rules time-supplement block.

    Returns:
        :class:`_SupplementsResult` with zero amounts and ``False`` support
        flags when the CCNL has no work-rules schema or no hours were supplied.

    Raises:
        OutOfScopeError: If any hours are requested but the CCNL has no
            time_supplements schema.
        RuntimeError: If ``work_rules`` or ``time_supplements`` is ``None``
            despite ``wr_schema_present=True`` (indicates a data bug).
    """
    ts_input = scenario.time_supplements
    wr_schema_present = (
        ccnl.work_rules is not None and ccnl.work_rules.time_supplements is not None
    )
    zero_result = _SupplementsResult(
        overtime=_ZERO,
        night=_ZERO,
        holiday=_ZERO,
        trace=(),
        overtime_supported=False,
        night_supported=False,
        holiday_supported=False,
    )
    if ts_input is None:
        return zero_result
    if (
        ts_input.weekday_hours
        + ts_input.supplementare_hours
        + ts_input.night_hours
        + ts_input.holiday_hours
        + ts_input.night_holiday_hours
    ) == _ZERO:
        return zero_result
    if not wr_schema_present:
        msg = "time_supplements requested but not modelled for this CCNL"
        raise OutOfScopeError(msg, feature="overtime", reason="no_schema")
    work_rules_ts = ccnl.work_rules
    if (  # pragma: no cover
        work_rules_ts is None or work_rules_ts.time_supplements is None
    ):
        msg = "time_supplements is None despite wr_schema_present=True"
        raise RuntimeError(msg)
    ts_schema = work_rules_ts.time_supplements
    if ts_schema.hourly_base_method == "gross_incl_allowances":
        wr_warnings.append(
            "hourly_base_method='gross_incl_allowances' is not yet"
            " implemented; time supplements cannot be computed"
        )
        return _SupplementsResult(
            overtime=_ZERO,
            night=_ZERO,
            holiday=_ZERO,
            trace=(),
            overtime_supported=False,
            night_supported=False,
            holiday_supported=False,
        )
    bands = ts_schema.overtime_bands
    ts = ts_input
    kind_hours: dict[WorkKind, Decimal] = {
        WorkKind.WEEKDAY: ts.weekday_hours,
        WorkKind.SUPPLEMENTARE: ts.supplementare_hours,
        WorkKind.NIGHT: ts.night_hours,
        WorkKind.HOLIDAY: ts.holiday_hours,
        WorkKind.NIGHT_HOLIDAY: ts.night_holiday_hours,
    }
    _warn_missing_kind_bands(bands, kind_hours, wr_warnings)
    _warn_tiered_bands_without_weeks(bands, ts, kind_hours, wr_warnings)
    wd_uncovered = ts.weekday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.WEEKDAY
    )
    sl_uncovered = ts.supplementare_hours > _ZERO and not _kind_supported(
        bands, WorkKind.SUPPLEMENTARE
    )
    ho_uncovered = ts.holiday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.HOLIDAY
    )
    nh_uncovered = ts.night_holiday_hours > _ZERO and not _kind_supported(
        bands, WorkKind.NIGHT_HOLIDAY
    )
    overtime_supported = (
        _kind_supported(bands, WorkKind.WEEKDAY, WorkKind.SUPPLEMENTARE)
        and not wd_uncovered
        and not sl_uncovered
    )
    night_supported = _kind_supported(bands, WorkKind.NIGHT)
    holiday_supported = (
        _kind_supported(bands, WorkKind.HOLIDAY, WorkKind.NIGHT_HOLIDAY)
        and not ho_uncovered
        and not nh_uncovered
    )
    overtime, night, holiday, trace = compute_time_supplements(
        supps_input=ts_input,
        supplements_schema=ts_schema,
        base_monthly_full_time=base_monthly_full_time,
        hourly_divisor=hourly_divisor,
        as_of=as_of,
    )
    return _SupplementsResult(
        overtime=overtime,
        night=night,
        holiday=holiday,
        trace=trace,
        overtime_supported=overtime_supported,
        night_supported=night_supported,
        holiday_supported=holiday_supported,
    )
