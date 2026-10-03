# Assurance

A payroll result answers one question for an integration: can this amount be
paid as it is? The answer is `result.is_payable`, and `result.blockers` says
why not. Both come from `result.assurance`, a `ResultAssurance` derived from
what the run recorded; neither is set by the caller.

| Field | Answers |
|---|---|
| `result.is_payable` | Can the amounts of this result be paid as computed? |
| `result.blockers` | What stops them, one `ResultBlocker` per reason |
| `result.assurance` | The axes the answer is derived from: calculation, coverage, evidence, rulesets, mode |
| `result.rulesets` | Which rulesets (CCNL, tax, INPS, variable pay, surtax) the run read, each a `RulesetAssurance` with identity, hash, kind and readiness |

`YearResult` exposes the same four fields for the whole year: each axis is the
worst of its runs, rulesets and blockers are listed once each, and the year is
payable only when every run is.

## Payability rules

A result is payable only when it has no blocker. Each of the following adds
one:

| `BlockerCode` | `feature` | `detail` | Raised when |
|---|---|---|---|
| `calculation_issue` | `None` | issue code | The run raised an issue (an assumption, a fallback, an unrecovered shortfall) |
| `calculation_issue` | capability | decision reason | A decision is not `final` |
| `missing_fact` | `None` | fact name | An issue names a fact the calculation needs and the request did not supply |
| `capability_not_computed` | capability | gap kind | A capability that applies to the run is unsupported, unresolved or partial |
| `rule_source_weak` | capability | `assumed` or `missing` | An executed capability read a rule weaker than the evidence its registry entry accepts (`derived` for every capability today), or no rule of the run carries a record |
| `caller_supplied_rule` | capability | field names | The caller supplied a rate or multiplier in place of a bundled rule |
| `ruleset_not_production` | `None` | ruleset id | `operational` mode only: a ruleset that tracks readiness (today, the CCNL) is not `production` with a `verified` confidence; `no_ruleset_tracks_readiness` when the CCNL has no ruleset identity |

A `derived` rule (taken from a cited document location, with no recorded
human check) lowers the evidence axis but does not block on its own. The
bundle holds no `verified` rule yet, so requiring `verified` would block every
result; the evidence axis keeps the difference visible instead.

Each blocker also carries a `remediation` sentence for a human reader. Branch
on `code`, `feature` and `detail`, not on the sentence.

### What the bundle gives today

For the first level of each CCNL, a regular run of June 2026 with no event,
no result is payable. None has a coverage gap: the capabilities the engine
does not compute (INAIL, health funds, maternity, ...) do not apply to an
ordinary month or are outside the request (see the
[capability matrix](../contracts/capability-matrix.md)). Every run carries a
`rule_source_weak` blocker on `somma_esente`, whose cut points are
reconstructions. Most also read an `assumed` base salary:
<!-- trust:extra-months-assumed -->121 of 125<!-- /trust:extra-months-assumed -->
CCNLs cite no clause for their number of monthly payments. The bundle holds
<!-- trust:rules-missing -->85<!-- /trust:rules-missing --> `missing` rules
(see [Provenance](provenance.md#current-counts)); a run that reads one also
raises a `rule_source_missing` issue and is `incomplete`.

Use the amounts for simulation, with the blockers shown; do not pay them
automatically. In `operational` mode every one of these runs also carries a
`ruleset_not_production` blocker: no bundled CCNL is `production` (see
[Readiness](readiness.md#simulation-and-operational-modes)).

## Assurance axes

| Axis | Type | Derived from |
|---|---|---|
| `calculation` | `CalculationStatus` | Worst status of `result.issues` and `result.decisions`; `final` when there are none |
| `coverage` | `CoverageStatus` | `result.capability_report.status` |
| `evidence` | `EvidenceStatus` | Weakest provenance of the payable rules the run read (`verified`, `derived`, `assumed`, `missing`); `missing` when none carries a record |
| `rulesets` | `tuple[RulesetAssurance, ...]` | Identity, version, hash, kind, readiness and confidence of the CCNL ruleset and of each ruleset a payable rule was read from |
| `mode` | `EngineMode` | `simulation` (default) or `operational`, from the engine |
| `payability` | `Payability` | `payable` exactly when `blockers` is empty |

### Calculation

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts. |
| `incomplete` | At least one amount could not be determined. |
| `rejected` | The inputs cannot produce a meaningful result. |

`result.decisions` records what each capability decided and on which rule, so
a result can be explained line by line whatever its status.

Issues that lower the calculation axis include:

| Code | Status | When |
|---|---|---|
| `rule_source_missing` | `incomplete` | An executed capability read a payable rule whose provenance status is `missing` |
| `employer_rate_category_assumed` | `provisional` | The sector sets INPS employer rates by worker category (artigianato: impiegati and quadri 24.71%), the level fixes no category and none was declared, so the general rate (26.93%, the operai rate) applied |
| `somma_esente_income_assumed` | `provisional` | The reddito complessivo of the somma esente is taken as the employment income of this employer |
| `withholding_shortfall_unrecovered` | `provisional` | The pay of the run cannot cover the tax due; the worker must be told the amount |

### Coverage

`result.capability_report` compares the capability registry of the fiscal
year with what the calculation observed. The registry is the single source
of coverage: the same entries drive the contracts index and the
[capability matrix](../contracts/capability-matrix.md). Each entry declares
its implementation (`native`, `caller_supplied`, `partial`, `unsupported`),
an applicability predicate, the handler that decides and traces it, the
facts it reads and the weakest evidence its rules may have.
`capability_report.scope` gives each capability as `applicable`,
`not_applicable` or `outside_input` for the run. Only an applicable
capability can leave a `CapabilityGap`, and each gap is a
`capability_not_computed` blocker.

| `status` | When |
|---|---|
| `complete` | No gaps |
| `partial` | Every gap is a `partial_result` (a capability implemented in full came out partial) or a `partial_implementation` (sickness, family deductions, ... executed) |
| `incomplete` | Any other gap: an applicable capability is `unsupported` (residual leave on the run that closes the employment) or `unresolved` |

`rule_sources` maps each executed capability that reads bundled rules to the
weakest provenance status among them. Capabilities computed only from
caller-declared amounts do not appear.
`caller_supplied` maps each capability that used a rate or an amount the
caller supplied in place of a rule (an overtime hourly rate or explicit
multiplier, a sickness integration rate) to the event fields it took; see
[Decisions](decisions.md#caller-supplied-values).

## Reading the assurance

```python
from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)

engine = PayrollEngine.bundled()
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    )
)

if not result.is_payable:
    for blocker in result.blockers:
        print(blocker.code.value, blocker.feature, blocker.detail)

assurance = result.assurance
print(assurance.calculation, assurance.coverage, assurance.evidence)
for ruleset in result.rulesets:
    print(ruleset.id, ruleset.kind, ruleset.readiness, ruleset.source_hash[:12])
```
