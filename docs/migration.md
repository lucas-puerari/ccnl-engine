# Migration guide

## Rounding and bundled repository moved to their layers

Two internal modules moved so that the layers import in one direction only.
Names exported from `ccnl_engine` and amounts are unchanged.

| Before | After |
|---|---|
| `ccnl_engine.payroll.service.rounding` | `ccnl_engine.payroll.domain.rounding` |
| `ccnl_engine.knowledge.service.bundled_knowledge_repository` | `ccnl_engine.payroll.service.bundled_knowledge_repository` |

## Engine package flattened into capabilities

The `ccnl_engine.engine` wrapper is removed. Its subpackages are now
capabilities directly under `ccnl_engine`. Only internal module paths change:
names exported from `ccnl_engine` are unchanged, and so are amounts.

| Before | After |
|---|---|
| `ccnl_engine.engine.contract.*` | `ccnl_engine.contract.*` |
| `ccnl_engine.engine.tax.*` | `ccnl_engine.tax.*` |
| `ccnl_engine.engine.surtax.domain.rules` | `ccnl_engine.tax.domain.surtax_rules` |
| `ccnl_engine.engine.surtax.service.loaders` | `ccnl_engine.tax.service.surtax_loaders` |
| `ccnl_engine.engine.provenance.*` | `ccnl_engine.provenance.*` |
| `ccnl_engine.engine.metadata.domain.rules` | `ccnl_engine.provenance.domain.ruleset_identity` |
| `ccnl_engine.engine.diff.*` | `ccnl_engine.diff.*` |
| `ccnl_engine.engine.errors` | `ccnl_engine.shared.domain.errors` |
| `ccnl_engine.engine.primitives.domain.primitives` | `ccnl_engine.shared.domain.primitives` |
| `ccnl_engine.engine.io.service.*` | `ccnl_engine.knowledge.service.*` |
| `ccnl_engine.engine.capability_catalog` | `ccnl_engine.payroll.domain.capability_catalog` |
| `ccnl_engine.engine.knowledge_repository` | `ccnl_engine.payroll.application.knowledge_repository` |
| `PolicyResolver.load()` | `ccnl_engine.payroll.service.policy_loader.load_policy_resolver()` |

The paths in the "After" column of the next section predate this change: read
them through the table above.

## Legacy modules and aliases removed

Every public name is now imported from `ccnl_engine`; internal modules are
imported from the module that defines them. The re-export modules, the empty
`serialization` stubs and the alias names are removed without a compatibility
layer. Amounts are unchanged.

| Before | After |
|---|---|
| `from ccnl_engine.events import OvertimeEvent` (any work event) | `from ccnl_engine import OvertimeEvent` |
| `PayrollState` | `PeriodState` |
| `PayrollCalendar` | `WorkCalendar` |
| `ccnl_engine.api.PeriodInput` (any name of `ccnl_engine.api`) | `ccnl_engine.PeriodInput` |
| `ccnl_engine.engine.contract.domain.ccnl.CCNL` | `ccnl_engine.engine.contract.domain.identity.CCNL` (identity, coverage, metadata and enums); other names from their own module: `compensation`, `absence`, `category`, `seniority`, `sickness`, `working_time` |
| `ccnl_engine.engine.tax.domain.rules.YearRules` | `ccnl_engine.engine.tax.domain.ruleset.YearRules`; other names from `contribution_rules`, `credit_rules`, `irpef_rules`, `tfr_rules` |
| `ccnl_engine.engine.tax.service.loaders.load_year_rules` | `ccnl_engine.engine.tax.service.tax_annual_assembler.load_year_rules`; the other loaders from `tax_optional_loaders`, `tax_resource_reader`, `tax_tier_resolver` |
| `from ccnl_engine.engine.tax import load_year_rules` (and the same for `contract`, `surtax`, `diff`, `io`, `metadata`, `primitives`, `provenance`) | import from the defining module, e.g. `ccnl_engine.engine.surtax.service.loaders.load_surtax_rules` |
| `ccnl_engine.knowledge.version.__version__` | `ccnl_engine.knowledge.__version__` |
| `ccnl_engine.engine.serialization` | removed: it held no code |

Unused internals are removed as well: the `Ledger` and `Posting` classes and
the `AccountPolicy` alias of `payroll.domain.ledger`, `AnnualisedPay`,
`MonthlyPayChain.scaled_selective()`, `resolve_tax_computation` (use `compute_tax(...).computation`),
`RulesetIdentity.as_dict()`, and the contribution helpers
`inps_contribution`, `inps_employee_additional`, `tfr` and `fund_applies_to`
(the payroll uses `resolve_contributions`).

## PeriodInput and YearInput

The facade no longer takes a flat request. `calculate_period()` takes a
`PeriodInput` and `calculate_year()` a `YearInput`; both group the facts by
owner and are validated when built. There is no compatibility layer: every
name in the left column is removed.

| Before | After |
|---|---|
| `engine.calculate(PayrollRequest(...))` | `engine.calculate_period(PeriodInput(...))` |
| `engine.calculate_year(PayrollYearRequest(...))` | `engine.calculate_year(YearInput(...))` |
| `PayrollEngine.from_builtin_data()` | `PayrollEngine.bundled()` |
| `PayrollRequest.ccnl_slug`, `level_code` | `Employment.ccnl_slug`, `Employment.level_code` |
| `EmploymentFacts(...)` | `Employment(...)`, with the CCNL slug and the level |
| `EmploymentFacts(weekly_hours=25, full_time_weekly_hours=40)` | `Employment(weekly_hours=WeeklyHours(25), full_time_weekly_hours=WeeklyHours(40))` |
| `EmploymentFacts(seniority_months=60)` | `Employment(seniority_months=SeniorityMonths(60))` |
| `EmploymentFacts(started_on=..., ended_on=...)` | `Employment(employment_period=EmploymentPeriod(started_on, ended_on))` |
| `EmploymentFacts(contributable_hours=Decimal(108))` | `PeriodFacts(contributable_hours=ContributableHours(Decimal(108)))` |
| sector derived from the CCNL tax sector | `Employment.sector` (`EmploymentSector.PRIVATE` or `PUBLIC`), `None` means unknown |
| `Employer()` (50 employees when omitted) | `EmployerProfile(headcount=Headcount(n))`, required on every input |
| no employer activity | `EmployerProfile.activity` (`EmployerActivity`), `None` means unknown |
| `prior_income=` on `BonusEvent`, `NightShiftEvent`, `HolidayWorkEvent`, `ShiftWorkEvent` | `PriorYearTaxFacts(employment_income=...)` on the input, once |
| `substitute_tax_waived=True` on an event | `PriorYearTaxFacts(waived_regimes=frozenset({SubstituteTaxRegime.RINNOVO}))` |
| renewal signing date not received | `BonusEvent(kind="contract_renewal", agreement_signed_on=...)` |
| `regione`, `comune_belfiore`, `family_composition`, `has_dependent_children` on the request | `PeriodFacts` of the run |
| `events=` on `PayrollRequest` | `PeriodFacts(events=...)` |
| `period_events={3: (...)}` | `YearInput.periods={3: PeriodFacts(events=...)}` |
| `per_run_events={"2026-12-thirteenth": (...)}` | `YearInput.periods={"2026-12-thirteenth": PeriodFacts(events=...)}` |
| year-level `regione`, family, `contributable_hours` | `YearInput.default_facts` (an entry in `periods` replaces it for its run) |
| `PayrollYearRequest.calendar` | `YearInput.calendar_override` |
| `PayrollResult` (alias of `PeriodCalculationResult`) | `PeriodResult` |
| `PayrollYearResult` (`YearCalculationResult`) | `YearResult`, with `closing_state` of the last run |
| `year.period_results[-1].closing_state` | `year.closing_state` |
| `SupplementaryAllowance`, `AgreementKind` | removed: second-level amounts are not an engine input |
| `RinnovoRules` | `PreferentialTaxRegime` with `agreements_signed_from` and `agreements_signed_until` |

```python
from dataclasses import replace
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerActivity,
    EmployerProfile,
    Employment,
    EmploymentSector,
    Headcount,
    NightShiftEvent,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PriorYearTaxFacts,
    SeniorityMonths,
    YearInput,
)

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority_months=SeniorityMonths(36),
    sector=EmploymentSector.PRIVATE,
)
employer = EmployerProfile(headcount=Headcount(100), activity=EmployerActivity.OTHER)
prior_year = PriorYearTaxFacts(employment_income=Decimal(30_000))
base = PeriodFacts(regione="IT-45", comune_belfiore="F257")

january = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
        facts=base,
        prior_year=prior_year,
    )
)

night = NightShiftEvent(event_date=date(2026, 3, 10), supplement_amount=Decimal(200))
year = engine.calculate_year(
    YearInput(
        year=2026,
        employment=employment,
        employer=employer,
        prior_year=prior_year,
        default_facts=base,
        periods={3: replace(base, events=(night,))},
    )
)
opening_2027 = engine.close_tax_year(year.closing_state)
```

Behaviour that changes with the inputs:

- The sector of the employment is declared, not derived from the CCNL: a
  public employer applying a private CCNL is public. When `sector` is `None`
  the renewal and the night, holiday and shift regimes are `unknown` and the
  result is `provisional`. Declare `EmploymentSector.PRIVATE` to keep a
  private-sector worker eligible.
- L. 199/2025 art. 1 c. 11 excludes the activities of c. 18 (food and
  beverage service, tourism, thermal establishments) from the night, holiday
  and shift regime: such an employer is `ineligible`, and an employer whose
  activity is `None` is `unknown`.
- A renewal increment is eligible only when `agreement_signed_on` lies
  between 1 January 2024 and 31 December 2026; without it the renewal is
  `unknown`.
- A year run takes one prior-year income for every regime and every run:
  the same worker cannot carry different incomes on different events.
- Naming the same run twice in `periods` (by month and by run id) raises
  `InvalidInputError`, a `ValueError`, at construction.
- `default_facts` must carry no event.

Amounts are unchanged for the same facts: the documentation examples print
the same figures as before the change.

## Earlier changes

The sections below document earlier releases. Their code uses the names of
the release that introduced them; the table above gives the current name.

### From `estimate_annual()` to `PayrollEngine`

The entry point changed from `estimate_annual()` to `PayrollEngine`.

`estimate_annual()` computed an annual gross-to-net projection in a single call.
`PayrollEngine.calculate()` (now `calculate_period()`) computed one payroll run at a time, threading
YTD state (`PeriodState`) between runs. `PayrollEngine.calculate_year()` does
the full sequence in one call.

#### Before (removed)

```python
from datetime import date
# estimate_annual was removed in v0.5; use PayrollEngine instead.
result = ...  # AnnualEstimateInput / estimate_annual no longer available
```

The current API is described in the first section of this page.

#### `estimate_annual` is removed

`estimate_annual` and the `ccnl_engine.engine.payroll` namespace were removed
in v0.5. Migrate to `PayrollEngine` for all new code.

### Surtax codes and decisions

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

### Payroll state: tax year and obligations

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

### Credit accounts and run ids

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

### Decisions and capability report

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

### Invariants and input checks

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

### Fiscal rule corrections

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
