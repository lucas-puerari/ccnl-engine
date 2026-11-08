"""Confetra sixth-month leave: (2400 + 2 * 2400 / 12) / 30 = 93.333333 daily."""

from datetime import date
from decimal import Decimal

from ccnl_engine.absence.insured.parental.inputs import (
    ParentalLeaveEvent,
    ParentalLeaveTaken,
)
from ccnl_engine.events import InpsSicknessBase
from ccnl_engine.period.results import PeriodResult

from .test_handlers import _amounts, _run


def _leave(
    start: int, taken: ParentalLeaveTaken, *, end: date | None = date(2025, 12, 31)
) -> ParentalLeaveEvent:
    return ParentalLeaveEvent(
        date(2026, 1, start),
        date(2026, 1, 31),
        date(2025, 9, 1),
        taken,
        end,
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
    )


def _confetra(leave: ParentalLeaveEvent) -> PeriodResult:
    return _run(
        leave,
        ccnl_id="logistica-trasporto-confetra",
        level_code="3",
        year=2026,
        month=1,
    )


def test_first_day_at_standard_inps_rate() -> None:
    """Jan 1-30: 30 * (50%-30%) * 93.333333 = 560.00; Jan 31 adds zero."""
    result = _confetra(_leave(1, ParentalLeaveTaken(0, 90, 0)))
    assert _amounts(result)["absence_integration_item"] == ("intg", Decimal("560.00"))
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("868.00"))
    assert "insured_absence_ccnl_not_modelled" not in {i.code for i in result.issues}


def test_first_day_at_enhanced_inps_rate() -> None:
    """31 * 80% * 93.333333 = 2314.67; INPS exceeds the 50% target."""
    result = _confetra(_leave(1, ParentalLeaveTaken(0, 0, 0)))
    assert "absence_integration_item" not in _amounts(result)
    assert _amounts(result)["maternity_item"] == ("inps", Decimal("2314.67"))


def test_later_start_and_unknown_end() -> None:
    """Jan 11-30: 20 * 20% * 93.333333 = 373.33; unknown end pays zero."""
    leave = _leave(11, ParentalLeaveTaken(0, 90, 0))
    result = _confetra(leave)
    assert _amounts(result)["absence_integration_item"] == ("intg", Decimal("373.33"))
    unknown = _confetra(_leave(11, ParentalLeaveTaken(0, 90, 0), end=None))
    assert "absence_integration_item" not in _amounts(unknown)
    assert ("parental_sixth_month_end_unknown", "protection_ended_on") in {
        (i.code, i.fact) for i in unknown.issues
    }


def test_unknown_end_outside_possible_window() -> None:
    """A leave a year after birth cannot be in the thirty-day sixth-month window."""
    leave = ParentalLeaveEvent(
        date(2026, 9, 1),
        date(2026, 9, 10),
        date(2025, 9, 1),
        ParentalLeaveTaken(0, 90, 0),
        parental_base_pay=InpsSicknessBase(Decimal(2400), Decimal(0)),
    )
    result = _run(
        leave, ccnl_id="logistica-trasporto-confetra", level_code="3", month=9
    )
    assert "parental_sixth_month_end_unknown" not in {i.code for i in result.issues}
