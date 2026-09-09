# Engine

The engine takes a payroll scenario — employee, employment relationship, and
applicable rules — and returns a fully itemised `PayrollResult`. It is a pure
function: given the same inputs and the same knowledge base version, it always
produces the same output.

## Entry point: `compute()`

```python
from ccnl_engine import compute, load_ccnl, load_year_rules
from ccnl_engine import Employee, ContractPosition, WorkArrangement, Permanent
from datetime import date

ccnl  = load_ccnl("metalmeccanico-federmeccanica.json")
rules = load_year_rules(2026, ccnl.meta.tax_sector, num_employees=50)

employee = Employee(
    position=ContractPosition(
        level_code="C3",
        as_of=date(2026, 1, 1),
        employment=Permanent(),
    ),
    arrangement=WorkArrangement(),
)

calculation = compute(ccnl, rules, employee)
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
   ↓
10. Assemble PayrollResult: gross, net, employer cost, scope, warnings, confidence
```

Steps 7–9 are fiscal and can be parameterised heavily. See
[Fiscal](fiscal.md) for the full reference.

## Input types

| Type | What it describes |
|---|---|
| `Employee` | The worker: position, arrangement, tax profile |
| `ContractPosition` | Level code, reference date, employment type |
| `WorkArrangement` | Hours, seniority, second-level allowances, salary overrides |
| `TaxProfile` | Fiscal inputs: region, comune, mortgage interest |
| `Employer` | Employer-side inputs: headcount tier, second-level supplements |

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
