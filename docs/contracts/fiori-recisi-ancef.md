# CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)

| | |
|---|---|
| **CNEL code** | `H201` |
| **Sector** | Fiori recisi, verde e piante ornamentali (import-export) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-03-30 |
| **Workers (est.)** | ~1.3k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCEF
    - FLAI-CGIL
    - FISASCAT-CISL
    - UIL Tucs

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
| `Q` | Quadro | € 2,700.25 | — |
| `1S` | 1° Super | € 2,460.21 | — |
| `1` | 1° livello | € 2,185.36 | — |
| `2` | 2° livello | € 1,920.48 | — |
| `3` | 3° livello | € 1,792.57 | — |
| `4` | 4° livello | € 1,655.26 | — |
| `5` | 5° livello | € 1,576.97 | — |
| `6` | 6° livello | € 1,478.65 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 34.70 |
| `1S` | € 30.30 |
| `1` | € 29.50 |
| `2` | € 26.90 |
| `3` | € 25.00 |
| `4` | € 23.70 |
| `5` | € 23.10 |
| `6` | € 22.40 |

## Apprenticeship

**professionalizzante - dest livelli 1-2** (type: `under_classification`)  
Destination levels: `1`, `2`

**professionalizzante - dest livelli 3-4** (type: `under_classification`)  
Destination levels: `3`, `4`

**professionalizzante - dest livello 5** (type: `under_classification`)  
Destination levels: `5`

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-03-30 | [↗](https://www.ccnlportatili.it/ccnl/fiori-recisi/) |
| — | — | 2023-03-30 | [↗](https://www.redigo.info/tabelle-retributive/fiori-recisi-ancef) |
| — | — | 2023-03-30 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=29864) |

??? note "Coverage notes"
    CCNL signed 30/03/2023 by ANCEF, FLAI-CGIL, FISASCAT-CISL, UIL Tucs. Valid 01/01/2023-31/12/2026.
    
    Salary model: conglobated. ilccnl.it shows contingenza=0 and EDR=0 for all levels at 2026-01-01. No split components.
    
    8 levels (highest to lowest): Q, 1S, 1, 2, 3, 4, 5, 6. 4 tranches: 01/01/2023, 01/01/2024, 01/01/2025, 01/01/2026.
    
    Salary values at all 4 tranches confirmed from redigo.info tabelle retributive (structured table, all 8 levels).
    
    Additional months: 14. Art. 38 (tredicesima) + Art. 39 (quattordicesima). Confirmed from FISASCAT announcement.
    
    Hourly divisor: 170. Art. 45 of the CCNL. Confirmed from ccnlportatili.it and ilccnl.it.
    
    Seniority (Art. 48): triennale cadence (36 months), maximum 10 scatti. Per-level amounts confirmed from ccnlportatili.it; Q and 1S and levels 1-2 amounts cross-checked against ilccnl.it (Q=34.70, 1S=30.30, 1=29.50, 2=26.90).
    
    Apprenticeship (Art. 15): under_classification. Durations by destination group confirmed from olympus.uniurb.it (2023 renewal): L1-L2=36mo, L3-L4=30mo, L5=27mo. L5 structure (12mo at lb=1, then lb=0) confirmed from esterinocafasso.it 2023 renewal coverage.
    
    Headcount: 1,341 workers (ADAPT 18 Rapporto CNEL, 2022 UniEmens data). FISASCAT quotes ~15,000 addetti del settore — this is sector-wide (including florists and growers under other CCNLs); ADAPT figure is INPS code H201 only.
    
    SIMPLIFICATION: L1-L2 and L3-L4 apprenticeship pay progression (2 levels below for first half, 1 level below for second half) confirmed from 2023 renewal news (UILTuCS / farecontrattazione.adapt.it): "due livelli inferiori alla mansione per la prima metà, un livello inferiore per la seconda metà." For L5: 12mo at level 6, then level 5 (from olympus.uniurb.it). Engine uses 100% passthrough because schema requires static pay_level_code; dynamic sub-level changes cannot be modelled (structural engine limitation). Durations are confirmed from olympus.uniurb.it; the internal half-split structure is not independently confirmed from the 2023 CCNL primary text for L1-L4.
    
    tax_sector=terziario: ANCEF represents importers and wholesalers of cut flowers (commercio all'ingrosso). The INPS sector code is terziario (commercial trade, ATECO G). Terziario rates (FISASCAT/Confcommercio). This is consistent and confirmed — no dedicated floricoltura INPS sector code exists for the importing/wholesale sub-sector.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/fiori-recisi-ancef.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/fiori-recisi-ancef.py"
```
