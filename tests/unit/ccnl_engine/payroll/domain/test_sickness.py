"""Unit tests for SicknessCase and SicknessCaseEvent domain types."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.errors import InvalidInputError, OutOfScopeError
from ccnl_engine.payroll.domain.events import SicknessCaseEvent
from ccnl_engine.payroll.domain.sickness import SicknessCase

_ZERO = Decimal(0)
_ONE = Decimal(1)
_START = date(2026, 1, 10)
_END = date(2026, 1, 15)


def _case(**kwargs: object) -> SicknessCase:
    defaults: dict[str, object] = {
        "episode_start": _START,
        "episode_end": _END,
        "working_days": 5,
        "waiting_period_days": 3,
        "gross_daily": Decimal("80.00"),
        "inps_daily_rate": Decimal("0.50"),
        "integration_rate": Decimal("1.00"),
    }
    defaults.update(kwargs)
    return SicknessCase(**defaults)  # type: ignore[arg-type]


class TestSicknessCaseFields:
    """SicknessCase stores all fields correctly."""

    def test_fields_stored(self) -> None:
        """All fields are stored and retrievable."""
        sc = _case()
        assert sc.episode_start == _START
        assert sc.episode_end == _END
        assert sc.working_days == 5
        assert sc.waiting_period_days == 3
        assert sc.gross_daily == Decimal("80.00")
        assert sc.inps_daily_rate == Decimal("0.50")
        assert sc.integration_rate == Decimal("1.00")
        assert sc.carenza_integration_rate == _ZERO
        assert sc.cumulative_sick_days_ytd == 0

    def test_frozen(self) -> None:
        """SicknessCase is immutable."""
        sc = _case()
        with pytest.raises(FrozenInstanceError):
            sc.working_days = 10  # type: ignore[misc]


class TestSicknessCaseValidation:
    """SicknessCase.__post_init__ enforces all constraints."""

    def test_episode_end_before_start_raises(self) -> None:
        """episode_end before episode_start raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(episode_start=date(2026, 1, 20), episode_end=date(2026, 1, 10))

    def test_working_days_zero_raises(self) -> None:
        """working_days = 0 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(working_days=0)

    def test_waiting_period_negative_raises(self) -> None:
        """Negative waiting_period_days raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(waiting_period_days=-1)

    def test_waiting_period_exceeds_working_days_raises(self) -> None:
        """waiting_period_days > working_days raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(working_days=3, waiting_period_days=5)

    def test_gross_daily_negative_raises(self) -> None:
        """Negative gross_daily raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(gross_daily=Decimal("-0.01"))

    def test_inps_rate_below_zero_raises(self) -> None:
        """inps_daily_rate below 0 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(inps_daily_rate=Decimal("-0.01"))

    def test_inps_rate_above_one_raises(self) -> None:
        """inps_daily_rate above 1 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(inps_daily_rate=Decimal("1.01"))

    def test_integration_rate_below_zero_raises(self) -> None:
        """integration_rate below 0 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(integration_rate=Decimal("-0.01"))

    def test_integration_rate_above_one_raises(self) -> None:
        """integration_rate above 1 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(integration_rate=Decimal("1.01"))

    def test_carenza_rate_below_zero_raises(self) -> None:
        """carenza_integration_rate below 0 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(carenza_integration_rate=Decimal("-0.01"))

    def test_carenza_rate_above_one_raises(self) -> None:
        """carenza_integration_rate above 1 raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(carenza_integration_rate=Decimal("1.01"))

    def test_cumulative_sick_days_negative_raises(self) -> None:
        """Negative cumulative_sick_days_ytd raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            _case(cumulative_sick_days_ytd=-1)

    def test_cumulative_sick_days_positive_raises_out_of_scope(self) -> None:
        """cumulative_sick_days_ytd > 0 raises OutOfScopeError.

        Tier-based sickness integration is not yet implemented.
        """
        with pytest.raises(OutOfScopeError):
            _case(cumulative_sick_days_ytd=1)

    def test_boundary_inps_rate_zero_accepted(self) -> None:
        """inps_daily_rate = 0 is accepted."""
        sc = _case(inps_daily_rate=_ZERO)
        assert sc.inps_daily_rate == _ZERO

    def test_boundary_inps_rate_one_accepted(self) -> None:
        """inps_daily_rate = 1 is accepted."""
        sc = _case(inps_daily_rate=_ONE)
        assert sc.inps_daily_rate == _ONE

    def test_boundary_waiting_equals_working_accepted(self) -> None:
        """waiting_period_days == working_days is accepted (all carenza)."""
        sc = _case(working_days=5, waiting_period_days=5)
        assert sc.indemnifiable_days == 0

    def test_gross_daily_zero_accepted(self) -> None:
        """gross_daily = 0 is accepted."""
        sc = _case(gross_daily=_ZERO)
        assert sc.gross_daily == _ZERO


class TestSicknessCaseProperties:
    """SicknessCase computed properties."""

    def test_indemnifiable_days_normal(self) -> None:
        """indemnifiable_days = working_days - waiting_period_days."""
        sc = _case(working_days=5, waiting_period_days=3)
        assert sc.indemnifiable_days == 2

    def test_indemnifiable_days_no_carenza(self) -> None:
        """indemnifiable_days equals working_days when no carenza."""
        sc = _case(working_days=5, waiting_period_days=0)
        assert sc.indemnifiable_days == 5

    def test_indemnifiable_days_full_carenza(self) -> None:
        """indemnifiable_days is 0 when all days are carenza."""
        sc = _case(working_days=5, waiting_period_days=5)
        assert sc.indemnifiable_days == 0

    def test_spans_multiple_months_same_month(self) -> None:
        """spans_multiple_months is False within the same month."""
        sc = _case(episode_start=date(2026, 1, 10), episode_end=date(2026, 1, 20))
        assert sc.spans_multiple_months is False

    def test_spans_multiple_months_different_month(self) -> None:
        """spans_multiple_months is True when crossing a month boundary."""
        sc = _case(
            episode_start=date(2026, 1, 25),
            episode_end=date(2026, 2, 5),
        )
        assert sc.spans_multiple_months is True

    def test_spans_multiple_months_different_year(self) -> None:
        """spans_multiple_months is True when crossing a year boundary."""
        sc = _case(
            episode_start=date(2026, 12, 29),
            episode_end=date(2027, 1, 3),
        )
        assert sc.spans_multiple_months is True

    def test_spans_multiple_months_same_day(self) -> None:
        """spans_multiple_months is False for a single-day episode."""
        sc = _case(
            episode_start=date(2026, 3, 15),
            episode_end=date(2026, 3, 15),
            working_days=1,
            waiting_period_days=0,
        )
        assert sc.spans_multiple_months is False


class TestSicknessCaseEvent:
    """SicknessCaseEvent validation."""

    def _sickness_case(self) -> SicknessCase:
        return _case(
            episode_start=date(2026, 1, 10),
            episode_end=date(2026, 1, 15),
        )

    def test_valid_event(self) -> None:
        """SicknessCaseEvent is constructed successfully when event_date matches."""
        case = self._sickness_case()
        evt = SicknessCaseEvent(event_date=date(2026, 1, 10), case=case)
        assert evt.event_date == date(2026, 1, 10)
        assert evt.case is case

    def test_event_date_before_episode_start_raises(self) -> None:
        """event_date < case.episode_start raises InvalidInputError."""
        case = self._sickness_case()
        with pytest.raises(InvalidInputError):
            SicknessCaseEvent(event_date=date(2026, 1, 9), case=case)

    def test_event_date_after_episode_start_accepted(self) -> None:
        """event_date > case.episode_start is accepted (multi-period episode)."""
        case = self._sickness_case()
        evt = SicknessCaseEvent(event_date=date(2026, 1, 11), case=case)
        assert evt.event_date == date(2026, 1, 11)

    def test_frozen(self) -> None:
        """SicknessCaseEvent is immutable."""
        case = self._sickness_case()
        evt = SicknessCaseEvent(event_date=date(2026, 1, 10), case=case)
        with pytest.raises(FrozenInstanceError):
            evt.event_date = date(2026, 1, 12)  # type: ignore[misc]
