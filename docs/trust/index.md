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
| **Case** | Does the user's scenario fall within the modelled scope? | `calculation_scope` and `warnings` |

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

## Three verifiability layers

Every result carries three independent layers:

```
PayrollResult
 ├── confidence           "low" | "medium" | "high"
 ├── calculation_scope    what was computed, excluded, or not run
 ├── warnings             active gaps the caller must know
 └── provenance           chain of source documents behind every rule
```

### 1. Confidence

A single three-tier signal derived automatically from the result:

| Level | Meaning |
|---|---|
| `"high"` | Complete computation, no warnings, all salary-table sources verified |
| `"medium"` | Complete or partial with no warnings, but some sources are unverified |
| `"low"` | One or more active warnings — the engine detected a gap it cannot quantify |

```python
result = calculation.result
print(result.confidence)  # "medium"
```

See [Confidence](confidence.md) for the full derivation.

### 2. Scope

`calculation_scope` declares every engine feature as `"verified"`,
`"excluded"`, or `"not_computed"`:

```python
for item in result.calculation_scope:
    print(item.feature, item.status)
# irpef                    verified
# addizionale_regionale    verified
# family_deductions        excluded    ← deliberate caller choice
# overtime                 not_computed
```

`"excluded"` means the caller deliberately omitted that input (e.g. no
region was passed, so regional surtax is zero and excluded).
`"not_computed"` means the feature exists but the contract's work-rules data
does not yet include it.

Callers must never silently ignore `calculation_scope`: a `net_annual` that
omits family deductions is meaningfully different from one that includes them.

### 3. Warnings

`warnings` is a tuple of strings describing active gaps — situations where the
engine was asked to compute something it could not fully handle:

```python
for w in result.warnings:
    print(w)
# "CCNL schema missing time_supplements block — L3 not computed"
```

A non-empty `warnings` tuple sets `confidence = "low"` automatically.

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
for kind, identity in calc.ruleset_version.items():
    print(kind, identity)
# ccnl  metalmeccanico-federmeccanica@2026.2
# tax   tax/2026/industria@2026.2
# inps  inps@2026.2
```

`ruleset_version` is a plain `dict[str, str]` mapping ruleset kind (e.g.
`"ccnl"`, `"tax"`, `"inps"`) to an `"id@version"` string.

To reproduce a historical result, pin the same `ccnl-engine` package version
and dataset version. `calc.engine_version` is the string version of the
engine that produced the result.

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
> rule and at least two reference test cases that exercise the feature
> end-to-end and assert exact output values.

A feature with no reference case has no proof of correctness.
Reference cases live in `tests/integration/cases/` and are byte-identical
assertions — the test fails if a salary table change shifts any output by
even one cent.

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
