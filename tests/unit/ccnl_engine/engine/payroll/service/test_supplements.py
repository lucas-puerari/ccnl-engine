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
from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
from ccnl_engine.engine.payroll.service.supplements import (
    _supplement_for_band,
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
        periods=[
            ValidityPeriod(
                valid_from=date(2020, 1, 1),
                valid_until=None,
                value=Decimal(value),
            )
        ]
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
        applies_to_kinds=[WorkKind(k) for k in applies_to],
    )


@pytest.fixture
def schema() -> TimeSupplements:
    """Return a TimeSupplements schema with three percentage bands.

    Returns:
        A TimeSupplements with weekday/night/holiday percentage bands.
    """
    return TimeSupplements(
        hourly_base_method="minimo_tabellare",
        overtime_bands=[
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
            overtime_bands=[
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
            overtime_bands=[
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
            overtime_bands=[_band("SUPPL", "percentage", "0.10", ["supplementare"])]
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
            TimeSupplements(overtime_bands=[]),
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
            overtime_bands=[
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
            overtime_bands=[_band("OT_ZERO", "percentage", "0.00", ["weekday"])]
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
