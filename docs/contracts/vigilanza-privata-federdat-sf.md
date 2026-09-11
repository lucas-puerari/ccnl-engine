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
| **L1 — Gross** | ✅ implemented |
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
**Maximum:** 10 increments

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-02-16 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf) |

??? note "Coverage notes"
    CCNL HV17 FEDERDAT SF (Servizi Fiduciari) section. Conglobated, divisor 173. 5 levels (A-E). 14a mensilita from 01/01/2024; before that 13 months. 8 tranches, last at 01/04/2026 (SF schedule). Level F absent from tables (may be entry/apprenticeship only; verify base CCNL 2013).
    
    SENIORITY: amounts from UILTUCS tabelle PDF (Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf), cadence 36m: A=29.00, B=26.00, C=22.00, D=19.00, E=17.50 EUR/scatto. July 9 2026 renewal (FEDERDAT-CONFIAL) increased maximum_count from 6 to 10; per-scatto amounts for SF not independently verifiable from a post-rinnovo public source (ilccnl.it shows Q–III for GPG only; SF behind registration). Values assumed unchanged pending primary source confirmation.
    
    Apprenticeship: 100% passthrough confirmed from CCNL FEDERDAT Art. 86: "L'Apprendista ha diritto per tutta la durata del periodo di apprendistato all'inquadramento e alla corrispondente retribuzione del livello finale di collocazione." (FESICA PDF, CCNL ISTITUTI AZIENDE VIGILANZA PRIVATA, Art. 86). Engine models this correctly as 100% of destination level salary.
    
    ADDITIONAL MONTHS: 13 for Jun 2023-Dec 2023 (pre-quattordicesima); 14 from 01/01/2024 onward (quattordicesima introduced by rinnovo July 2023 renewal, per fiscoetasse.com). Level E: entry-level for first 9 months of tenure per contract text — correct by design.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/vigilanza-privata-federdat-sf.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vigilanza-privata-federdat-sf.py"
```
