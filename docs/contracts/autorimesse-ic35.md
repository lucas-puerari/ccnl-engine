# CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)

| | |
|---|---|
| **CNEL code** | `IC35` |
| **Sector** | Autorimesse e noleggio automezzi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-12-09 |
| **Workers (est.)** | ~41k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIASA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Livello Q1 (Quadro di primo livello) | € 2,319.11 | — |
| `Q2` | Livello Q2 (Quadro di secondo livello) | € 2,319.11 | — |
| `A1` | Livello A1 | € 2,319.11 | — |
| `A2` | Livello A2 | € 2,183.36 | — |
| `B1` | Livello B1 | € 1,991.05 | — |
| `B2` | Livello B2 | € 1,900.55 | — |
| `B3` | Livello B3 | € 1,821.35 | — |
| `C1` | Livello C1 | € 1,753.48 | — |
| `C2` | Livello C2 | € 1,561.16 | — |
| `C3` | Livello C3 | € 1,448.04 | — |
| `C4` | Livello C4 | € 1,131.27 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 33.10 |
| `Q2` | € 33.10 |
| `A1` | € 33.10 |
| `A2` | € 32.19 |
| `B1` | € 30.36 |
| `B2` | € 29.57 |
| `B3` | € 29.39 |
| `C1` | € 29.23 |
| `C2` | € 27.17 |
| `C3` | € 26.61 |
| `C4` | € 25.35 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `Q1`, `Q2`, `A1`, `A2`, `B1`, `B2`, `B3`, `C1`, `C2`, `C3`, `C4`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Sezione Appalti (Art. 81-89) excluded. The appalto sub-section defines a separate A1-SA to C4-SA level ladder with different tranche dates and amounts, for companies doing washing/shuttling/car prep on behalf of rental firms. Not modeled: out of scope for the main contract coverage.

!!! warning ""
    SIMPLIFICATION: Ticket restaurant excluded. Art. 44/84 provides 8.00 EUR/day (from 01/01/2023), rising to 10.00 EUR/day from 01/04/2027, conditional on >= 5 hours worked. Per-day and conditional: not representable as a monthly fixed allowance.

!!! warning ""
    SIMPLIFICATION: Hourly divisor 173 applies to standard 40h/week staff. The 2019 CCNL notes 182 (autisti/drivers) and 191 (custodi/security) in specific roles. Only 173 modeled here: dominant case. Verify per-role divisor for drivers and security classifications.

!!! warning ""
    SIMPLIFICATION: Apprenticeship article numbers from 2019 CCNL may have changed in the current consolidated text (Art. numbering in 2025 verbale differs from 2019 PDF). The 85/90/95 percentage structure is from the 2019 source and is assumed unchanged.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-09 | [↗](https://www.filtcgil.it/images/Contratti/Mobilita/ic35-verbale-accordo-09122025.pdf) |
| — | — | 2019-10-23 | [↗](https://www.comuneportofinomare.it/wp-content/uploads/CCNL-Autorimesse.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione tabellare (Allegato 1 of 2025-12-09 verbale); fixed_allowances = CONTINGENZA (per-level, frozen) + EDR (10.33 all levels, frozen since Protocollo Intesa 1992) + EAR (per-level, frozen; Art. 41 vigente CCNL; labeled 'E.A.S. CCNL 23/10/2019' in Allegato 1).
    
    Hourly divisor 173 confirmed from 2019 CCNL primary source. Cross-check: 40h/week x 52 / 12 = 173.33, consistent with 173.
    
    Additional months: 14. The 2025-12-09 verbale page 5 explicitly states 'tredicesima, la quattordicesima mensilita' for fixed-term workers, confirming both for all workers.
    
    Q1, Q2, A1 share parametro 205 and identical paga base and contingenza per Allegato 1. Allegato 1 gives no salary basis for ordering among the three; order Q1 > Q2 > A1 is conventional.
    
    Seniority: biennial (cadence_months=24), max 9 tranches from 2019 CCNL primary source. No seniority modifications found in the 2025 renewal text reviewed; amounts treated as unchanged (absence of evidence, not positive confirmation).
    
    Apprenticeship: percentage type, 85/90/95 percent by year of contract. Source: 2019 CCNL primary source. The 2025 renewal does not address apprenticeship provisions (absence of evidence, not positive confirmation).
    
    Source status: the 2025-12-09 document is a signed 'ipotesi di accordo' (conditional agreement). OO.SS. were to dissolve the reserve by 31/01/2026. As of 2026-09-05 the January 2026 tranches are in effect per public reporting; formal scioglimento not independently verified. Source is a signatory union PDF and sufficient as primary source.
    
    Headcount: 41,438 workers (contratticcnl.it, CNEL/INPS archive, IC35, 2025).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/autorimesse-ic35.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autorimesse-ic35.py"
```
