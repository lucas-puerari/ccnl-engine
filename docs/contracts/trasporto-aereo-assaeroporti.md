# CCNL Trasporto Aereo — Gestori Aeroportuali

| | |
|---|---|
| **CNEL code** | `I810` |
| **Sector** | trasporto aereo |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-06-04 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assaeroporti — Associazione Italiana Gestori Aeroporti
    - FILT-CGIL — Federazione Italiana Lavoratori Trasporti
    - FIT-CISL — Federazione Italiana Trasporti
    - Uiltrasporti
    - UGL Trasporto Aereo

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
| `1S` | Livello 1S — Quadri | € 2,174.53 | — |
| `1` | Livello 1 | € 1,973.18 | — |
| `2A` | Livello 2A | € 1,804.05 | — |
| `2B` | Livello 2B | € 1,691.30 | — |
| `3` | Livello 3 | € 1,570.49 | — |
| `4` | Livello 4 | € 1,417.47 | — |
| `5` | Livello 5 | € 1,336.93 | — |
| `6` | Livello 6 | € 1,256.39 | — |
| `7` | Livello 7 | € 1,127.53 | — |
| `8` | Livello 8 | € 1,014.78 | — |
| `9` | Livello 9 | € 805.38 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 37.29 |
| `1` | € 34.45 |
| `2A` | € 32.18 |
| `2B` | € 30.47 |
| `3` | € 29.33 |
| `4` | € 27.42 |
| `5` | € 26.65 |
| `6` | € 25.31 |
| `7` | € 24.22 |
| `8` | € 22.67 |
| `9` | € 0.00 |

## Apprenticeship

**professionalizzante_18m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.90

**professionalizzante_24m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.95

**professionalizzante_36m** (type: `percentage`)  
Destination levels: `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2B`, `2A`, `1`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    LEVEL 9 SENIORITY. Art. G23 seniority table lists amounts for levels 1S through 8 only. Level 9 is absent. Modelled as 0.00; not confirmed whether intentional exclusion or typographical omission.

!!! warning ""
    SUPPLEMENTARY ALLOWANCES. Role-conditional allowances (turno, campo, maneggio denaro, DPI) and the una tantum of EUR 500 (Art. G20, October 2025) are not modelled. All are attendance- or role-conditional or one-time payments.

!!! warning ""
    ART. G6 RECLASSIFICATION. A supplementary agreement of 23 March 2026 reportedly amended Art. G6 (professional classification). The amendment text was not retrieved; its effect on level codes and salary tables for as_of dates from 2026-03-01 onward is unverified. Hourly divisor taken from Art. G28 text; no official hourly-rate column available in the source for back-calculation cross-check.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-06-04 | [↗](https://assaeroporti.com/wp-content/uploads/2025/06/CCNL-Parte-Specifica-versione-accessibile.pdf) |
| — | — | 2025-06-04 | [↗](https://assaeroporti.com/ccnl-del-trasporto-aereo/) |

??? note "Coverage notes"
    APPRENTICESHIP TRACKS. Art. G14 §16 defines three professionalising tracks (18m, 24m, 36m) with percentage tables by semester. All three are implemented. Art. G14 does not restrict which track applies per destination level; employers and workers choose the duration per PFI. When calling compute() with Apprentice for any covered level, set Apprentice.track to 'professionalizzante_18m', 'professionalizzante_24m', or 'professionalizzante_36m'. Source: CCNL Parte Specifica Gestori Aeroportuali (assaeroporti.com, 04/06/2025), Art. G14 §16 table.
    
    EDR APPRENTICESHIP EXEMPTION. Art. G14 §16 limits the apprenticeship percentage to 'minimi tabellari in vigore, indennità di contingenza'. EDR (Art. G22) is not listed and is therefore paid at full value for apprentices. Modelled via apprenticeship_pct_relevant=false on all EDR allowances.
    
    SENIORITY CAP: maximum_count=8, as per 2025 rinnovo (signed 04/06/2025, FILT-CGIL comunicato) which recognized the 8th scatto from 01/01/2026 for all workers with ≥16 years seniority. Pre-1993 employees with 16+ years already captured under this rule. Engine has no hire-date input; this is a structural limitation — maximum_count=8 is the correct model for the vast majority of new hires.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/trasporto-aereo-assaeroporti.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/trasporto-aereo-assaeroporti.py"
```
