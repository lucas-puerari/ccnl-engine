# `ccnl_engine.results`

The types read from a result: its assurance, blockers, decisions and
issues, the model limitations, the capability gaps, the runs a year left
out, the ledger account kinds and the remittance lines.

## Assurance and payability

Every result answers "can these amounts be paid as they are?" with
`is_payable`, and says why not with `blockers`, one `ResultBlocker` per
reason, each with a stable `BlockerCode`, the `feature` it concerns, a
machine-readable `detail`, a `remediation` and the `totals` it leaves
unreliable (`ResultTotal`: `net_pay`, `employer_cost`, or both). Both come
from `assurance`, a `ResultAssurance` derived from the run.

`is_payable` holds when both totals are reliable. Each total also has its
own answer: `is_net_pay_payable` (no blocker touches the net pay) and
`is_employer_cost_complete` (no blocker touches the employer cost). An open
limitation on an amount only the employer owes, such as the mètaSalute
health fund of the Metalmeccanico CCNL, leaves the employer cost short and
the net pay payable. `period_employer_cost` never includes the INAIL premium,
which rests on the tariff rate of the employer, nor IRAP.

The assurance axes:

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

::: ccnl_engine.results.PUBLIC_FACTS

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

::: ccnl_engine.results.ResultTotal

::: ccnl_engine.results.UncoveredRun

::: ccnl_engine.results.UnresolvedRequirement

## JSON form of a result

`result_to_json` writes a `PeriodResult`, a `CompetenceYearResult` or a
`TaxYearResult` as JSON, with the same tagged values as a request: every
field under `result` and, under `derived`, `is_payable`,
`is_net_pay_payable`, `is_employer_cost_complete`, `blockers` and the
totals, which a reader outside Python could not compute. The JSON is output
only: a result is recomputed from its request, not read back.

::: ccnl_engine.results.result_to_json

::: ccnl_engine.results.ExtraMonthProgress

::: ccnl_engine.results.PayslipLine

::: ccnl_engine.results.Progressives

::: ccnl_engine.results.VoceUnit

::: ccnl_engine.results.VoceSide

## Comparing with another payroll

`compare_totals` compares the eight totals of a run with the payslip of
another payroll computed from the same facts: build the request with
`request_from_json` or the input types, run it, pass the other payroll's
totals by name (`TOTALS`), and read one `TotalDifference` per total and
whether the run is payable. The perimeter of each total is the one of the
[validation packets](../trust/validation-packet.md).

```python
from decimal import Decimal

from ccnl_engine.results import compare_totals

comparison = compare_totals(result, {"net": Decimal("1527.84")})
for difference in comparison.differences:
    print(difference.total, difference.engine, difference.difference)
```

::: ccnl_engine.results.compare_totals

::: ccnl_engine.results.TOTALS

::: ccnl_engine.results.TotalsComparison

::: ccnl_engine.results.TotalDifference
