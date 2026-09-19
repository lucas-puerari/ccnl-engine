"""Tests for the estimate_annual and estimate_period_effects entry points."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.bilateral_funds import FlatMonthlyFund
from ccnl_engine.engine.payroll.domain.calculation import Calculation
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.payroll_result import PeriodPayroll
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WelfareInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    _annual_to_scenario,
    estimate_annual,
    estimate_period_effects,
)

_CCNL = "metalmeccanico-federmeccanica.json"
_AS_OF = date(2026, 1, 1)


def _base_scenario() -> AnnualEstimateInput:
    return AnnualEstimateInput(
        employee=Employee(level_code="C2"),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


class TestAnnualPayrollScenario:
    """Construction and field access for AnnualEstimateInput."""

    def test_minimal_construction(self) -> None:
        """AnnualEstimateInput initialises with defaults for optional fields."""
        s = _base_scenario()
        assert s.employee.level_code == "C2"
        assert s.employment.ccnl == _CCNL
        assert s.family is None
        assert s.art15_deductions is None
        assert s.bilateral_funds == ()

    def test_frozen(self) -> None:
        """AnnualEstimateInput is immutable."""
        s = _base_scenario()
        with pytest.raises(Exception, match="frozen"):
            s.employee = Employee(level_code="D1")  # type: ignore[misc]

    def test_extra_field_rejected(self) -> None:
        """AnnualEstimateInput rejects unknown fields."""
        with pytest.raises(Exception, match="extra"):
            AnnualEstimateInput.model_validate({
                "employee": {"level_code": "C2"},
                "employment": {
                    "ccnl": _CCNL,
                    "contract": {"type": "permanent"},
                    "employer": {"num_employees": 50},
                    "as_of": "2026-01-01",
                },
                "unknown_field": 123,
            })


class TestPayPeriod:
    """Construction and field access for PeriodPayrollInput."""

    def test_empty_period(self) -> None:
        """An empty PeriodPayrollInput has all-None event fields."""
        p = PeriodPayrollInput()
        assert p.time_supplements is None
        assert p.absence_days is None
        assert p.leave_input is None
        assert p.sick_input is None
        assert p.fringe_benefit_input is None
        assert p.welfare_input is None
        assert p.bonus_input is None

    def test_period_with_overtime(self) -> None:
        """PeriodPayrollInput stores OvertimeHours correctly."""
        p = PeriodPayrollInput(time_supplements=OvertimeHours(weekday_hours=Decimal(8)))
        assert p.time_supplements is not None
        assert p.time_supplements.weekday_hours == Decimal(8)

    def test_period_with_all_fields(self) -> None:
        """PeriodPayrollInput accepts every optional event field."""
        p = PeriodPayrollInput(
            time_supplements=OvertimeHours(weekday_hours=Decimal(4)),
            absence_days=AbsenceDays(unpaid_days=Decimal(1)),
            leave_input=LeaveInput(taken_days=Decimal(2)),
            sick_input=SickInput(sick_days=Decimal(3)),
            fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal(500)),
            welfare_input=WelfareInput(annual_amount=Decimal(200)),
            bonus_input=BonusInput(annual_amount=Decimal(1000), eligible_for_pdr=False),
        )
        assert p.absence_days is not None
        assert p.absence_days.unpaid_days == Decimal(1)
        assert p.welfare_input is not None
        assert p.welfare_input.annual_amount == Decimal(200)

    def test_frozen(self) -> None:
        """PeriodPayrollInput is immutable."""
        p = PeriodPayrollInput()
        with pytest.raises(Exception, match="frozen"):
            p.time_supplements = OvertimeHours()  # type: ignore[misc]

    def test_extra_field_rejected(self) -> None:
        """PeriodPayrollInput rejects unknown fields."""
        with pytest.raises(Exception, match="extra"):
            PeriodPayrollInput.model_validate({"unknown_field": True})


class TestAnnualToScenario:
    """Unit tests for the internal _annual_to_scenario helper."""

    def test_without_period_maps_structural_fields(self) -> None:
        """_annual_to_scenario with no period yields all-None event fields."""
        s = _base_scenario()
        result = _annual_to_scenario(s)
        assert result.employee is s.employee
        assert result.employment is s.employment
        assert result.time_supplements is None
        assert result.absence_days is None
        assert result.fringe_benefit_input is None

    def test_with_period_merges_events(self) -> None:
        """_annual_to_scenario with a period merges period event fields."""
        s = _base_scenario()
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(weekday_hours=Decimal(8)),
            absence_days=AbsenceDays(unpaid_days=Decimal(1)),
        )
        result = _annual_to_scenario(s, period)
        assert result.time_supplements is period.time_supplements
        assert result.absence_days is period.absence_days
        assert result.welfare_input is None

    def test_bilateral_funds_propagated(self) -> None:
        """Bilateral funds from AnnualEstimateInput carry over."""
        s = AnnualEstimateInput(
            employee=Employee(level_code="C2"),
            employment=Employment(
                ccnl=_CCNL,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=_AS_OF,
            ),
            bilateral_funds=(
                FlatMonthlyFund(
                    employee_monthly=Decimal(5), employer_monthly=Decimal(10)
                ),
            ),
        )
        result = _annual_to_scenario(s)
        assert len(result.bilateral_funds) == 1

    def test_period_none_has_no_time_supplements(self) -> None:
        """Explicit period=None yields no time supplements."""
        result = _annual_to_scenario(_base_scenario(), None)
        assert result.time_supplements is None


class TestEstimateAnnual:
    """Integration tests for estimate_annual."""

    def test_returns_calculation(self) -> None:
        """estimate_annual returns a Calculation instance."""
        result = estimate_annual(_base_scenario())
        assert isinstance(result, Calculation)

    def test_net_annual_positive(self) -> None:
        """estimate_annual produces a positive net_annual."""
        result = estimate_annual(_base_scenario())
        assert result.result.net_annual > Decimal(0)

    def test_no_period_events_in_result(self) -> None:
        """estimate_annual returns an AnnualEstimate, not a PeriodPayroll."""
        result = estimate_annual(_base_scenario())
        assert not isinstance(result.result, PeriodPayroll)

    def test_equivalent_to_compute_without_events(self) -> None:
        """estimate_annual matches compute() with no period events."""
        s = _base_scenario()
        annual = estimate_annual(s)
        direct = estimate_annual(AnnualEstimateInput(
            employee=s.employee, employment=s.employment
        ))
        assert annual.result.net_annual == direct.result.net_annual


class TestEstimatePeriodEffects:
    """Integration tests for estimate_period_effects."""

    def test_returns_calculation(self) -> None:
        """estimate_period_effects returns a Calculation."""
        result = estimate_period_effects(_base_scenario(), PeriodPayrollInput())
        assert isinstance(result, Calculation)

    def test_overtime_supplement_non_zero(self) -> None:
        """Overtime hours in PeriodPayrollInput produce a non-zero supplement."""
        with_overtime = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(
                time_supplements=OvertimeHours(weekday_hours=Decimal(8))
            ),
        )
        assert isinstance(with_overtime.result, PeriodPayroll)
        assert with_overtime.result.overtime_supplement_monthly > Decimal(0)
        assert with_overtime.result.time_supplements_monthly > Decimal(0)

    def test_net_annual_unchanged_by_overtime(self) -> None:
        """net_annual is not altered by period events — it remains an estimate."""
        base = estimate_annual(_base_scenario())
        with_overtime = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(
                time_supplements=OvertimeHours(weekday_hours=Decimal(8))
            ),
        )
        assert with_overtime.result.net_annual == base.result.net_annual

    def test_empty_period_equals_estimate_annual(self) -> None:
        """estimate_period_effects with empty period matches estimate_annual."""
        base = estimate_annual(_base_scenario())
        with_empty = estimate_period_effects(_base_scenario(), PeriodPayrollInput())
        assert with_empty.result.net_annual == base.result.net_annual

    def test_sick_days_appear_in_result(self) -> None:
        """Sick days in PeriodPayrollInput are reflected in sick_days_monthly."""
        sick = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(sick_input=SickInput(sick_days=Decimal(5))),
        )
        assert isinstance(sick.result, PeriodPayroll)
        assert sick.result.sick_days_monthly == Decimal(5)

    def test_fringe_benefit_in_period(self) -> None:
        """FringeBenefitInput in the period propagates to fringe_benefit_annual."""
        result = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(
                fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal(300))
            ),
        )
        assert isinstance(result.result, PeriodPayroll)
        assert result.result.fringe_benefit_annual == Decimal(300)

    def test_welfare_in_period(self) -> None:
        """WelfareInput in PeriodPayrollInput propagates to welfare_annual."""
        result = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(welfare_input=WelfareInput(annual_amount=Decimal(200))),
        )
        assert isinstance(result.result, PeriodPayroll)
        assert result.result.welfare_annual == Decimal(200)

    def test_bonus_in_period(self) -> None:
        """BonusInput in PeriodPayrollInput propagates to bonus_annual."""
        result = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(
                bonus_input=BonusInput(
                    annual_amount=Decimal(1000), eligible_for_pdr=False
                )
            ),
        )
        assert isinstance(result.result, PeriodPayroll)
        assert result.result.bonus_annual == Decimal(1000)

    def test_absence_days_reflected_in_result(self) -> None:
        """Absence days produce a deduction; net_annual remains the annual estimate."""
        base = estimate_annual(_base_scenario())
        with_absence = estimate_period_effects(
            _base_scenario(),
            PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=Decimal(3))),
        )
        assert isinstance(with_absence.result, PeriodPayroll)
        assert with_absence.result.absence_deduction_monthly > Decimal(0)
        assert with_absence.result.net_annual == base.result.net_annual
