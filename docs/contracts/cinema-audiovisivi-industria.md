# CCNL Industrie Cineaudiovisive (ANICA)

| | |
|---|---|
| **CNEL code** | `G111` |
| **Sector** | Cinema e audiovisivo |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-23 |
| **Workers (est.)** | ~2.3k |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR). Conglobated model.

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7S` | Livello 7 Super (QA — Quadro) | € 2,880.55 | 2028-01-01 |
| `7` | Livello 7 (QB — Quadro) | € 2,758.66 | 2028-01-01 |
| `6S` | Livello 6 Super | € 2,510.69 | 2028-01-01 |
| `6` | Livello 6 | € 2,430.46 | 2028-01-01 |
| `5S` | Livello 5 Super | € 2,217.61 | 2028-01-01 |
| `5` | Livello 5 | € 2,164.88 | 2028-01-01 |
| `4S` | Livello 4 Super | € 2,103.30 | 2028-01-01 |
| `4` | Livello 4 | € 1,980.32 | 2028-01-01 |
| `3` | Livello 3 | € 1,796.03 | 2028-01-01 |
| `2` | Livello 2 | € 1,608.31 | 2028-01-01 |
| `1` | Livello 1 | € 1,440.48 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `7S` | € 20.17 |
| `7` | € 19.37 |
| `6S` | € 17.56 |
| `6` | € 17.56 |
| `5S` | € 16.79 |
| `5` | € 16.01 |
| `4S` | € 14.46 |
| `4` | € 14.46 |
| `3` | € 13.94 |
| `2` | € 13.17 |
| `1` | € 12.65 |

## Apprenticeship

Not modeled (primary CCNL text not publicly available).

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP: provisions not modeled. Primary CCNL text (signed 23/07/2025) not publicly available at extraction time. Verify against official source before use.

!!! warning ""
    SALARY PERIODS: Jan 2025, Jan 2026, Jul 2027, and Jan 2028 values computed parametrically from the published Jul 2026 anchor table. The parametric scaling uses the L4 absolute increase per tranche (+45, +45, +90, +90 EUR) applied proportionally to all levels.

!!! warning ""
    BILATERAL FUNDS: No cinema-specific employer bilateral fund for impiegati/tecnici in production companies identified. Field left empty.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Industrie Cineaudiovisive (G111) — lavoro-economia.it | tabella_retributiva | 2026-07 | [↗](https://www.lavoro-economia.it/contratti-collettivi/ccnl.aspx?c=153) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. Paga base unica senza contingenza o EDR separati. 5 tranches: +45 a L4 dal 01/01/2025, +45 dal 01/01/2026, +90 dal 01/07/2026 (tabella pubblicata), +90 dal 01/07/2027, +90 dal 01/01/2028.

    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima, UILCOM informativa 24/07/2025).

    SENIORITY: 5 scatti biennali. Importi dalla tabella pubblicata luglio 2026.

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/cinema-audiovisivi-industria.json"
    ```
