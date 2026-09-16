"""Unit tests for compute_time_supplements service function."""

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.ccnl import (
    OvertimeBand,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.payroll.domain.calculation import TraceCategory
from ccnl_engine.engine.payroll.domain.supplements import (
    OvertimeHours,
    WeeklyOvertimeHours,
)
from ccnl_engine.engine.payroll.service.rounding import money as _money
from ccnl_engine.engine.payroll.service.supplements import (
    _slice_hours_for_band,
    _supplement_for_band,
    _supplements_for_kind,
    compute_time_supplements,
)

_AS_OF = date(2026, 9, 1)
_BASE = Decimal("2064.88")
_DIVISOR = Decimal(173)
_ZERO = Decimal(0)


def _ts(value: str) -> TimeSeries:
    """Build a single-period TimeSeries with the given value.

    Returns:
        A TimeSeries with one period valid from 2020-01-01.
    """
    return TimeSeries(
        periods=(
            ValidityPeriod(
                valid_from=date(2020, 1, 1),
                valid_until=None,
                value=Decimal(value),
            ),
        )
    )


def _band(
    code: str,
    kind: str,
    rate: str,
    applies_to: list[str],
) -> OvertimeBand:
    """Build an OvertimeBand without provenance fields.

    Returns:
        An OvertimeBand for unit tests.
    """
    return OvertimeBand(
        code=code,
        description=code,
        kind=TimeSupplementKind(kind),
        rate=_ts(rate),
        applies_to_kinds=[WorkKind(k) for k in applies_to],  # type: ignore[arg-type]
    )


@pytest.fixture
def schema() -> TimeSupplements:
    """Return a TimeSupplements schema with three percentage bands.

    Returns:
        A TimeSupplements with weekday/night/holiday percentage bands.
    """
    return TimeSupplements(
        hourly_base_method="minimo_tabellare",
        overtime_bands=[  # type: ignore[arg-type]
            _band("OT_DIURNO", "percentage", "0.15", ["weekday"]),
            _band("OT_NOTTURNO", "percentage", "0.20", ["night"]),
            _band("OT_FESTIVO", "percentage", "0.30", ["holiday"]),
        ],
    )


class TestComputeTimeSupplements:
    """Pure-math tests for compute_time_supplements."""

    def test_zero_hours_all_zero(self, schema: TimeSupplements) -> None:
        """Zero input hours produce zero output."""
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(), schema, _BASE, _DIVISOR, _AS_OF
        )
        assert ot == _ZERO
        assert ni == _ZERO
        assert ho == _ZERO
        assert steps == ()

    def test_weekday_only(self, schema: TimeSupplements) -> None:
        """10 weekday OT hours at 15%: 10 * 0.15 * (2064.88/173) = 17.90."""
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(weekday_hours=Decimal(10)),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == Decimal("17.90")
        assert ni == _ZERO
        assert ho == _ZERO
        assert len(steps) == 2  # 1 band step + SUPPLEMENT_TOTAL
        assert steps[0].category == TraceCategory.TIME_SUPPLEMENT
        assert steps[-1].category == TraceCategory.SUPPLEMENT_TOTAL
        assert steps[-1].amount == Decimal("17.90")

    def test_night_only(self, schema: TimeSupplements) -> None:
        """5 night hours at 20%: 5 * 0.20 * (2064.88/173) = 11.94."""
        ot, ni, ho, _steps = compute_time_supplements(
            OvertimeHours(night_hours=Decimal(5)),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == _ZERO
        assert ni == Decimal("11.94")
        assert ho == _ZERO

    def test_holiday_only(self, schema: TimeSupplements) -> None:
        """2 holiday hours at 30%: 2 * 0.30 * (2064.88/173) = 7.16."""
        ot, ni, ho, _steps = compute_time_supplements(
            OvertimeHours(holiday_hours=Decimal(2)),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == _ZERO
        assert ni == _ZERO
        assert ho == Decimal("7.16")

    def test_mixed_accumulates(self, schema: TimeSupplements) -> None:
        """All three bands accumulate when all hour types are non-zero."""
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(
                weekday_hours=Decimal(4),
                night_hours=Decimal(3),
                holiday_hours=Decimal(2),
            ),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == Decimal("7.16")
        assert ni == Decimal("7.16")
        assert ho == Decimal("7.16")
        total_step = steps[-1]
        assert total_step.category == TraceCategory.SUPPLEMENT_TOTAL
        assert total_step.amount == Decimal("21.48")

    def test_indennita_per_hour_band(self) -> None:
        """An indennita_per_hour band uses rate * hours directly."""
        schema_indennita = TimeSupplements(
            overtime_bands=[  # type: ignore[arg-type]
                _band("NOTTE_INDENNITA", "indennita_per_hour", "5.00", ["night"])
            ]
        )
        _ot, ni, _ho, _steps = compute_time_supplements(
            OvertimeHours(night_hours=Decimal(4)),
            schema_indennita,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ni == Decimal("20.00")  # 4h * EUR 5.00

    def test_indennita_per_shift_band(self) -> None:
        """An indennita_per_shift band uses rate * count directly."""
        schema_shift = TimeSupplements(
            overtime_bands=[  # type: ignore[arg-type]
                _band("SHIFT_NOTTE", "indennita_per_shift", "10.00", ["night"])
            ]
        )
        _ot, ni, _ho, _steps = compute_time_supplements(
            OvertimeHours(night_hours=Decimal(3)),
            schema_shift,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ni == Decimal("30.00")  # 3 shifts * EUR 10.00

    def test_supplementare_counts_toward_overtime(self) -> None:
        """supplementare_hours accumulate into the overtime total."""
        supps_schema = TimeSupplements(
            overtime_bands=[_band("SUPPL", "percentage", "0.10", ["supplementare"])]  # type: ignore[arg-type]
        )
        ot, ni, ho, _steps = compute_time_supplements(
            OvertimeHours(supplementare_hours=Decimal(8)),
            supps_schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        # 8 * 0.10 * (2064.88 / 173) = 9.55...
        assert ot > _ZERO
        assert ni == _ZERO
        assert ho == _ZERO

    def test_empty_bands_produces_no_steps(self) -> None:
        """A schema with no bands produces empty steps."""
        ot, _ni, _ho, steps = compute_time_supplements(
            OvertimeHours(weekday_hours=Decimal(10)),
            TimeSupplements(overtime_bands=[]),  # type: ignore[arg-type]
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == _ZERO
        assert steps == ()

    def test_band_with_zero_hours_returns_zero_directly(self) -> None:
        """_supplement_for_band returns zero when hours is zero (internal guard)."""
        band = _band("OT_DIURNO", "percentage", "0.15", ["weekday"])
        result = _supplement_for_band(band, _ZERO, _BASE / _DIVISOR, _AS_OF)
        assert result == _ZERO

    def test_night_holiday_counts_toward_holiday_bucket(self) -> None:
        """night_holiday_hours accumulate into the holiday bucket."""
        schema_nh = TimeSupplements(
            overtime_bands=[  # type: ignore[arg-type]
                _band("OT_FEST_NOTT", "percentage", "0.85", ["night_holiday"])
            ]
        )
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(night_holiday_hours=Decimal(2)),
            schema_nh,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        # 2 * 0.85 * (2064.88 / 173) ≈ 20.29
        assert ho == Decimal("20.29")
        assert ot == _ZERO
        assert ni == _ZERO
        assert steps[-1].category == TraceCategory.SUPPLEMENT_TOTAL

    def test_zero_rate_band_is_skipped(self) -> None:
        """A band with rate=0 produces no supplement and no trace step."""
        schema_zero = TimeSupplements(
            overtime_bands=[_band("OT_ZERO", "percentage", "0.00", ["weekday"])]  # type: ignore[arg-type]
        )
        ot, _ni, _ho, steps = compute_time_supplements(
            OvertimeHours(weekday_hours=Decimal(10)),
            schema_zero,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        assert ot == _ZERO
        assert steps == ()  # zero raw -> skipped, no SUPPLEMENT_TOTAL either


def _band_with_threshold(
    code: str,
    rate: str,
    applies_to: list[str],
    threshold: int | None = None,
) -> OvertimeBand:
    """Build an OvertimeBand with an optional weekly hour threshold.

    Returns:
        An OvertimeBand for unit tests.
    """
    return OvertimeBand(
        code=code,
        description=code,
        kind=TimeSupplementKind("percentage"),
        rate=TimeSeries(
            periods=(
                ValidityPeriod(
                    valid_from=date(2020, 1, 1),
                    valid_until=None,
                    value=Decimal(rate),
                ),
            )
        ),
        applies_to_kinds=[WorkKind(k) for k in applies_to],  # type: ignore[arg-type]
        hour_threshold_per_week=threshold,
    )


class TestSliceHoursForBand:
    """_slice_hours_for_band partitions hours by weekly threshold."""

    def test_single_band_gets_all_hours(self) -> None:
        """One band with no threshold receives all hours."""
        bands = [_band_with_threshold("B1", "0.15", ["weekday"])]
        result = _slice_hours_for_band(0, bands, Decimal(10))
        assert result == Decimal(10)

    def test_first_band_capped_at_next_threshold(self) -> None:
        """First band (threshold=0) receives min(total, next_threshold)."""
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=4),
        ]
        result = _slice_hours_for_band(0, bands, Decimal(10))
        assert result == Decimal(4)  # min(10, 4) - 0

    def test_last_band_gets_remainder(self) -> None:
        """Second band (threshold=4) receives max(0, total - 4)."""
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=4),
        ]
        result = _slice_hours_for_band(1, bands, Decimal(10))
        assert result == Decimal(6)  # 10 - 4

    def test_hours_below_last_band_threshold_returns_zero(self) -> None:
        """Total hours below last band's threshold: last band gets zero."""
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=8),
        ]
        result = _slice_hours_for_band(1, bands, Decimal(5))
        assert result == _ZERO  # max(0, 5 - 8) = 0


class TestSupplementsForKind:
    """_supplements_for_kind returns correct (amount, bucket, label, detail) entries."""

    def test_single_band_returns_one_entry(self) -> None:
        """One band: returns one tuple with correct values."""
        bands = [_band_with_threshold("OT", "0.15", ["weekday"])]
        hourly_base = _BASE / _DIVISOR
        results = _supplements_for_kind(
            WorkKind.WEEKDAY, bands, Decimal(10), hourly_base, _AS_OF
        )
        assert len(results) == 1
        _amount, bucket, label, detail = results[0]
        assert bucket == "overtime"
        assert label == "OT"
        assert "weekday" in detail

    def test_two_bands_partitioned_by_threshold(self) -> None:
        """Two bands at 15%/20% with threshold=4: hours are split, not summed.

        10 weekday hours: band1 (15%, hrs 0-4) + band2 (20%, hrs 4-10).
        hourly_base = 2064.88 / 173
        band1: 4 * 0.15 * hourly_base
        band2: 6 * 0.20 * hourly_base
        Total = (0.60 + 1.20) * hourly_base — not (0.15+0.20)*10*hourly_base.
        """
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=4),
        ]
        hourly_base = _BASE / _DIVISOR
        results = _supplements_for_kind(
            WorkKind.WEEKDAY, bands, Decimal(10), hourly_base, _AS_OF
        )
        assert len(results) == 2
        amount1 = results[0][0]
        amount2 = results[1][0]
        # Verify band2 is larger (6 hrs at 20%) than band1 (4 hrs at 15%)
        assert amount2 > amount1

    def test_hours_below_threshold_skips_last_band(self) -> None:
        """Total hours below last band's threshold: last band produces no entry."""
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=8),
        ]
        hourly_base = _BASE / _DIVISOR
        results = _supplements_for_kind(
            WorkKind.WEEKDAY, bands, Decimal(5), hourly_base, _AS_OF
        )
        assert len(results) == 1  # only B1 (5 hrs), B2 gets 0 hrs


class TestComputeTimeSupplementsTieredBands:
    """compute_time_supplements with threshold-partitioned weekday bands."""

    def test_two_tiered_weekday_bands_partitioned(self) -> None:
        """Two weekday bands at 15%/20% with threshold=4: hours partitioned, not summed.

        10 weekday hrs: band1 (15%) gets 4 hrs, band2 (20%) gets 6 hrs.
        hourly_base = 2064.88 / 173 = 11.9358...
        band1: 4 * 0.15 * hourly_base = 7.16
        band2: 6 * 0.20 * hourly_base = 14.32 (approx)
        total overtime = money(7.16 + 14.32) vs wrong sum = (0.15+0.20)*10*hourly_base
        """
        schema = TimeSupplements(
            hourly_base_method="minimo_tabellare",
            overtime_bands=[  # type: ignore[arg-type]
                _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
                _band_with_threshold("B2", "0.20", ["weekday"], threshold=4),
            ],
        )
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(weekday_hours=Decimal(10)),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        # With partitioning: 4*0.15 + 6*0.20 = 0.60+1.20 = 1.80 * hourly_base
        # Wrong sum: (0.15+0.20)*10 = 3.50 * hourly_base
        hourly_base = _BASE / _DIVISOR
        expected = (
            Decimal(4) * Decimal("0.15") * hourly_base
            + Decimal(6) * Decimal("0.20") * hourly_base
        )

        assert ot == _money(expected)
        assert ni == _ZERO
        assert ho == _ZERO
        assert len(steps) == 3  # B1 + B2 + total


class TestHighBaseThresholdNormalisation:
    """_slice_hours_for_band normalises thresholds relative to the first band."""

    def test_single_band_with_high_threshold_gets_all_overtime_hours(self) -> None:
        """One band with threshold=40 receives all overtime hours unchanged.

        The threshold represents the standard weekly schedule (40 h/week),
        not an offset within overtime.  All hours in OvertimeHours are already
        in excess of that schedule, so the full 8 h are usable.
        """
        bands = [_band_with_threshold("B1", "0.15", ["weekday"], threshold=40)]
        result = _slice_hours_for_band(0, bands, Decimal(8))
        assert result == Decimal(8)

    def test_two_bands_with_high_base_threshold_normalised(self) -> None:
        """Two bands with thresholds 40/48: normalised to 0/8 for overtime hours."""
        bands = [
            _band_with_threshold("B1", "0.15", ["weekday"], threshold=40),
            _band_with_threshold("B2", "0.20", ["weekday"], threshold=48),
        ]
        # 10 overtime hours: band1 gets min(10, 8)-0=8, band2 gets 10-8=2
        assert _slice_hours_for_band(0, bands, Decimal(10)) == Decimal(8)
        assert _slice_hours_for_band(1, bands, Decimal(10)) == Decimal(2)

    def test_high_threshold_single_band_integrates_with_compute(self) -> None:
        """A band with threshold=40 computes the correct supplement via full stack.

        Without normalisation the 8 overtime hours would be zeroed out
        because max(0, 8-40) = 0.
        """
        schema = TimeSupplements(
            hourly_base_method="minimo_tabellare",
            overtime_bands=[  # type: ignore[arg-type]
                _band_with_threshold("B40", "0.15", ["weekday"], threshold=40)
            ],
        )
        ot, ni, ho, steps = compute_time_supplements(
            OvertimeHours(weekday_hours=Decimal(8)),
            schema,
            _BASE,
            _DIVISOR,
            _AS_OF,
        )
        hourly_base = _BASE / _DIVISOR
        expected = _money(Decimal(8) * Decimal("0.15") * hourly_base)
        assert ot == expected
        assert ni == _ZERO
        assert ho == _ZERO
        assert len(steps) == 2  # 1 band + SUPPLEMENT_TOTAL


class TestComputeTimeSupplementsWeeklyBreakdown:
    """compute_time_supplements with per-week OvertimeHours.weeks breakdown."""

    def test_weekly_breakdown_with_tiered_bands(self) -> None:
        """Weekly path partitions each week independently then sums.

        Two weekday bands: B1 (15%, 0-4 h/week), B2 (20%, 4+ h/week).
        Two weeks: W1 = 6 h (B1: 4h, B2: 2h), W2 = 3 h (B1: 3h, B2: 0h).
        Monthly total = 9 h.  Total per band: B1 = 7 h, B2 = 2 h.

        Compare to monthly-only path (treats 9 h as one week):
        Monthly-only: B1 = 4 h, B2 = 5 h — overstates B2.
        """
        schema = TimeSupplements(
            hourly_base_method="minimo_tabellare",
            overtime_bands=[  # type: ignore[arg-type]
                _band_with_threshold("B1", "0.15", ["weekday"], threshold=None),
                _band_with_threshold("B2", "0.20", ["weekday"], threshold=4),
            ],
        )
        oh = OvertimeHours.from_weeks((
            WeeklyOvertimeHours(weekday_hours=Decimal(6)),
            WeeklyOvertimeHours(weekday_hours=Decimal(3)),
        ))
        ot, ni, ho, steps = compute_time_supplements(
            oh, schema, _BASE, _DIVISOR, _AS_OF
        )
        hourly_base = _BASE / _DIVISOR
        # B1 receives 7 h (4 from W1 + 3 from W2), B2 receives 2 h (2 from W1).
        # money() is applied once per band, then once more at bucket level.
        b1_amount = _money(Decimal(7) * Decimal("0.15") * hourly_base)
        b2_amount = _money(Decimal(2) * Decimal("0.20") * hourly_base)
        expected = _money(b1_amount + b2_amount)
        assert ot == expected
        assert ni == _ZERO
        assert ho == _ZERO
        assert len(steps) == 3  # B1 + B2 + SUPPLEMENT_TOTAL

    def test_weekly_path_single_band_same_as_monthly(self) -> None:
        """With one band, weekly and monthly paths produce the same result."""
        schema = TimeSupplements(
            hourly_base_method="minimo_tabellare",
            overtime_bands=[  # type: ignore[arg-type]
                _band_with_threshold("B1", "0.15", ["weekday"]),
            ],
        )
        total = Decimal(10)
        oh_monthly = OvertimeHours(weekday_hours=total)
        oh_weekly = OvertimeHours.from_weeks((
            WeeklyOvertimeHours(weekday_hours=Decimal(4)),
            WeeklyOvertimeHours(weekday_hours=Decimal(6)),
        ))
        ot_m, _, _, _ = compute_time_supplements(
            oh_monthly, schema, _BASE, _DIVISOR, _AS_OF
        )
        ot_w, _, _, _ = compute_time_supplements(
            oh_weekly, schema, _BASE, _DIVISOR, _AS_OF
        )
        assert ot_m == ot_w
