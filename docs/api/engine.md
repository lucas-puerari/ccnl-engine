# Engine

Core computation functions and types.

See [Guide: Employment types](../domain/employment-types.md) and
[Guide: Pay components](../engine/pay-components.md) for worked examples.

## Entry point

::: ccnl_engine.api
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
(`ccnl_id`, `name`, `cnel_code`, `readiness`, `validity`) per bundled CCNL and
`engine.inspect_ruleset(ccnl_id)` returns the `RulesetAssurance` of one CCNL,
by slug or CNEL code: the same value the run reports in `result.rulesets`.

```python
engine = PayrollEngine.bundled(mode="operational")
ruleset = engine.inspect_ruleset("metalmeccanico-federmeccanica")
if not ruleset.is_production:
    print(ruleset.readiness, ruleset.confidence)  # → exploratory unverified
```

| `RulesetAssurance` field | Meaning |
|---|---|
| `identity` | `RulesetIdentity`: id, version, validity, source and `source_hash` |
| `kind` | `RulesetKind`: `ccnl`, `tax`, `inps` or `surtax`, set by the loader |
| `readiness` | `RulesetReadiness` for a CCNL; `None` when the kind tracks no tier |
| `confidence` | `VerificationStatus`: the CCNL `verification.confidence`, or the identity `verification_status` |
| `confidence_contradicts_readiness` | `True` when a `reviewed` or `production` tier lacks a `verified` confidence |
| `is_production` | `production` and a confidence that agrees |

::: ccnl_engine.payroll.assurance.policies_engine_mode
    options:
      members:
        - EngineMode

::: ccnl_engine.provenance.ruleset.models_assurance
    options:
      members:
        - RulesetAssurance
        - RulesetKind

`ContractSummary.validity` is the `ValidityWindow` (`first_day`,
`last_day`, both included, `last_day` `None` when open-ended) on which every
rule of the CCNL has a value in the bundle: pay tables, parameters and work
rules. A run whose month it covers never raises `MissingRuleError`; a run
outside it raises that error when it reads a rule not in force on its date.
Four CCNLs have 2026 pay tables that start after January (`anas` on 1 March,
`igiene-ambientale-utilitalia` on 1 February,
`lavanderie-industriali-assosistema` on 1 May, `metalmeccanico-confimi-pmi`
on 1 June): a competence or tax year of theirs from January is partial (see
[Results](#results-and-calculation-status)).

```python
(anas,) = (c for c in engine.list_contracts() if c.ccnl_id == "anas")
anas.validity.first_day  # → datetime.date(2026, 3, 1)
```

::: ccnl_engine.contract.catalog.loaders_discovery
    options:
      members:
        - ContractSummary

::: ccnl_engine.contract.identity.models_validity_window
    options:
      members:
        - ValidityWindow

## Inputs

`calculate_period` takes a `PeriodInput`, `calculate_competence_year` a
`CompetenceYearPlan` and `calculate_tax_year` a `TaxYearPlan` of competence
years. They group the facts by owner and are validated when built;
`import_opening_balances` takes the `OpeningBalances` of another provider:

| Model | Holds |
|---|---|
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, weekly and full-time `WeeklyHours`, `SeniorityFact`, roles, `ContributionHistory` (IVS massimale eligibility), sector (`None` means unknown), `PensionFundEnrolment` or `NoPensionFund` (`None` means unknown) |
| `EmployerProfile` | `Headcount` (required, no size is assumed) and activity (`None` means unknown) |
| `PriorYearTaxFacts` | prior-year employment income and the regimes waived in writing, read by every substitute-tax regime and the PdR |
| `CurrentYearTaxFacts` | income of the tax year beyond this employment, the main dwelling excluded, with its date and `IncomeEstimateQuality`; the Art. 12 family deductions add it to the employment income (`None` means unknown, a blocker when a dependent is entitled) |
| `PeriodFacts` | events, contributable hours, region and Belfiore code, family composition, dependent children of one run |

::: ccnl_engine.payroll.period.inputs
    options:
      members:
        - PeriodInput
        - PeriodFacts

::: ccnl_engine.payroll.year.inputs_competence_plan
    options:
      members:
        - CompetenceYearPlan

::: ccnl_engine.payroll.year.inputs_tax_plan
    options:
      members:
        - TaxYearPlan

::: ccnl_engine.payroll.state.services_opening_balance
    options:
      members:
        - OpeningBalances

::: ccnl_engine.payroll.contribution.models_inps_base
    options:
      members:
        - InpsBaseYtd

::: ccnl_engine.payroll.employment.inputs
    options:
      members:
        - Employment

::: ccnl_engine.payroll.contribution.inputs_pension_fund
    options:
      members:
        - PensionFundEnrolment
        - NoPensionFund

::: ccnl_engine.payroll.employment.inputs_fact
    options:
      members:
        - EmploymentPeriod
        - WeeklyHours
        - SeniorityFact
        - SenioritySource
        - ContributableHours

::: ccnl_engine.payroll.employment.inputs_employer
    options:
      members:
        - EmployerProfile
        - Headcount

::: ccnl_engine.payroll.taxation.inputs_prior_year
    options:
      members:
        - PriorYearTaxFacts

::: ccnl_engine.payroll.taxation.inputs_current_year
    options:
      members:
        - CurrentYearTaxFacts
        - IncomeEstimateQuality

::: ccnl_engine.tax.regime.models
    options:
      members:
        - EmploymentSector
        - EmployerActivity
        - SubstituteTaxRegime

::: ccnl_engine.tax.contribution.models_zone_reduction
    options:
      members:
        - AgriculturalZone

::: ccnl_engine.payroll.period.models_run
    options:
      members:
        - PayrollRun
        - PayrollRunId

::: ccnl_engine.payroll.year.models_payment
    options:
      members:
        - PaymentId

## Errors

Every error the engine raises for an input, a data gap or a bundle defect
is a `CcnlEngineError` exported at the root, with a stable `code` (one of
`ccnl_engine.errors.PUBLIC_ERROR_CODES`), the `feature` and the `ruleset` it concerns and a
`remediation`. None of them is a `ValueError`: catch `CcnlEngineError`, or
one of its subclasses.

| Error | `code` | Raised when |
|---|---|---|
| `InvalidInputError` | `invalid_input` | An input or a facade argument is not what it must be; `field` names it, e.g. `"PeriodFacts.events[2]"` or `"Employment.roles['x']"` |
| `UnknownCcnlError` | `unknown_ccnl` | The CCNL slug or code is not in the bundle |
| `UnknownLevelError` | `unknown_level` | The level code is not a level of the CCNL |
| `MissingRuleError` | `missing_rule` | The bundle has no value of a rule on the date a run reads it |
| `MissingRequiredFactError` | `missing_required_fact` | A computation path needs a fact the caller did not supply |
| `UnsupportedTaxYearError` | `unsupported_tax_year` | The bundle has no tax tables for the tax year of the payment |
| `OutOfScopeError` | `out_of_scope` | The engine does not model the requested computation |
| `DataIntegrityError` | `data_integrity` | A bundled file fails an integrity check, or a run breaks a state invariant |

Inputs are frozen dataclasses validated on construction by shared
validators: scalars by type and range (`Decimal` amounts finite and below
`1E+9` in magnitude, `int` fields never a `bool`, dates never a
`datetime`, enums as a member or its string value), collections element by
element and stored as tuples or frozensets once valid. A missing fact that
lowers a result is a `CalculationIssue` whose `fact` is the name of the
public field to set (`seniority`, `contribution_history`, `sector`,
`activity`, `agreement_signed_on`, `employment_income`).

::: ccnl_engine.errors
    options:
      members:
        - CcnlEngineError
        - InvalidInputError
        - MissingRuleError
        - MissingRequiredFactError

## Year calendar

`CompetenceYearPlan` derives the calendar from the CCNL when `calendar_override` is
omitted. A different calendar is accepted only as a validated
`CalendarOverride`.

::: ccnl_engine.payroll.year.inputs_calendar_override
    options:
      members:
        - CalendarOverride
        - CalendarOverrideReason

::: ccnl_engine.contract.employment.models_category
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

::: ccnl_engine.payroll.period.results
    options:
      members:
        - PeriodResult

::: ccnl_engine.payroll.year.results
    options:
      members:
        - PaymentsResult
        - CompetenceYearResult
        - TaxYearResult

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

::: ccnl_engine.payroll.capability.rules_requirement
    options:
      members:
        - UnresolvedRequirement

::: ccnl_engine.payroll.year.models_uncovered_run
    options:
      members:
        - UncoveredRun

::: ccnl_engine.payroll.assurance.models
    options:
      members:
        - ResultAssurance
        - ResultBlocker
        - BlockerCode
        - CoverageStatus
        - EvidenceStatus
        - Payability

::: ccnl_engine.knowledge.limitation.models
    options:
      members:
        - ModelLimitation
        - MonetaryImpact
        - LimitationStatus

::: ccnl_engine.payroll.ledger.models_remittance
    options:
      members:
        - RemittanceLine
        - RemittanceColumn
        - remittance_summary

::: ccnl_engine.payroll.assurance.models_decision
    options:
      members:
        - CalculationStatus
        - CalculationIssue
        - CalculationDecision
