# Confidence

`PayrollResult.confidence` is a three-tier signal that summarises how much
to trust a specific computation result. It is derived automatically — callers
do not set it.

## The three levels

| Level | When assigned |
|---|---|
| `"low"` | Any active warning is present |
| `"medium"` | Complete or partial computation with no warnings, but at least one source (salary table, fiscal ruleset, or INPS ruleset) has `verification_status != "verified"` |
| `"high"` | Complete computation, no warnings, every salary-table source and every consumed ruleset is `"verified"` |

```python
from ccnl_engine import compute, PayrollScenario, Employee, Employment, Employer, Permanent
from datetime import date

scenario = PayrollScenario(
    employee=Employee(level_code="C2"),
    employment=Employment(
        ccnl="metalmeccanico-federmeccanica.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        calculation_date=date(2026, 1, 1),
    ),
)
result = compute(scenario).result
print(result.confidence)   # "low" | "medium" | "high"
```

## Derivation logic

```
warnings non-empty?
  YES → "low"
  NO  ↓

Any salary provenance or consumed ruleset with verification_status != "verified"?
  YES → "medium"
  NO  ↓

status == "complete" and all sources verified?
  YES → "high"
  NO  → "medium"
```

### What counts as a verified source

Two categories of sources are evaluated for the `"high"` gate:

1. **Salary provenance** — every `RuleProvenance` record collected from the
   CCNL schema (pay level, base-salary period, allowances, seniority). Records
   whose `extraction.verification_status` is not `"verified"` cause the result
   to be classified `"medium"`.

2. **Consumed rulesets** — the `RulesetIdentity` objects for the fiscal and
   INPS year files (and surtax when loaded). Their `verification_status` is
   evaluated alongside salary provenance. A fiscal or INPS ruleset marked
   `"unverified"` therefore prevents `"high"` confidence even when every CCNL
   salary figure has been human-reviewed.

### Why `fiscal_simplifications` does not affect confidence

The `fiscal_simplifications` frozenset records deliberate caller omissions
(e.g. no region passed → addizionale regionale excluded). These reflect
choices, not uncertainty. They appear in `calculation_scope` as `"excluded"`
items so callers can account for them, but they do not lower confidence.

### Why `"partial"` status does not always mean `"low"`

A computation is `"partial"` when certain L3 work-rule features are absent
from the contract's data (e.g. sickness rules not yet modelled). This is
expected and declared in `calculation_scope`. As long as there are no
warnings, the result is still useful and gets `"medium"` — not `"low"`.

A warning is reserved for situations the engine cannot quantify at all, such
as a contract whose JSON schema is missing a required block.

## Using confidence in practice

```python
result = compute(scenario).result

if result.confidence == "low":
    # Something is wrong — read warnings before using the number
    for warning in result.warnings:
        print("WARNING:", warning)

elif result.confidence == "medium":
    # Result is usable; check what's excluded
    excluded = [
        item.feature for item in result.calculation_scope
        if item.status == "excluded"
    ]
    if excluded:
        print("Excluded from net:", excluded)

else:  # "high"
    # All salary sources and rulesets verified, no warnings, complete computation
    pass
```

## What raises confidence to `"high"`

Currently, most contracts have `verification_status = "unverified"` on their
salary-table provenance, and the fiscal/INPS rulesets also carry
`"unverified"` until a human reviewer confirms the statutory parameters. This
means the default confidence for a normal computation is `"medium"`. Confidence
reaches `"high"` only when every salary figure and every consumed ruleset has
been human-reviewed and set to `"verified"`.

This is intentional: `"high"` is a strong claim. It requires that a specific
person confirmed a specific value from a specific document on a specific date.

See [Provenance](provenance.md) for the verification workflow.
