# API reference

The reference of every public type and function, one page per public
namespace.

## Public namespaces

The public API is the package root and four namespaces. Each public name has
exactly one import path: there are no aliases.

| Module | Holds |
|---|---|
| [`ccnl_engine`](ccnl_engine.md) | The common path: `PayrollEngine`, the request and plan types (`PeriodInput`, `PeriodFacts`, `PayrollRun`, `Employment`, `EmployerProfile`, `Headcount`, `CompetenceYearPlan`, `TaxYearPlan`), the results the facade returns (`PeriodResult`, `CompetenceYearResult`, `TaxYearResult`), every public error, `engine_version` and `bundle_version` |
| [`ccnl_engine.inputs`](inputs.md) | Facts beyond the common path: contract types, hours, seniority, family, prior and current year tax facts, calendar, engine mode, opening state and imported balances |
| [`ccnl_engine.events`](events.md) | Work events of a period and the `PeriodId` an arrears event refers to |
| [`ccnl_engine.results`](results.md) | Assurance, blockers, decisions, issues, model limitations, capability gaps, runs a year left out, ledger account kinds and remittance lines |
| [`ccnl_engine.catalog`](catalog.md) | Bundled contracts and their discovery, ruleset identity and readiness, the capability catalog |

The errors are exported at the root and described together in
[Errors](errors.md). [Data bundle](knowledge.md) describes the data the
engine reads and `bundle_version`.

Any module below these namespaces (the root, `inputs`, `events`,
`results`, `catalog` and `repository`) is internal and may change without
notice, including the loaders. CI checks that each page documents every name of its namespace and
no internal module.

## Guide cross-references

| Guide | Relevant API |
|---|---|
| [Employment types](../domain/employment-types.md) | `Permanent`, `FixedTerm`, `NaspiExclusion`, `Apprentice` |
| [Pay components](../engine/pay-components.md) | `Employment.seniority`, `Employment.weekly_hours`, `WorkerCategory`, `BilateralFundEvent` |
| [Second level](../engine/second-level.md) | `CompetenceYearPlan`, `CalendarOverride` |
| [Fiscal](../engine/fiscal.md) | `CalculationDecision`, `CalculationIssue` |
| [Domestic work](../engine/domestic-work.md) | `Employment.weekly_hours`, `PeriodFacts.contributable_hours` |
