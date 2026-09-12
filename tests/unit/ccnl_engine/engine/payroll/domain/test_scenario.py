"""Tests for PayrollScenario domain types: validation and properties.

Covers:
* Employee.__post_init__ — part_time_pct and weekly_hours validation
* Employee.seniority_count / seniority_months / seniority_months_as_of
* Agreement.__post_init__ — ad_personam_monthly validation
* Employer.__post_init__ — num_employees validation
* Employment.tax_year override (None vs explicit year)
* PayrollScenario round-trips
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
)

_DATE = date(2026, 6, 1)
_D = Decimal


# ---------------------------------------------------------------------------
# Employee validation
# ---------------------------------------------------------------------------


class TestEmployeeValidation:
    """Employee.__post_init__ enforces part_time_pct and weekly_hours."""

    def test_part_time_pct_zero_raises(self) -> None:
        """part_time_pct=0 is rejected."""
        with pytest.raises(ValueError, match="part_time_pct"):
            Employee(level_code="4", part_time_pct=_D("0"))

    def test_part_time_pct_negative_raises(self) -> None:
        """Negative part_time_pct is rejected."""
        with pytest.raises(ValueError, match="part_time_pct"):
            Employee(level_code="4", part_time_pct=_D("-0.5"))

    def test_part_time_pct_above_one_raises(self) -> None:
        """part_time_pct > 1 is rejected."""
        with pytest.raises(ValueError, match="part_time_pct"):
            Employee(level_code="4", part_time_pct=_D("1.01"))

    def test_part_time_pct_one_accepted(self) -> None:
        """part_time_pct=1 (full-time) is valid."""
        e = Employee(level_code="4", part_time_pct=_D("1"))
        assert e.part_time_pct == _D("1")

    def test_part_time_pct_half_accepted(self) -> None:
        """part_time_pct=0.5 is valid."""
        e = Employee(level_code="4", part_time_pct=_D("0.5"))
        assert e.part_time_pct == _D("0.5")

    def test_weekly_hours_zero_raises(self) -> None:
        """weekly_hours=0 is rejected."""
        with pytest.raises(ValueError, match="weekly_hours"):
            Employee(level_code="4", weekly_hours=_D("0"))

    def test_weekly_hours_negative_raises(self) -> None:
        """Negative weekly_hours is rejected."""
        with pytest.raises(ValueError, match="weekly_hours"):
            Employee(level_code="4", weekly_hours=_D("-1"))

    def test_weekly_hours_none_accepted(self) -> None:
        """weekly_hours=None (default) is valid."""
        e = Employee(level_code="4", weekly_hours=None)
        assert e.weekly_hours is None

    def test_weekly_hours_positive_accepted(self) -> None:
        """weekly_hours > 0 is valid."""
        e = Employee(level_code="4", weekly_hours=_D("40"))
        assert e.weekly_hours == _D("40")


# ---------------------------------------------------------------------------
# Employee seniority properties
# ---------------------------------------------------------------------------


class TestEmployeeSeniorityProperties:
    """seniority_count and seniority_months return the right value or None."""

    def test_seniority_count_from_by_count(self) -> None:
        """seniority_count returns the value when seniority is SeniorityByCount."""
        e = Employee(level_code="4", seniority=SeniorityByCount(3))
        assert e.seniority_count == 3
        assert e.seniority_months is None

    def test_seniority_months_from_by_months(self) -> None:
        """seniority_months returns the value when seniority is SeniorityByMonths."""
        e = Employee(level_code="4", seniority=SeniorityByMonths(36))
        assert e.seniority_months == 36
        assert e.seniority_count is None

    def test_both_none_when_no_seniority(self) -> None:
        """Both properties return None when seniority is None."""
        e = Employee(level_code="4", seniority=None)
        assert e.seniority_count is None
        assert e.seniority_months is None

    def test_seniority_months_none_for_by_date(self) -> None:
        """seniority_months returns None when expressed as a date (no as_of)."""
        e = Employee(level_code="4", seniority=SeniorityByDate(date(2023, 1, 1)))
        assert e.seniority_months is None
        assert e.seniority_count is None


class TestSeniorityMonthsAsOf:
    """Employee.seniority_months_as_of resolves all three union variants."""

    def test_by_months_returns_stored_value(self) -> None:
        """SeniorityByMonths: stored value is returned regardless of as_of."""
        e = Employee(level_code="4", seniority=SeniorityByMonths(36))
        assert e.seniority_months_as_of(date(2026, 1, 1)) == 36

    def test_by_date_computes_calendar_months(self) -> None:
        """SeniorityByDate: months gap between hire and as_of is computed."""
        # Hired 2023-01-01, calculation 2026-01-01 → 36 months exactly.
        e = Employee(level_code="4", seniority=SeniorityByDate(date(2023, 1, 1)))
        assert e.seniority_months_as_of(date(2026, 1, 1)) == 36

    def test_by_date_mid_year_gap(self) -> None:
        """SeniorityByDate: partial-year gaps computed correctly."""
        # Hired 2022-03-01, calculation 2026-09-01 → 54 months.
        e = Employee(level_code="4", seniority=SeniorityByDate(date(2022, 3, 1)))
        assert e.seniority_months_as_of(date(2026, 9, 1)) == 54

    def test_by_count_returns_none(self) -> None:
        """SeniorityByCount: months not applicable — None returned."""
        e = Employee(level_code="4", seniority=SeniorityByCount(3))
        assert e.seniority_months_as_of(date(2026, 1, 1)) is None

    def test_none_seniority_returns_none(self) -> None:
        """No seniority: None returned."""
        e = Employee(level_code="4", seniority=None)
        assert e.seniority_months_as_of(date(2026, 1, 1)) is None

    def test_by_date_future_hire_raises(self) -> None:
        """R17: hire_date after calculation_date raises ValueError."""
        e = Employee(level_code="4", seniority=SeniorityByDate(date(2026, 10, 1)))
        with pytest.raises(ValueError, match=r"hire_date.*after.*calculation_date"):
            e.seniority_months_as_of(date(2026, 9, 1))


# ---------------------------------------------------------------------------
# Agreement validation
# ---------------------------------------------------------------------------


class TestAgreementValidation:
    """Agreement.__post_init__ enforces ad_personam_monthly >= 0."""

    def test_negative_ad_personam_raises(self) -> None:
        """Negative ad_personam_monthly is rejected."""
        with pytest.raises(ValueError, match="ad_personam_monthly"):
            Agreement(ad_personam_monthly=_D("-1"))

    def test_zero_ad_personam_accepted(self) -> None:
        """ad_personam_monthly=0 is valid."""
        a = Agreement(ad_personam_monthly=_D("0"))
        assert a.ad_personam_monthly == _D("0")

    def test_positive_ad_personam_accepted(self) -> None:
        """Positive ad_personam_monthly is valid."""
        a = Agreement(ad_personam_monthly=_D("150"))
        assert a.ad_personam_monthly == _D("150")


# ---------------------------------------------------------------------------
# Employer validation
# ---------------------------------------------------------------------------


class TestEmployerValidation:
    """Employer.__post_init__ enforces num_employees >= 1."""

    def test_zero_employees_raises(self) -> None:
        """num_employees=0 is rejected."""
        with pytest.raises(ValueError, match="num_employees"):
            Employer(num_employees=0)

    def test_negative_employees_raises(self) -> None:
        """Negative num_employees is rejected."""
        with pytest.raises(ValueError, match="num_employees"):
            Employer(num_employees=-10)

    def test_one_employee_accepted(self) -> None:
        """num_employees=1 is valid."""
        emp = Employer(num_employees=1)
        assert emp.num_employees == 1

    def test_large_headcount_accepted(self) -> None:
        """Large headcount is valid."""
        emp = Employer(num_employees=10000)
        assert emp.num_employees == 10000


# ---------------------------------------------------------------------------
# Employment.tax_year override
# ---------------------------------------------------------------------------


class TestEmploymentTaxYear:
    """Employment.tax_year defaults to None; can be set to any int."""

    def test_default_tax_year_is_none(self) -> None:
        """tax_year defaults to None when not supplied."""
        emp = Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=_DATE,
        )
        assert emp.tax_year is None

    def test_explicit_tax_year(self) -> None:
        """tax_year can be set to an explicit year."""
        emp = Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=_DATE,
            tax_year=2026,
        )
        assert emp.tax_year == 2026

    def test_tax_year_can_differ_from_calculation_date_year(self) -> None:
        """tax_year may differ from calculation_date.year (cross-year computation)."""
        emp = Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2025, 11, 1),
            tax_year=2026,
        )
        assert emp.calculation_date.year == 2025
        assert emp.tax_year == 2026


# ---------------------------------------------------------------------------
# Jurisdiction construction
# ---------------------------------------------------------------------------


class TestJurisdiction:
    """Jurisdiction holds regione and comune_belfiore."""

    def test_defaults_to_none(self) -> None:
        """Both fields default to None."""
        j = Jurisdiction()
        assert j.regione is None
        assert j.comune_belfiore is None

    def test_with_both_fields(self) -> None:
        """Both fields can be set."""
        j = Jurisdiction(regione="Lombardia", comune_belfiore="F205")
        assert j.regione == "Lombardia"
        assert j.comune_belfiore == "F205"


# ---------------------------------------------------------------------------
# PayrollScenario construction
# ---------------------------------------------------------------------------


class TestPayrollScenario:
    """PayrollScenario composes Employee and Employment."""

    def test_basic_construction(self) -> None:
        """PayrollScenario stores employee and employment."""
        scenario = PayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="test.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=_DATE,
            ),
        )
        assert scenario.employee.level_code == "4"
        assert scenario.employment.ccnl == "test.json"
        assert scenario.employment.tax_year is None

    def test_frozen(self) -> None:
        """PayrollScenario is immutable (frozen dataclass)."""
        scenario = PayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl="test.json",
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=_DATE,
            ),
        )
        with pytest.raises((AttributeError, TypeError)):
            scenario.employee = Employee(level_code="5")  # type: ignore[misc]
