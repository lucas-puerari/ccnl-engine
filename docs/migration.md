# Migration guide: period-first API

## What changed

The entry point changed from `estimate_annual()` to `PayrollEngine`.

`estimate_annual()` computed an annual gross-to-net projection in a single call.
`PayrollEngine.calculate()` computes one payroll run at a time, threading
YTD state (`PeriodState`) between runs. `PayrollEngine.calculate_year()` does
the full sequence in one call.

## Before (legacy — removed)

```python
from datetime import date
# estimate_annual was removed in v0.5; use PayrollEngine instead.
result = ...  # AnnualEstimateInput / estimate_annual no longer available
```

## After (current API)

```python
from datetime import date

from ccnl_engine import PayrollEngine, PayrollRequest, PayrollRun, PayrollYearRequest

engine = PayrollEngine.bundled()

# Single period
result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
    )
)
print(result.period_gross)
print(result.period_net)

# Full year: the calendar is derived from the CCNL (13 runs for metalmeccanico)
year = engine.calculate_year(
    PayrollYearRequest(
        year=2026,
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
    )
)
print(year.annual_gross)
```

## Key differences

| | Legacy (`estimate_annual`) | `PayrollEngine.calculate_year` |
|---|---|---|
| Input model | `AnnualEstimateInput` | `PayrollYearRequest` |
| Output model | `AnnualEstimate` | `YearCalculationResult` |
| YTD state | internal, not exposed | threaded via `PeriodState` |
| Run sequence | implicit (annual) | derived from the CCNL; `CalendarOverride` with a reason to change it |
| Events | via `PeriodPayrollInput` | via `period_events` dict |

## `estimate_annual` is removed

`estimate_annual` and the `ccnl_engine.engine.payroll` namespace were removed
in v0.5. Migrate to `PayrollEngine` for all new code.
