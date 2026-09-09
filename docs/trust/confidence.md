# Confidence

`PayrollResult.confidence` is a three-tier signal that summarises how much
to trust a specific computation result. It is derived automatically — callers
do not set it.

## The three levels

| Level | When assigned |
|---|---|
| `"low"` | Any active warning is present |
| `"medium"` | Complete or partial computation with no warnings, but at least one salary-table source has `verification_status != "verified"` |
| `"high"` | Complete computation, no warnings, every salary-table source is `"verified"` |

```python
result = compute(ccnl, rules, employee).result
print(result.confidence)   # "low" | "medium" | "high"
```

## Derivation logic

```
warnings non-empty?
  YES → "low"
  NO  ↓

Any salary-table provenance with verification_status != "verified"?
  YES → "medium"
  NO  ↓

status == "complete" and no unverified salary sources?
  YES → "high"
  NO  → "medium"
```

### What counts as a salary-table source

Only provenance records with `rule_id` containing `TABELLA_RETRIBUTIVA` (the
source kind for salary tables) are evaluated for the `"high"` gate. Tax
brackets, INPS rates, and surtax tables are not included in this check —
their data comes from official government publications and is assumed
authoritative.

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
result = compute(ccnl, rules, employee).result

if result.confidence == "low":
    # Something is wrong — read warnings before using the number
    for w in result.warnings:
        print("WARNING:", w)

elif result.confidence == "medium":
    # Result is usable; check what's excluded
    excluded = [
        i.feature for i in result.calculation_scope
        if i.status == "excluded"
    ]
    if excluded:
        print("Excluded from net:", excluded)

else:  # "high"
    # All salary sources verified, no warnings, complete computation
    pass
```

## What raises confidence to `"high"`

Currently, most contracts have `verification_status = "unverified"` on their
salary-table provenance. This means the default confidence for a normal
computation is `"medium"`. Confidence reaches `"high"` only when a human
reviewer has cross-checked every salary figure against the primary source
document and set `verification_status = "verified"` on each provenance block.

This is intentional: `"high"` is a strong claim. It requires that a specific
person confirmed a specific value from a specific document on a specific date.

See [Provenance](provenance.md) for the verification workflow.
