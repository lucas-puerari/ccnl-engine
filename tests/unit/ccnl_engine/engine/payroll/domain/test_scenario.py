"""Tests for PayrollScenario domain types: validation and properties.

Covers:
* Employee.__post_init__ — part_time_ratio and weekly_hours validation
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
from pydantic import ValidationError

from ccnl_engine.engine.payroll.domain.employee import (
    SeniorityByCount,
    SeniorityByDate,
    SeniorityByMonths,
)
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    Agreement,
    AnnualizedAssumption,
    Employee,
    Employer,
    Employment,
    Jurisdiction,
    PayrollScenario,
    TaxPeriod,
)

_DATE = date(2026, 6, 1)
_D = Decimal


# ---------------------------------------------------------------------------
# Employee validation
# ---------------------------------------------------------------------------


class TestEmployeeValidation:
    """Employee.__post_init__ enforces part_time_ratio and weekly_hours."""

    def test_part_time_ratio_zero_raises(self) -> None:
        """part_time_ratio=0 is rejected."""
        with pytest.raises(ValueError, match="part_time_ratio"):
            Employee(level_code="4", part_time_ratio=_D("0"))

    def test_part_time_ratio_negative_raises(self) -> None:
        """Negative part_time_ratio is rejected."""
        with pytest.raises(ValueError, match="part_time_ratio"):
            Employee(level_code="4", part_time_ratio=_D("-0.5"))

    def test_part_time_ratio_above_one_raises(self) -> None:
        """part_time_ratio > 1 is rejected."""
        with pytest.raises(ValueError, match="part_time_ratio"):
            Employee(level_code="4", part_time_ratio=_D("1.01"))

    def test_part_time_ratio_one_accepted(self) -> None:
        """part_time_ratio=1 (full-time) is valid."""
        e = Employee(level_code="4", part_time_ratio=_D("1"))
        assert e.part_time_ratio == _D("1")

    def test_part_time_ratio_half_accepted(self) -> None:
        """part_time_ratio=0.5 is valid."""
        e = Employee(level_code="4", part_time_ratio=_D("0.5"))
        assert e.part_time_ratio == _D("0.5")

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
        e = Employee(level_code="4", seniority=SeniorityByCount(value=3))
        assert e.seniority_count == 3
        assert e.seniority_months is None

    def test_seniority_months_from_by_months(self) -> None:
        """seniority_months returns the value when seniority is SeniorityByMonths."""
        e = Employee(level_code="4", seniority=SeniorityByMonths(value=36))
        assert e.seniority_months == 36
        assert e.seniority_count is None

    def test_both_none_when_no_seniority(self) -> None:
        """Both properties return None when seniority is None."""
        e = Employee(level_code="4", seniority=None)
        assert e.seniority_count is None
        assert e.seniority_months is None

    def test_seniority_months_none_for_by_date(self) -> None:
        """seniority_months returns None when expressed as a date (no as_of)."""
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2023, 1, 1)))
        assert e.seniority_months is None
        assert e.seniority_count is None


class TestSeniorityMonthsAsOf:
    """Employee.seniority_months_as_of resolves all three union variants."""

    def test_by_months_returns_stored_value(self) -> None:
        """SeniorityByMonths: stored value is returned regardless of as_of."""
        e = Employee(level_code="4", seniority=SeniorityByMonths(value=36))
        assert e.seniority_months_as_of(date(2026, 1, 1)) == 36

    def test_by_date_computes_calendar_months(self) -> None:
        """SeniorityByDate: months gap between hire and as_of is computed."""
        # Hired 2023-01-01, calculation 2026-01-01 → 36 months exactly.
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2023, 1, 1)))
        assert e.seniority_months_as_of(date(2026, 1, 1)) == 36

    def test_by_date_mid_year_gap(self) -> None:
        """SeniorityByDate: partial-year gaps computed correctly."""
        # Hired 2022-03-01, calculation 2026-09-01 → 54 months.
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2022, 3, 1)))
        assert e.seniority_months_as_of(date(2026, 9, 1)) == 54

    def test_by_count_returns_none(self) -> None:
        """SeniorityByCount: months not applicable — None returned."""
        e = Employee(level_code="4", seniority=SeniorityByCount(value=3))
        assert e.seniority_months_as_of(date(2026, 1, 1)) is None

    def test_none_seniority_returns_none(self) -> None:
        """No seniority: None returned."""
        e = Employee(level_code="4", seniority=None)
        assert e.seniority_months_as_of(date(2026, 1, 1)) is None

    def test_by_date_future_hire_raises(self) -> None:
        """hire_date in a future month raises ValueError."""
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2026, 10, 1)))
        with pytest.raises(ValueError, match=r"hire_date.*after.*as_of"):
            e.seniority_months_as_of(date(2026, 9, 1))

    def test_by_date_same_month_future_day_raises(self) -> None:
        """hire_date later in the same month raises ValueError."""
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2026, 9, 30)))
        with pytest.raises(ValueError, match=r"hire_date.*after.*as_of"):
            e.seniority_months_as_of(date(2026, 9, 1))

    def test_by_date_same_day_returns_zero(self) -> None:
        """hire_date == as_of returns 0 months (first day of employment)."""
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2026, 9, 1)))
        assert e.seniority_months_as_of(date(2026, 9, 1)) == 0

    def test_by_date_prior_month_returns_one(self) -> None:
        """hire_date in the immediately preceding month returns 1."""
        e = Employee(level_code="4", seniority=SeniorityByDate(value=date(2026, 8, 31)))
        assert e.seniority_months_as_of(date(2026, 9, 1)) == 1


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

    def test_inail_rate_none_by_default(self) -> None:
        """inail_rate defaults to None (INAIL not modelled)."""
        emp = Employer(num_employees=1)
        assert emp.inail_rate is None

    def test_inail_rate_zero_accepted(self) -> None:
        """inail_rate=0 is valid (zero-rate edge case)."""
        emp = Employer(num_employees=1, inail_rate=Decimal("0.000"))
        assert emp.inail_rate == Decimal(0)

    def test_inail_rate_positive_accepted(self) -> None:
        """A positive inail_rate is accepted."""
        emp = Employer(num_employees=1, inail_rate=Decimal("0.015"))
        assert emp.inail_rate == Decimal("0.015")

    def test_negative_inail_rate_raises(self) -> None:
        """Negative inail_rate is rejected."""
        with pytest.raises(ValueError, match="inail_rate"):
            Employer(num_employees=1, inail_rate=Decimal("-0.001"))

    def test_exemption_none_by_default(self) -> None:
        """inps_employer_exemption_annual defaults to None."""
        emp = Employer(num_employees=1)
        assert emp.inps_employer_exemption_annual is None

    def test_exemption_zero_accepted(self) -> None:
        """inps_employer_exemption_annual=0 is valid."""
        emp = Employer(num_employees=1, inps_employer_exemption_annual=Decimal(0))
        assert emp.inps_employer_exemption_annual == Decimal(0)

    def test_exemption_positive_accepted(self) -> None:
        """A positive exemption amount is accepted."""
        emp = Employer(num_employees=1, inps_employer_exemption_annual=Decimal(8060))
        assert emp.inps_employer_exemption_annual == Decimal(8060)

    def test_negative_exemption_raises(self) -> None:
        """Negative inps_employer_exemption_annual is rejected."""
        with pytest.raises(ValueError, match="inps_employer_exemption_annual"):
            Employer(num_employees=1, inps_employer_exemption_annual=Decimal(-1))


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
            as_of=_DATE,
        )
        assert emp.tax_year is None

    def test_explicit_tax_year(self) -> None:
        """tax_year can be set to an explicit year."""
        emp = Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_DATE,
            tax_year=2026,
        )
        assert emp.tax_year == 2026

    def test_tax_year_can_differ_from_as_of_year(self) -> None:
        """tax_year may differ from as_of.year (cross-year computation)."""
        emp = Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2025, 11, 1),
            tax_year=2026,
        )
        assert emp.as_of.year == 2025
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
                as_of=_DATE,
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
                as_of=_DATE,
            ),
        )
        with pytest.raises((AttributeError, TypeError, ValidationError)):
            scenario.employee = Employee(level_code="5")  # type: ignore[misc]


class TestAnnualizedAssumption:
    """AnnualizedAssumption validation."""

    def test_default_type(self) -> None:
        """AnnualizedAssumption.type is 'annualized'."""
        assert AnnualizedAssumption().type == "annualized"

    def test_frozen(self) -> None:
        """AnnualizedAssumption is immutable."""
        a = AnnualizedAssumption()
        with pytest.raises((AttributeError, TypeError, ValidationError)):
            a.type = "other"  # type: ignore[misc,assignment]


class TestTaxPeriod:
    """TaxPeriod validation."""

    def test_valid(self) -> None:
        """TaxPeriod accepts valid inputs."""
        tp = TaxPeriod(
            start=date(2026, 1, 1),
            end=date(2026, 12, 31),
            eligible_work_days=365,
        )
        assert tp.eligible_work_days == 365

    def test_valid_partial_year(self) -> None:
        """TaxPeriod accepts eligible_work_days less than span."""
        tp = TaxPeriod(
            start=date(2026, 3, 1),
            end=date(2026, 12, 31),
            eligible_work_days=200,
        )
        assert tp.eligible_work_days == 200

    def test_start_after_end_raises(self) -> None:
        """TaxPeriod rejects start > end."""
        with pytest.raises(ValidationError, match=r"start.*after.*end|end.*start"):
            TaxPeriod(
                start=date(2026, 12, 31),
                end=date(2026, 1, 1),
                eligible_work_days=1,
            )

    def test_eligible_work_days_zero_raises(self) -> None:
        """TaxPeriod rejects eligible_work_days == 0."""
        with pytest.raises(ValidationError, match="eligible_work_days"):
            TaxPeriod(
                start=date(2026, 1, 1),
                end=date(2026, 12, 31),
                eligible_work_days=0,
            )

    def test_eligible_work_days_exceeds_span_raises(self) -> None:
        """TaxPeriod rejects eligible_work_days > (end - start).days + 1."""
        with pytest.raises(ValidationError, match="eligible_work_days"):
            TaxPeriod(
                start=date(2026, 6, 1),
                end=date(2026, 6, 30),
                eligible_work_days=31,
            )

    def test_discriminator_type(self) -> None:
        """TaxPeriod.type is 'tax_period'."""
        tp = TaxPeriod(
            start=date(2026, 1, 1),
            end=date(2026, 12, 31),
            eligible_work_days=365,
        )
        assert tp.type == "tax_period"


# ---------------------------------------------------------------------------
# PayrollScenario.prior_period_irpef_withheld validation
# ---------------------------------------------------------------------------


def _base_scenario(**kwargs: object) -> PayrollScenario:
    return PayrollScenario(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl="test.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_DATE,
        ),
        **kwargs,  # type: ignore[arg-type]
    )


class TestPriorIrpefWithheld:
    """PayrollScenario.prior_period_irpef_withheld validation."""

    def test_prior_irpef_none_by_default(self) -> None:
        """prior_period_irpef_withheld defaults to None."""
        assert _base_scenario().prior_period_irpef_withheld is None

    def test_prior_irpef_zero_accepted(self) -> None:
        """prior_period_irpef_withheld=0 is valid."""
        s = _base_scenario(prior_period_irpef_withheld=Decimal(0))
        assert s.prior_period_irpef_withheld == Decimal(0)

    def test_prior_irpef_positive_accepted(self) -> None:
        """A positive prior_period_irpef_withheld is accepted."""
        s = _base_scenario(prior_period_irpef_withheld=Decimal("1500.00"))
        assert s.prior_period_irpef_withheld == Decimal("1500.00")

    def test_negative_prior_irpef_raises(self) -> None:
        """Negative prior_period_irpef_withheld is rejected."""
        with pytest.raises(ValidationError, match="prior_period_irpef_withheld"):
            _base_scenario(prior_period_irpef_withheld=Decimal(-1))


class TestMaternityIndemnity:
    """PayrollScenario.maternity_inps_indemnity_annual validation."""

    def test_maternity_none_by_default(self) -> None:
        """maternity_inps_indemnity_annual defaults to None."""
        assert _base_scenario().maternity_inps_indemnity_annual is None

    def test_maternity_zero_accepted(self) -> None:
        """maternity_inps_indemnity_annual=0 is valid."""
        s = _base_scenario(maternity_inps_indemnity_annual=Decimal(0))
        assert s.maternity_inps_indemnity_annual == Decimal(0)

    def test_maternity_positive_accepted(self) -> None:
        """A positive maternity_inps_indemnity_annual is accepted."""
        s = _base_scenario(maternity_inps_indemnity_annual=Decimal("3200.00"))
        assert s.maternity_inps_indemnity_annual == Decimal("3200.00")

    def test_negative_maternity_raises(self) -> None:
        """Negative maternity_inps_indemnity_annual is rejected."""
        with pytest.raises(ValidationError, match="maternity_inps_indemnity_annual"):
            _base_scenario(maternity_inps_indemnity_annual=Decimal(-1))


class TestWorkplaceInjuryIndemnity:
    """PayrollScenario.workplace_injury_inail_indemnity_annual validation."""

    def test_injury_none_by_default(self) -> None:
        """workplace_injury_inail_indemnity_annual defaults to None."""
        assert _base_scenario().workplace_injury_inail_indemnity_annual is None

    def test_injury_zero_accepted(self) -> None:
        """workplace_injury_inail_indemnity_annual=0 is valid."""
        s = _base_scenario(workplace_injury_inail_indemnity_annual=Decimal(0))
        assert s.workplace_injury_inail_indemnity_annual == Decimal(0)

    def test_injury_positive_accepted(self) -> None:
        """A positive workplace_injury_inail_indemnity_annual is accepted."""
        s = _base_scenario(workplace_injury_inail_indemnity_annual=Decimal("800.00"))
        assert s.workplace_injury_inail_indemnity_annual == Decimal("800.00")

    def test_negative_injury_raises(self) -> None:
        """Negative workplace_injury_inail_indemnity_annual is rejected."""
        with pytest.raises(
            ValidationError, match="workplace_injury_inail_indemnity_annual"
        ):
            _base_scenario(workplace_injury_inail_indemnity_annual=Decimal(-1))


class TestTerminationPayouts:
    """PayrollScenario termination payout field validation."""

    def test_residual_leave_none_by_default(self) -> None:
        """termination_residual_leave_payout_annual defaults to None."""
        assert _base_scenario().termination_residual_leave_payout_annual is None

    def test_residual_leave_zero_accepted(self) -> None:
        """termination_residual_leave_payout_annual=0 is valid."""
        s = _base_scenario(termination_residual_leave_payout_annual=Decimal(0))
        assert s.termination_residual_leave_payout_annual == Decimal(0)

    def test_residual_leave_positive_accepted(self) -> None:
        """A positive termination_residual_leave_payout_annual is accepted."""
        s = _base_scenario(termination_residual_leave_payout_annual=Decimal("1200.00"))
        assert s.termination_residual_leave_payout_annual == Decimal("1200.00")

    def test_negative_residual_leave_raises(self) -> None:
        """Negative termination_residual_leave_payout_annual is rejected."""
        with pytest.raises(
            ValidationError, match="termination_residual_leave_payout_annual"
        ):
            _base_scenario(termination_residual_leave_payout_annual=Decimal(-1))

    def test_tfr_liquidation_none_by_default(self) -> None:
        """termination_tfr_liquidation_annual defaults to None."""
        assert _base_scenario().termination_tfr_liquidation_annual is None

    def test_tfr_liquidation_zero_accepted(self) -> None:
        """termination_tfr_liquidation_annual=0 is valid."""
        s = _base_scenario(termination_tfr_liquidation_annual=Decimal(0))
        assert s.termination_tfr_liquidation_annual == Decimal(0)

    def test_tfr_liquidation_positive_accepted(self) -> None:
        """A positive termination_tfr_liquidation_annual is accepted."""
        s = _base_scenario(termination_tfr_liquidation_annual=Decimal("8000.00"))
        assert s.termination_tfr_liquidation_annual == Decimal("8000.00")

    def test_negative_tfr_liquidation_raises(self) -> None:
        """Negative termination_tfr_liquidation_annual is rejected."""
        with pytest.raises(ValidationError, match="termination_tfr_liquidation_annual"):
            _base_scenario(termination_tfr_liquidation_annual=Decimal(-1))


class TestContractRenewalArrears:
    """PayrollScenario contract_renewal_arrears_annual field validation."""

    def test_arrears_none_by_default(self) -> None:
        """contract_renewal_arrears_annual defaults to None."""
        assert _base_scenario().contract_renewal_arrears_annual is None

    def test_arrears_zero_accepted(self) -> None:
        """contract_renewal_arrears_annual=0 is valid."""
        s = _base_scenario(contract_renewal_arrears_annual=Decimal(0))
        assert s.contract_renewal_arrears_annual == Decimal(0)

    def test_arrears_positive_accepted(self) -> None:
        """A positive contract_renewal_arrears_annual is accepted."""
        s = _base_scenario(contract_renewal_arrears_annual=Decimal("2400.00"))
        assert s.contract_renewal_arrears_annual == Decimal("2400.00")

    def test_negative_arrears_raises(self) -> None:
        """Negative contract_renewal_arrears_annual is rejected."""
        with pytest.raises(ValidationError, match="contract_renewal_arrears_annual"):
            _base_scenario(contract_renewal_arrears_annual=Decimal(-1))
