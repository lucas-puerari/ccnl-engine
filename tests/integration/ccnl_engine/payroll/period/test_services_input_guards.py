"""Guards of calculate_period: event dates, policy resolution, reconciliation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.errors import DataIntegrityError, InvalidInputError
from ccnl_engine.payroll.amount.loaders_policy import load_policy_resolver
from ccnl_engine.payroll.amount.policies import PolicyContext
from ccnl_engine.payroll.assurance import validators as _reconcile_mod
from ccnl_engine.payroll.assurance.validators import (
    ReconciliationResult,
    ReconciliationViolation,
)
from ccnl_engine.payroll.event.facade import AbsenceEvent, ArrearsEvent, OvertimeEvent
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.period.services_shared import _require_resolution
from ccnl_engine.payroll.state.models import PeriodState
from tests.fixtures.period_requests import period_request
from tests.helpers import EMPLOYER_50

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
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


# ---------------------------------------------------------------------------
# Large unpaid absences and period_gross
#
# Since absences post to EMPLOYEE_DEDUCTIONS (not CASH_EARNINGS), period_gross
# equals the base salary and is non-negative regardless of absence size.
# Metalmeccanico C3 gross is 2,158.26 EUR in January 2026.
# ---------------------------------------------------------------------------


def test_large_absence_does_not_produce_negative_gross() -> None:
    """AbsenceEvent(hours=80) is accepted and period_gross stays positive.

    Absences post to EMPLOYEE_DEDUCTIONS so period_gross reflects base
    salary only.  80 hours at 12.50 EUR deduct 1,000 EUR, below the monthly
    pay; the calculation succeeds with a positive gross and net.
    """
    absence = AbsenceEvent(
        event_date=date(_YEAR, 1, 15),
        hours=Decimal(80),
        hourly_rate=Decimal("12.50"),
    )
    result = calculate_period(period_request(events=(absence,)))
    assert result.period_gross > Decimal(0)
    assert result.period_net >= Decimal(0)


def test_absence_above_monthly_pay_is_invalid_input() -> None:
    """An absence deduction above the monthly pay is rejected up front.

    240 hours at 12.50 EUR deduct 3,000 EUR from 2,158.26 EUR of pay: the
    INPS base would turn negative.  The deduction is checked against the
    pay of the run before any amount is computed.
    """
    absence = AbsenceEvent(
        event_date=date(_YEAR, 1, 15),
        hours=Decimal(240),
        hourly_rate=Decimal("12.50"),
    )
    with pytest.raises(InvalidInputError, match=r"more than the pay of the run"):
        calculate_period(period_request(events=(absence,)))


# ---------------------------------------------------------------------------
# AbsenceEvent with impossible hours accepted silently
#
# A monthly payroll period has at most ~184 working hours (23 days x 8 h).
# AbsenceEvent(hours=1000) in a single month is physically impossible and
# must raise InvalidInputError before reaching the computation.
# Currently the engine accepts it and produces a large negative period_gross.
# ---------------------------------------------------------------------------


def test_absence_event_impossible_hours_raises() -> None:
    """AbsenceEvent with 1,000 hours must raise InvalidInputError.

    Source: physical constraint — a month has at most ~184 working hours.
    Fixed in refactor/canonical-domain: _check_event_date validates hours <= 240.
    """
    absence = AbsenceEvent(
        event_date=date(_YEAR, 1, 15),
        hours=Decimal(1000),
        hourly_rate=Decimal("12.50"),
    )
    with pytest.raises(InvalidInputError):
        calculate_period(period_request(events=(absence,)))
