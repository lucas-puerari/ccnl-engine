"""Tests for PayrollPeriod, YTDState, compute_period, and compute_year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

import ccnl_engine.engine.payroll.service.orchestrator as _orch
from ccnl_engine import (
    AnnualPayrollScenario,
    Employee,
    Employer,
    Employment,
    InvalidInputError,
    PayPeriod,
    PayrollBundle,
    PayrollPeriod,
    Permanent,
    YTDState,
    compute_period,
    compute_year,
)
from ccnl_engine.engine.payroll.domain.bundle import make_bundle
from ccnl_engine.engine.payroll.domain.calculation import Calculation
from ccnl_engine.engine.payroll.domain.period import PayrollPeriod as _DomainPeriod
from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
from tests.helpers import make_minimal_ccnl, make_year_rules

_CCNL = "commercio-confcommercio.json"

_SCENARIO = AnnualPayrollScenario(
    employee=Employee(level_code="4"),
    employment=Employment(
        ccnl=_CCNL,
        contract=Permanent(),
        employer=Employer(num_employees=50),
        as_of=date(2026, 1, 1),
    ),
)


def _make_bundle() -> PayrollBundle:
    """Return a minimal PayrollBundle for loader-bypass tests.

    Returns:
        A :class:`PayrollBundle` built from minimal test fixtures.
    """
    return make_bundle(make_minimal_ccnl(), make_year_rules(), None)


class TestYTDState:
    """Tests for YTDState dataclass."""

    def test_defaults_are_zero(self) -> None:
        """All fields default to zero."""
        ytd = YTDState()
        assert ytd.taxable_income == Decimal(0)
        assert ytd.irpef_withheld == Decimal(0)
        assert ytd.inps_employee == Decimal(0)

    def test_explicit_values(self) -> None:
        """Explicit values are stored correctly."""
        ytd = YTDState(
            taxable_income=Decimal(10000),
            irpef_withheld=Decimal(2000),
            inps_employee=Decimal(900),
        )
        assert ytd.taxable_income == Decimal(10000)
        assert ytd.irpef_withheld == Decimal(2000)
        assert ytd.inps_employee == Decimal(900)

    def test_is_frozen(self) -> None:
        """YTDState is immutable."""
        ytd = YTDState()
        with pytest.raises((TypeError, AttributeError)):
            ytd.taxable_income = Decimal(1)  # type: ignore[misc]

    def test_equality(self) -> None:
        """Two YTDState with the same values are equal."""
        assert YTDState(Decimal(1), Decimal(2), Decimal(3)) == YTDState(
            Decimal(1), Decimal(2), Decimal(3)
        )


class TestPayrollPeriodDomain:
    """Tests for PayrollPeriod domain type."""

    def test_required_fields(self) -> None:
        """Year and month are stored correctly."""
        p = PayrollPeriod(year=2026, month=3)
        assert p.year == 2026
        assert p.month == 3

    def test_default_events_is_empty_payperiod(self) -> None:
        """Events defaults to a PayPeriod with no special events."""
        p = PayrollPeriod(year=2026, month=1)
        assert isinstance(p.events, PayPeriod)
        assert p.events.time_supplements is None

    def test_default_ytd_is_zero(self) -> None:
        """Ytd defaults to YTDState with all zeros."""
        p = PayrollPeriod(year=2026, month=1)
        assert p.ytd == YTDState()

    def test_default_status_is_open(self) -> None:
        """Status defaults to 'open'."""
        p = PayrollPeriod(year=2026, month=6)
        assert p.status == "open"

    def test_closed_status(self) -> None:
        """Status can be set to 'closed'."""
        p = PayrollPeriod(year=2026, month=6, status="closed")
        assert p.status == "closed"

    def test_is_frozen(self) -> None:
        """PayrollPeriod is immutable after construction."""
        p = PayrollPeriod(year=2026, month=1)
        with pytest.raises((TypeError, AttributeError)):
            p.month = 2  # type: ignore[misc]

    def test_custom_ytd(self) -> None:
        """Custom YTD state is stored correctly."""
        ytd = YTDState(taxable_income=Decimal(5000))
        p = PayrollPeriod(year=2026, month=2, ytd=ytd)
        assert p.ytd.taxable_income == Decimal(5000)

    def test_public_api_reexport(self) -> None:
        """PayrollPeriod and YTDState are accessible from the top-level API."""
        assert _DomainPeriod is PayrollPeriod


class TestComputePeriod:
    """Tests for compute_period()."""

    def test_uses_period_year_and_month_as_as_of(self) -> None:
        """compute_period overrides as_of to date(year, month, 1)."""
        result = compute_period(_SCENARIO, PayrollPeriod(year=2026, month=7))
        assert result.result.as_of == date(2026, 7, 1)

    def test_result_is_calculation(self) -> None:
        """compute_period returns a Calculation."""
        result = compute_period(_SCENARIO, PayrollPeriod(year=2026, month=1))
        assert isinstance(result, Calculation)

    def test_passes_events_to_estimate_period_effects(self) -> None:
        """Period events are forwarded to the underlying compute."""
        events = PayPeriod(time_supplements=OvertimeHours(weekday_hours=Decimal(10)))
        result = compute_period(
            _SCENARIO, PayrollPeriod(year=2026, month=1, events=events)
        )
        assert result is not None

    def test_accepts_bundle(self) -> None:
        """compute_period accepts an optional bundle and skips loaders."""
        bundle = _make_bundle()
        with patch(
            "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
        ) as mock_ccnl:
            compute_period(_SCENARIO, PayrollPeriod(year=2026, month=3), bundle)
        mock_ccnl.assert_not_called()

    def test_deterministic(self) -> None:
        """Same period inputs always produce the same result."""
        p = PayrollPeriod(year=2026, month=4)
        r1 = compute_period(_SCENARIO, p)
        r2 = compute_period(_SCENARIO, p)
        assert r1.result.net_annual == r2.result.net_annual


class TestComputeYear:
    """Tests for compute_year()."""

    def test_returns_twelve_calculations(self) -> None:
        """compute_year returns exactly 12 Calculation instances."""
        results = compute_year(_SCENARIO, 2026)
        assert len(results) == 12

    def test_months_have_correct_as_of_dates(self) -> None:
        """Each result's as_of date matches its month."""
        results = compute_year(_SCENARIO, 2026)
        for i, calc in enumerate(results):
            assert calc.result.as_of == date(2026, i + 1, 1), (
                f"month {i + 1}: expected as_of=date(2026, {i + 1}, 1), "
                f"got {calc.result.as_of}"
            )

    def test_accepts_bundle(self) -> None:
        """compute_year accepts an optional bundle."""
        bundle = _make_bundle()
        with patch(
            "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl"
        ) as mock_ccnl:
            compute_year(_SCENARIO, 2026, bundle=bundle)
        mock_ccnl.assert_not_called()

    def test_accepts_month_events(self) -> None:
        """compute_year accepts per-month events."""
        events = [PayPeriod()] * 11 + [
            PayPeriod(time_supplements=OvertimeHours(weekday_hours=Decimal(8)))
        ]
        results = compute_year(_SCENARIO, 2026, month_events=events)
        assert len(results) == 12

    def test_wrong_month_events_length_raises(self) -> None:
        """Providing fewer than 12 month_events raises InvalidInputError."""
        with pytest.raises(InvalidInputError):
            compute_year(_SCENARIO, 2026, month_events=[PayPeriod()] * 6)

    def test_ytd_threads_across_months(self) -> None:
        """Each period in compute_year receives the cumulative YTD from prior months."""
        captured_ytds: list[YTDState] = []

        original_compute_period = _orch.compute_period

        def _capturing(
            scenario: AnnualPayrollScenario,
            period: PayrollPeriod,
            bundle: PayrollBundle | None = None,
        ) -> Calculation:
            """Capture each period's YTD then delegate.

            Returns:
                The Calculation produced by the real compute_period.
            """
            captured_ytds.append(period.ytd)
            return original_compute_period(scenario, period, bundle)

        with patch(
            "ccnl_engine.engine.payroll.service.orchestrator.compute_period",
            side_effect=_capturing,
        ):
            compute_year(_SCENARIO, 2026)

        assert len(captured_ytds) == 12
        assert captured_ytds[0] == YTDState()
        assert captured_ytds[1].taxable_income > Decimal(0)
        assert captured_ytds[11].taxable_income > captured_ytds[1].taxable_income

    def test_mid_year_hire_partial_sequence(self) -> None:
        """compute_period called for each month independently covers hire mid-year."""
        july_scenario = AnnualPayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl=_CCNL,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 7, 1),
            ),
        )
        results = [
            compute_period(july_scenario, PayrollPeriod(year=2026, month=m))
            for m in range(7, 13)
        ]
        assert len(results) == 6
        for calc in results:
            assert calc.result.net_annual > Decimal(0)

    def test_ral_change_mid_year(self) -> None:
        """Scenarios with different levels can be computed period-by-period."""
        scenario_l3 = AnnualPayrollScenario(
            employee=Employee(level_code="3"),
            employment=Employment(
                ccnl=_CCNL,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 1, 1),
            ),
        )
        scenario_l4 = AnnualPayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl=_CCNL,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2026, 7, 1),
            ),
        )
        first_half = [
            compute_period(scenario_l3, PayrollPeriod(year=2026, month=m))
            for m in range(1, 7)
        ]
        second_half = [
            compute_period(scenario_l4, PayrollPeriod(year=2026, month=m))
            for m in range(7, 13)
        ]
        assert len(first_half) == 6
        assert len(second_half) == 6
        # level 3 earns more than level 4 in commercio-confcommercio
        assert (
            first_half[0].result.earnings.gross_monthly
            > second_half[0].result.earnings.gross_monthly
        )
