# Engine

The engine takes a payroll scenario — employee, employment relationship, and
applicable rules — and returns a fully itemised `PayrollResult`. It is a pure
function: given the same inputs and the same knowledge base version, it always
produces the same output.

## Entry point: `compute()`

```python
from datetime import date
from ccnl_engine import (
    Employee, Employer, Employment,
    OvertimeHours, PayrollScenario, Permanent, compute,
)

calculation = compute(PayrollScenario(
    employee=Employee(level_code="C3"),
    employment=Employment(
        ccnl="metalmeccanico-federmeccanica.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        calculation_date=date(2026, 1, 1),
    ),
    # L3: optional work-rules inputs (informational — not in net_annual)
    time_supplements=OvertimeHours(weekday_hours=8),
))

result = calculation.result
```

`compute()` returns a `Calculation`, not a `PayrollResult` directly. The
`Calculation` wraps the result with the engine version, ruleset identities,
and a serialisable input snapshot — everything needed to reproduce or audit
the figure later. See [Trust: Versioning](../trust/index.md#versioning).

## Computation chain

The engine applies rules in a fixed sequence:

```
1. Resolve time-series values (base salary, seniority amounts, hourly divisor)
   ↓
2. Apply part-time coefficient and apprenticeship percentage
   ↓
3. Add fixed allowances and second-level supplements
   ↓
4. Compute INPS contributions (employee + employer, NASpI addizionale if fixed-term)
   ↓
5. Compute TFR accrual (Art. 2120 c.c.)
   ↓
6. Compute employer contractual funds
   ↓
7. Compute IRPEF: bracket tax → work-income deduction → trattamento integrativo
   ↓
8. Apply regional + municipal surtax (when jurisdiction is provided)
   ↓
9. Apply Art. 12 family deductions and Art. 15 mortgage interest deduction
   (reduce irpef_net / net_annual; only when inputs are provided)
   ↓
10. Compute L3 work-rules supplements (informational — do not mutate gross/net):
    overtime pay, absence deduction, leave accrual, sick-pay integration,
    fringe benefits, welfare, PdR bonus
    ↓
11. Assemble PayrollResult: gross, net, employer cost, scope, warnings, confidence
```

Steps 7–9 are fiscal and can be parameterised heavily. See
[Fiscal](fiscal.md) for the full reference. Step 10 is optional — see
[Work rules](work-rules.md).

## Input types

| Type | What it describes |
|---|---|
| `PayrollScenario` | Top-level container: employee + employment + optional L3 inputs |
| `Employee` | The worker: level code, seniority, part-time, jurisdiction, agreement |
| `Employment` | CCNL file, contract type, employer, calculation date |
| `Employer` | Headcount tier, second-level allowances |
| `OvertimeHours` | Weekday/night/holiday overtime hours (L3, informational) |
| `AbsenceDays` | Unpaid absence days in the period (L3, informational) |
| `LeaveInput` | Leave days consumed (L3, informational) |
| `SickInput` | Sick-leave calendar days (L3, informational) |
| `FringeBenefitInput` | Fringe-benefit annual amount and threshold flag (L3, informational) |
| `WelfareInput` | Welfare annual amount (L3, informational) |
| `BonusInput` | Annual bonus and PdR eligibility (L3, informational) |
| `FamilyComposition` | Dependent spouse/children (Art. 12 TUIR; mutates net_annual) |
| `Art15Deductions` | Mortgage-interest deduction (Art. 15 TUIR; mutates net_annual) |

Full type reference: [API: Engine](../api/engine.md).

## Output: `PayrollResult`

The result contains every gross, net, and cost component. Key fields:

```python
result.gross_monthly          # total monthly gross (base + seniority + allowances)
result.net_annual             # annual net after INPS, IRPEF, surtax
result.employer_cost_annual   # total annual employer cost
result.confidence             # "low" | "medium" | "high"
result.calculation_scope      # list of ScopeItem(feature, status)
result.warnings               # active gaps the caller must know
```

See [Trust: Confidence](../trust/confidence.md) for how the three-tier
confidence score is derived.

## Guides

| Page | Contents |
|---|---|
| [Pay components](pay-components.md) | Part-time, seniority, RAL overrides |
| [Second level](second-level.md) | Territorial and company supplements |
| [Fiscal](fiscal.md) | IRPEF, surtax, family and Art. 15 deductions |
| [Domestic work](domestic-work.md) | Flat per-hour contributions, non-withholding employer |
| [Work rules](work-rules.md) | L3: overtime, absence, leave, sickness, bonus, welfare |
