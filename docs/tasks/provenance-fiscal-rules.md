# Task: Verify the provenance of fiscal rule files

**Scope**: `src/ccnl_engine/knowledge/tax/`, `inps/`, `surtax/` JSON files

---

## Current state

Every payable block of the fiscal files carries a provenance record (see
[Trust: Provenance](../trust/provenance.md)): one per block of the tax and
INPS files, the sibling `irpef_brackets_provenance` and
`fixed_term_additional_rate_provenance`, one per surtax table, and the
`source_status` of each substitute-tax regime.

The records cite what each file already recorded in its notes and ruleset
source. None is `verified`: no file names a reviewer and a date. The blocks
recorded as `assumed` are:

| File | Block | Why |
|---|---|---|
| `tax/data/2026-*.json` | `somma_esente` | Band cut points are reconstructions from worked examples |
| `tax/data/2026-pubblica-amministrazione.json` | `fixed_term_additional_rate` | Exemption cited from commentary, no clause located |
| `inps/data/2026-artigianato.json` | `inps` | Aggregator rates; INPS circular not retrieved |
| `inps/data/2026-edilizia.json` | `inps` | Proxy values from a 1998 rate structure |
| `inps/data/2026-pubblica-amministrazione.json` | `apprentice` | Schema placeholder |
| `surtax/data/regionale-2026.json` | table | Publisher named, no document or date |

---

## What needs to be done

For each block:

1. Check the stored values against the primary source (Gazzetta Ufficiale,
   INPS circular, MEF table).
2. Record the location precisely in `location` (`section`, `page`, `quote`).
3. When the check is done, add an `extraction` with `verified_by` and
   `verified_at` and set `status` to `verified`. The model rejects
   `verified` without both.
4. When a value changes, update it and run
   `uv run python scripts/data/assign_rule_provenance.py` to rehash the file.

Primary sources to check against:

- IRPEF and credits 2026: L. 199/2025 art. 1 cc. 2-4, L. 207/2024 art. 1
  cc. 4-7, D.L. 3/2020 art. 1, Art. 13 TUIR.
- INPS: the annual INPS circulars per sector (Circ. 6/2026 for the IVS
  ceiling and rates, Circ. 9/2026 for domestic work), D.Lgs. 148/2015 for
  CIGO, CIGS and FIS.
- Surtax: the MEF tables of the addizionale regionale and comunale.

---

## Acceptance criteria

- `python scripts/ci/check_provenance.py --rules` passes and reports the
  block as `verified`.
- No value changed without a recomputed `source_hash`.
- `uv run pytest` still passes at 100% coverage.
