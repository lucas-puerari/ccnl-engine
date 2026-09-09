# CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas

| | |
|---|---|
| **CNEL code** | `K321` |
| **Sector** | gas e acqua |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-08 |
| **Workers (est.)** | ~65k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Utilitalia
    - Proxigas
    - Anfida
    - Assogas
    - FILCTEM-CGIL
    - FEMCA-CISL
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
| `Q` | Level Q (Quadri) — par. 200.74 — managerial, highest responsibility | € 3,577.47 | — |
| `8` | Level 8 — par. 181.29 — senior expert, broad managerial-technical responsibility | € 3,230.84 | — |
| `7` | Level 7 — par. 167.50 — expert, advanced coordination | € 2,985.08 | — |
| `6` | Level 6 — par. 153.69 — senior specialist, technical-organisational roles | € 2,738.97 | — |
| `5` | Level 5 — par. 139.96 — highly skilled, broad autonomy | € 2,494.28 | — |
| `4` | Level 4 — par. 131.42 — specialist, complex tasks requiring expertise | € 2,342.01 | — |
| `3` | Level 3 — par. 122.95 — skilled operative, autonomous in standard tasks | € 2,191.09 | — |
| `2` | Level 2 — par. 111.15 — semi-skilled, partial autonomy | € 1,980.76 | — |
| `1` | Level 1 — par. 100 — unskilled, non-autonomous, routine operations | € 1,782.14 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 0.00 |
| `3` | € 0.00 |
| `4` | € 0.00 |
| `5` | € 0.00 |
| `6` | € 0.00 |
| `7` | € 0.00 |
| `8` | € 0.00 |
| `Q` | € 0.00 |

## Apprenticeship

**professionalizzante_24** (type: `percentage`)  
Destination levels: `7`, `8`  
percentage: 1.00

**professionalizzante_30** (type: `percentage`)  
Destination levels: `2`, `4`, `5`, `6`  
percentage: 1.00

**professionalizzante_36** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SENIORITY: abolished from 31/12/2015 (§5.5 of CCNL PDF). Frozen as 'elemento ad personam non riassorbibile' at the individual amount accrued by each worker as at 31/12/2015. No new increments can be earned by any worker hired after 2015. Modelled as maximum_count=0 (all amounts 0.00) — no seniority is added for new hires. SIMPLIFICATION: the frozen elemento ad personam for pre-2016 hires is individual and not computable from level alone; it is not modelled.

!!! warning ""
    INPS: reuses 2026-industria.json. Gas and water utilities (aziende private del settore gas-acqua) are classified under 'attività industriali' for INPS contribution purposes. Employer associations Utilitalia and Proxigas are Confindustria-aligned. SIMPLIFICATION: exact INPS circular for this sector not verified; 2026-industria.json rates used as proxy.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-09-30 | [↗](https://sosvavsrl.it/media/attachments/2024/05/24/ccnl.pdf) |
| — | — | 2025-05-08 | [↗](https://ilccnl.it/contratto/ccnl/gas-e-acqua---aziende-private-dal-010102) |
| — | — | 2025-05-08 | [↗](https://www.filctemcgil.it/index.php/notiziario/news/gas-acqua) |

??? note "Coverage notes"
    SALARY MODEL: conglobated contingenza ('minimi tabellari integrati') with EDR 10.33 shown separately. Confirmed from scheda riassuntiva PDF (CCNL 30/09/2022, sosvavsrl.it), section heading 'Minimi tabellari integrati'. EDR is a fixed statutory element (frozen since 1997, Accordo interconfederale) shown as a distinct line in all salary tables; modelled as fixed_allowance for each level.
    
    HOURLY DIVISOR: 167. Stated explicitly in §4.3 of the PDF scheda riassuntiva: 'Coefficiente orario: 167'. Corresponds to 38h 30min contractual week (§4.4). Back-calculation: L1(2024-09-01)=1677.64/167=10.05 EUR/h.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Stated in §4.1: 'Mensilità: 14'. Tredicesima confirmed §5.3, quattordicesima confirmed §5.4.
    
    LEVEL Q ALLOWANCE: Indennità di funzione 51.65 EUR/month (12 mensilità) per §2.1 of the CCNL PDF. Shown separately from minimo and EDR in all salary tables.
    
    COVERAGE: CCNL covers approximately 50,000 workers in about 600 private gas and water distribution companies (source: filctemcgil.it, 2025 renewal announcement). CNEL code K321.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/gas-acqua-utilitalia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/gas-acqua-utilitalia.py"
```
