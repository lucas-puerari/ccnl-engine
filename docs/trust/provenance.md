# Provenance

Every payable rule in the knowledge base carries a provenance record: where
the value comes from and how far that source backs it. The record is
machine-readable, so callers can inspect which article or table produced a
figure, and the engine can refuse to present an amount as reliable when no
source backs it.

## Payable rules

A payable rule is a bundled value that the payroll run reads to compute a
posted amount.

| Rule | Where it lives | Record |
|---|---|---|
| Salary table | `ccnl/data/*.json`: `levels[].base_salary.periods[]` | Per period, or inherited from the level |
| Fixed allowance | `ccnl/data/*.json`: `levels[].fixed_allowances[]` | Per allowance, or inherited from the level |
| Seniority increments | `ccnl/data/*.json`: `parameters.seniority_increments` | Per block |
| Extra-month entitlement | `ccnl/data/*.json`: `parameters.additional_months.periods[]` | Per period |
| Extra-month accrual threshold | `ccnl/data/*.json`: `parameters.accrual_rule` | Per rule; a CCNL without the field is listed as `missing` (the engine default applies) |
| First-tier overtime bands | `ccnl/data/*.json`: `work_rules.time_supplements.overtime_bands[]` with code `OT_*`, kind `percentage`, no hour threshold and no context condition | Per band |
| Absence rule (daily quota of partial months and sick days) | `ccnl/data/*.json`: `work_rules.absence_rules` | Per rule |
| Sickness rule | `ccnl/data/*.json`: `work_rules.sickness_rules` | Per rule |
| INPS sick-pay indemnity bands | `inps/data/sick-pay-rates.json`: `bands` | Sibling `bands_provenance` |
| IRPEF brackets | `tax/data/<year>-<sector>.json`: `irpef_brackets` | Sibling `irpef_brackets_provenance` |
| Art. 13 work deduction, its minimum | `tax/data/<year>-<sector>.json`: `work_deduction`, `work_deduction.minimum` | Per block |
| Trattamento integrativo, ulteriore detrazione | `tax/data/<year>-<sector>.json` | Per block |
| Somma esente | `tax/data/somma-esente-<year>.json`: `somma_esente` | Per block |
| TFR divisor, additional IVS deduction | `tax/data/<year>-<sector>.json`: `tfr`, `tfr.additional_ivs` | Per block |
| Fixed-term addizionale NASpI | `tax/data/<year>-<sector>.json`: `fixed_term_additional_rate`, `fixed_term_renewal_increment`, `fixed_term_exempt_categories` | One sibling `fixed_term_additional_rate_provenance` for the three |
| INPS rates, 1% additional IVS | `inps/data/<year>-<sector>.json`: `inps`, `inps.employee_additional`, `apprentice`, `domestic_contributions` | Per block |
| Regional and municipal surtax | `surtax/data/regionale-<year>.json`, `comunale-<year>.json` | Per table (file-level `provenance`); an entry may override it |
| Art. 12 family deductions | `tax/data/family-deductions-<year>.json`: `spouse`, `children`, `other_dependents` | Per block |
| Fringe-benefit thresholds, PdR limits | `tax/data/variable-pay-rules-2026.json`: `fringe_benefit`, `pdr` | Per block |
| Substitute-tax regimes | `tax/data/variable-pay-rules-2026.json`: `rinnovo`, `notte_festivi_turni` | Their `source` location with `source_status` |

CCNL rules carry one record per rule, because each salary tranche and
allowance is read from its own row of a table. Fiscal values are statutory
parameters stated once per block (the brackets of one comma, the constants
of one article), so their record is per block: a record per bracket would
repeat the same citation, and a record per file would mix blocks with
different backing (for example the public administration fixed-term
exemption, cited from commentary, sits next to the IRPEF brackets of the
law). The surtax
tables come from one MEF publication each, so they carry one record per
table instead of one per municipality.

A sub-block of a fiscal block that carries its own record (the Art. 13
minimum, the TFR additional IVS, the 1% employee IVS) is a payable rule of
its own, with the capabilities of its block: the inventory walks every
nested record of a block, not a fixed list of keys. The per-row records of
the surtax tables are the exception: the inventory keeps one rule per
table, while a run reports the record of the row it read.

Bundled values the run does not read are not payable: the other CCNL work
rules (overtime bands beyond an hour threshold, conditional or paid per hour
or per shift, leave), apprenticeship tracks, the Art. 15 deductions and the
`sterilizzazione_detrazioni` block. That block holds the 440 EUR reduction of
art. 16-ter c. 5-bis TUIR (L. 199/2025 art. 1 c. 4), which lowers only the
19% oneri, party donations and catastrophe premiums: the payroll computes
none of them, so the reduction never touches the Art. 12 and Art. 13
deductions or the ulteriore detrazione.

## The provenance record

```json
{
  "provenance": {
    "status": "derived",
    "location": {
      "source_document": {
        "document_id": "ccnl-commercio-confcommercio-2019",
        "title": "CCNL Terziario Distribuzione e Servizi, Testo Unico 2019",
        "kind": "associazione",
        "url": "https://www.confcommercio.it/-/ccnl-terziario-distribuzione",
        "published_on": "2024-03-22"
      },
      "section": "Art. 205, Scatti di anzianità",
      "quote": null
    },
    "extraction": {
      "method": "manual",
      "extraction_timestamp": "2026-08-30T00:00:00",
      "verified_by": null,
      "verified_at": null,
      "verification_status": "unverified",
      "effective_from": "1990-01-01",
      "effective_until": null,
      "back_calculation": null
    },
    "transformation": null,
    "note": "Dieci scatti triennali"
  }
}
```

| Field | Description |
|---|---|
| `status` | `verified`, `derived`, `assumed` or `missing` (see below) |
| `location.source_document` | The document: `document_id`, `title`, `kind`, `url`, `published_on`. The `document_id` with `published_on` identifies the version |
| `location.section` / `page` / `quote` | Article, comma or table; page; verbatim excerpt |
| `extraction` | Method, validity (`effective_from` / `effective_until`) and reviewer (`verified_by` / `verified_at`). Optional: when absent, the validity is the one of the period or ruleset that holds the rule |
| `transformation` | How the source text became the stored value, when not verbatim |
| `note` | Free-form context, such as a known simplification |

Document kinds: `gazzetta`, `cnel`, `inps_circolare`, `legge`, `dpr`, `dl`,
`dlgs` and `amministrazione` (MEF, Agenzia delle Entrate) are official;
`associazione`, `tabella_retributiva`, `rivista` and `altro` are secondary.
Authority is a separate axis from the status: a `derived` value may come
from a secondary document.

## Provenance status

| Status | Meaning | Record requirements |
|---|---|---|
| `verified` | A named reviewer checked the value against the cited location on a recorded date: a person, or an AI review the owner of the ruleset authorised | A citation (below), `extraction.verified_by` and `extraction.verified_at` |
| `derived` | Taken or computed from a cited document location, without a recorded check | A citation (below) |
| `assumed` | Adopted without a located citation: an unchecked AI extraction, a reconstruction or estimate, or a value whose clause was never located | `location` optional |
| `missing` | No source backs the value | no `location` |

The model rejects a record whose status disagrees with what it records.

### A label never outruns its evidence

A `derived` or `verified` record claims a located source, so the loaders
and the schema gate reject it when:

- it has no **citation**: an http(s) `location.source_document.url` and a
  `location.section` or `location.page` (the article and comma, or the
  page of the table). A title without a URL, or a URL without a clause, is
  not a citation;
- the ruleset of its file declares `source_type: "estimated"`: the file
  says its values are approximated without a primary source, so no rule in
  it can be read from one;
- its `note` or `transformation` records an estimate.

`extraction.verification_status: "unverified"` is not a reason: it is what
`derived` means, a value read from a cited location without a recorded
check. A record that fails is `assumed`, keeping its location, quote and
transformation, and its note says why.
`scripts/data/demote_weak_labels.py` applies the rule to the whole bundle
(every provenance record of every data file, payable or not, and the
`source_status` of the substitute-tax regimes) and rehashes the files it
changes; it only lowers labels. A record raised back to `derived` after
its source is located must drop that note, which the gate reads as an
estimate.
Nothing becomes `verified` without a named reviewer and a date. The
reviewer is a person, or an AI review the owner of the ruleset authorised:
then `verified_by` (or `verification.human_reviewed_by`) names the model and
the authorising owner, e.g. `claude-opus-5-5 (AI review authorised by the
owner, lucas-puerari)`, and the owner stays accountable for it. The legacy
`extraction.verification_status: "verified"` alone, or the file-level
`verification.human_reviewed_by`, does not say which value was checked by
whom, so such records are `derived`.

A statutory block that is the same for every sector lives in a year file
of its own, with an `official_primary` ruleset, rather than in the
`estimated` sector files: the somma esente of L. 207/2024 art. 1 cc. 4-5
(`tax/data/somma-esente-<year>.json`, ruleset `tax/<year>/somma-esente`)
is `derived`, its record quoting the Gazzetta Ufficiale text of the two
commi and saying in `transformation` how the bands store them. The loader
merges it into the rules of every sector, and a sector file that carries
its own copy does not load. The IRPEF brackets, the Art. 13 deduction and
the other credits stay in the sector files, `assumed`, until their text
is quoted the same way.

`scripts/data/assign_rule_provenance.py` assigns the status of existing
records from what they record and fills the fiscal blocks from the citations
in each file's notes and ruleset source (or, where the data records none,
the rule model docstrings; the record then says so in `transformation`).
The script is idempotent and rehashes the files it changes.

### Current counts

Generated from the bundle by `scripts/docs/gen_trust_counts.py`; CI fails
when they drift.

<!-- trust:provenance-table -->

| Status | CCNL rules | Fiscal blocks | Total |
|---|---:|---:|---:|
| `verified` | 0 | 0 | 0 |
| `derived` | 5 869 | 113 | 5 982 |
| `assumed` | 690 | 133 | 823 |
| `missing` | 85 | 0 | 85 |

<!-- /trust:provenance-table -->

Of the <!-- trust:rules-missing -->85<!-- /trust:rules-missing --> `missing`
rules, <!-- trust:accrual-missing -->85<!-- /trust:accrual-missing --> are
extra-month accrual thresholds of CCNLs whose signed clause is not in the
bundle. `assumed` covers every rule of a ruleset that declares
`source_type: "estimated"` (the 2026 sector tax and INPS files and a few
CCNLs), the
records that cite no URL (the INPS sick-pay bands, the PdR limits), the
AI-extracted CCNL values (including
<!-- trust:accrual-assumed -->38<!-- /trust:accrual-assumed --> accrual
thresholds read from signed texts, each with its article and quote),
extra-month counts with no located clause, the
artigianato and edilizia INPS proxies, the PA apprentice placeholder, the PA
fixed-term exemption and the regional surtax table.
`python scripts/ci/check_provenance.py --rules` prints the same counts.

## Enforcement

- **Load time.** A schema-0.5 CCNL without a record on a level, salary
  period, allowance, seniority block or additional-months period does not
  load. No CCNL, tax, INPS or surtax file loads with a label that outruns
  its evidence (see [above](#a-label-never-outruns-its-evidence)): the
  loader raises `DataIntegrityError`.
- **CI, schema gate.** `scripts/ci/check_provenance.py --schema` fails when
  any payable rule of the bundle has no record or an unknown status, and
  lists every `missing` record. It also fails when a record lacks the
  evidence its status or readiness claims (see below), when a label
  outruns its evidence, when a `reviewed` or `production` CCNL has an
  `assumed` or `missing` payable rule in its own file or a `confidence`
  other than `verified`, or when a CCNL ruleset id is not `ccnl/<ccnl_id>`.
  These errors have no baseline: the gate rejects every one.
  `tests/architecture/test_data_quality.py` runs the same inventory.
- **CI, evidence gate.** `scripts/ci/check_provenance.py --evidence`
  compares the bundle with the shrink-only baseline
  `scripts/ci/provenance_baseline.json`, which lists every `assumed` or
  `missing` payable rule and every open model limitation. It judges each
  rule, never the weakest status of a capability, and fails on a rule or a
  limitation the baseline does not list, on a rule
  weaker than its baseline status, and on a baseline entry that no longer
  holds. The counts per capability and per CCNL therefore never grow; the
  gate prints them, and the [capability matrix](../contracts/capability-matrix.md)
  shows them for each capability and each CCNL.
- **Run time.** A capability that executed and read a `missing` rule adds a
  `rule_source_missing` issue naming the rule, and the result is
  `incomplete`. `result.capability_report.rule_sources` holds, for each
  executed capability, the weakest status among the rules it read; an
  `assumed` or `missing` one is a `rule_source_weak` blocker and the result
  is not payable. See [Assurance](confidence.md).

## Evidence for promotion

Promoting a rule to `verified`, or a CCNL to readiness `production`, is a
human task: no script raises a status. The schema gate requires:

| Claim | Fields |
|---|---|
| Rule `verified` | A citation, `extraction.verified_by`, `extraction.verified_at`, an exact location (`location.page` or `location.section`), and `location.source_document.sha256`, the sha256 of the document file the value was read from |
| CCNL readiness `reviewed` | `confidence` `verified` and no `assumed` or `missing` payable rule in the CCNL file |
| CCNL readiness `production` | The `reviewed` evidence, `verification.owner`, `verification.human_reviewed_by`, `verification.last_reviewed` and `verification.review_due` after the last review |

## Updating the evidence baseline

After sourcing a rule or resolving a limitation, shrink the baseline and commit it with the data change:

```bash
python scripts/ci/check_provenance.py --update-baseline
```

The command refuses to add an entry. A new `assumed` or `missing` rule (for
example a new CCNL without `parameters.accrual_rule`, which is listed as
`missing`) is accepted only with an explicit flag, and the pull request
must justify the baseline diff:

```bash
python scripts/ci/check_provenance.py --update-baseline --allow-growth
```

## Reading provenance

```python
from ccnl_engine.contract.service.loaders import load_ccnl

ccnl = load_ccnl("commercio-confcommercio.json")

for level in ccnl.levels:
    for period in level.base_salary.periods:
        record = period.provenance or level.provenance
        if record is None or record.location is None:
            continue
        src = record.location.source_document
        print(f"{level.code}: {src.title} ({src.url})")
        print(f"  section: {record.location.section}")
        print(f"  status:  {record.status}")
```

A `PeriodResult` links back to its sources through `result.bundle_version`,
the rulesets in `result.rulesets`, the `rule` and `rule_version` of each
decision in `result.decisions`, and the per-capability statuses in
`result.capability_report.rule_sources`. The full
JSON of each contract, provenance included, is shown on its page under
[Contracts](../contracts/index.md).
