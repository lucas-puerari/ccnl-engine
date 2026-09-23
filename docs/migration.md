# Migration guide: period-first API

## What changed

The preferred entry point changed from `estimate_annual()` to `PayrollEngine`.

`estimate_annual()` computed an annual gross-to-net projection in a single call.
`PayrollEngine.calculate()` computes one payroll run at a time, threading
YTD state (`PeriodState`) between runs. `PayrollEngine.calculate_year()` does
the full sequence in one call.

## Before (legacy)

```python
from datetime import date
from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual
from ccnl_engine import AnnualEstimateInput, Employee, Employer, Employment, Permanent

result = estimate_annual(
    AnnualEstimateInput(
        employee=Employee(level_code="C3"),
        employment=Employment(
            ccnl="metalmeccanico-federmeccanica.json",
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 1, 1),
        ),
    )
).result

print(result.net_annual)
print(result.earnings.gross_monthly)
```

## After (preferred)

```python
from ccnl_engine import PayrollEngine, PayrollRequest, PayrollRun, PayrollYearRequest
from ccnl_engine.payroll.domain.calendar import ExtraMonthSchedule, WorkCalendar

engine = PayrollEngine.from_builtin_data()

# Single period
result = engine.calculate(PayrollRequest(
    run=PayrollRun.regular(year=2026, month=1),
    payment_date=date(2026, 1, 28),
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
))
print(result.period_gross)
print(result.period_net)

# Full year (13-month calendar)
year = engine.calculate_year(PayrollYearRequest(
    year=2026,
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    calendar=WorkCalendar(
        year=2026,
        extra_months=(ExtraMonthSchedule(name="tredicesima", payment_month=12),),
    ),
))
print(year.annual_gross)
```

## Key differences

| | `estimate_annual` | `PayrollEngine.calculate_year` |
|---|---|---|
| Input model | `AnnualEstimateInput` | `PayrollYearRequest` |
| Output model | `AnnualEstimate` | `YearCalculationResult` |
| YTD state | internal, not exposed | threaded via `PeriodState` |
| Run sequence | implicit (annual) | explicit via `WorkCalendar` |
| Events | via `PeriodPayrollInput` | via `period_events` dict |

## `estimate_annual` is still available

`estimate_annual` is no longer in the `ccnl_engine` root namespace but
remains at `ccnl_engine.engine.payroll.service.orchestrator.estimate_annual`.
Import it directly if you need it during a migration.

No compatibility shim is planned. Migrate to `PayrollEngine` for new code.
