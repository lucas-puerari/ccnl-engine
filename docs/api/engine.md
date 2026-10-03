# Engine

Core computation functions and types.

See [Guide: Employment types](../domain/employment-types.md) and
[Guide: Pay components](../engine/pay-components.md) for worked examples.

## Entry point

::: ccnl_engine.api.facade
    options:
      members:
        - PayrollEngine

## Modes and catalog

`PayrollEngine.bundled(mode=...)` sets the payability policy of every result;
both modes compute the same amounts:

| Mode | Payable when |
|---|---|
| `simulation` (default) | No blocker. Ruleset readiness is reported in `result.rulesets`, not enforced. |
| `operational` | No blocker, and every ruleset that tracks readiness is `production` with a `verified` confidence. Otherwise the result carries one `ruleset_not_production` blocker per such ruleset (detail: the ruleset id), and the amounts stay inspectable. |

An operational engine returns a result with blockers rather than refusing
before the calculation: the amounts, the other blockers and the readiness of
every ruleset remain visible, and a year aggregates its runs as in
simulation. Readiness is tracked for CCNL rulesets only, so today the
operational gate is the CCNL tier; tax, INPS and surtax rulesets report
`readiness = None` and never raise it. A run whose CCNL has no ruleset
identity fails closed with the detail `no_ruleset_tracks_readiness`.

Before any run, `engine.list_contracts()` returns one `ContractSummary`
(`ccnl_id`, `name`, `cnel_code`, `readiness`) per bundled CCNL and
`engine.inspect_ruleset(ccnl_id)` returns the `RulesetAssurance` of one CCNL,
by slug or CNEL code: the same value the run reports in `result.rulesets`.

```python
engine = PayrollEngine.bundled(mode="operational")
ruleset = engine.inspect_ruleset("metalmeccanico-federmeccanica")
if not ruleset.is_production:
    print(ruleset.readiness, ruleset.confidence)  # → reviewed unverified
```

| `RulesetAssurance` field | Meaning |
|---|---|
| `identity` | `RulesetIdentity`: id, version, validity, source and `source_hash` |
| `kind` | `RulesetKind`: `ccnl`, `tax`, `inps` or `surtax`, set by the loader |
| `readiness` | `RulesetReadiness` for a CCNL; `None` when the kind tracks no tier |
| `confidence` | `VerificationStatus`: the CCNL `verification.confidence`, or the identity `verification_status` |
| `confidence_contradicts_readiness` | `True` when a `reviewed` or `production` tier lacks a `verified` confidence |
| `is_production` | `production` and a confidence that agrees |

::: ccnl_engine.payroll.domain.engine_mode
    options:
      members:
        - EngineMode

::: ccnl_engine.provenance.domain.ruleset_assurance
    options:
      members:
        - RulesetAssurance
        - RulesetKind

::: ccnl_engine.contract.service.discovery
    options:
      members:
        - ContractSummary

## Inputs

`calculate_period` takes a `PeriodInput`, `calculate_year` a `YearInput`.
Both group the facts by owner and are validated when built:

| Model | Holds |
|---|---|
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, weekly and full-time `WeeklyHours`, `SeniorityFact`, roles, `ContributionHistory` (IVS massimale eligibility), sector (`None` means unknown), `PensionFundEnrolment` (`None` means not enrolled) |
| `EmployerProfile` | `Headcount` (required, no size is assumed) and activity (`None` means unknown) |
| `PriorYearTaxFacts` | prior-year employment income and the regimes waived in writing, read by every substitute-tax regime and the PdR |
| `PeriodFacts` | events, contributable hours, region and Belfiore code, family composition, dependent children of one run |

::: ccnl_engine.payroll.domain.inputs
    options:
      members:
        - PeriodInput
        - PeriodFacts

::: ccnl_engine.payroll.domain.year_input
    options:
      members:
        - YearInput

::: ccnl_engine.payroll.domain.employment
    options:
      members:
        - Employment

::: ccnl_engine.payroll.domain.pension_fund
    options:
      members:
        - PensionFundEnrolment

::: ccnl_engine.payroll.domain.employment_facts
    options:
      members:
        - EmploymentPeriod
        - WeeklyHours
        - SeniorityFact
        - SenioritySource
        - ContributableHours

::: ccnl_engine.payroll.domain.employer
    options:
      members:
        - EmployerProfile
        - Headcount

::: ccnl_engine.payroll.domain.prior_year
    options:
      members:
        - PriorYearTaxFacts

::: ccnl_engine.tax.domain.preferential_regime
    options:
      members:
        - EmploymentSector
        - EmployerActivity
        - SubstituteTaxRegime

::: ccnl_engine.payroll.domain.run
    options:
      members:
        - PayrollRun
        - PayrollRunId

## Year calendar

`YearInput` derives the calendar from the CCNL when `calendar_override` is
omitted. A different calendar is accepted only as a validated
`CalendarOverride`.

::: ccnl_engine.payroll.domain.calendar_override
    options:
      members:
        - CalendarOverride
        - CalendarOverrideReason

::: ccnl_engine.contract.domain.category
    options:
      members:
        - WorkerCategory

## Results and calculation status

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
the capability report has no gap, no executed rule is `assumed` or `missing`
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
[Fiscal computation](../engine/fiscal.md#surtax-decisions).  The year result
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
blocker, and the report `status` is the coverage axis of the assurance:
`partial` when every gap is partial, `incomplete` otherwise.

::: ccnl_engine.payroll.domain.period
    options:
      members:
        - PeriodResult

::: ccnl_engine.payroll.application.calculate_year
    options:
      members:
        - YearResult

::: ccnl_engine.payroll.domain.assurance
    options:
      members:
        - ResultAssurance
        - ResultBlocker
        - BlockerCode
        - CoverageStatus
        - EvidenceStatus
        - Payability

::: ccnl_engine.shared.domain.limitation
    options:
      members:
        - ModelLimitation
        - MonetaryImpact
        - LimitationStatus

::: ccnl_engine.payroll.domain.remittance
    options:
      members:
        - RemittanceLine
        - RemittanceColumn
        - remittance_summary

::: ccnl_engine.payroll.domain.decisions
    options:
      members:
        - CalculationStatus
        - CalculationIssue
        - CalculationDecision
