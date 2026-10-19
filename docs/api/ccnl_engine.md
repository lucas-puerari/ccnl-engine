# `ccnl_engine`

The package root holds the common path: the facade, the request and plan
types, the results the facade returns, the errors and the versions. Every
other public name lives in one of the four namespaces: see
[API reference](index.md).

## Entry point

::: ccnl_engine.PayrollEngine

## Modes

`PayrollEngine.bundled(mode=...)` sets the payability policy of every result;
both modes compute the same amounts. `EngineMode` is in
[`ccnl_engine.inputs`](inputs.md).

| Mode | Payable when |
|---|---|
| `simulation` (default) | No blocker. Ruleset readiness is reported in `result.rulesets`, not enforced. |
| `operational` | No blocker, and every ruleset that tracks readiness is `production` with a `verified` confidence and a `review_due` not before the payment date. Otherwise the result carries one `ruleset_not_production` blocker per such ruleset (detail: the ruleset id), and the amounts stay inspectable. |

An operational engine returns a result with blockers rather than refusing
before the calculation: the amounts, the other blockers and the readiness of
every ruleset remain visible, and a year aggregates its runs as in
simulation. Readiness is tracked for CCNL rulesets only, so today the
operational gate is the CCNL tier; tax, INPS and surtax rulesets report
`readiness = None` and never raise it. A run whose CCNL has no ruleset
identity fails closed with the detail `no_ruleset_tracks_readiness`.

## Requests and plans

`calculate_period` takes a `PeriodInput`, `calculate_competence_year` a
`CompetenceYearPlan` and `calculate_tax_year` a `TaxYearPlan` of competence
years. They group the facts by owner and are validated when built;
`import_opening_balances` takes the `OpeningBalances` of another provider:

| Model | Holds |
|---|---|
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, weekly and full-time `WeeklyHours` (Decimal, e.g. `37.5`), `WorkPattern` (vertical or mixed part time), `SeniorityFact`, roles, `ContributionHistory` (IVS massimale eligibility), sector (`None` means unknown), `PensionFundEnrolment` or `NoPensionFund` (`None` means unknown) |
| `EmployerProfile` | `Headcount` (required, no size is assumed) and activity (`None` means unknown) |
| `PriorYearTaxFacts` | prior-year employment income and the regimes waived in writing, read by every substitute-tax regime and the PdR |
| `CurrentYearTaxFacts` | income of the tax year beyond this employment, the main dwelling excluded, with its date and `IncomeEstimateQuality`; the Art. 12 family deductions add it to the employment income (`None` means unknown, a blocker when a dependent is entitled) |
| `PeriodFacts` | events, contributable hours, region and Belfiore code, family composition, dependent children of one run |

The other facts these types take are in [`ccnl_engine.inputs`](inputs.md),
the work events in [`ccnl_engine.events`](events.md).

::: ccnl_engine.PeriodInput

::: ccnl_engine.PeriodFacts

::: ccnl_engine.PayrollRun

::: ccnl_engine.Employment

::: ccnl_engine.EmployerProfile

::: ccnl_engine.Headcount

::: ccnl_engine.CompetenceYearPlan

::: ccnl_engine.TaxYearPlan

## Year calendar

`CompetenceYearPlan` derives the calendar from the CCNL when `calendar_override` is
omitted. A different calendar is accepted only as a validated
`CalendarOverride`.

## Results

What a result says about its own reliability (assurance, blockers,
decisions, the capability report) is described in
[`ccnl_engine.results`](results.md).

::: ccnl_engine.PeriodResult

::: ccnl_engine.CompetenceYearResult

::: ccnl_engine.TaxYearResult

The assurance of a competence or tax year is incremental: `assurance`,
`is_payable`, `blockers` and `rulesets` assess the payments computed by the
call, listed in `assessed_payments`. A payment the opening state already
closed (a resumed or retried plan, a late December carried in from the
previous competence year) is vouched for by the result of the call that
computed it. A call that computed no payment assessed nothing: it is not
payable, with `missing` evidence and a `rule_source_weak` blocker (and in
`operational` mode a `ruleset_not_production` blocker).

A competence or tax year does not compute a run whose competence date has
no base salary of the CCNL level in the bundle. The run is listed in
`uncovered_runs` as an `UncoveredRun` (its `payment`, the fields of the
`MissingRuleError` it would raise, and that error as `error`) and adds a `run_not_computed` blocker
whose `detail` is the run id; the other runs are computed on a withholding
schedule without it, so the year is partial and not payable. A year in
which no run has a base salary raises the `MissingRuleError` of its first
run.

## Errors

Every error is exported at the root: see [Errors](errors.md).

## Versions

::: ccnl_engine.engine_version

::: ccnl_engine.bundle_version
