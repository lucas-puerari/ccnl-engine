# CCNL Turismo — Federalberghi/Faita

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-05 |
| **Workers (est.)** | ~220k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalberghi
    - Faita (L'Ospitalità Italiana)
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS

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
| `A` | Level A | € 2,495.22 | — |
| `B` | Level B | € 2,310.11 | — |
| `1` | Level 1 | € 2,152.32 | — |
| `2` | Level 2 | € 1,967.20 | — |
| `3` | Level 3 | € 1,855.32 | — |
| `4` | Level 4 | € 1,750.69 | — |
| `5` | Level 5 | € 1,641.85 | — |
| `6s` | Level 6 super | € 1,578.72 | — |
| `6` | Level 6 | € 1,556.35 | — |
| `7` | Level 7 | € 1,458.42 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 40.80 |
| `B` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6s`, `6`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    The level category (quadro/impiegato/operaio) is indicative. The CCNL 2010 uses numeric levels 1-6 plus A, B, 6s, 7 with no formal contractual category distinction.

!!! warning ""
    Layer 3 (overtime, night work, public holidays) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2010-01-01 | [↗](http://www.uiltucs.it/pdf/turismo/CCNL_Turismo_Confcommercio_2010.pdf) |
| — | — | 2014-01-18 | [↗](https://uiltucs.it/wp-content/uploads/2019/01/CCNL-Federalberghi-18.01.2014.pdf) |
| — | — | 2024-07-05 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/ccnl_turismo_ipotesi_accordo_5-luglio-2024_agg_11_7_24.pdf) |

??? note "Coverage notes"
    CNEL code H052 is shared with CCNL Agenzie di Viaggio Fiavet — the engine allows duplicates.
    
    Apprenticeship durations Art. 54 CCNL 2010 (visual confirm page 89): grades 2/3/4=48m, 5/6s=36m, 6=24m. Levels A/B/1/7 are not apprenticeship destinations.
    
    Apprenticeship percentages Art. 58 CCNL 2010 (pdftotext pages 90-97): 1st year=80%, 2nd year=85%, 3rd year=90%, from 4th year=95%. Uniform for all destination levels.
    
    Hourly divisor 172 from Art. 151 CCNL 2010 (standard working hours 40h/week). Verification: 1550.69/9.01=172.1 (Jul-2024: 1620.69/9.42=172.0).
    
    14 monthly payments from Art. 160 (thirteenth) and Art. 161 (fourteenth) of the 2024 renewal.
    
    Seniority increments Art. 158 CCNL 2010: six triennial increments (cadence_months=36, maximum_count=6). Per-level amounts visually verified from PDF image pages 140-141: A=40.80, B=39.25, 1=37.70, 2=36.15, 3=34.86, 4=33.05, 5=32.54, 6s=31.25, 6=30.99, 7=30.47.
    
    Base salary table effective 01.04.2016 from the 2014 renewal (UILTuCS PDF): A=2210.16, B=2046.20, 1=1906.44, 2=1742.47, 3=1643.37, 4=1550.69, 5=1454.28, 6s=1398.37, 6=1378.55, 7=1291.81.
    
    5 salary tranches 2024-2027 from the 5 July 2024 renewal (UILTuCS PDF): Jul-2024, Jun-2025, May-2026, Apr-2027, Nov-2027.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/turismo-federalberghi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/turismo-federalberghi.py"
```
