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

## Surtax codes and decisions

- `regione` takes the ISO 3166-2:IT region code (`IT-45` Emilia-Romagna,
  `IT-25` Lombardia, ...), with `IT-BZ` and `IT-TN` for the autonomous
  provinces, listed in `ccnl_engine.payroll.domain.jurisdiction.REGION_CODES`.
  A region name such as `"Lombardia"`, a short code such as `"ER"` and
  `"IT-32"` (Trentino-Alto Adige) now raise `InvalidInputError`, like a
  malformed Belfiore code.  Before, a code such as `"ER"` matched no regional row and the
  regional surtax was silently zero.
- A well-formed code without a table row makes the result `incomplete`, with
  the issue `regional_surtax_unknown` or `municipal_surtax_unknown`.
- `ccnl_engine.payroll.domain.fiscal.FiscalSimplification` is removed: read the
  surtax outcome from `result.decisions` (capabilities
  `addizionale_regionale`, `addizionale_comunale`).

## Payroll state: tax year and obligations

`PayrollState` (`PeriodState`) is now a composite of the tax year state and
the obligations that survive the year change.

| Before | After |
|---|---|
| `state.earnings`, `state.tax`, `state.fringe`, `state.trattamento`, `state.somma_esente`, `state.work_time_regime` | `state.ytd.<same name>` |
| `state.regular_periods_closed`, `state.tax_withholding_periods_closed`, `state.closed_run_ids` | `state.ytd.<same name>` |
| `state.tax_year` | unchanged (shortcut for `state.ytd.tax_year`) |
| `PayrollState(tax=TaxYtd(...), ...)` | `PayrollState(ytd=TaxYearState(tax=TaxYtd(...), ...))`, or `OpeningBalances(...).to_state()` |
| `TrattamentoAccount(plan=...)` | `PayrollState(obligations=EmploymentObligations(recoveries=(RecoveryObligation(tax_year, plan),)))` |
| `closing_state.zero()` to start a new year (dropped a running recovery) | `PayrollEngine.close_tax_year(closing_state)` |
| `calculate_year` always started from zero | `PayrollYearRequest.opening_state` / `calculate_year(opening_state=...)` |

- `PeriodState.SCHEMA_VERSION` is now 2.
- `TaxYearState.withholding_slots` records the slots of the schedule of the
  last run; `close_tax_year` requires them all closed.
- Installments of a recovery carried from an earlier year are posted as a
  negative tax credit line `trattamento_integrativo_recovery_{year}_{run_id}`
  and no longer suppress the trattamento integrativo of the new year.
- `KnowledgeRepository` gains `load_variable_pay_rules(year)` and
  `load_family_deduction_rules(year)`; a custom repository must implement
  them.
- New public names: `OpeningBalances`, `RecoveryObligation`, `RecoveryPlan`.
