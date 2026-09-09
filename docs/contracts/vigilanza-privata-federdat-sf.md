# CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — SF

| | |
|---|---|
| **CNEL code** | `HV17` |
| **Sector** | vigilanza privata — servizi fiduciari (SF) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-05-04 |
| **Workers (est.)** | ~40k |
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
| `A` | Livello A | € 2,032.24 | — |
| `B` | Livello B | € 1,849.18 | — |
| `C` | Livello C | € 1,556.29 | — |
| `D` | Livello D | € 1,300.00 | — |
| `E` | Livello E (entry, primi 9 mesi) | € 1,207.14 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `E` | € 17.50 |
| `D` | € 19.00 |
| `C` | € 22.00 |
| `B` | € 26.00 |
| `A` | € 29.00 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `E`, `D`, `C`, `B`, `A`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Seniority amounts not found in renewal PDF (base CCNL 2013, art. 23 SF). Cadence 36m and max 6 scatti assumed (same as GPG section). Amounts are approximate proxies; verify against base text.

!!! warning ""
    Apprenticeship: 100% passthrough. Rules not found in renewal document; verify against CCNL FEDERDAT base text.

!!! warning ""
    additional_months=13 for the period 01/06/2023-01/01/2024; 14 from 01/01/2024 onward. Level E is used for first 9 months of tenure (per contract text).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-02-16 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf) |

??? note "Coverage notes"
    CCNL HV17 FEDERDAT SF (Servizi Fiduciari) section. Conglobated, divisor 173. 5 levels (A-E). 14a mensilita from 01/01/2024; before that 13 months. 8 tranches, last at 01/04/2026 (SF schedule). Level F absent from tables (may be entry/apprenticeship only; verify base CCNL 2013).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vigilanza-privata-federdat-sf.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vigilanza-privata-federdat-sf.py"
```
