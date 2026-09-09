# CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG

| | |
|---|---|
| **CNEL code** | `HV17` |
| **Sector** | vigilanza privata — guardie particolari giurate (GPG) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-05-04 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERDAT
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ⚠️ partial |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Livello Q (Quadro) | € 2,434.74 | — |
| `I` | Livello I | € 2,086.89 | — |
| `II` | Livello II | € 1,946.09 | — |
| `III` | Livello III | € 1,723.31 | — |
| `IV` | Livello IV | € 1,528.88 | — |
| `V` | Livello V | € 1,450.44 | — |
| `VI` | Livello VI (convenzionale) | € 1,350.44 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `VI` | € 19.66 |
| `V` | € 20.52 |
| `IV` | € 21.13 |
| `III` | € 22.46 |
| `II` | € 23.83 |
| `I` | € 26.12 |
| `Q` | € 31.30 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `VI`, `V`, `IV`, `III`, `II`, `I`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority amounts not found in renewal PDF (base CCNL 2013, art. 106 GPG). Values proxied from ASSIV CCNL (HV40, same sector). Cadence 36m and max 6 scatti confirmed ('6 trienni' in source).

!!! warning ""
    Apprenticeship: 100% passthrough. Rules not found in renewal document; verify against CCNL FEDERDAT base text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-02-16 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf) |

??? note "Coverage notes"
    CCNL HV17 FEDERDAT GPG section. Conglobated, 14 months, divisor 173. 7 levels. 6 tranches: 01/06/2023, 01/06/2024, 01/06/2025, 01/12/2025, 01/04/2026, 01/12/2026. Contract validity: 01/06/2023-31/12/2026.
    
    Level VI salary at 01/06/2024 (1185.44) is anomalously high vs prior tranche (1108.06) — confirmed by source as conventional riallineamento for level VI.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vigilanza-privata-federdat-gpg.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vigilanza-privata-federdat-gpg.py"
```
