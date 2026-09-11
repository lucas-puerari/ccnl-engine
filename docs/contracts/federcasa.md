# CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa

| | |
|---|---|
| **CNEL code** | `T611` |
| **Sector** | Case popolari |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-11-06 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federcasa
    - FP CGIL
    - FPS CISL
    - UIL FPL
    - Fesica Confsal

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
| `Q1` | Quadro 1 (parametro 220) | € 3,483.40 | — |
| `Q2` | Quadro 2 (parametro 190) | € 3,001.82 | — |
| `As` | Area A Super (parametro 176) | € 2,773.72 | — |
| `A1` | Area A 1 (parametro 162) | € 2,542.96 | — |
| `A2` | Area A 2 (parametro 150) | € 2,358.35 | — |
| `A3` | Area A 3 (parametro 138) | € 2,169.12 | — |
| `Bs` | Area B Super (parametro 137) | € 2,143.87 | — |
| `B1` | Area B 1 (parametro 135) | € 2,084.39 | — |
| `B2` | Area B 2 (parametro 128) | € 1,979.16 | — |
| `B3` | Area B 3 (parametro 121) | € 1,874.51 | — |
| `C1` | Area C 1 (parametro 118) | € 1,829.95 | — |
| `C2` | Area C 2 (parametro 114) | € 1,762.49 | — |
| `C3` | Area C 3 (parametro 110) | € 1,706.87 | — |
| `Ds` | Area D Super (parametro 108) | € 1,699.39 | — |
| `D1` | Area D 1 (parametro 103) | € 1,601.65 | — |
| `D2` | Area D 2 (parametro 100) | € 1,548.03 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 14 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 38.25 |
| `Q2` | € 31.50 |
| `As` | € 28.35 |
| `A1` | € 25.20 |
| `A2` | € 22.05 |
| `A3` | € 19.35 |
| `Bs` | € 18.90 |
| `B1` | € 18.45 |
| `B2` | € 16.74 |
| `B3` | € 15.39 |
| `C1` | € 14.85 |
| `C2` | € 13.95 |
| `C3` | € 13.05 |
| `Ds` | € 12.60 |
| `D1` | € 12.06 |
| `D2` | € 11.61 |

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-11-06 | [↗](https://cislfp.it/wp-content/uploads/2024/11/CCNL-Federcasa-2022-2024.pdf) |
| — | — | 2024-11-06 | [↗](https://cislfp.it/wp-content/uploads/2024/11/Tabelle-economiche-CCNL-Federcasa-2022-2024.pdf) |
| — | — | 2024-11-06 | [↗](https://ilccnl.it/ccnl/federcasa/federcasa/tabelleretributive) |

??? note "Coverage notes"
    Salary model: conglobated. Art. 71 (p.63): retribuzione base = minimi tabellari. Art. 72 (p.64): single importo column, no contingenza or EDR columns. Confirmed by ilccnl.it (A1, A2, A3, As, B1 at 01/12/2024).
    
    16 levels (highest to lowest): Q1, Q2, As, A1, A2, A3, Bs, B1, B2, B3, C1, C2, C3, Ds, D1, D2.
    
    Single salary period from 01/12/2024 (Art. 72). Increases for 2022, 2023, and pre-Dec 2024 paid as una tantum (IVC and arretrati), not as tabellare changes.
    
    Dec 2024 increase formula: NUOVO = round(OLD x 1.075, 2). Confirmed: A1 2365.54 x 1.075 = 2542.96, A2 2193.81 x 1.075 = 2358.35, A3 2017.79 x 1.075 = 2169.12, As 2580.20 x 1.075 = 2773.72, B1 1938.97 x 1.075 = 2084.39 (all matching ilccnl.it to the cent).
    
    Hourly divisor 156 from Art. 71.5: 'un importo pari ad 1/156 della retribuzione individuale mensile'. Also derived from 36h/week x 52/12 = 156.
    
    Art. 71.5 defines 'retribuzione oraria' as 1/156 of monthly including tredicesima and quattordicesima quotas. Engine uses gross_monthly / 156 without those quotas, so engine hourly_rate differs slightly from the contractual figure.
    
    Additional months: 14. Art. 76 (p.68): tredicesima in December + quattordicesima in June.
    
    Seniority: biennale cadence (Art. 73.1: 'al compimento di ogni biennio'), maximum 14 (Art. 73.2: 'un massimo di 14 aumenti periodici'). Art. 73.4: scatti maturated from 01/01/2018 reduced by 10%.
    
    Apprenticeship: Art. 19 defers terms to accordo interconfederale 18/05/2016 and a CCNL-specific agreement within 6 months of signing. No public text of that agreement found.
    
    Headcount: not verified. No CNEL/ADAPT figure located for T611 Federcasa.
    
    tax_sector=terziario: Federcasa entities (ex-IACP/ATER/ATC) left the public-sector comparto (Art. 1.2 CCNL Federcasa). Actual INPS classification not publicly documented; terziario is the best available proxy (commercial/housing entities without industria-style CIG). Same approach as other para-public entities in the engine.
    
    Seniority amounts use the 10%-reduced values (post-01/01/2018 cohort per Art. 73.4). Workers hired before ~1990 may still have pre-2018 grandfathered scatti at full amounts (engine cannot model the two cohorts separately). New-hire case is exact; long-tenure pre-2018 cohort is understated by ~10%. Structural engine limitation.
    
    CCNL expired 31/12/2024. Art. 4 B.5-8 mandates IVC (Indennità Vacanza Contrattuale) at 30% of IPCA (~Mar 2025) and 50% (~Sep 2025) during the renewal gap. Engine models tabellare only; IVC during the gap is not included. This is a structural out-of-scope element (ultrattività compensation, not a tabellare change).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/federcasa.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/federcasa.py"
```
