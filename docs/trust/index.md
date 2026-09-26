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
| **Software** | Does the engine apply its rules consistently? | 100% coverage, mypy strict, reference cases |
| **Source** | Do the modelled rules match the current authoritative sources? | Ruleset readiness tier |
| **Case** | Does the user's scenario fall within the modelled scope? | `status`, `issues`, `decisions` and `capability_report` |

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

The `readiness` tier is exposed on every CCNL through `ccnl.verification.readiness`
and shown in the [CCNL coverage matrix](../contracts/index.md).

See [Readiness](readiness.md) for promotion criteria and the current status of
each tier.

## Result signals

Every result carries its own reliability signals:

```
PeriodResult
 ├── status               final | provisional | incomplete | rejected
 ├── issues               conditions that lowered the status
 ├── decisions            what each capability decided, from which inputs
 ├── capability_report    catalog features the run did not execute
 └── bundle_version       knowledge-base version of the calculation
```

`YearResult` exposes the worst status of its runs, their issues (each once)
and their decisions in payment order.

### 1. Status

| Status | Meaning |
|---|---|
| `final` | Every capability decided from known rules and facts. |
| `provisional` | Computed, but a decision rests on an assumption that may change the amounts, e.g. an unknown prior-year income for a substitute-tax regime. |
| `incomplete` | At least one amount could not be determined, e.g. a surtax without a table; do not pay as is. |
| `rejected` | The inputs cannot produce a meaningful result. |

```python
from ccnl_engine import CalculationStatus

if result.status is not CalculationStatus.FINAL:
    for issue in result.issues:
        print(issue.code, issue.status, issue.message)
```

An unknown normative fact never yields a `final` result: the rule it drives
is not applied and an issue says why. See
[Results and calculation status](../api/engine.md#results-and-calculation-status).

### 2. Decisions

`result.decisions` records every decision a capability took: its
`reason_code`, the normalized `inputs` it read, the rule and rule version
applied, the normative source and the amount. A capability that ran and found
nothing due still records a decision with amount 0.

### 3. Capability report

`result.capability_report` compares what the run executed with the capability
catalog of the tax year. Each gap names the feature and why it is missing
(`feature_absent`, `not_computed`, `unresolved`,
`promised_computed_got_partial`). Its `confidence` summarises the gaps; see
[Confidence](confidence.md).

## Provenance {#provenance}

Every rule in a CCNL JSON — every salary table entry, every seniority amount,
every work-rule parameter — carries a `provenance` block that records:

- **source_document**: the primary document (URL, title, publication date)
- **section**: the specific article, table, or page
- **extraction**: method (`manual`, `ai`, `back_calculation`, or `import`), timestamp, verifier
- **verification_status**: `"verified"` | `"unverified"` | `"needs_review"`

See [Provenance](provenance.md) for the full schema and how to read it.

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

Every change to the codebase — including JSON data files — must pass all
four gates before merging:

| Gate | Tool | Standard |
|---|---|---|
| Tests (100% branch coverage) | `uv run pytest` | Hard gate — no exceptions |
| Lint | `uv run ruff check src/ tests/` | Zero errors |
| Types | `uv run mypy src/ tests/` | Zero errors, strict mode |
| Complexity | `uv run complexipy src/` | ≤ 15 per function |

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
`PayrollEngine`. A case asserts only the values its source states (base
salary, fixed allowances and period gross from the cited table), to the cent.

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
status, and rejects a modified case that drops its `source`. Expected values
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
