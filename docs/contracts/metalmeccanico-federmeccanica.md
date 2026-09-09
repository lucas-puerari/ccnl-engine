# CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)

| | |
|---|---|
| **CNEL code** | `C011` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~1,7M |
| **Ruleset version** | `2026.3` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federmeccanica
    - Assistal
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

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
| `A1` | Level 8 — quadro, maximum professional grade | € 2,907.01 | — |
| `B3` | Level 7 — high technical or managerial expertise | € 2,838.99 | — |
| `B2` | Level 6 — specialist technician, department head, technical employee | € 2,542.98 | — |
| `B1` | Level 5 Super — highly specialised worker, technician | € 2,370.33 | — |
| `C3` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,211.43 | — |
| `C2` | Level 4 — specialist worker 1st category, white-collar employee | € 2,064.88 | — |
| `C1` | Level 3 — skilled worker, clerical employee | € 2,022.12 | — |
| `D2` | Level 2 — standardised operations, simple white-collar duties | € 1,979.37 | — |
| `D1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,784.94 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.05 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 40.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_30** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_24** (type: `percentage`)  
Destination levels: `D2`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-11-22 | [↗](https://www.contratticcnl.it/metalmeccanici/tabelle-retributive/) |
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-metalmeccanici-industria/) |
| — | — | — | [↗](https://www.lexplain.it/scatti-di-anzianita-contratto-metalmeccanici-industria/) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the 'consolidated table minimums' of the CCNL Federmeccanica-Assistal, which incorporate base pay, contingenza, and EDR into a single figure (Federmeccanica practice since 2001). For this reason fixed_allowances is empty for all levels.
    
    JUNE 2025 TRANCHE: values verified against the agreement of 12 June 2025 (source: studiomorettistp.it and dinunzio.it, which report the official Federmeccanica-Assistal consolidated table minimums). All 9 levels confirmed.
    
    JUNE 2024 AND JUNE 2026 TRANCHES: values verified on contratticcnl.it (updated July 2026) and lexplain.it.
    
    SENIORITY INCREMENTS: the proposal to replace monthly increments with a one-off 'early settlement' was REJECTED by the unions during the CCNL 2025-2028 negotiations (November 2025 agreement). Increments remain recurring monthly additions as provided by Art. 6 of the current CCNL. The model (seniority_count × amount_by_level) is correct. The amounts in amount_by_level are verified on lexplain.it.
    
    APPRENTICESHIP: professionalizzante (accordo integrativo 20/04/2021). Eligible levels: D2, C1, C2, C3, B1, B2, B3 (D1 and A1 excluded). Pay: 85% (first third), 90% (second third), 95% (third third), then classified at destination. Three duration tracks: 36m (standard), 30m (diploma EQF 4-7 consistent with profession), 24m (D2 serial repetitive production only). Source: accordo 20/04/2021 Federmeccanica art. 'Apprendistato professionalizzante', reproduced in MySolution circolare Marini 13/05/2021.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12 = 173.33 rounded to 173, Federmeccanica standard).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Federmeccanica CCNL. The performance bonus/variable company element is not modelled (layer 3).
    
    INPS: the employer rates in 2026-industria.json are calculated for verified components (IVS 23.81% + DS 1.61% + CUAF 2.48% + CIGO D.Lgs.148/2015 + FIS/CIGS Circ.INPS 5/2025). Resulting totals: ≤15 employees = 30.13%, 16-50 employees = 30.20%, >50 employees = 30.50%. Does not include INAIL. The CIGS employee share (0.30% for >15 employees) is not yet modelled in employee_rate.
    
    JUN 2021, JUN 2022, JUN 2023 TRANCHES: values retrieved from lexplain.it (metalworking industry pay tables; secondary aggregator source). Cross-check: D1 Jun-2024=1719.67 confirms exact alignment with data already present. Four annual tranches (Jun 2021-2024) based on the IPCA mechanism from the CCNL 05/02/2021.
    
    OVERTIME/NIGHT/HOLIDAY (L3): percentages modelled per Art. 14 CCNL Federmeccanica 2021 (straordinario diurno 15%, lavoro notturno 20%, lavoro festivo 30%). Source: testo contrattuale Art. 14. Provenance unverified -- rates need cross-check against official 2025 renewal text.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanico-federmeccanica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanico-federmeccanica.py"
```
