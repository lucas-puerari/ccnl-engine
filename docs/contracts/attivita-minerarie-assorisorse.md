# CCNL Attività Minerarie (ASSORISORSE)

| | |
|---|---|
| **CNEL code** | `B282` |
| **Sector** | Industria estrattiva — Miniere, cave, saline, metallurgia estrattiva |
| **Tax sector** | `industria` |
| **Last renewal** | 2022-07-13 |
| **Workers (est.)** | ~3000 |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSORISORSE (Risorse Naturali ed Energie Sostenibili)
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🚫 not implemented |

## Salary table

Conglobated model — amounts are total monthly minima (Art. 17). Values from the
2025-01-01 tranche (final increase of the 2022-2025 contract cycle).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Livello 1 Super — quadri direttivi e tecnici di alta specializzazione | € 3,037.95 | 2025-01-01 |
| `1` | Livello 1 — impiegati direttivi e tecnici specializzati | € 2,991.12 | 2025-01-01 |
| `2` | Livello 2 — impiegati di concetto e operai altamente specializzati | € 2,768.11 | 2025-01-01 |
| `3` | Livello 3 — impiegati d'ordine e operai specializzati | € 2,460.22 | 2025-01-01 |
| `4` | Livello 4 — operai qualificati e addetti a mansioni specifiche | € 2,228.15 | 2025-01-01 |
| `5` | Livello 5 — operai comuni con autonomia operativa | € 2,103.19 | 2025-01-01 |
| `6` | Livello 6 — operai comuni | € 1,981.71 | 2025-01-01 |
| `7` | Livello 7 — operai generici con mansioni semplici | € 1,856.57 | 2025-01-01 |
| `8` | Livello 8 — operai ausiliari e addetti a cernita | € 1,705.38 | 2025-01-01 |

## Seniority increments

Not modeled — amounts not available from the scanned renewal protocol PDF.

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1S`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`

| Period | Percentage |
|---|---:|
| 0–12 months | 85% |
| 12–24 months | 90% |
| 24+ months | 95% |

## Known simplifications

!!! warning ""
    SIMPLIFICATION: Seniority increments (scatti di anzianità) not modeled —
    amounts not found in the scanned renewal protocol (OCR of pages 1-10).
    Seniority always returns 0.00 regardless of service length.

!!! warning ""
    SIMPLIFICATION: Source PDF is scanned (image-based, CCITT compression).
    Salary values extracted via OCR (Ghostscript + Tesseract 5.5.3).
    Amounts verified by cross-checking parametrale ratios and incremental
    consistency across four tranches.

!!! warning ""
    SIMPLIFICATION: Hourly divisor (173) and additional months (13) assumed
    from standard industria conventions. Not explicitly confirmed from the
    scanned renewal protocol — verify against the full CCNL text (Art. orario,
    Art. gratifica natalizia).

!!! warning ""
    SIMPLIFICATION: Work rules (overtime, leave, sick leave) not modeled.
    The available source is a renewal protocol covering salary increases and
    HSE provisions, not the complete CCNL text.

## Sources

- [Rinnovo CCNL Attività Minerarie 2022-2025 (FILCTEM-CGIL)](https://www.filctemcgil.it/images/download/CONTRATTI/miniere/220713_ATTIVITA%20MINERARIE_RINNOVO%20CCNL%202022-2025.pdf)
  — ASSORISORSE + FILCTEM-CGIL + FEMCA-CISL + UILTEC-UIL, Roma 13 luglio 2022
