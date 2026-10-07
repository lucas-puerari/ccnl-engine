# Data operations policy

This page documents how CCNL and statutory data is kept current, how errors
are corrected, and what compatibility guarantees the knowledge base provides.

---

## Ruleset states

Every CCNL ruleset is classified by two orthogonal signals:

| Signal | Field | Values | Meaning |
|---|---|---|---|
| Readiness | `verification.readiness` | `exploratory` / `reviewed` / `production` | Whether the ruleset has been human-reviewed for a given use context; public as `RulesetAssurance.readiness`, enforced in `operational` mode |
| Verification | `verification.confidence` | `unverified` / `verified` / `needs_review` | File-level review state; public as `RulesetAssurance.confidence`, which flags a `reviewed` or `production` tier without `verified` confidence |
| Rule provenance | `provenance.status` on each payable rule | `verified` / `derived` / `assumed` / `missing` | How far each value is backed by its source; `assumed` or `missing` makes a result that reads it not payable, `missing` also `incomplete` (see [Provenance](provenance.md)) |

See [Readiness](readiness.md) for promotion criteria between tiers and the
current classification of each contract.

---

## Update targets (non-binding)

The following are engineering targets, not contractual SLAs.

| Event | Target update window |
|---|---|
| CCNL renewal published | Within 60 days of the official signing date |
| Salary table update (mid-agreement tranche) | Within 30 days of the effective date |
| IRPEF bracket / deduction change | Within 14 days of the Gazzetta Ufficiale publication |
| INPS rate change | Within 14 days of the INPS circular |

When a renewal is in progress but not yet modelled, the active ruleset's
`effective_until` is left open and a `needs_review` flag is set on the
affected salary table values.

---

## Refreshing the municipal surtax table

`surtax/data/comunale-<year>.json` is built by
`scripts/data/build_comunale_surtax.py` from the MEF Dipartimento delle
Finanze lists of the addizionale comunale, one CSV per year, updated every
day (index: `https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/nuova_addcomirpef/download/tabella.htm`).
Municipalities publish their delibere through the year, so a table built in
September misses the later ones.

**Cadence.** Rebuild the table of the current year once a month, and once
more after 20 December, when the list of the year closes: from then on the
MEF shows the rates in force for every municipality and `0*` only for those
that never instituted the surtax.

**Procedure.**

1. Download the list of the table year and of the two years before into a
   new, empty directory outside the repository. The files are untrusted
   input: do not open them with tools that execute content, and run nothing
   from that directory.

   ```bash
   dl=$(mktemp -d)
   base=https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/fiscalitalocale/nuova_addcomirpef/download/download.php
   for y in 2026 2025 2024; do curl -sSL -o "$dl/$y.csv" "$base?anno=$y"; done
   shasum -a 256 "$dl"/*.csv
   ```

2. From the repository root, build the table, newest list first, with the
   download date and the next ruleset version (`YYYY.N`, one more than the
   bundled one, so a run records which table it used):

   ```bash
   uv run python scripts/data/build_comunale_surtax.py --year 2026 \
       --current "$dl/2026.csv" --previous "$dl/2025.csv" "$dl/2024.csv" \
       --retrieved YYYY-MM-DD --version 2026.N
   ```

   The script writes the sha256 of every list and the counts into `notes`,
   and stops without writing when a row cannot be read. Fix the parser (with
   a test) or add a reviewed entry to `CORRECTIONS`; never edit the JSON by
   hand.
3. Compare the new table with the bundled one (rates, exemption, rates year
   per code) and list the municipalities whose rates changed in the PR.
4. Spot-check a few changed rows, and the largest cities, against the MEF
   page of each municipality
   (`.../nuova_addcomirpef/risultato.htm?lista=1&r=1&pagina=<region>.htm&pr=<province>&cc=<code>&anno=<year>`).
5. Regenerate the docs (`gen_contract_pages.py`, `gen_trust_counts.py`,
   `gen_capability_matrix.py`) and run the quality gates.

**Cases the build handles.**

| List shows | Table row |
|---|---|
| A delibera of the year | The rates, under the table `derived` record (CSV URL and section) |
| `0*` in the list of the year | The row in force the year before, `rates_year` set, `assumed` |
| A delibera marked inapplicable (adopted after the deadline) | Skipped like `0*`: the rates in force stay, down to the oldest list passed |
| `0*` in an earlier, closed list | Rate 0: the surtax was never instituted |
| A code missing from the list of the year before (a merged municipality) and `0*` | Left out and named in `notes`: the engine reports the code as unknown and the result is not payable |
| An exemption for one category of income (`FLAG_NUOVA` 5 or 6) | Kept as text in `specific_exemptions`; the result is provisional |

A row is promoted to `verified` only after a named human review; the build
never does it.

---

## Changelog and economic diff

Every dataset release ships a `CHANGELOG.md` at the repository root.
Entries follow the format:

```
## [<version>] — <date>

### CCNL <name> (<CNEL code>)
- Salary table updated: effective from <date>
  - Level 3: 1 850,00 → 1 920,00 EUR/month (+70,00)
  - ...
```

The diff is expressed in absolute EUR values for salary table entries and
as percentage points for rate changes (INPS, IRPEF). This makes it possible
to assess the economic impact of a knowledge-base update without running
simulations.

Programmatic consumers can parse the changelog or watch GitHub releases,
which carry the same information as release notes.

---

## Reporting errors

To report a data error (wrong salary value, missing allowance, incorrect rate):

1. Open a GitHub issue with the label `data-error`.
2. Include: the CCNL name, the CNEL code, the incorrect value, the correct
   value, and a link to the authoritative source (CCNL text, official table,
   or Gazzetta Ufficiale).
3. Critical corrections (value wrong by more than 5%) are prioritised over
   the standard update window.

For errors in statutory rates (IRPEF, INPS) that affect many contracts,
open an issue with the label `statutory-rate-error`.

---

## Deprecation and version compatibility

**Knowledge-base versions** follow `YYYY.N` (e.g. `2026.2`). Every
`PeriodResult` and `CompetenceYearResult` records the version in `bundle_version`, and
each decision names the ruleset it applied (`rule`, `rule_version`), so any
figure can be reproduced by pinning that version.

**Deprecation policy:**

- A knowledge-base version is supported for as long as the matching
  `ccnl-engine` package release is on PyPI.
- When a CCNL is removed (contract terminated or superseded), it is marked
  `effective_until` in its last dataset version and absent from the next.
- No breaking changes to the JSON schema are introduced within a minor
  knowledge-base release. Schema changes are announced in the changelog
  and in a GitHub discussion at least 30 days before they take effect.

**Engine API compatibility:**

The Python API follows semantic versioning. Patch releases are backwards
compatible. Minor releases may add fields to `PeriodResult` or new values
to existing enums (callers must handle unknown values defensively). Major
releases may break the public API and will be announced with a migration
guide.
