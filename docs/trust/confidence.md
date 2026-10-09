# Assurance

A payroll result answers one question for an integration: can this amount be
paid as it is? The answer is `result.is_payable`, and `result.blockers` says
why not. Both come from `result.assurance`, a `ResultAssurance` derived from
the run; neither is set by the caller.

The answer is fail-closed. A run is payable only when every capability it
requires is computed on facts the caller supplied, or ruled out by a
decision of the run. A default never decides a capability: a fact left to
its default is not the fact it stands for.

| Field | Answers |
|---|---|
| `result.is_payable` | Can the amounts of this result be paid as computed? |
| `result.blockers` | What stops them, one `ResultBlocker` per reason |
| `result.assurance` | The axes the answer is derived from: calculation, coverage, evidence, rulesets, mode, limitations |
| `result.rulesets` | Which rulesets (CCNL, tax, INPS, variable pay, surtax) the run read, each a `RulesetAssurance` with identity, hash, kind and readiness |

`CompetenceYearResult` exposes the same four fields for the whole year: each axis is the
worst of its runs, rulesets, blockers and limitations are listed once each, and the year is
payable only when every run is.

## Fail-closed payability

What a run must cover comes from the capability registry of the fiscal year
(`knowledge/capabilities/data/<year>.json`) and from the run itself:

- every capability that applies to the run (its predicate holds: a core
  stage, an event the request declares, the run that closes the employment)
  must be computed in full; otherwise it is a coverage gap;
- every capability whose registry entry declares `applicability_facts` is
  required in every run. It must be ruled out by a decision of the run, or
  decided on the supplied facts. When no decision rules it out and one of
  those facts is left to its default, each such fact is an
  `UnresolvedRequirement` in `result.capability_report.unresolved` and a
  `requirement_unresolved` blocker. A decision the capability took on other
  facts does not resolve it: posting an installment of last year's surtax
  does not decide this year's.

The required capabilities and their applicability facts today:

| Capability | Applicability fact | Ruled out by |
|---|---|---|
| `addizionale_regionale` | `facts.regione` | a supplied region, or an employer that is not a withholding agent |
| `addizionale_comunale` | `facts.comune_belfiore` | a supplied municipality, or an employer that is not a withholding agent |
| `family_deductions` | `facts.family_composition` | a supplied composition (`FamilyComposition()` states that there is no dependant), or an employer that is not a withholding agent |

A household employer is not a withholding agent (art. 23 c. 1 DPR
600/1973): its run decides that no surtax and no deduction is due, so it
needs neither fact. A resident owes both surtaxes when net IRPEF is due
(D.Lgs. 446/1997 art. 50 c. 2, D.Lgs. 360/1998 art. 1 c. 4), so an unknown
residence cannot stand for "no surtax". The run also records a
`residence_unknown` decision on each surtax whose code is missing
(incomplete, amount `None`, `inputs["fact"]` naming the fact), so its
calculation is `incomplete` too; see
[Surtax decisions](../engine/surtax.md#surtax-decisions).

The registry rejects an applicability fact that is not one of the facts the
capability reads, one on a capability that is not `decided`, and one the
request has no reader for.

## Payability rules

A result is payable only when it has no blocker. Each of the following adds
one:

| `BlockerCode` | `feature` | `detail` | Raised when |
|---|---|---|---|
| `calculation_issue` | `None` | issue code | The run raised an issue (an assumption, a fallback, an unrecovered shortfall) |
| `calculation_issue` | capability | decision reason | A decision is not `final` |
| `missing_fact` | `None` | fact name | An issue names a fact the calculation needs and the request did not supply |
| `requirement_unresolved` | capability | fact path | No decision ruled out a required capability and its applicability fact (e.g. `facts.regione`) was left to its default |
| `capability_not_computed` | capability | gap kind | A capability that applies to the run is unsupported, unresolved or partial |
| `rule_source_weak` | capability | `assumed` or `missing` | An executed capability read a rule weaker than the evidence its registry entry accepts (`derived` for every capability today), or no rule of the run carries a record |
| `caller_supplied_rule` | capability | field names | The caller supplied a rate or multiplier in place of a bundled rule |
| `open_limitation` | capability | limitation id | An open [model limitation](#model-limitations) with monetary impact `yes` or `unknown` applies to the run |
| `run_not_computed` | rule name (`base_salary`) | run id | Competence or tax year only: a run was left out because the bundle holds no base salary of its level on its competence date; see `ContractSummary.validity` |
| `ruleset_not_production` | `None` | ruleset id | `operational` mode only: a ruleset that tracks readiness (today, the CCNL) is not `production` with a `verified` confidence; `no_ruleset_tracks_readiness` when the CCNL has no ruleset identity |

A `derived` rule (taken from a cited document location, with no recorded
human check) lowers the evidence axis but does not block on its own. The
bundle holds no `verified` rule yet, so requiring `verified` would block every
result; the evidence axis keeps the difference visible instead.

Each blocker also carries a `remediation` sentence for a human reader. Branch
on `code`, `feature` and `detail`, not on the sentence.

### What the bundle gives today

For the first level of each CCNL, a regular run of June 2026 with no event,
for a worker whose residence and empty family are stated, no result is
payable. Without the residence or the family, each run also carries a
`requirement_unresolved` blocker per unknown fact; without the residence,
the `residence_unknown` surtax decisions add a `calculation_issue` and a
`capability_not_computed` blocker per missing code. None has a coverage gap: the capabilities the engine
does not compute (INAIL, health funds, maternity, ...) do not apply to an
ordinary month or are outside the request (see the
[capability matrix](../contracts/capability-matrix.md)). Every run that
reads a 2026 sector tax or INPS file is blocked on IRPEF, INPS, TFR, the
trattamento integrativo and the ulteriore detrazione: those rulesets declare
`source_type: "estimated"`, so their rules are `assumed` (see
[Provenance](provenance.md#a-label-never-outruns-its-evidence)). The
somma esente is `derived` from its own ruleset, quoted from L. 207/2024
art. 1 cc. 4-5, and blocks no run by its label. Most also
read an `assumed` base salary:
<!-- trust:extra-months-assumed -->121 of 126<!-- /trust:extra-months-assumed -->
CCNLs cite no clause for their number of monthly payments. The bundle holds
<!-- trust:rules-missing -->86<!-- /trust:rules-missing --> `missing` rules
(see [Provenance](provenance.md#current-counts)); a run that reads one also
raises a `rule_source_missing` issue and is `incomplete`.

A minority of these runs also carry an `open_limitation` blocker: the
limitations that concern every ordinary month of their CCNL (an INPS rate
reused from another sector, a salary table read from a proxy source).

Use the amounts for simulation, with the blockers shown; do not pay them
automatically. In `operational` mode every one of these runs also carries a
`ruleset_not_production` blocker: no bundled CCNL is `production` (see
[Readiness](readiness.md#simulation-and-operational-modes)).

## Defaults of the public inputs

Every field with a default in the public input types (the request and plan
types of `ccnl_engine`, the facts of `ccnl_engine.inputs`, the events of
`ccnl_engine.events`) is classified in
`ccnl_engine.payroll.domain.input_defaults`, and
`tests/architecture/test_input_defaults.py` fails on a defaulted field
without a classification, or on a classification without its field:

- `absence_is_fact`: the default is the fact. No event happened, the
  employment has not ended, the worker waived no regime, declared no
  certified disability and no sole-parent condition, and exercised no
  contributory option.
- `requires_fact`: the default stands for a fact the caller has not stated.
  Each entry names the capability the fact feeds and how a run honours it:
  - `requirement`: an applicability fact of the registry (residence,
    family composition), so a `requirement_unresolved` blocker;
  - `reported`: the run reports the fact as missing when the capability
    needs it, with a `missing_fact` blocker or an input error (seniority,
    category, contribution history, sector, employer activity, prior-year
    income, current-year income with a dependant, signing date of a
    renewal, reference period of renewal arrears, contributable hours of a
    domestic CCNL, a child's birth date, the own income, residency,
    cohabitation and share of a dependant that may qualify for an art. 12
    TUIR deduction,
    the apprenticeship track among several, the additional 1% IVS other
    employers withheld when their base is imported and a run settles the
    1%, the opening state of a run that is not the first of an employment
    whose start is stated, the INPS base of other employments when the INPS
    rules carry a massimale or a 1% threshold, the TFR fund at 31 December
    of the year before on a December run, the Fondo Tesoreria destination
    of the TFR, the first day of the imported sickness history and the
    exemption of a short absence when a CCNL counting several sickness
    episodes needs them, the income beyond the employment when a somma
    esente is due, the full time of an employment whose weekly hours are
    stated, the roles of a worker on a level with an allowance restricted
    to a role, the enrolment in a pension fund of every CCNL but domestic
    work, the
    suspension of accrual of an absence that could change a rateo, the
    renewals and the NASpI exclusion of a fixed-term contract);
  - `pending`: not honoured yet. The default still selects a branch without
    a blocker. Treat these fields as required and state them.

The `pending` fields:

| Field | What the default does today |
|---|---|
| `Employment.employment_period` | A full month and full ratei, even for a hire or a termination within the month (a run after the first still needs its opening state) |
| `Employment.weekly_hours` | Full time (a domestic CCNL raises without it) |

A `pending` field becomes `requirement` or `reported` when its default can
be told apart from a stated value (a field that defaults to `True` or `0`
cannot) and the run blocks on it, or leaves the registry when its default
is removed. For every `requires_fact` field, the run that states the fact
has at most the blockers of the run that leaves it to its default
(`tests/acceptance/public_api/test_default_facts.py`, on the request pairs
of `tests/fixtures/default_cases.py`): a false default is never the one
path that looks payable. `Dependent.dependent_from` and `dependent_until` have no
default: `None` states an open end. `OpeningBalances.inps_bases`, `surtax_obligations` and
`recoveries` have no default: an import states what the previous provider
determined, `()` when there is nothing, and a closed run of a competence
year without its INPS base is an input error. The opening state is judged
on its content, not on the default: `PeriodState.zero()` passed
explicitly after the start of the employment blocks as the default does,
and so does every run that descends from it (`PeriodState.history_known`
is `False` on its closing state). See
[Opening state and imported balances](../engine/opening-state.md).

## Model limitations

A known simplification of the model is data, not a comment. The registry has
<!-- trust:limitations-total -->264<!-- /trust:limitations-total --> `ModelLimitation`
entries: one per `simplification` note of a CCNL file that can move an
amount, and <!-- trust:limitations-engine -->7<!-- /trust:limitations-engine -->
engine limitations of code paths several CCNLs share
(`knowledge/limitations/data/engine.json`: the apprenticeship midpoint and
the apprentice seniority increment, both resolved; a percentage
apprenticeship reducing an allowance whose `apprenticeship_pct_relevant` flag
the data leaves at its default; two sickness paths).
A CCNL whose midpoint components are unsourced carries its own
`<ccnl_id>/apprenticeship_midpoint_components` limitation. A CCNL that declares no
apprentice seniority amount carries its own `<ccnl_id>/apprentice_seniority`
limitation, recorded when an apprentice has matured increments the level
pays. Each entry has a stable `id`, the `capability` and `variant` it
limits, the `rulesets` and dates it affects, a `monetary_impact` (`yes`,
`no`, `unknown`), a `status` (`open`, `resolved`), its `source` and a
`remediation`.

The <!-- trust:simplification-notes -->325<!-- /trust:simplification-notes -->
simplification notes of the bundle each state their impact on what the engine
computes from the bundle:
<!-- trust:simplification-yes -->79<!-- /trust:simplification-yes --> `yes`,
<!-- trust:simplification-unknown -->178<!-- /trust:simplification-unknown --> `unknown`
and <!-- trust:simplification-no -->68<!-- /trust:simplification-no --> `no` (the
engine refuses the case, or takes the value from the caller). A file whose
note can move an amount without declaring a limitation does not load, so the
bundle build fails on an unmapped note.

A limitation applies to a run only when its predicate holds, never because
the run uses its CCNL:

- the capability it limits applies to the run (an overtime limitation needs an
  overtime event);
- the run date, contract type, level, worker category, run kind and seniority
  fall within its `applies_when` scope (an unknown category or seniority does
  not rule a run out);
- an engine limitation applies only when the run takes its code path, and the
  run records the traversal (an apprentice in a midpoint period of a CCNL
  whose midpoint components are unsourced);
- <!-- trust:limitations-outside-input -->43<!-- /trust:limitations-outside-input -->
  limitations depend on a fact the request cannot express (a hire date before
  a transitional regime, a fund the worker joins, a sector section): they are
  documented on the contract page and never recorded on a run.

Every applicable limitation is listed in `result.assurance.limitations`; an
open one with impact `yes` or `unknown` adds an `open_limitation` blocker.
Open limitations with an impact also lower the capability they limit to
`partial` in the [capability matrix](../contracts/capability-matrix.md), and
each contract page lists its limitations under "Known simplifications".

## Assurance axes

| Axis | Type | Derived from |
|---|---|---|
| `calculation` | `CalculationStatus` | Worst status of `result.issues` and `result.decisions`; `final` when there are none |
| `coverage` | `CoverageStatus` | `result.capability_report.status`: gaps and unresolved requirements |
| `evidence` | `EvidenceStatus` | Weakest provenance of the payable rules the run read (`verified`, `derived`, `assumed`, `missing`); `missing` when none carries a record |
| `rulesets` | `tuple[RulesetAssurance, ...]` | Identity, version, hash, kind, readiness and confidence of the CCNL ruleset and of each ruleset a payable rule was read from |
| `mode` | `EngineMode` | `simulation` (default) or `operational`, from the engine |
| `payability` | `Payability` | `payable` exactly when `blockers` is empty |
| `limitations` | `tuple[ModelLimitation, ...]` | The model limitations that apply to the run, open or resolved, whatever their impact |

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
| `somma_esente_band_assumed` | `provisional` | The worker has employment income from other employers this tax year; the percentage of the somma esente is taken on the income of this employer alone |
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
`capability_not_computed` blocker. `capability_report.unresolved` lists the
required capabilities left undecided by a default (see
[Fail-closed payability](#fail-closed-payability)).

| `status` | When |
|---|---|
| `complete` | No gaps and no unresolved requirement |
| `partial` | Every gap is a `partial_result` (a capability implemented in full came out partial) or a `partial_implementation` (sickness, foreign tax credit, ... executed) |
| `incomplete` | An unresolved requirement, or any other gap: an applicable capability is `unsupported` (residual leave on the run that closes the employment) or `unresolved` |

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
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.inputs import Permanent

engine = PayrollEngine.bundled()
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            contract_type=Permanent(),
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(regione="IT-25"),  # municipality and family unknown
    )
)

if not result.is_payable:
    for blocker in result.blockers:
        print(blocker.code.value, blocker.feature, blocker.detail)
# among others (the seniority is unknown too):
# → requirement_unresolved addizionale_comunale facts.comune_belfiore
# → requirement_unresolved family_deductions facts.family_composition

for requirement in result.capability_report.unresolved:
    print(requirement.feature, requirement.fact)

assurance = result.assurance
print(assurance.calculation, assurance.coverage, assurance.evidence)
for ruleset in result.rulesets:
    print(ruleset.id, ruleset.kind, ruleset.readiness, ruleset.source_hash[:12])
```
