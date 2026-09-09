# Trust

A payroll figure is only as useful as the confidence you can place in it.
This section documents every mechanism the engine uses to make its results
verifiable, reproducible, and transparent about their own limits.

## Three verifiability layers

Every `compute()` result carries three independent layers:

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
- **extraction**: method (`manual` or `ai_assisted`), timestamp, verifier
- **verification_status**: `"verified"` | `"unverified"` | `"needs_review"`

See [Provenance](provenance.md) for the full schema and how to read it.

## Versioning {#versioning}

Every payroll computation records exactly which ruleset versions it used:

```python
calc = compute(ccnl, rules, employee)

for identity in calc.ruleset_versions:
    print(identity)
# ccnl/metalmeccanico-federmeccanica@2026.2
# tax/2026/industria@2026.2
# surtax/2026@2026.2
```

Each `RulesetIdentity` carries:

- `id` — stable identifier for the ruleset
- `version` — dataset version at computation time
- `source_hash` — SHA-256 of the underlying JSON file
- `effective_from` / `effective_until` — validity window
- `verification_status` — data confidence

To reproduce a historical result, pin the same `ccnl-engine` package version
and dataset version. The engine's `engine_version()` function returns the
current runtime version.

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
