# CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)

| | |
|---|---|
| **CNEL code** | `K051` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Elettricita Futura
    - Utilitalia
    - Enel SpA
    - GSE
    - Sogin SpA
    - Terna SpA
    - FILCTEM-CGIL
    - FLAEI-CISL
    - UILTEC-UIL

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
| `QS` | Senior Quadro | € 4,399.12 | — |
| `Q` | Quadro | € 3,947.60 | — |
| `ASS` | Senior Senior Specialist Area | € 3,484.42 | — |
| `AS` | Senior Specialist Area | € 3,261.27 | — |
| `A1S` | Area 1 Senior | € 3,124.14 | — |
| `A1` | Area 1 | € 2,980.96 | — |
| `BSS` | Area B Senior Senior | € 2,838.72 | — |
| `BS` | Area B Senior | € 2,717.73 | — |
| `B1S` | Area B1 Senior | € 2,589.64 | — |
| `B1` | Area B1 | € 2,473.33 | — |
| `B2S` | Area B2 Senior | € 2,309.87 | — |
| `B2` | Area B2 | € 2,149.26 | — |
| `CS` | Area C Senior | € 1,905.68 | — |
| `C1` | Area C1 | € 1,724.71 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `QS` | € 49.01 |
| `Q` | € 46.33 |
| `ASS` | € 43.07 |
| `AS` | € 39.82 |
| `A1S` | € 37.86 |
| `A1` | € 35.74 |
| `BSS` | € 33.72 |
| `BS` | € 31.97 |
| `B1S` | € 30.16 |
| `B1` | € 28.46 |
| `B2S` | € 26.13 |
| `B2` | € 23.81 |
| `CS` | € 20.30 |
| `C1` | € 17.66 |

## Apprenticeship

**gruppo_c** (type: `percentage`)  
Destination levels: `CS`  
percentage: 1.00

**gruppo_b** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_a_bss** (type: `percentage`)  
Destination levels: `BSS`, `A1`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-02-11 | [↗](https://www.contratticcnl.it/elettrico/tabelle-retributive/) |
| — | — | 2025-02-11 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92) |

??? note "Coverage notes"
    Salary model is split. base_salary = paga base (time-series, 4 tranches from the 2025-02-11 renewal); fixed_allowances = EDR (Elemento Distinto della Retribuzione) frozen at EUR 10.33/month since 1988, same for all levels.
    
    hourly_divisor 173.33 as stated by the contract (40h/week statutory base: 40 x 52 / 12). Actual weekly hours are 38 (non-shift) or 40 (shift); the divisor is contractually fixed on the 40h base.
    
    Seniority cadence 24 months (biennale), maximum 5 scatti (10 years of service per contract text). Amounts vary by level (kitech.it, April 2026).
    
    APPRENTICESHIP (Art. 15 CCNL 2025-02-11, apprendistato professionalizzante). Three tracks by qualification group. Gruppo C (dest CS, 36m): yr1=86%, yr2=90%, yr3=96%, then 100%. Gruppo B excl. BSS (dest B1, 36m): same progression. BSS + Gruppo A (dest BSS and A1, 24m): yr1=86%, yr2=96%, then 100%. Source: Art. 15 para.5 table (CCNL full text PDF filctemcgil.it, 2025-02-11). Note: only the four qualification levels explicitly cited in Art.15 (CS, B1, BSS, A1) are modelled; S-suffix variants (B1S, A1S, etc.) are senior-grade levels not addressed in the apprenticeship article.
    
    APR 2027 VALUES: confirmed via parametric derivation. The CCNL elettrici system applies a fixed valore-punto increase each tranche (same absolute amount per parametro per tranche). Apr 2026 and Apr 2027 increments are equal across all 14 levels (ratio=1.000 verified); A1S reference level gets +65.50 EUR matching the search-confirmed '+65 EUR average TEM' for Apr 2027 (fiscoetasse.com, pmi.it). October 2027 values verified against contratticcnl.it (all 14 levels match).
    
    Workers covered: approximately 63,000 in 687 companies (Enel SpA, Terna SpA, GSE, Sogin, Energia Libera and affiliated). Agreement signed 2025-02-11; valid until 2027-12-31.
    
    INPS rates from 2026-industria.json (industria sector, 50 employees tier). IRPEF 2026 brackets applied (L. 199/2025).
    
    contratticcnl.it shows data alignment errors for BSS, BS, B1 in the April 2026 and April 2027 columns; kitech.it April 2026 values used as authoritative for all 14 levels.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/elettrico-elettricita-futura.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/elettrico-elettricita-futura.py"
```
