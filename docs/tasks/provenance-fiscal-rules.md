# Task: Populate provenance for fiscal rule files

**Priority**: Medium (prerequisite for auditor trace — Step 4 of the trace roadmap)

**Scope**: `src/ccnl_engine/knowledge/tax/`, `inps/`, `surtax/` JSON files

---

## Background

The `CalculationTrace.fiscal_steps` chain (added in `feature/calculation-trace-fiscal`)
emits step-by-step derivations from gross to net. To expose the auditor view
("which norm justifies this figure?"), each fiscal rule file needs its
`ruleset.source` and `ruleset.verification_status` fields filled in.

### Current state (measured 2026-09-09)

| Domain | Files | `source` | `verification_status` |
|---|---|---|---|
| CCNL levels | 991 levels across 103 files | 100% populated | varies |
| Tax (IRPEF brackets, deductions) | 11 files | `"unavailable"` | `"unverified"` |
| INPS rates | 9 files | `"unavailable"` | `"unverified"` |
| Surtax (regionale, comunale) | 2 files | `"unavailable"` | `"unverified"` |

CCNL data is already covered. Fiscal rule files are the gap.

---

## What needs to be done

For each file in `knowledge/tax/data/`, `inps/data/`, `surtax/data/`:

1. **Identify the primary normative source** (see references below).
2. **Replace `source: "unavailable"`** with a structured citation string:
   `"<type>/<id>"` — e.g. `"legge/207-2024"`, `"dm/2024-01-22"`,
   `"circolare-inps/32-2024"`.
3. **Set `verification_status: "verified"`** after cross-checking the rates
   against the source document.
4. **Update `source_hash`** if any rate values were corrected during the check.

Do NOT add a top-level `provenance` field — the existing `ruleset` block
is the correct schema for file-level provenance.

---

## Files and their normative sources

### Tax files (`knowledge/tax/data/`)

Each file is named `{year}-{sector}.json`. The IRPEF brackets and deduction
formulas are statutory (same across sectors for a given year), set by the
annual legge di bilancio or specific DL/DPR.

| Year | Primary source |
|---|---|
| 2026 | L. 207/2024 (legge di bilancio 2025, art. 1 cc. 2-7) + L. 199/2025 (riforma IRPEF) |
| 2025 | L. 213/2023 (legge di bilancio 2024) + D.Lgs. 216/2023 |
| 2024 | D.Lgs. 216/2023 + L. 213/2023 |

The `work_income_deduction` formula is Art. 13 TUIR (DPR 917/1986) as amended
by the applicable legge di bilancio.

The `trattamento_integrativo` parameters are Art. 1 D.L. 3/2020 as amended.

### INPS files (`knowledge/inps/data/`)

Each file covers one sector/year. Rates come from:

- **Industria / commercio / terziario**: circolari INPS annual rate tables,
  typically Circolare INPS n. 5-10 of each year + aliquote D.Lgs. 148/2015
  for FIS/CIGS funds.
- **Artigianato**: circolari INPS for artigianato sector rates.
- **Agricoltura**: circolari INPS for agriculture.
- **Credito**: specific CCNL-level INPS rates per bancari-ABI contract.
- **Lavoro domestico**: specific domestic flat rates per DM.

Use [INPS → Datori → Aliquote contributive] for each sector.

### Surtax files (`knowledge/surtax/data/`)

- **Addizionale regionale**: each region deliberates its rates by 31/12 of the
  previous year. Source: MEF database at
  `https://www.finanze.gov.it/it/fiscalita-regionale-e-locale/addizionale-irpef/addizionale-regionale/`.
- **Addizionale comunale**: MEF database at
  `https://www.finanze.gov.it/it/fiscalita-regionale-e-locale/addizionale-irpef/addizionale-comunale/`.

For both, verification means checking that the bracket rates in the JSON match
the deliberated rates for the reference year.

---

## Acceptance criteria

- Every file in `tax/data/`, `inps/data/`, `surtax/data/` has:
  - `ruleset.source` != `"unavailable"`
  - `ruleset.verification_status` == `"verified"`
- No existing rate values changed without an updated `source_hash`.
- `uv run pytest` still passes at 100% coverage after any JSON changes.

---

## Out of scope

- Adding per-bracket or per-rate citations inside each file (fine-grained
  provenance). The file-level citation is sufficient for the auditor view.
- Changing the `RuleProvenance` schema — it is already correct.
- CCNL level/seniority provenance — already 100% covered.
