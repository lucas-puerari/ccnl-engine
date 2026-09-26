# Payroll state and the year change

Every run opens with a `PayrollState` and returns the next one as
`result.closing_state`. The state has two parts with different lifetimes:

| Part | Type | Lifetime | Holds |
|---|---|---|---|
| `state.ytd` | `TaxYearState` | one tax year | run counters, withholding slots, closed run ids, YTD earnings, fringe, tax withheld, trattamento integrativo, somma esente, night/holiday/shift cap |
| `state.obligations` | `EmploymentObligations` | the employment | installment recoveries still running (D.L. 3/2020 art. 1 c. 3) |

`state.tax_year` is a shortcut for `state.ytd.tax_year`.

## Within a tax year

Pass the `closing_state` of a run as the `opening_state` of the next run of
the same tax year. `PayrollState.zero()` opens the first run of a new
employment. A run attributed to another tax year
(see [tax year attribution](index.md)) is rejected with `InvalidInputError`.

## Opening the next tax year

`PayrollEngine.close_tax_year(closing_state)` takes the closing state of the
last run of year N and returns the opening state of N+1:

- `ytd` restarts: no run closed, every YTD account at zero, bound to N+1.
  This includes the night, holiday and shift cap account, which is annual.
- `obligations` is carried unchanged. A recovery keeps the tax year that
  opened it; its remaining installments are due from the first run of N+1,
  one per run, until the last one.

The input must be a year-end state: bound to a tax year, with every
withholding slot of the year closed. The state after December but before the
tredicesima is rejected, and so is a hand-built state that never ran.

Single runs computed with `PayrollEngine.calculate()` use the standard
withholding schedule of the CCNL. For an employment that did not cover the
whole year that schedule is never completed, so `close_tax_year` rejects the
state: compute the year with `calculate_year`, whose schedule follows the
employment, or build the N+1 state with `OpeningBalances`.

`PayrollState.zero()` is the state of a new employment: used at the year
change it drops every obligation, which cannot be told apart from a new
employment.

```python
from ccnl_engine import PayrollEngine, PayrollYearRequest

engine = PayrollEngine.bundled()
year_2026 = engine.calculate_year(
    PayrollYearRequest(
        year=2026,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
    )
)
opening_2027 = engine.close_tax_year(year_2026.period_results[-1].closing_state)
# engine.calculate_year(PayrollYearRequest(year=2027, ..., opening_state=opening_2027))
```

`calculate_year` accepts `opening_state` only when it closes no run of the
year: `PayrollState.zero()` or the result of `close_tax_year`.

## Recovery carried into the next year

The conguaglio of year N can find that trattamento integrativo was not due.
Above 60 EUR the recovery runs in eight equal installments from the payslip
of the conguaglio (D.L. 3/2020 art. 1 c. 3), so it often continues into N+1.

- Installments posted in N enter the N `TrattamentoAccount.recovered`.
- Installments posted in N+1 are a negative tax credit line on the payslip
  (`trattamento_integrativo_recovery_{N}_{run_id}`, account `CREDITS`). They
  do not enter the N+1 trattamento integrativo account, and the N+1
  trattamento integrativo is computed as for any other year.
- Invariant I19 checks that each carried recovery posts its next
  installment and closes one installment further along.

At most one recovery per origin year is held. The recovery opened by the
conguaglio of the current year runs inside the conguaglio, as before.

## Balances from a previous provider

`OpeningBalances` takes the progressive totals of a previous payroll
provider for one tax year, with the recoveries still running, and validates
them: every amount non-negative with at most two decimals, trattamento
recovered not above recognized, taxed fringe not above fringe value, no
recovery opened after the tax year. `to_state()` returns the `PayrollState`
for the first run the engine computes.

```python
from decimal import Decimal

from ccnl_engine import OpeningBalances, RecoveryObligation, RecoveryPlan

opening = OpeningBalances(
    tax_year=2027,
    recoveries=(
        RecoveryObligation(
            tax_year=2026,
            plan=RecoveryPlan(
                kind="trattamento_integrativo",
                original_amount=Decimal(160),
                installment_amount=Decimal(20),
                installments_total=8,
                installments_posted=4,
            ),
        ),
    ),
).to_state()
```
