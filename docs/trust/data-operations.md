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

A row is promoted to `verified` only after a named review (a person, or an AI review the owner authorised); the build
never does it.

---

## Calendar of yearly data

The bundle ships the tax and INPS tables of the years
`ccnl_engine.catalog.supported_tax_years()` returns; a payment of another
tax year raises `UnsupportedTaxYearError` naming them.  Rules of one year are
never applied to another as final: a year whose sources are not published
yet ships as a provisional copy of the year before.  Its rulesets set
`provisional: true`, `source_type: estimated` and `assumed` records, and
every run that reads them traverses the open engine limitation
`provisional_ruleset` (tax) or `provisional_inps_ruleset` (INPS) and is
not payable.  The 2027 tables are provisional
(October 2026); the TFR revaluation of 2027 is not shipped, because its
substitute tax rule changes (table below).

| When | Task |
|---|---|
| Mid-January | Insert the ISTAT FOI index (without tobacco) of December of the previous year in `tax/data/tfr-revaluation-<year>.json` (`december` is `null` until then): every December run with a TFR fund to revalue is blocked without it (art. 2120 c. 4 c.c.). |
| After the budget law and the INPS circulars of the year | Build the `<year>-<sector>.json` tax and INPS files, the somma esente, family deductions, variable pay, surtax and TFR revaluation files of the year, each record with its own source; drop the `provisional` flag of each, and resolve `provisional_ruleset` when no provisional ruleset is left. |

Provisions of 2026 that change or end in 2027, to settle when the 2027
rulesets are built (sources on Normattiva, read in October 2026):

| Provision | Status in 2027 | Engine use |
|---|---|---|
| Art. 23 DPR 600/1973 (withholding by the sostituto) | Repealed from 1 January 2027, replaced by D.Lgs. 33/2025 (Testo unico versamenti e riscossione) | Per-run withholding and conguaglio |
| Art. 17 TUIR (separate taxation) and the text of art. 21 TUIR | Replaced from 1 January 2027 by arts. 19 and 23 of the testo unico of D.Lgs. 19 giugno 2026 n. 117, same rules: the engine cites them from tax year 2027 | Arrears of earlier years |
| Art. 11 c. 1 TUIR (IRPEF brackets) | Art. 11 c. 1 of the testo unico of D.Lgs. 117/2026: 23%, 33%, 43% at 28,000 and 50,000 EUR, as in 2026 | IRPEF of the provisional 2027 tables |
| L. 207/2024 art. 1 c. 6 (ulteriore detrazione) | Carried into art. 13 of the testo unico of D.Lgs. 117/2026 (its heading cites "articolo 1, comma 6, legge 30 dicembre 2024, n. 207") | Ulteriore detrazione and its recovery |
| D.Lgs. 47/2000 art. 11 cc. 3-4 (substitute tax on the TFR revaluation) | Repealed from 1 January 2027 by D.Lgs. 33/2025, as amended by D.L. 200/2025 | TFR revaluation tax |

## Release notes and economic diff

Every dataset release is published as a GitHub release whose notes list
the changes in the format:

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

Programmatic consumers can watch GitHub releases or compare two dates of a
CCNL with the rules diff of the engine.

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
  knowledge-base release. Schema changes are announced in the release notes
  and in a GitHub discussion at least 30 days before they take effect.

**Engine API compatibility:**

The Python API follows semantic versioning. Patch releases are backwards
compatible. Minor releases may add fields to `PeriodResult` or new values
to existing enums (callers must handle unknown values defensively). Major
releases may break the public API and will be announced with a migration
guide.
