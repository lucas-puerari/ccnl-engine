# CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)

| | |
|---|---|
| **CNEL code** | `E015` |
| **Sector** | panificazione e alimentazione artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Alimentazione
    - CNA Alimentare
    - Casartigiani
    - CLAAI
    - FAI-CISL
    - FLAI-CGIL
    - UILA-UIL

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
| `A1S` | Level A1 Super — senior executive quadro / top-level manager | € 2,248.73 | — |
| `B1` | Level B1 — senior operations manager | € 2,165.67 | — |
| `A1` | Level A1 — production technical manager | € 2,056.93 | — |
| `A2` | Level A2 — specialist technician / department head | € 1,926.61 | — |
| `B2` | Level B2 — highly specialised operator | € 1,779.96 | — |
| `A3` | Level A3 — qualified production technician | € 1,764.45 | — |
| `B3S` | Level B3 Super — specialist operator with extended duties | € 1,732.79 | — |
| `B3` | Level B3 — specialist production operator | € 1,676.43 | — |
| `A4` | Level A4 — qualified support worker | € 1,671.86 | — |
| `B4` | Level B4 — general worker and first-time hire | € 1,589.80 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `B4` | € 14.46 |
| `A4` | € 14.46 |
| `B3` | € 16.01 |
| `B3S` | € 17.64 |
| `A3` | € 16.01 |
| `B2` | € 19.11 |
| `A2` | € 17.56 |
| `A1` | € 19.11 |
| `B1` | € 21.69 |
| `A1S` | € 21.69 |

## Apprenticeship

**gruppo_1_panificatori** (type: `percentage`)  
Destination levels: `A1`  
percentage: 1.00

**gruppo_a2_panificatori** (type: `percentage`)  
Destination levels: `A2`  
percentage: 1.00

**gruppo_a3_panificatori** (type: `percentage`)  
Destination levels: `A3`  
percentage: 1.00

**gruppo_b1_addetti** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_b2_addetti** (type: `percentage`)  
Destination levels: `B2`  
percentage: 1.00

**gruppo_b3s_addetti** (type: `percentage`)  
Destination levels: `B3S`  
percentage: 1.00

**gruppo_b4_addetti** (type: `percentage`)  
Destination levels: `B3`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    IND.SPECIALE: Indennita Speciale art.33 ter is fixed per level and does not change across tranches (confirmed: same amounts from 1995 to date, not subject to renewal increases). Folded into TOTALE base_salary for simplicity; the engine has no per-level fixed-allowance that is non-absorbable and constant — modeling as part of base_salary is the cleanest approach and does not affect any computation.

!!! warning ""
    ERR: Elemento Retributivo Residuo (0.44 EUR/month) is a national fixed element, identical for all levels. Folded into TOTALE; the rounding impact on any level is less than 0.01 EUR/month.

!!! warning ""
    IND.FUNZIONE A1S: Indennita di Funzione 36.15 EUR/month for level A1S introduced from April 2026 (Art. 33 quater, CCNL 2024). Included in the Apr 2026 TOTALE value (2248.73) as confirmed by lavoro-economia.it. Not modeled as a separate fixed_allowance.

!!! warning ""
    ERT (VENETO): Elemento Retributivo Territoriale Veneto (ERT, expired 31.12.2025) was a territorial supplement specific to Veneto. Not modeled at national level.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-06 | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/2024-06-06-CCNL-AREA-ALIMENTAZIONE-ARTIGIANATO-PANIFICAZIONE-2023-2026.pdf) |
| — | — | — | [↗](https://www.artser.it/approfondimenti/accordo-di-rinnovo-del-ccnl-area-alimentazione-e-panificazione.html) |

??? note "Coverage notes"
    SALARY MODEL: unified TOTALE as base_salary. Each level's TOTALE = Tabellare conglobato (contingenza+EDR absorbed, per Art. 32 + conglobamento clause) + Indennità Speciale per Panificazione (Art. 33, fixed per level since Aug 1995) + ERR (0.44 EUR/month, fixed). Ind.Speciale confirmed from Art. 33 table in UILA CCNL PDF: A1S=94.77, A1=88.06, A2=82.63, A3=75.92, A4=72.05, B1=92.19, B2=76.44, B3S=74.87, B3=72.56, B4=68.69. ERR=0.44. All folded into base_salary; fixed_allowances=[] for all levels. Cross-verified: artser.it tabellare A2 Apr 2024 = 1705.54; 1705.54 + 82.63 + 0.44 = 1788.61 exact match across all 4 tranches (diff constant 83.07 EUR). Art. 31 confirms hourly divisor 173.
    
    ADDITIONAL MONTHS: 13. Art. 33 (Ind.Speciale) replaced the quattordicesima from August 1995 ('viene a cessare, per tutti i lavoratori, la maturazione dei ratei relativi alla ex 14a mensilita'). Art. 36 (Gratifica natalizia) confirms only tredicesima remains. Source: UILA CCNL PDF Art. 33 and Art. 36.
    
    TRANCHE DATES: four tranches — 2024-04-01 (April 2024, first 2024 renewal tranche), 2025-01-01 (January 2025), 2025-11-01 (November 2025), 2026-04-01 (April 2026). Source: ilccnl.it panificazione tables + lavoro-economia.it renewal PDF (CCNL 6 June 2024).
    
    HOURLY DIVISOR: 173, derived from 40-hour work week. Formula: 40 h/week x 52/12 = 173.33, rounded to 173 per contract practice. Verified: A2 Apr 2024 = 1788.61 / 173 = 10.34 EUR/h; A1 Apr 2024 = 1909.58 / 173 = 11.04 EUR/h; B1 Apr 2024 = 2010.49 / 173 = 11.62 EUR/h — consistent divisor 173 across 3 levels, confirming TOTALE model.
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Governed by Art. 34-bis (Aumenti periodici di anzianita per il settore della Panificazione). In force since 1 January 1996 per Art. 34-bis text ('A decorrere dal 1 gennaio 1996, i lavoratori, esclusi gli apprendisti, hanno diritto a maturare aumenti periodici di anzianita per ogni biennio [...] fino ad un massimo di 5 bienni'). The June 2024 renewal (Art. 58 amendment) separately added seniority for APPRENTICES (10 EUR flat from 2025-01-01) — that is a distinct provision. Per-level amounts confirmed from Art. 34-bis table in UILA CCNL PDF: A1S=21.69, A1=19.11, A2=17.56, A3=16.01, A4=14.46, B1=21.69, B2=19.11, B3S=17.64, B3=16.01, B4=14.46 EUR/scatto. valid_from set to 1996-01-01. The apprentice scatto (10 EUR flat from 2025-01-01, Art. 58 as amended by the June 2024 renewal) is modelled as seniority_increments.apprentice_amount.
    
    APPRENTICESHIP: 1° Gruppo only (Panificazione Gruppo A livelli A1s, A1 → destination A1, duration 5 anni/10 semestri). Percentages confirmed from Art. 58 table in UILA CCNL PDF (p. 69, Settore Panificazione Gruppo A 1° Gruppo): sem 1-2=70%, sem 3-4=75%, sem 5-6=84%, sem 7-8=90%, sem 9-10=100%. Converted to 12-month periods: 0-12mo=70%, 12-24mo=75%, 24-36mo=84%, 36-48mo=90%, 48-60mo=100%. Source: Art. 58, UILA CCNL PDF.
    
    PRE-APRIL-2024: periods before 2024-04-01 are outside the modelled window (2018-2022 CCNL values not included).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector, existing file).
    
    APPRENTICESHIP gruppi A2, A3, B1, B2, B3S, B4 added from formazione-apprendistato.com panificazione table (medium-high confidence: secondary aggregator + IPSOA 2024 news confirm 2024 rinnovo structure). Semiannual progressions as per Art. 58 + Allegato apprendistato. Gruppo 1° (dest=A1, primary source UILA PDF) unchanged.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/panificazione-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/panificazione-artigianato-confartigianato.py"
```
