# `ccnl_engine.results`

The types read from a result: its assurance, blockers, decisions and
issues, the model limitations, the capability gaps, the runs a year left
out, the ledger account kinds and the remittance lines.

## Assurance and payability

Every result answers "can these amounts be paid as they are?" with
`is_payable`, and says why not with `blockers`, one `ResultBlocker` per
reason, each with a stable `BlockerCode`, the `feature` it concerns, a
machine-readable `detail` and a `remediation`. Both come from `assurance`, a
`ResultAssurance` derived from the run:

| Axis | Type | Derived from |
|---|---|---|
| `calculation` | `CalculationStatus` | Worst status of the issues and decisions |
| `coverage` | `CoverageStatus` | The capability report |
| `evidence` | `EvidenceStatus` | Weakest provenance of the payable rules read |
| `rulesets` | `RulesetAssurance` tuple | The CCNL ruleset and every ruleset a payable rule was read from, with readiness; also `result.rulesets` |
| `mode` | `EngineMode` | The mode of the engine; `operational` adds `ruleset_not_production` blockers |
| `payability` | `Payability` | `payable` exactly when there is no blocker |
| `limitations` | `ModelLimitation` tuple | The known model simplifications that apply to the run; an open one with monetary impact `yes` or `unknown` is also an `open_limitation` blocker |

A result is payable only when it raised no issue, every decision is final,
the capability report has no gap and no unresolved requirement, no executed
rule is `assumed` or `missing`
no rule was supplied by the caller and no open model limitation with a
monetary impact applies; in `operational` mode, also only
when the CCNL ruleset is `production`. A `derived` rule lowers `evidence`
but does not block. See [Assurance](../trust/confidence.md) for the rules.

The year result combines the assurance of its runs (each axis the worst,
rulesets, blockers and limitations each once; payable only when every run is) and lists
their issues in payment order, each issue once: one repeated on every run
(same `code` and `message`) is listed at its first run.

```python
result = engine.calculate_period(period_input)
if not result.is_payable:
    for blocker in result.blockers:
        print(blocker.code.value, blocker.feature, blocker.detail)
```

The calculation axis:

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts. |
| `incomplete` | At least one amount could not be determined; do not pay as is. |
| `rejected` | The inputs cannot produce a meaningful result. |

Compare statuses with `severity` or `CalculationStatus.worst()`: the string
values do not sort in severity order.

An `incomplete` result still carries amounts, but at least one of them is
missing, not zero: for example a surtax whose table is unknown is withheld
as 0, flagged by the issue `regional_surtax_unknown` or
`municipal_surtax_unknown`, recorded by a decision with no amount and
reported as a blocker, so the result is not payable.  `result.decisions` records what each capability
decided, e.g. the surtax and tax credit decisions described in
[Fiscal computation](../engine/surtax.md#surtax-decisions).  The year result
exposes the decisions of its periods in payment order.

### Capability report

`result.capability_report` compares what the run executed with the capability
registry of the tax year.  Each feature is traced from what actually ran,
never from the presence of an input:

- the core stages (base salary, INPS, TFR, IRPEF) run on every period;
- an event feature (overtime, welfare, ...) is computed only when one of its
  events posted a non-zero amount or took a decision, otherwise skipped;
- every other feature follows its decisions: `final` is computed (a zero
  amount with its reason counts), `provisional` is partial, `incomplete` or
  `rejected` is unresolved, and no decision is not applicable.

Each registry entry declares an applicability predicate, and
`capability_report.scope` gives the result for the run: `applicable`,
`not_applicable` (the predicate is false, or the handler ruled it out) or
`outside_input` (the request has no field for the fact that makes it apply).
An applicable capability is a gap when it is `unsupported` (the engine does
not compute it, e.g. residual leave on the run that closes the employment),
`unresolved` (e.g. a surtax without a table), a `partial_result` of a
capability implemented in full, or a `partial_implementation` that executed
(sickness, family deductions). Every gap is a `capability_not_computed`
blocker.

The gaps alone are a blocklist: a capability whose handler took no decision
because a fact was left to its default looks `not_applicable`. An entry
that declares `applicability_facts` (the residence for the regional and
municipal surtaxes, the family composition for the family deductions) is
therefore required in every run: it must be ruled out by a decision of the
run or decided on the supplied facts, never on a default. Each such fact
left to its default, on a run that did not rule the capability out, is an
`UnresolvedRequirement` in
`capability_report.unresolved` and a `requirement_unresolved` blocker. The
report `status` is the coverage axis of the assurance: `incomplete` with an
unresolved requirement, otherwise `partial` when every gap is partial and
`incomplete` with any other gap.

::: ccnl_engine.results.AccountKind

::: ccnl_engine.results.BlockerCode

::: ccnl_engine.results.CalculationDecision

::: ccnl_engine.results.CalculationIssue

::: ccnl_engine.results.CalculationStatus

::: ccnl_engine.results.CapabilityGap

::: ccnl_engine.results.CapabilityScope

::: ccnl_engine.results.CoverageStatus

::: ccnl_engine.results.DecisionOrigin

::: ccnl_engine.results.EvidenceStatus

::: ccnl_engine.results.LimitationStatus

::: ccnl_engine.results.ModelLimitation

::: ccnl_engine.results.MonetaryImpact

::: ccnl_engine.results.Payability

::: ccnl_engine.results.RemittanceColumn

::: ccnl_engine.results.RemittanceLine

::: ccnl_engine.results.ResultAssurance

::: ccnl_engine.results.ResultBlocker

::: ccnl_engine.results.UncoveredRun

::: ccnl_engine.results.UnresolvedRequirement
