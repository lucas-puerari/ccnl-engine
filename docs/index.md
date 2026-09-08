# ccnl-engine

Python library for computing gross-to-net salary and employer cost from Italian
collective labor agreements (CCNL) and statutory contribution rates.

[**Demo**](../demo/) · [**GitHub**](https://github.com/lucas-puerari/ccnl-engine) · [**CCNL coverage**](contracts/index.md)

---

## Four pillars

| Pillar | What it covers |
|---|---|
| **Domain** | How Italian labor law and CCNLs are represented as typed models |
| **Rules** | The versioned knowledge base: CCNL tables, INPS rates, IRPEF brackets |
| **Engine** | How rules are applied to produce a reproducible payroll figure |
| **Trust** | Provenance, scope, versioning, and reference cases that make results verifiable |

---

## Documentation

| Section | Description |
|---|---|
| [Get started](getting-started/index.md) | Install, quickstart, and first payroll in 10 lines |
| [Domain](domain/index.md) | What CCNLs are, how Italian labor law structures them |
| [Guide](guide/employment-types.md) | How to use every library feature with worked examples |
| [Contracts](contracts/index.md) | All 100+ supported contracts — salary tables, sources, coverage |
| [API reference](api/index.md) | Full reference for every public type and function |
| [Governance](governance.md) | Release pipeline and quality gates |

---

## Why trust a number from this engine?

Every `compute()` result carries three verifiability layers:

1. **Provenance** — each rule links to its primary source document (CCNL article,
   INPS circular, tax schedule) with a URL, section, and verification status.
2. **Versioning** — `calculation.ruleset_version` records the exact knowledge-base
   snapshot, so any figure can be reproduced verbatim after a CCNL renewal.
3. **Scope** — `PayrollResult.calculation_scope` declares every feature as
   `verified`, `excluded`, or `not_computed`, so callers are never silently wrong.

```python
for item in result.calculation_scope:
    print(item.feature, item.status)
# base_salary       verified
# irpef             verified
# family_deductions excluded   ← explicitly absent from net figure
# overtime          excluded
```

See [example 11 — Why this number?](examples/11_why_this_number.py) for a
full walkthrough of all three layers.

---

## Scope

**Always computed (L1 — gross, L2 — net):**

- IRPEF gross and net (Art. 11–13 TUIR), work income deductions,
  *trattamento integrativo* (Art. 1 D.L. 3/2020)
- Regional and municipal income tax surcharges
  (*addizionale regionale e comunale IRPEF*)
- INPS contributions (employee and employer), resolved by headcount tier
- TFR accrual
- Contractual employer funds
- Part-time scaling, seniority increments, fixed allowances
- Apprenticeship contracts (under-classification and percentage tracks)
- Fixed-term contracts (NASpI *addizionale*)
- Second-level bargaining — territorial and company supplementary allowances
- Domestic work (flat per-hour contributions, non-withholding employer)

**L3 — time supplements (pilot: metalmeccanico):**

- Overtime pay (lavoro straordinario diurno, notturno, festivo)
- Night and holiday premiums

**Explicitly excluded (always reported in `calculation_scope`):**

- Family-dependent deductions (Art. 12 TUIR) — `family_deductions: excluded`
- Regional/municipal surtax when jurisdiction is not provided

**Not yet implemented:**

- Sick-pay integrations and leave accruals
- Performance bonuses
- Welfare and fringe benefits

Each gap is reported in `PayrollResult.warnings` or `calculation_scope` so the
caller knows exactly what is missing from the net figure.

---

## Disclaimer

Not legal or tax advice. Always verify results against official sources or a
qualified payroll professional.
