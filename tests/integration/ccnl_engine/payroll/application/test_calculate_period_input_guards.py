"""Guards of calculate_period: event dates, policy resolution, reconciliation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application import reconcile as _reconcile_mod
from ccnl_engine.payroll.application._period_utils import _require_resolution
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import (
    ReconciliationResult,
    ReconciliationViolation,
)
from ccnl_engine.payroll.domain.events import AbsenceEvent, ArrearsEvent, OvertimeEvent
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.policy import PolicyContext
from ccnl_engine.payroll.service.policy_loader import load_policy_resolver
from ccnl_engine.shared.domain.errors import DataIntegrityError, InvalidInputError
from tests.helpers import EMPLOYER_50

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_ZERO = Decimal(0)

_RESOLVER = load_policy_resolver()
_POLICY_CTX = PolicyContext(year=2026, as_of=date(2026, 1, 1))


class TestEventDateValidation:
    """Events outside the competence period raise InvalidInputError."""

    def test_overtime_outside_period_raises(self) -> None:
        """OvertimeEvent with event_date outside period raises InvalidInputError."""
        out_of_period = OvertimeEvent(
            event_date=date(2026, 2, 10),  # February, not January
            hours=Decimal(8),
            hourly_rate=Decimal(20),
            multiplier=Decimal("1.25"),
        )
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(out_of_period,),
        )
        with pytest.raises(InvalidInputError, match="outside period"):
            calculate_period(req)

    def test_arrears_event_outside_period_allowed(self) -> None:
        """ArrearsEvent may reference past periods without raising."""
        past_arrears = ArrearsEvent(
            event_date=date(2025, 12, 1),  # prior year
            amount=Decimal("500.00"),
            separate_tax_rate=Decimal("0.23"),
        )
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(past_arrears,),
        )
        result = calculate_period(req)
        assert result.period_gross > _ZERO

    def test_absence_event_hours_above_max_raises(self) -> None:
        """AbsenceEvent with hours > 240 raises InvalidInputError."""
        absence = AbsenceEvent(
            event_date=date(2026, 1, 15),
            hours=Decimal(241),
            hourly_rate=Decimal("12.50"),
        )
        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
            events=(absence,),
        )
        with pytest.raises(InvalidInputError, match="hours"):
            calculate_period(req)

    def test_absence_event_hours_zero_raises(self) -> None:
        """AbsenceEvent with hours=0 raises InvalidInputError at construction."""
        with pytest.raises(InvalidInputError, match="hours"):
            AbsenceEvent(
                event_date=date(2026, 1, 15),
                hours=Decimal(0),
                hourly_rate=Decimal("12.50"),
            )


class TestRequireResolution:
    """_require_resolution raises DataIntegrityError for unknown pay-item kinds."""

    def test_unknown_kind_raises_data_integrity_error(self) -> None:
        """Resolving an unknown kind raises DataIntegrityError."""
        with pytest.raises(DataIntegrityError, match="No policy rule found"):
            _require_resolution(_RESOLVER, "nonexistent_kind_xyz", _POLICY_CTX)


class TestReconciliationFailureGuard:
    """calculate_period raises DataIntegrityError when reconciliation fails."""

    def test_reconciliation_failure_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When _reconcile returns violations, DataIntegrityError is raised."""
        fake_result = ReconciliationResult(
            violations=(
                ReconciliationViolation(
                    invariant_id="net_identity", message="test violation"
                ),
            )
        )
        monkeypatch.setattr(_reconcile_mod, "reconcile", lambda *_: fake_result)

        req = PeriodCalculationRequest(
            employer=EMPLOYER_50,
            period_id=PeriodId(year=2026, month=1),
            payment_date=date(2026, 1, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=PeriodState.zero(),
        )
        with pytest.raises(DataIntegrityError, match="Period reconciliation failed"):
            calculate_period(req)
