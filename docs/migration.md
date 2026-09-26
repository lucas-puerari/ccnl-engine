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
  and no longer suppress the trattamento integrativo of the new year.  Each one records a decision with capability
  `trattamento_integrativo_recovery`.
- `KnowledgeRepository` gains `load_variable_pay_rules(year)` and
  `load_family_deduction_rules(year)`; a custom repository must implement
  them.
- New public names: `OpeningBalances`, `RecoveryObligation`, `RecoveryPlan`.

## Credit accounts and run ids

| Before | After |
|---|---|
| `state.ytd.closed_run_ids: frozenset[str]` | `tuple[PayrollRunId, ...]` in closing order; `PayrollRunId.parse("2026-01-regular")` |
| `OpeningBalances(closed_run_ids=frozenset({"2026-06-regular"}))` | `OpeningBalances(closed_run_ids=(PayrollRunId.parse("2026-06-regular"),))` |
| `obligations.recovery_of(tax_year)` | `obligations.recovery_of(tax_year, kind)`, kind `"trattamento_integrativo"` or `"somma_esente"` |
| `SommaEsenteAccount(recognized=...)` only | `CreditAccount` schema: `recognized`, `recovered`, `due`, `reason`, `net`, `residual` |
| bare period run id `"2026_01"` in item ids | `"2026-01-regular"`, the regular run of the month |

- A run already closed, of a year after the tax year, or before a closed run
  of the tax year raises `InvalidInputError` (feature `payroll_run`), a
  subclass of `ValueError` as before.
- Every YTD total rejects a negative amount. A run producing one fails with
  `DataIntegrityError`; an `OpeningBalances` with one raises
  `InvalidInputError` naming the account field (`EarningsYtd.gross`).
- The somma esente is settled at the conguaglio: the credits of a full year
  now add up to the annual amount (before, the last slot paid a plain share
  and the total could drift by several EUR from the annual due). An excess
  is recovered in full up to 60 EUR, in ten installments above it
  (L. 207/2024 art. 1 c. 7). Every run records a decision with capability
  `somma_esente`; carried installments record `somma_esente_recovery`.
- `OpeningBalances` gains `somma_esente_recovered`.
- `PeriodState.SCHEMA_VERSION` is now 3: a persisted state of version 2
  needs its closed run ids parsed into `PayrollRunId` and its credit accounts
  read with `due` and `reason` unset.
- New public name: `PayrollRunId`.

## Decisions and capability report

- `result.decisions` now also holds the decisions of the tax credits
  (`ulteriore_detrazione_lavoro`, `trattamento_integrativo`), of the worker
  category, of seniority, of family deductions and of the PdR substitute tax.
  Filter by `capability` instead of assuming only surtax or regime records.
  `YearCalculationResult.decisions` concatenates the decisions of every run.
- The capability report traces each feature from what the run executed: an
  event present in the request with no effect is skipped, and the two credits
  are no longer always computed.  A surtax without a table is now reported as
  an `unresolved` gap (`CapabilityGapKind.UNRESOLVED`).
- `trattamento_integrativo` and `ulteriore_detrazione_lavoro` moved from
  `ccnl_engine.payroll.service.irpef` to
  `ccnl_engine.payroll.service.irpef_credits`.

## Invariants and input checks

- The reconciliation invariants have descriptive codes instead of `I1` to
  `I19` and `L1` to `L4` (for example `net_identity` for `I9`,
  `employee_contribution_non_negative` for `L3`); see the
  [glossary](domain/glossary.md#reconciliation-invariants). The code is the
  `invariant_id` of a `ReconciliationViolation` and appears as `[code]` in
  the `DataIntegrityError` message.
- `legal_invariants` is renamed `sign_invariants`; `reconcile()` takes an
  optional `RunFacts` for the checks that need facts the result does not
  carry.
- `PeriodCalculationRequest` rejects a field of the wrong type (a raw `int`
  for `weekly_hours`, a string for `payment_date`) with `InvalidInputError`
  instead of an `AttributeError` later, and a regular run for a month
  without a day of employment with `InvalidInputError`.
- The IRPEF projection enters the current run with its actual employee
  INPS (IVS ceiling and 1% addizionale included) instead of the total rate
  times the gross; only the slots still to come are projected at the rate.
  Above the 1% addizionale threshold the conguaglio now settles on the final
  taxable income: for bancari-abi QD4 in 2026 the IRPEF withheld over the
  year falls by 22.19 EUR (18,333.08 to 18,310.89 EUR). Below the threshold
  the annual IRPEF is unchanged and single runs can move by a cent.
- Unpaid absences above the monthly pay of the run raise `InvalidInputError`
  instead of `DataIntegrityError`. Absences that leave less pay than the
  IRPEF and surtax due no longer raise `OutOfScopeError`: the taxes are
  withheld up to the pay left and the rest is carried in
  `state.ytd.shortfall` to the next runs (see
  [Fiscal: shortfall](engine/fiscal.md#pay-that-does-not-cover-the-tax)).
  Metalmeccanico C3 with 160 absence hours in January 2026 now nets
  0.00 EUR, withholding 143.25 of the 162.33 EUR of IRPEF due, and February
  withholds the 19.08 EUR carried. `OutOfScopeError` (reason
  `withholding_shortfall`) remains only when the other deductions exceed
  the pay left.

## Fiscal rule corrections

- The ulteriore detrazione (L. 207/2024 art. 1 c. 6) recognized by the
  withholding is tracked in `state.ytd.ulteriore_detrazione`. An excess
  found at the conguaglio above 60 EUR is recovered in ten installments
  (c. 7): the first on the conguaglio, nine from the first run of the next
  year. Before, the conguaglio took it back in full. No bundled scenario
  changes: none reaches the conguaglio with the deduction no longer due.
- `OpeningBalances` accepts `*_due` and `*_reason` for each credit, the
  ulteriore detrazione totals and the IRPEF and surtax shortfall.
- The capability catalog declares `somma_esente`, `withholding_shortfall`
  and the two substitute tax regimes (`partially_computed`: their
  eligibility rests on the declared prior income).
- One-off income of a run (bonus, overtime, ordinary arrears, excess PdR,
  ratei settled at termination) has its IRPEF withheld on that run: the net
  annual IRPEF with the income less the net annual IRPEF without it. Before,
  that tax was spread over the remaining slots, so a 20,000 EUR bonus in
  November left the tredicesima run with a negative net and the year failed
  with `DataIntegrityError`. The annual IRPEF is unchanged; the runs that
  pay one-off income withhold more and the later runs less.
- The regional and municipal surtaxes are due only when the net IRPEF
  (gross less the deductions) is due, not the gross IRPEF. A 12-hour
  part-time Metalmeccanico C3 in Lombardia no longer withholds 93.71 EUR of
  regional surtax a year; the decisions record `no_irpef_due`.
- The work deduction, the ulteriore detrazione and the trattamento
  integrativo follow `days / 365` without truncating the day ratio to four
  decimals: 92 days of the 1,955 EUR deduction give 492.77 EUR instead of
  492.66. The ulteriore detrazione is rounded to cents.
- The somma esente percentage is chosen on the employment income
  annualised to the whole year and applied to the income of the year: a
  Metalmeccanico C3 ended on 31 May receives 507.90 EUR (4.8%) instead of
  560.80 (5.3%).
- A run with a somma esente due carries the `provisional` issue
  `somma_esente_income_assumed`: the reddito complessivo is taken as the
  employment income. Low-income results that were `final` are now
  `provisional`. `YearCalculationResult.issues` lists an issue repeated on
  every run once, at its first run (same `code` and `message`); the issues
  of each run stay on `period_results`.
- The projection of a future tredicesima or quattordicesima uses the rateo
  accrued on the employment period instead of a full month: a worker hired
  on 1 July withholds evenly over the seven slots of the year instead of
  overwithholding until the conguaglio.
