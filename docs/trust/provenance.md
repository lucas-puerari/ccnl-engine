# Provenance

Every fact in the knowledge base traces to a primary source document. The
provenance system makes that trace machine-readable, so callers can inspect
exactly which article or table produced a given salary figure.

## The provenance block

Each rule in a CCNL JSON carries a `provenance` object at the point where
the fact is stated:

```json
{
  "seniority_increments": {
    "cadence_months": 36,
    "maximum_count": 10,
    "amount_by_level": { ... },
    "provenance": {
      "location": {
        "source_document": {
          "document_id": "ccnl-commercio-confcommercio-2019",
          "title": "CCNL Terziario Distribuzione e Servizi — Testo Unico 2019",
          "kind": "associazione",
          "url": "https://www.confcommercio.it/-/ccnl-terziario-distribuzione",
          "published_on": "2024-03-22"
        },
        "section": "Art. 205 — Scatti di anzianità",
        "quote": null
      },
      "extraction": {
        "method": "ai",
        "model": "claude-sonnet-4-6",
        "extraction_timestamp": "2026-08-30T00:00:00",
        "verified_by": null,
        "verified_at": null,
        "verification_status": "unverified",
        "effective_from": "1990-01-01",
        "effective_until": null,
        "back_calculation": null
      },
      "note": "Dieci scatti triennali; importi vigenti dal 01/01/1990..."
    }
  }
}
```

## Provenance fields

### `location`

| Field | Description |
|---|---|
| `source_document.document_id` | Stable identifier for the document |
| `source_document.title` | Human-readable document title |
| `source_document.kind` | Document type: `tabella_retributiva`, `associazione`, `official_contract`, `renewal_summary`, `official_codification` |
| `source_document.url` | URL of the primary source |
| `source_document.published_on` | Publication or agreement date |
| `section` | Article, table, or page reference within the document |
| `quote` | Verbatim excerpt when relevant (optional) |

### `extraction`

| Field | Description |
|---|---|
| `method` | `"ai"` \| `"manual"` \| `"back_calculation"` \| `"import"` |
| `model` | Model identifier; required when `method` is `"ai"`, null otherwise |
| `extraction_timestamp` | When the fact was extracted |
| `verified_by` | Name or identifier of human reviewer (null if unverified) |
| `verified_at` | Date of human verification |
| `verification_status` | `"verified"` \| `"unverified"` \| `"needs_review"` |
| `effective_from` | First date this specific fact is valid |
| `effective_until` | Last date this fact is valid (null = open-ended) |
| `back_calculation` | How the value was derived (e.g. hourly rate back-calculation) |

## Verification status

The `verification_status` field is the most important signal for callers:

| Status | Meaning |
|---|---|
| `"verified"` | A human has compared the extracted value to the primary source document and confirmed it |
| `"unverified"` | The value was extracted but has not been independently checked |
| `"needs_review"` | The value was verified but a subsequent renewal may have changed it |

Verification status is informational: the engine does not read it when it
computes a result, so an unverified figure does not change `result.status`
or the capability report. See [Trust: Confidence](confidence.md).

## Provenance and payroll results

A `PayrollResult` does not carry provenance records. It links back to its
sources in two ways:

- `result.bundle_version` is the version of the knowledge bundle used.
- `result.decisions` records, for each capability that logs a decision, the
  `rule` and `rule_version` it applied.

To see where a contract figure comes from, read the provenance on the loaded
CCNL. Every pay level, every non-gap salary period and every fixed allowance
carries one.

```python
from ccnl_engine.engine.contract.service.loaders import load_ccnl

ccnl = load_ccnl("commercio-confcommercio.json")

for level in ccnl.levels:
    for period in level.base_salary.periods:
        if period.provenance is None:
            continue
        src = period.provenance.location.source_document
        print(f"{level.code}: {src.title} ({src.url})")
        print(f"  section: {period.provenance.location.section}")
        print(f"  status:  {period.provenance.extraction.verification_status}")
```

The full JSON of each contract, provenance included, is also shown on its
page under [Contracts](../contracts/index.md).
