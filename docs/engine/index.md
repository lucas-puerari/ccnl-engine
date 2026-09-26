# Engine

The engine takes a payroll scenario — employee, employment relationship, and
applicable rules — and returns a fully itemised `PayrollResult`. It is a pure
function: given the same inputs and the same knowledge base version, it always
produces the same output.

## Entry point: `PayrollEngine`

Construct the engine with `PayrollEngine.bundled()` and call
`calculate()` for a single pay run or `calculate_year()` for a full year:

```python
from datetime import date

from ccnl_engine import (
    Employer,
    EmploymentFacts,
    Headcount,
    PayrollEngine,
    PayrollRequest,
    PayrollRun,
)

engine = PayrollEngine.bundled()

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(),
        employer=Employer(headcount=Headcount(50)),
    )
)
print(result.period_gross)
print(result.period_net)
```

To add period-specific events (overtime, absences, benefits), pass them on
`PayrollRequest`:

```python
from ccnl_engine.payroll.domain.events import OvertimeEvent

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        events=(
            OvertimeEvent(
                event_date=date(2026, 1, 10),
                hours=8,
                hourly_rate=...,
                multiplier=...,
            ),
        ),
    )
)
```

`calculate()` returns a `PeriodCalculationResult` with gross, net, pay items,
and a full ledger of every accounting entry. See [API: Engine](../api/engine.md).

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
| `PayrollRequest` | Full period request: run, payment date, CCNL slug, level, employment facts, employer, events |
| `EmploymentFacts` | Contract shape: type, hours, seniority, ceiling status; impossible values are rejected on construction |
| `Employer` | The employer; its `Headcount` (at least 1) selects the INPS rate tier. Defaults to 50 employees |
| `PayrollRun` | The pay run: year, month, and run kind (regular / thirteenth / fourteenth) |
| `FamilyComposition` | Dependent spouse and children (Art. 12 TUIR) |
| `OvertimeEvent` | Overtime hours for a specific date |
| `AbsenceEvent` | Unpaid absence days in the period |
| `SickLeaveEvent` | Sick-leave calendar days |
| `FringeEvent` | Fringe-benefit value and threshold flag |
| `WelfareEvent` | Welfare benefit annual amount |
| `BonusEvent` | PdR bonus amount and eligibility |

Full type reference: [API: Engine](../api/engine.md).

## Output: `PayrollResult`

The result contains every gross, net, and cost component. Key fields:

```python
result.period_gross         # gross entitlement for the period (before absence deductions)
result.period_net           # net pay for this period
result.period_employer_cost # total employer cost (gross + contributions + TFR accrual)
result.unpaid_absence_deduction  # wages withheld for unpaid absences
result.closing_state        # YTD state — pass as opening_state for the next period
result.pay_items            # all pay items produced
result.ledger_entries       # full accounting ledger
result.capability_report    # feature support and confidence for this CCNL
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
