# CCNL Carta e Cartone — Aziende Industriali (Assocarta)

| | |
|---|---|
| **CNEL code** | `G022` |
| **Sector** | carta-cartone |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-02-10 |
| **Workers (est.)** | ~35k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assocarta
    - Assografici
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL
    - UGL-carta e stampa

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
| `Q` | Q — executive manager, maximum technical or managerial responsibility | € 3,103.54 | — |
| `AS` | AS — special level, senior technical manager | € 3,093.45 | — |
| `A` | A — 6th category worker, production process supervisor | € 2,714.79 | — |
| `B1` | B1 — 5th category worker, highly qualified technician | € 2,467.92 | — |
| `B2S` | B2S — 4th category worker (super), plant-responsible technician | € 2,405.61 | — |
| `B2` | B2 — 4th category worker, technician with advanced specialisation | € 2,325.19 | — |
| `C1S` | C1S — 3rd category worker (super), highly specialised operator | € 2,190.60 | — |
| `C1` | C1 — 3rd category worker (higher grade), specialised operator | € 2,110.11 | — |
| `C2` | C2 — 3rd category worker, assigned to specialised processing | € 1,966.74 | — |
| `C3` | C3 — 3rd category worker, assigned to semi-specialised processing | € 1,864.67 | — |
| `D1` | D1 — 2nd category worker (higher grade), qualified operator | € 1,782.99 | — |
| `D2` | D2 — 2nd category worker, auxiliary machinery operator | € 1,680.55 | — |
| `E` | E — 1st category worker, simple and executive tasks | € 1,568.08 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 15.49 |
| `AS` | € 15.49 |
| `A` | € 15.49 |
| `B1` | € 13.94 |
| `B2S` | € 13.69 |
| `B2` | € 13.69 |
| `C1S` | € 13.43 |
| `C1` | € 13.43 |
| `C2` | € 13.17 |
| `C3` | € 12.91 |
| `D1` | € 12.39 |
| `D2` | € 11.88 |
| `E` | € 11.62 |

## Apprenticeship

**triennale** (type: `percentage`)  
Destination levels: `C3`, `C2`, `C1`, `C1S`, `B2`, `B2S`, `B1`, `A`  
percentage: 0.95

**biennale_categoria_D** (type: `percentage`)  
Destination levels: `D2`, `D1`  
percentage: 0.95

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-01 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-carta-industria-anno-2024-e-precedenti/) |
| — | — | 2026-04-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx) |
| — | — | 2021-07-28 | [↗](https://www.pisacaneboxes.com/wp-content/uploads/2022/02/ccnl-carta-industria2022.pdf) |
| — | — | 2026-02-10 | [↗](https://www.zetaservice.com/wp-content/uploads/2026/02/RINNOVO-CCNL-CARTA-AZIENDE-INDUSTRIALI-G022.pdf) |

??? note "Coverage notes"
    SALARY MODEL: two tranches modelled — 2024-07-01 (last tranche of CCNL 28/07/2021, source: lexplain.it) and 2026-04-01 (first tranche of rinnovo 10/02/2026, source: kitech.it). The 2024 tranche total = paga base + EMC (Elemento di Modernizzazione Contrattuale, EUR 20.00 at C1, parametrised). The 2026 rinnovo is conglobated: EMC absorbed into the new paga base. Both periods are modelled as base_salary totals; fixed_allowances=[] for all levels. The +125 EUR increase on C1 paga base (rinnovo) minus the EMC (EUR 20 abolished) = net +105 EUR on C1 total (1855.11 → 1960.11).
    
    FUTURE TRANCHES: +45 EUR at C1 from 01.01.2027, +45 from 01.01.2028, +60 from 01.09.2028 confirmed from rinnovo 10.02.2026 (zetaservice PDF). Per-level amounts are parametrically derived: each level increment = C1_increment × (level_2026-04-01 / C1_2026-04-01), rounded to cent. Math-verified all 13 levels × 3 tranches: all within ±0.02 EUR of parametric formula — consistent with the conglobated coefficient scale of the 2026 rinnovo.
    
    CONGLOBATED CHECK: 2024 values confirmed via lexplain.it (paga base + EMC columns explicit). 2026 values from kitech.it; rinnovo zetaservice PDF confirms Q (2882.91) and C1 (1960.11) at 2026-04-01, consistent with kitech. Level ordering is strictly monotone at both tranche dates.
    
    HOURLY DIVISOR: 173 (40h/week, Art. Orario di Lavoro CCNL 28/07/2021; confirmed ilccnl.it).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: CCNL 28/07/2021 Art. Tredicesima mensilità. Quattordicesima not provided.
    
    SENIORITY: biennale (24 months), max 5 scatti. Per-level amounts from CCNL 28/07/2021 Art. Aumenti periodici di anzianità (pisacaneboxes.com PDF, verified). Amounts unchanged in rinnovo 10/02/2026.
    
    APPRENTICESHIP professionalizzante, percentage type (CCNL 28/07/2021 Art. Apprendistato professionalizzante, pisacaneboxes.com PDF): track 'triennale' (36 months, 6 semesters 70/75/80/85/90/95%) for destination levels C3, C2, C1, C1S, B2, B2S, B1, A; track 'biennale_categoria_D' (24 months, 6 quadrimestri with the same percentages) for D2 and D1. E, AS and Q are not apprenticeship destinations. The final 95% period is open-ended: after the contractual duration the worker is qualified and paid at 100% as a permanent employee.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Assocarta is a Confindustria federation; CIGO applicable per D.Lgs. 148/2015.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/carta-cartone-assocarta.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/carta-cartone-assocarta.py"
```
