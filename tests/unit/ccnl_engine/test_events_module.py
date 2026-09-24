"""Smoke tests for the stable ccnl_engine.events public module."""

from __future__ import annotations

import ccnl_engine.events as events_mod


def test_events_module_exports_all_event_types() -> None:
    """Every event type listed in __all__ must be importable from ccnl_engine.events."""
    expected = {
        "AbsenceEvent",
        "ArrearsEvent",
        "BilateralFundEvent",
        "BonusEvent",
        "FringeEvent",
        "HolidayWorkEvent",
        "NightShiftEvent",
        "OvertimeEvent",
        "SickLeaveEvent",
        "SicknessCaseEvent",
        "TerminationTFREvent",
        "WelfareEvent",
        "WorkEvent",
    }
    assert set(events_mod.__all__) == expected
    for name in events_mod.__all__:
        assert hasattr(events_mod, name), f"Missing from ccnl_engine.events: {name}"
