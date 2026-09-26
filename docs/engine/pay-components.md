# Pay components

This page covers the runtime knobs that adjust gross pay beyond the CCNL table
minimum: part-time scaling, seniority, and individually negotiated salary.

See [Domain: Components](../domain/components.md) for the legal background.

## Part-time

Pass `part_time_ratio` (a `Decimal` between 0 and 1 exclusive) to `Employee`.
Base salary, seniority, and contractual allowances all scale proportionally.
Individually frozen *ad personam* amounts do not scale.

```python
--8 < --"docs/examples/04_part_time.py"
```

## Seniority increments (*scatti di anzianità*)

Two equivalent ways to specify seniority:

- `SeniorityByCount(n)` — you already know how many increments have matured.
- `SeniorityByMonths(m)` — total service months; the engine derives the count from
  the CCNL cadence.

```python
--8 < --"docs/examples/05_seniority.py"
```

### Worker category

Some CCNLs price seniority by legal category (art. 2095 c.c.): in Servizi
Postali in Appalto FISE an *operaio* and an *impiegato* on the same level earn
different increments. Pass the category as `EmploymentFacts.category`, a
`WorkerCategory` (`operaio`, `impiegato`, `quadro`, `dirigente`). The same
value selects category-specific INPS employer rates (e.g. *impiegati* in
artigianato).

- A level reserved to one category (e.g. a `quadro` level) supplies it when
  you omit it; declaring a different category raises `InvalidInputError`.
- When increments for the level exist only per category and you pass
  `seniority_months` without a category, the calculation raises
  `InvalidInputError` instead of silently dropping the increment.

## Individually negotiated salary (*RAL concordata*)

When a worker's annual gross is negotiated above the CCNL minimum, pass a
`SalaryOverrides` with a `RalOverride`. The engine uses this figure directly and
derives monthly and hourly rates from it, instead of building pay from the level
table.

```python
--8 < --"docs/examples/09_negotiated_ral.py"
```

**API reference:** [`WorkArrangement`](../api/engine.md),
[`SeniorityByCount`, `SeniorityByMonths`](../api/engine.md),
[`SalaryOverrides`, `RalOverride`](../api/engine.md)

## Bilateral funds (*fondi bilaterali*)

Many CCNLs require contributions to sector bilateral bodies (health funds,
training funds, supplementary pension). Pass a tuple of fund inputs on
`AnnualEstimateInput.bilateral_funds`:

```python
from decimal import Decimal
from ccnl_engine import FlatMonthlyFund, RateFund

# A fixed-amount fund: e.g. EST (€2.00/month employee + €13.00/month employer)
est = FlatMonthlyFund(
    employee_monthly=Decimal("2.00"),
    employer_monthly=Decimal("13.00"),
)

# A rate-based fund applied to the TFR base: e.g. Fon.Te (0.55 % + 1.55 %)
fon_te = RateFund(
    employee_rate=Decimal("0.0055"),
    employer_rate=Decimal("0.0155"),
    base="tfr_base",          # or "gross_annual"
)

scenario = AnnualEstimateInput(
    ...
    bilateral_funds=(est, fon_te),
)
```

The engine annualises flat funds (× 12) and applies rates to the chosen base.
Results appear in `PayrollResult`:

| Field | Effect |
|---|---|
| `bilateral_employee_annual` | Deducted from `net_annual` |
| `bilateral_employer_annual` | Added to `employer_cost_annual` |

When `bilateral_funds` is empty (the default), both fields are `0` and the
`NO_BILATERAL_FUNDS` flag appears in `fiscal_simplifications`.

**API reference:** [`FlatMonthlyFund`, `RateFund`](../api/engine.md)
