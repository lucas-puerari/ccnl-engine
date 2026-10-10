# Task: Verify the provenance of fiscal rule files

**Scope**: `src/ccnl_engine/knowledge/taxation/`, `social_security/`, `surtax/` JSON files

---

## Current state

Every payable block of the fiscal files carries a provenance record (see
[Trust: Provenance](../trust/provenance.md)): one per block of the tax and
INPS files, the sibling `irpef_brackets_provenance` and
`fixed_term_additional_rate_provenance`, one per surtax table, and the
`source_status` of each substitute-tax regime.

The records cite what each file already recorded in its notes and ruleset
source. None is `verified`: no file names a reviewer and a date.  Every
record of a file whose ruleset is `estimated` (the eight sector tax files and
the eight sector INPS files) is `assumed` under the label gate (see
[Trust: Provenance](../trust/provenance.md)); the statutory blocks that do
not depend on the sector live in their own files and are `derived` (the somma
esente in `taxation/exemption/2026.json`).  The `assumed` blocks with an
open question beyond the missing citation are:

| File | Block | Open question |
|---|---|---|
| `social_security/contribution/2026/{agricoltura,artigianato,credito}.json` | `apprentice` | No apprentice table of the sector: the CISOA of agricoltura, the NASpI reduction of the artigiani and the Fondo di solidarietà del credito are not settled |
| `social_security/contribution/2026/credito.json` | `inps` | Totals of a 2012 INPS table; the Fondo di solidarietà del credito (0.20%, BCC 0.36%) is not modelled |
| `social_security/contribution/2026/artigianato.json` | `inps` | Aggregator rates; INPS circular not retrieved |
| `social_security/contribution/2026/pubblica-amministrazione.json` | `apprentice` | Schema placeholder |
| `surtax/municipal/2026.json` | rows carried from an earlier year | No applicable 2026 delibera in the MEF list; the rates in force are carried forward (L. 296/2006 art. 1 c. 169) |
| `surtax/municipal/2026.json` | A112 Airuno, A785 Bentivoglio | Third band of the MEF list repeats the second; read as 28,000.01-50,000 |

Each open question is also in the `note` of its record, so a run that reads
the rule shows it through the `rule_source_weak` blocker of its capability.

The regional table is `derived` row by row from the MEF 2026 pages (URL and
publication date per row, retrieved on 27 September 2026); the municipal
table is `derived` from the MEF 2026 CSV list and is regenerated with
`scripts/data/build_comunale_surtax.py`.

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

- IRPEF and credits 2026: L. 199/2025 art. 1 cc. 3-4, L. 207/2024 art. 1
  cc. 4-7, D.L. 3/2020 art. 1, Art. 13 TUIR.
- INPS: the annual INPS circulars per sector (Circ. 6/2026 for the IVS
  ceiling and rates, Circ. 9/2026 for domestic work), D.Lgs. 148/2015 for
  CIGO, CIGS and FIS.
- Surtax: the MEF pages of the addizionale regionale
  (`addregirpef.php?reg=NN&anno=2026`, the URL of each row) and the
  *elenco generale* CSV of the addizionale comunale
  (`nuova_addcomirpef/download/download.php?anno=2026`).

---

## Acceptance criteria

- `python scripts/ci/check_provenance.py --rules` passes and reports the
  block as `verified`.
- No value changed without a recomputed `source_hash`.
- `uv run pytest` still passes at 100% coverage.
