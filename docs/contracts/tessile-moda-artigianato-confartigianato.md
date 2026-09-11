# CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato

| | |
|---|---|
| **CNEL code** | `V751` |
| **Sector** | tessile moda chimica ceramica artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-07-16 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Federmoda
    - CNA Produzione
    - CNA Artistico e Tradizionale
    - CNA Servizi alla Comunità
    - Confartigianato Moda
    - Confartigianato Chimica
    - Confartigianato Ceramica
    - Casartigiani
    - CLAAI
    - Filctem CGIL
    - Femca CISL
    - Uiltec UIL

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
| `6S` | Level 6S — senior manager / technical director (incl. function allowance EUR 20.66) | € 2,133.07 | — |
| `6` | Level 6 — skilled technician / senior clerical employee | € 1,978.15 | — |
| `5` | Level 5 — specialist operator / clerical employee | € 1,813.50 | — |
| `4` | Level 4 — highly qualified operator | € 1,675.42 | — |
| `3` | Level 3 — specialist operator | € 1,606.03 | — |
| `2` | Level 2 — qualified operator | € 1,538.39 | — |
| `1` | Level 1 — basic operator | € 1,454.41 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 7.23 |
| `2` | € 7.75 |
| `3` | € 8.26 |
| `4` | € 9.30 |
| `5` | € 10.85 |
| `6` | € 12.91 |
| `6S` | € 15.49 |

## Apprenticeship

**gruppo_1_abb** (type: `percentage`)  
Destination levels: `4`, `5`, `6`, `6S`  
percentage: 1.00

**gruppo_2_abb** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3_abb** (type: `percentage`)  
Destination levels: `2`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Only tessile-abbigliamento sub-sector modelled. Chimica-ceramica sub-sectors (different salary tables) are not modelled. CNEL code V751 covers all three sub-sectors.

!!! warning ""
    APPRENTICE SENIORITY treated as uniform 6.00 EUR from 2025-01-01 regardless of hire date. Strictly, only workers hired after 17 Jul 2024 get 6.00 from Jan 2025; workers hired before that date remain at 5.16. For new hires this model is correct.

!!! warning ""
    LEVEL CATEGORY: all levels left null (no primary-source text confirming operaio/impiegato split). The 2026-artigianato.json tier applies the impiegato rate (0.2471) for category='impiegato'/'quadro' vs. default 0.2693. Employer cost for higher levels (5, 6, 6S) may be slightly overestimated until categories are confirmed from primary CCNL text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-16 | [↗](https://www.kitech.it/ccnl/tessile-abbigliamento-artigianato) |
| — | — | — | [↗](https://www.eber.org) |
| — | — | 2024-07-16 | [↗](https://olympus.uniurb.it) |
| — | — | 2017-12-14 | [↗](https://www.cna.it) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Back-calculation: L3 Jan 2025 = 1502.03/173 = 8.68 EUR/h; L4 Jan 2025 = 1566.69/173 = 9.05 EUR/h; L6 Jan 2025 = 1849.57/173 = 10.69 EUR/h — consistent divisor 173 across levels confirms conglobated model.
    
    CNEL CODE: V751 confirmed from EBER (Ente Bilaterale Emilia-Romagna) 'Allegato 2 — Sintesi codifica contratti INPS e CNEL', INPS code 003. D025 found on lavoro-economia.it refers to the older separate 'Area Tessile-Moda' pre-unification entry; V751 covers the current unified area contract (tessile+chimica+ceramica).
    
    TRANCHE DATES: four tranches — 2024-07-01 (retroactive from renewal 16 Jul 2024), 2025-01-01, 2025-10-01, 2026-10-01. Source: FEMCA CISL Bergamo salary sheet, cross-checked kitech.it.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 9 CCNL tessile-moda artigianato). Formula: 40 h/week × 52/12 = 173.33 rounded to 173 per contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it / CNA PDF art. mensilità aggiuntive.
    
    SENIORITY: biennale (every 24 months), maximum 4 scatti. Per-level amounts from Art. 67 CNA PDF 2017 (primary source): 6S=15.49, 6=12.91, 5=10.85, 4=9.30, 3=8.26, 2=7.75, 1=7.23 EUR. Unchanged in 2024 rinnovo.
    
    APPRENTICE SENIORITY: raised from 5.16 to 6.00 EUR by 2024 rinnovo (Art. 25), effective 2025-01-01 for new hires after 17 Jul 2024. Modelled as uniform 6.00 from 2025-01-01 (pre-Jul-2024 hires staying at 5.16 not separately tracked — minor simplification for new engagements).
    
    APPRENTICESHIP: 3 gruppi (Art. 68 CNA PDF 2017, Section 7 retribution marked 'Omissis' in 2024 rinnovo = unchanged). Gruppo 1 (destination levels 4-6S, max 54 months), Gruppo 2 (destination level 3, max 42 months), Gruppo 3 (destination level 2, max 24 months). Level 1 has no apprenticeship track.
    
    Level 6S indennità di funzione (EUR 20.66) confirmed fixed across all four tranches. Verification 2026-09-09: web sources show L6S minimi (without indennità) as 1922.59/1975.32/2039.91/2112.41 (Jul 2024/Jan 2025/Oct 2025/Oct 2026); file stores 1943.25/1995.98/2060.57/2133.07 — difference exactly 20.66 EUR at every tranche (kitech.it Oct 2025 confirmation plus back-check against all 4 tranches). Indennità conglobata in base_salary (no separate fixed_allowances entry).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tessile-moda-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tessile-moda-artigianato-confartigianato.py"
```
