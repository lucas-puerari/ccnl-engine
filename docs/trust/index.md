# Trust

A payroll figure is only as useful as the confidence you can place in it.
This section documents every mechanism the engine uses to make its results
verifiable, reproducible, and transparent about their own limits.

## Three layers of correctness {#correctness}

A simulation can be correct at the software level but wrong at the data level,
or correct at both levels but incomplete for your specific scenario. The engine
makes all three explicit:

| Layer | Question | Measured by |
|---|---|---|
| **Software** | Does the engine apply its rules consistently? | 100% branch coverage, mypy strict, reference table cases, legal scenario tests |
| **Source** | Do the modelled rules match the current authoritative sources? | Ruleset readiness tier |
| **Case** | Does the user's scenario fall within the modelled scope? | `is_payable`, `blockers` and `assurance`, with `issues` and `decisions` |

See [Correctness layers](correctness.md) for the full breakdown and a guide to
reading all three together.

## Ruleset readiness {#readiness}

Before reading about result-level signals, understand the ruleset-level
classification that tells you whether a CCNL is cleared for a given use context.

| Tier | Symbol | Meaning | Safe for |
|---|:---:|---|---|
| `exploratory` | 🧪 | Extracted and traced; no human review of key values | Demo, research, prototyping |
| `reviewed` | 👁 | Key L1 values human-verified against primary sources | Product simulations with explicit disclaimer |
| `production` | 🏭 | Full review, reference case, named owner, update policy | Operational flows |

The `readiness` tier of every CCNL is public: `engine.list_contracts()` lists it
on each `ContractSummary`, `engine.inspect_ruleset(ccnl_id)` returns the full
`RulesetAssurance`, and every result reports it in `result.rulesets`. It is
also shown in the [CCNL coverage matrix](../contracts/index.md). An engine
built with `mode="operational"` blocks payment from any CCNL that is not
`production`.

See [Readiness](readiness.md) for promotion criteria and the current status of
each tier.

## Result signals

Every result carries its own assurance:

```
PeriodResult
 ├── is_payable           whether the amounts can be paid as computed
 ├── blockers             every reason they cannot, machine-readable
 ├── assurance            calculation, coverage, evidence, rulesets, payability
 ├── rulesets             rulesets the executed rules came from
 ├── issues               conditions that lowered the calculation axis
 ├── decisions            what each capability decided, from which inputs
 ├── capability_report    applicable capabilities the run did not cover
 └── bundle_version       knowledge-base version of the calculation
```

`YearResult` exposes the same assurance for the whole year (each axis the
worst of its runs, rulesets and blockers listed once, payable only when every
run is), the issues of its runs (each once) and their decisions in payment
order.

### 1. Payability

`result.is_payable` is the only answer to "can this amount be paid?". A result
is payable only when nothing blocks it; each `ResultBlocker` has a stable
`code`, the `feature` it concerns, a machine-readable `detail` and a
`remediation`.

```python
if not result.is_payable:
    for blocker in result.blockers:
        print(blocker.code.value, blocker.feature, blocker.detail)
```

Known simplifications of the model are part of the answer:
`result.assurance.limitations` lists the model limitations that apply to the
run, and an open one that can move an amount is an `open_limitation` blocker
(see [Model limitations](confidence.md#model-limitations)).

An unknown normative fact never yields a payable result: the rule it drives
is not applied and an issue says why. See [Assurance](confidence.md) for the
payability rules, the axes and what the bundle gives today.

### 2. Decisions

`result.decisions` records every decision a capability took: its
`reason_code`, the normalized `inputs` it read, the rule and rule version
applied, the normative source and the amount. A capability that ran and found
nothing due still records a decision with amount 0.
Every posted amount rests on at least one decision: the base stages (pay
chain, INPS, TFR, IRPEF) record one each, and a rate or amount the caller
supplies in place of a rule is recorded with origin `caller_supplied`. See
[Decisions](decisions.md).

### 3. Capability report

`result.capability_report` compares what the run executed with the capability
registry of the tax year, the single source of coverage (see the
[capability matrix](../contracts/capability-matrix.md)). `scope` says, for
every capability, whether it is `applicable` to the run, `not_applicable` or
`outside_input` (the request has no field for the fact that would make it
apply). Only an applicable capability can leave a gap: `unsupported` (the
engine does not compute it), `unresolved`, `partial_result` or
`partial_implementation`. Each gap blocks payability. Its `status` is the
coverage axis of the assurance, and `rule_sources` gives the weakest
provenance status of the rules each executed capability read; see
[Assurance](confidence.md).

## Provenance {#provenance}

Every payable rule (salary tables, allowances, seniority and extra-month
entitlements, INPS rates, IRPEF brackets, deductions and credits, the TFR
divisor, surtax tables, substitute-tax regime parameters) carries a
`provenance` record:

- **status**: `verified`, `derived`, `assumed` or `missing`
- **source_document** and **section**: the document and the article, table
  or page
- **extraction**: method, validity and reviewer, when recorded
- **transformation**: how the source text became the stored value

A rule read by a run with status `assumed` or `missing` makes the result not
payable; `missing` also makes it `incomplete`.
See [Provenance](provenance.md) for the schema, the granularity and the
current counts.

## Versioning {#versioning}

Every payroll computation records exactly which ruleset versions it used:

```python
from ccnl_engine import engine_version

print(result.bundle_version)  # knowledge-base version of the calculation
print(engine_version)  # engine package version
for decision in result.decisions:
    print(decision.capability, decision.rule, decision.rule_version)
```

Each decision names the ruleset it applied (`rule`, `rule_version`), e.g.
`tax/variable-pay-rules/2026` at `2026.1`. To reproduce a historical result,
pin the same `ccnl-engine` package version: it ships the knowledge bundle.

## Quality gates

Every change to the codebase, including JSON data files, must pass these
gates; the `CI` workflow runs all of them on every pull request:

| Gate | Command | Standard |
|---|---|---|
| Tests | `uv run pytest` | 100% branch coverage of `src/ccnl_engine` |
| Lint | `uv run ruff check src/ tests/ scripts/` | Zero errors |
| Format | `uv run ruff format --check src/ tests/ scripts/` | No changes |
| Types | `uv run mypy src/ tests/` and `uv run mypy scripts/ --explicit-package-bases` | Zero errors, strict mode |
| Structure | `uv run python scripts/ci/check_structure.py` | File, function and class size limits |
| Provenance | `python scripts/ci/check_provenance.py --all` | Every payable rule and reference case has a provenance record |
| Contract pages | `uv run python scripts/docs/gen_contract_pages.py --check` | Every page matches its CCNL data |
| Trust counts | `uv run python scripts/docs/gen_trust_counts.py --check` | Every count in `docs/trust/` matches the bundle |

Other workflows check the capability matrix, the contracts index, the
contract examples and the cognitive complexity of `src/`.

JSON changes in `knowledge/*/data/` are treated as code-level changes: they
alter engine behaviour and carry the same gates as Python source.

## No feature without provenance and reference cases

This is a hard rule:

> Every new feature must ship with a `provenance` entry on the relevant JSON
> rule and tests whose expected values come from a source independent of the
> engine: a signed table, an official worked example or a hand calculation
> formulated differently.

Expected values copied from engine output detect regressions only, never a
systematic error, so they are not accepted as proof of correctness.
Reference cases live in `tests/fixtures/expected/` and
`tests/acceptance/public_api/test_reference_cases.py` runs each one through
`PayrollEngine`. They are reference table cases, not full payslips: a case
asserts only the values its source states (base salary, fixed allowances and
period gross from the cited table), to the cent, and never net pay,
contributions, taxes or employer cost. Of the
<!-- trust:reference-cases -->5<!-- /trust:reference-cases --> cases,
<!-- trust:reference-cases-verified -->0<!-- /trust:reference-cases-verified -->
are `verified` and
<!-- trust:reference-cases-source-linked -->5<!-- /trust:reference-cases-source-linked -->
are `source_linked`.

### Reference case verification status

Reference cases declare how far their expected values can be trusted with a
top-level `verification` field:

| Value | Meaning | `source` |
|---|---|---|
| `verified` | Expected values checked against an independent source (a real payslip or an official worked example) | Required |
| `source_linked` | The case cites the primary source it models; expected values are not checked against a payslip | Required |

`tests/architecture/test_data_quality.py` rejects a missing or unknown
value, a case without a `source` object, and a case whose inputs or expected
values differ from what the runner executes. In CI,
`scripts/ci/check_provenance.py` validates every case, prints the count per
status, and rejects a modified case that drops its `source`; the same script
fails when a payable rule of the bundle has no provenance record. Expected values
are never regenerated from the engine by a script: changing one is a reviewed
edit to the JSON file.

## Data operations

See [Data operations](data-operations.md) for:

- update targets after CCNL renewals and statutory rate changes
- changelog format and economic diff per release
- error reporting process
- deprecation and version compatibility guarantees

---

## Coverage notes and simplifications

Each contract's documentation page lists its `coverage.notes` — the
audit trail of modelling decisions. Notes marked `simplification` are the
known errors: places where the model intentionally diverges from the literal
contract text. Reading them before using a result in a sensitive context is
strongly recommended.

Example from CCNL Metalmeccanico:

!!! warning "Known simplification"
    The under-classification apprenticeship track applies a single percentage
    to the destination level's full salary. In practice, some companies apply
    the percentage to the base salary only (excluding seniority). The error
    is bounded by the seniority amount times the apprenticeship discount.
