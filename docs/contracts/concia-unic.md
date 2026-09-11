# CCNL per i lavoratori dell'industria conciaria (UNIC)

| | |
|---|---|
| **CNEL code** | `B101` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~22.6k |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - UNIC
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ⚠️ partial |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A — quadri, direttivi con elevata autonomia decisionale | € 2,937.60 | — |
| `B1` | Livello B1 — operai e impiegati con elevata specializzazione | € 2,494.04 | — |
| `B2` | Livello B2 — operai e impiegati specializzati | € 2,494.04 | — |
| `C1` | Livello C1 — operai e impiegati qualificati con funzioni di coordinamento | € 2,234.82 | — |
| `C2` | Livello C2 — operai e impiegati qualificati | € 2,234.82 | — |
| `D1` | Livello D1 — operai e impiegati con mansioni di concetto specializzate | € 2,041.99 | — |
| `D2` | Livello D2 — operai e impiegati con mansioni di concetto | € 2,041.99 | — |
| `E1` | Livello E1 — operai e impiegati qualificati con mansioni operative specializzate | € 1,783.71 | — |
| `E2` | Livello E2 — operai e impiegati con mansioni operative qualificate | € 1,783.71 | — |
| `E3` | Livello E3 — operai e impiegati con mansioni operative generiche specializzate | € 1,783.71 | — |
| `F1` | Livello F1 — lavoratori in periodo di prima formazione (parametro 100) | € 1,689.30 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 19.63 |
| `B1` | € 19.63 |
| `B2` | € 17.56 |
| `C1` | € 14.46 |
| `C2` | € 13.94 |
| `D1` | € 13.94 |
| `D2` | € 12.65 |
| `E1` | € 11.88 |
| `E2` | € 11.88 |
| `E3` | € 10.33 |
| `F1` | € 10.33 |

## Apprenticeship

**professionalizzante_A_B1_B2** (type: `under_classification`)  
Destination levels: `A`, `B1`, `B2`

**professionalizzante_C1_C2** (type: `under_classification`)  
Destination levels: `C1`, `C2`

**professionalizzante_D1** (type: `under_classification`)  
Destination levels: `D1`

**professionalizzante_D2** (type: `under_classification`)  
Destination levels: `D2`

**professionalizzante_E1** (type: `under_classification`)  
Destination levels: `E1`

**professionalizzante_E2** (type: `under_classification`)  
Destination levels: `E2`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    OVERTIME: 6 bands in contract (diurno fino 48h 15%, diurno oltre 48h prima ora 25%, oltre 48h successive 35%, notturno prima ora 61%, notturno successive 76%, festivo 71%). Engine supports one rate per applies_to_kinds; modeled as 15% diurno, 61% notturno, 71% festivo. Higher overtime bands omitted.

!!! warning ""
    DAILY DIVISOR: contract states quota giornaliera = 25 giorni/mese. DailyDivisorMethod has no by_25; by_26 used. Error: gross_daily overstated by ~3.8% for absence deductions.

!!! warning ""
    SICKNESS: Art. 60 (2024 renewal) — 3 seniority tiers: comporto 8/10/12 mesi, full-pay 3/4/5 mesi, half-pay 5/6/7 mesi. Modeled as base tier (0-5 years): 100% months 1-3, 50% months 4-8, max 240 days. Higher tiers not modeled — SicknessRules has no seniority-gated comporto.

!!! warning ""
    LEAVE: 20 gg up to 10 years; +2 gg from 11th year (132 months); +3 gg from 16th year over base (not over the 11-year tier; 192 months = 23 gg); 5 settimane (25 gg) from 18th year (216 months). Source: MySolution sintesi 2017 p. 4. ROL 68 ore/anno not modeled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-03-07 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/concia/240307_CONCIA_RINNOVO%20CCNL%202023-2026.pdf) |
| — | — | 2017-04-01 | [↗](https://www.mysolution.it/globalassets/_nuovomysolution/pdf-schede-sintesi/concia-industria_definitivo.pdf) |
| — | — | — | [↗](https://www.kitech.it/tabelle-retributive-concia-industria) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare (Allegato n. 1, CCNL 07/03/2024). EDR = 10.33 EUR (Accordo 31/07/1992, all levels). IPO = Indennità di posizione organizzativa, level-specific time series per tranche (levels B1, C1, D1, E1, E2). IND_FUNZIONE = 25.82 EUR (level A only, Indennità di funzione, art. 47 CCNL 2017). Back-calculation: D1 total 01/01/2026 = 2041.99+123.67+10.33 = 2175.99; kitech confirms 2176.00 (rounding). B1 total = 2494.04+222.01+10.33 = 2726.38; kitech confirms 2726.38. A total = 2937.60+25.82+10.33 = 2973.75; kitech confirms 2973.75.
    
    DECORRENZA: economic decorrenza 01/07/2023; first tranche 01/03/2024. Arretrati for 2023-07-01 to 2024-03-01 paid as lump sum. Series starts at 2024-03-01. SIMPLIFICATION: pre-tranche salary not modeled.
    
    HOURLY DIVISOR: contract states 'quota oraria = retribuzione mensile / 173' (Allegato n. 1). Cross-check: 40h/week × 52 / 12 = 173.3; divisor 173 verified. Source: primary CCNL PDF filctemcgil.it.
    
    IPO CROSS-CHECK: MySolution 2017 IPO at 01/05/2019: B1=182.63, C1=91.62, D1=103.98, E1=128.23, E2=73.02. Allegato n.1 pre-renewal (30/06/2023): B1=192.63, C1=96.62, D1=108.98, E1=135.73, E2=75.52. Deltas B1+10.00, C1+5.00, D1+5.00, E1+7.50, E2+2.50 — all clean round figures consistent with 2019-2023 renewal cycle.
    
    APPRENTICESHIP: under_classification per MySolution sintesi 2017 p. 5 (Allegato apprendistato). 6 tracks by destination level, all with levels_below 2 → 1 → 0. D1 period-2: source table prints E2, but 10 of 11 destination tracks are monotone 2->1->0; E2 (order 3) below D1 (order 6) would cut pay mid-track, so D2 (order 5, exactly 1 below D1) is the only consistent reading. Max 36 months per D.Lgs. 167/2011 as amended 26/04/2012 (footnote in source).
    
    SENIORITY: biennial (cadence_months=24), maximum 5 increments. Amounts from MySolution sintesi apr. 2017 p. 3 (CCNL previgente); confirmed unchanged — kitech.it 2024-tranche totals including 5 scatti match MySolution amounts across all 11 levels.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/concia-unic.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/concia-unic.py"
```
