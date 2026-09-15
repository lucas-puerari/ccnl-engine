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

All provenance records must have `"verified"` status for a result's confidence
to reach `"high"`. See [Trust: Confidence](confidence.md).

## Propagation into `PayrollResult`

The `provenance` field of a `PayrollResult` is a tuple of `RuleProvenance`
objects — one per rule applied during the computation. Each entry links a
computed quantity to its source:

```python
for prov in result.provenance:
    src = prov.location.source_document
    print(src.kind, prov.location.section)
# tabella_retributiva    Tabella retributiva — livello C3
# contratto_collettivo   Art. 205 — Scatti di anzianità
```

This tuple is also serialised by `result.to_dict()` and `result.to_json()`,
so provenance survives round-trips through storage and APIs.

## Reading provenance in practice

```python
from datetime import date

from ccnl_engine import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
    Permanent,
    compute,
)

calc = compute(PayrollScenario(
    employee=Employee(level_code="4"),
    employment=Employment(
        ccnl="commercio-confcommercio.json",
        contract=Permanent(),
        employer=Employer(num_employees=50),
        calculation_date=date(2026, 1, 1),
    ),
))
result = calc.result

for prov in result.provenance:
    src = prov.location.source_document
    print(f"{src.title} ({src.url})")
    print(f"  section: {prov.location.section}")
    print(f"  status:  {prov.extraction.verification_status}")
```

See also [example 11 — Why this number?](../examples.md) for a full
walkthrough combining provenance, scope, and warnings.
