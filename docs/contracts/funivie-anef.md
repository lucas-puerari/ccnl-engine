# CCNL Trasporto a Fune (Funivie Terrestri ed Aeree) - ANEF

| | |
|---|---|
| **CNEL code** | `I911` |
| **Sector** | Trasporto a fune |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-16 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANEF
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI
    - SAVT

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
| `1S` | 1° livello Super (parametro 210) | € 2,410.99 | — |
| `1` | 1° livello (parametro 195) | € 2,238.88 | — |
| `2` | 2° livello (parametro 176) | € 2,020.97 | — |
| `3` | 3° livello (parametro 160) | € 1,836.94 | — |
| `4` | 4° livello (parametro 145) | € 1,664.59 | — |
| `5` | 5° livello (parametro 130) | € 1,492.75 | — |
| `6` | 6° livello (parametro 120) | € 1,377.94 | — |
| `7` | 7° livello (parametro 100) | € 1,148.35 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 70.00 |
| `1` | € 65.00 |
| `2` | € 60.00 |
| `3` | € 55.00 |
| `4` | € 50.00 |
| `5` | € 45.00 |
| `6` | € 40.00 |
| `7` | € 35.00 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-16 | [↗](https://www.funiviearabba.it/wp-content/uploads/2025/12/Sintesi-CCNL-ANEF.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = paga base (Allegato 1). fixed_allowances = contingenza (per-level, Allegato 2). No EDR: ilccnl.it Oct-2025 table shows Terzo Elemento = 0.00; totals confirm base + contingenza only (e.g. 2179.27 + 528.67 = 2707.94).
    
    8 livelli retributivi (parametri 210/195/176/160/145/130/120/100 per Art. 18). Sintesi: '8 categorie professionali e altrettanti livelli retributivi'.
    
    Hourly divisor 173 from Art. 18 of the 2025 CCNL text (confirmed thaler.it and lavoro-economia.it).
    
    Additional months: 14 (tredicesima natalizia + quattordicesima luglio, confirmed thaler.it and lavoro-economia.it).
    
    Seniority from Allegato 3 (new-hire amounts, biennale cadence, max 5 scatti). Double-sourced: ilccnl.it Oct-2025 column confirms 1S=70, 1=65, 2=60, 3=55. Allegato 3.1 (pre-30/04/2016 cohort grandfathered amounts) not modelled.
    
    Tranche dates (Allegato 1): 2025-05-01, 2025-10-01, 2027-03-01, 2028-03-01.
    
    Headcount not verified; no CNEL/ADAPT figure located for I911. INPS-CNEL mapping: I911.
    
    tax_sector=industria: ANEF funivie operators are classified under ATECO H (trasporti) which INPS maps to the industria contribution table. No dedicated 'funivie' or 'trasporto-fune' TaxSector exists in the engine enum; industria is the correct proxy for this transport-infrastructure category.
    
    Indennita di funzione (118.79 EUR/month) for Quadri (L. 190/1985 status within levels 1S and 1) is not modelled. It is a person-status allowance tied to individual Quadro designation — not a livello retributivo. Structural engine limitation: the engine does not support per-person status allowances.
    
    Allegato 3.1 (grandfathered scatti for workers hired before 30/04/2016) not modelled. Only Allegato 3 (standard post-2016 cohort) amounts implemented. Structural scope decision: pre-2016 grandfathered amounts affect a declining cohort; the new-hire case is exact.
    
    Apprenticeship destinations limited to levels 1-6. Level 1S excluded: Quadro status per L. 190/1985 is a person-status designation acquired through individual deed, not a contractually defined apprenticeship destination.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/funivie-anef.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/funivie-anef.py"
```
