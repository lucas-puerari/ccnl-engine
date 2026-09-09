# Rules

The rules layer is the versioned knowledge base that the engine reads at
runtime. It contains no computation logic — only structured data loaded by
the loaders and validated against Pydantic schemas.

Three kinds of rules exist:

| Kind | What it holds | Format |
|---|---|---|
| **CCNL** | Salary tables, seniority amounts, apprenticeship tracks, work-rule parameters | JSON per contract |
| **Tax** | IRPEF brackets, deductions, contribution ceilings — by year | JSON per year |
| **Surtax** | Regional and municipal addizionale brackets — by year | JSON per year |

## How the knowledge base is structured

```
src/ccnl_engine/knowledge/
├── ccnl/
│   └── data/           ← one JSON file per contract (e.g. metalmeccanico-federmeccanica.json)
├── tax/
│   └── data/           ← one JSON file per year (e.g. 2026-industria.json)
├── surtax/
│   └── data/
│       ├── regionale-2026.json    ← regional brackets, all regions
│       └── comunale-2026.json     ← municipal brackets, ~7 000 comuni
└── __version__         ← dataset version string (e.g. "2026.2")
```

All files are bundled inside the Python package and read via
`importlib.resources` — no filesystem paths, no network access.

## Versioning

The entire knowledge base carries a single dataset version (`__version__`,
e.g. `"2026.2"`). It is bumped whenever any data file changes.

Every CCNL JSON additionally carries a per-contract `ruleset.version` and a
`ruleset.source_hash` (SHA-256 of the file content). The loaders verify the
hash at load time and raise `ValueError` on mismatch — tampered or
accidentally edited files are caught before any computation.

```python
from ccnl_engine import load_ccnl

ccnl = load_ccnl("metalmeccanico-federmeccanica.json")
print(ccnl.ruleset.id)          # "ccnl/metalmeccanico-federmeccanica"
print(ccnl.ruleset.version)     # "2026.2"
print(ccnl.ruleset.source_hash) # "4a7b..."
```

The ruleset identity is propagated into every `Calculation` so a payroll
figure can be reproduced exactly from any historical snapshot. See
[Trust: Versioning](../trust/index.md#versioning).

## CCNL JSON schema

Each CCNL file follows schema version `0.5`. The top-level keys:

| Key | Type | Description |
|---|---|---|
| `schema_version` | string | Schema revision (e.g. `"0.5"`) |
| `meta` | object | Identity: CNEL code, name, sector, signatories, sources, extraction metadata |
| `coverage` | object | Implementation status: `gross`, `net`, `work_rules`, plus `notes` |
| `parameters` | object | Contract-wide parameters: hourly divisor, additional months, seniority |
| `levels` | array | One object per classification level: code, base salary time-series, allowances |
| `apprenticeship` | array | Apprenticeship tracks (under-classification or percentage) |
| `ruleset` | object | Identity for integrity verification: `id`, `version`, `source_hash`, `verification_status` |
| `work_rules` | object | Time supplements, absence, leave, and sickness rules |

### `meta.sources`

Every fact in a CCNL file must trace back to a primary source. The `sources`
array on `meta` lists all documents used during extraction:

```json
{
  "document_id": "tabelle-retributive-commercio-2024",
  "title": "Tabelle retributive CCNL Terziario...",
  "kind": "tabella_retributiva",
  "url": "https://...",
  "published_on": "2024-03-28"
}
```

Individual parameters (levels, seniority, hourly divisor) also carry a
`provenance` block that pins the exact `source_document`, `section`, and
extraction metadata for that specific fact. See
[Trust: Provenance](../trust/provenance.md).

### `coverage.notes`

Coverage notes explain what is modelled, what is simplified, and what is
absent. Three `kind` values:

| Kind | Meaning |
|---|---|
| `source` | Records which source document was used and why |
| `info` | Documents a modelling decision or derivation (e.g. hourly divisor formula) |
| `simplification` | Marks a deliberate approximation — something real that the model gets slightly wrong |

`simplification` notes are the most important for callers: they are the
known errors. Each one appears on the contract's documentation page.

## Tax rules

Tax rules are loaded by year and employer size. The loader selects the
appropriate INPS rate tier (based on `num_employees`) and applies the
correct IRPEF bracket schedule:

```python
from ccnl_engine import load_year_rules

rules = load_year_rules(2026, tax_sector="industria", num_employees=50)
```

The `tax_sector` must match the CCNL's `meta.tax_sector`. Valid values:
`industria`, `commercio`, `artigianato`, `agricoltura`, `terziario`,
`credito`, `assicurazioni`, `pubblica_amministrazione`.

## Surtax rules

Regional and municipal surtax rates are loaded separately and passed
optionally to `compute()`. When omitted, the regional and municipal
components are zero and appear in `calculation_scope` as `"excluded"`.

```python
from ccnl_engine import load_surtax_rules

surtax = load_surtax_rules(2026)
```

The `SurtaxRules` object covers all Italian regions and ~7 000 comuni
(identified by their belfiore cadastral code).
