"""L3 work rules: overtime, absence, leave, sick pay, welfare, bonus.

Period-specific events (overtime, absences, benefits) live in PayPeriod and
are passed to estimate_period_effects() alongside the structural
AnnualPayrollScenario.  The engine reports each as an informational line item
— the amounts do NOT mutate gross_annual or net_annual.  Check
calculation_scope to see which features the CCNL actually models.
"""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    AbsenceDays,
    AnnualPayrollScenario,
    BonusInput,
    Employee,
    Employer,
    Employment,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    PayPeriod,
    Permanent,
    SickInput,
    WelfareInput,
    estimate_period_effects,
)

scenario = AnnualPayrollScenario(
    employee=Employee(level_code="C3"),
    employment=Employment(
        ccnl="metalmeccanico-federmeccanica.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        as_of=date(2026, 9, 1),
    ),
)
period = PayPeriod(
    # Overtime: 8 weekday hours + 4 night hours in the period
    time_supplements=OvertimeHours(
        weekday_hours=Decimal(8),
        night_hours=Decimal(4),
    ),
    # 1 day absent without pay
    absence_days=AbsenceDays(unpaid_days=Decimal(1)),
    # 2 leave days consumed
    leave_input=LeaveInput(taken_days=Decimal(2)),
    # 5 calendar days of illness
    sick_input=SickInput(sick_days=Decimal(5)),
    # Fringe benefits (e.g. company car, below the €1 000 threshold)
    fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal(800)),
    # Welfare contributions (always tax-exempt under Art. 51 c. 2 TUIR)
    welfare_input=WelfareInput(annual_amount=Decimal(500)),
    # PdR-eligible performance bonus
    bonus_input=BonusInput(
        annual_amount=Decimal(1000),
        eligible_for_pdr=True,
    ),
)
calculation = estimate_period_effects(scenario, period)

r = calculation.result

# ── Base payroll (L1 + L2) ────────────────────────────────────────────────────
print(f"Gross monthly:              {r.gross_monthly} EUR")
print(f"Net annual:                 {r.net_annual} EUR")
print(f"Employer cost:              {r.employer_cost_annual} EUR")

# ── L3: time supplements (informational) ──────────────────────────────────────
print(f"\nOvertime supplement:        {r.overtime_supplement_monthly} EUR/month")
print(f"Night supplement:           {r.night_supplement_monthly} EUR/month")
print(f"Holiday supplement:         {r.holiday_supplement_monthly} EUR/month")

# ── L3: absence (informational) ───────────────────────────────────────────────
print(f"\nAbsence deduction:          {r.absence_deduction_monthly} EUR/month")
print(f"Effective gross:            {r.effective_gross_monthly} EUR/month")

# ── L3: leave (informational) ─────────────────────────────────────────────────
print(f"\nLeave accrued this period:  {r.leave_accrued_days_monthly} days")
print(f"Leave balance:              {r.leave_balance_days} days")

# ── L3: sickness (informational) ──────────────────────────────────────────────
print(f"\nINPS indemnity:             {r.sick_inps_indemnity_monthly} EUR/month")
print(f"Employer integration:       {r.sick_company_integration_monthly} EUR/month")

# ── L3: benefits (informational) ──────────────────────────────────────────────
print(f"\nFringe benefit (annual):    {r.fringe_benefit_annual} EUR")
print(f"Welfare (annual):           {r.welfare_annual} EUR")
print(f"Bonus (annual):             {r.bonus_annual} EUR")
print(f"PdR flat tax (annual):      {r.bonus_pdr_flat_tax_annual} EUR")

# ── Scope: which features were actually computed? ──────────────────────────────
print("\nCalculation scope:")
for item in r.calculation_scope:
    if item.feature.startswith((
        "overtime",
        "absence",
        "leave",
        "sickness",
        "fringe",
        "welfare",
        "bonus",
    )):
        print(f"  {item.feature:<30} {item.status}")
