# Work rules (L3)

L3 inputs let callers attach work-event data to a payroll scenario.
The engine computes each supplement or deduction and reports it in `PayrollResult`
**as an informational line item — it does not fold the amounts into `gross_annual`
or `net_annual`**. This keeps the base payroll reproducible and independent of
month-by-month events, while still giving callers auditable breakdowns.

Each L3 feature is gated by CCNL support. If the active contract does not model
a feature, the output is `0` and `calculation_scope` records
`status="not_computed"` with a message explaining why.

---

## Inputs

All seven input types are frozen dataclasses. Pass any combination as keyword
arguments on `PayrollScenario`:

```python
from ccnl_engine import (
    AbsenceDays, BonusInput, FringeBenefitInput,
    LeaveInput, OvertimeHours, SickInput, WelfareInput,
)
```

### `OvertimeHours`

Hours worked beyond the standard schedule in the period.

| Field | Type | Description |
|---|---|---|
| `weekday_hours` | `Decimal` | Daytime weekday overtime (straordinario diurno) |
| `night_hours` | `Decimal` | Weekday night hours (lavoro notturno) |
| `holiday_hours` | `Decimal` | Daytime public-holiday hours |
| `night_holiday_hours` | `Decimal` | Night hours on a public holiday |

All fields default to `0`. At least one must be positive.

### `AbsenceDays`

| Field | Type | Description |
|---|---|---|
| `unpaid_days` | `Decimal` | Days absent without pay; must be >= 0 |

The engine applies either the *26-divisor* or the *daily-hours* method,
depending on the CCNL.

### `LeaveInput`

| Field | Type | Description |
|---|---|---|
| `taken_days` | `Decimal` | Leave days consumed in the period; must be >= 0 |

Reports `leave_accrued_days_monthly` and `leave_balance_days` in the result.

### `SickInput`

| Field | Type | Description |
|---|---|---|
| `sick_days` | `Decimal` | Calendar days of illness in the period; must be >= 0 |
| `cumulative_sick_days` | `Decimal \| None` | Running total for the year (determines integration band) |

Reports the INPS indemnity and the employer integration complement.

### `FringeBenefitInput`

| Field | Type | Description |
|---|---|---|
| `annual_amount` | `Decimal` | Total fringe-benefit value for the year |
| `has_dependent_children` | `bool` | Determines statutory threshold (€1 000 or €2 000) |

Reports the tax-exempt and taxable portions under Art. 51 c. 3 TUIR.

### `WelfareInput`

| Field | Type | Description |
|---|---|---|
| `annual_amount` | `Decimal` | Welfare annual amount (Art. 51 c. 2 TUIR; fully tax-exempt) |

### `BonusInput`

| Field | Type | Description |
|---|---|---|
| `annual_amount` | `Decimal` | Total bonus for the year |
| `eligible_for_pdr` | `bool` | Apply PdR preferential flat-tax regime when `True` |

When `eligible_for_pdr=True` the engine checks the statutory income ceiling and,
if met, applies the flat tax (*imposta sostitutiva*) up to the statutory maximum
(`PdRRules.max_amount`). The rate and ceiling are read from the versioned ruleset
for the year — not hardcoded. Amounts above the ceiling are reported as ordinarily
taxable.

---

## Attaching L3 inputs to a scenario

```python
from datetime import date
from decimal import Decimal
from ccnl_engine import (
    AbsenceDays, BonusInput, Employee, Employer, Employment,
    FringeBenefitInput, LeaveInput, OvertimeHours,
    PayrollScenario, Permanent, SickInput, WelfareInput, compute,
)

calculation = compute(PayrollScenario(
    employee=Employee(level_code="C3"),
    employment=Employment(
        ccnl="metalmeccanico-federmeccanica.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        calculation_date=date(2026, 9, 1),
    ),
    time_supplements=OvertimeHours(
        weekday_hours=Decimal(8),
        night_hours=Decimal(4),
    ),
    absence_days=AbsenceDays(unpaid_days=Decimal(1)),
    leave_input=LeaveInput(taken_days=Decimal(2)),
    sick_input=SickInput(sick_days=Decimal(5)),
    fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal(800)),
    welfare_input=WelfareInput(annual_amount=Decimal(500)),
    bonus_input=BonusInput(annual_amount=Decimal(1000), eligible_for_pdr=True),
))

r = calculation.result
print(r.overtime_supplement_monthly)        # weekday overtime gross
print(r.night_supplement_monthly)           # night premium
print(r.absence_deduction_monthly)          # deduction for unpaid absence
print(r.leave_accrued_days_monthly)         # days accrued this period
print(r.sick_inps_indemnity_monthly)        # INPS indemnity (informational)
print(r.sick_company_integration_monthly)   # employer complement
print(r.fringe_benefit_annual)              # total fringe (exempt+taxable)
print(r.welfare_annual)                     # welfare (always exempt)
print(r.bonus_annual)                       # total bonus
print(r.bonus_pdr_flat_tax_annual)          # imposta sostitutiva (0 if not eligible)
```

---

## Output fields

All L3 output fields are on `PayrollResult`. They default to `0` when the
corresponding input is not supplied.

| Field | Description |
|---|---|
| `overtime_supplement_monthly` | Weekday overtime gross supplement |
| `night_supplement_monthly` | Night-work premium |
| `holiday_supplement_monthly` | Holiday-work premium |
| `absence_deduction_monthly` | Gross deduction for unpaid absence days |
| `effective_gross_monthly` | `gross_monthly − absence_deduction_monthly` |
| `leave_accrued_days_monthly` | Leave days accrued in the period |
| `leave_balance_days` | Cumulative leave balance |
| `sick_inps_indemnity_monthly` | INPS indemnity for sick days |
| `sick_company_integration_monthly` | Employer integration over INPS |
| `fringe_benefit_annual` | Total fringe-benefit value |
| `welfare_annual` | Welfare amount (always tax-exempt) |
| `bonus_annual` | Total bonus |
| `bonus_pdr_flat_tax_annual` | Imposta sostitutiva on PdR-eligible portion |

---

## Scope and not-computed features

Each L3 feature is reported in `calculation_scope`. When a CCNL does not model
a feature, the engine sets `status="not_computed"` and logs a warning:

```python
for item in calculation.result.calculation_scope:
    print(item.feature, item.status)
# overtime         verified
# sickness         not_computed   ← CCNL does not model sick-pay integration
```

See [Trust: Scope](../trust/index.md) for details on how scope items are
populated.
