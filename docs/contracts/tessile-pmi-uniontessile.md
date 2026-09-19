# CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)

| | |
|---|---|
| **CNEL code** | `D018` |
| **Sector** | tessile abbigliamento moda PMI |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-18 |
| **Workers (est.)** | ~48k |
| **Ruleset version** | `—` |
| **Extraction** | 🧑 Manual |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Uniontessile-Confapi
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🟡 Needs review |
| **Last human review** | 2026-09-17 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-02-18 |
| **Last verified** | 2026-09-17 |
| **Next salary event** | 2027-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8` | Livello 8 — quadro | € 2,548.78 | 2027-01-01 |
| `7` | Livello 7 | € 2,403.51 | 2027-01-01 |
| `6` | Livello 6 | € 2,257.77 | 2027-01-01 |
| `5` | Livello 5 | € 2,116.84 | 2027-01-01 |
| `4` | Livello 4 | € 2,002.56 | 2027-01-01 |
| `3bis` | Livello 3 bis | € 1,955.72 | 2027-01-01 |
| `3` | Livello 3 | € 1,908.92 | 2027-01-01 |
| `2bis` | Livello 2 bis | € 1,850.15 | 2027-01-01 |
| `2` | Livello 2 | € 1,796.58 | 2027-01-01 |
| `1` | Livello 1 — base | € 1,558.00 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.71 |
| `2` | € 7.23 |
| `2bis` | € 7.23 |
| `3` | € 7.75 |
| `3bis` | € 7.75 |
| `4` | € 8.26 |
| `5` | € 9.81 |
| `6` | € 10.33 |
| `7` | € 11.88 |
| `8` | € 12.91 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SCOPE: tessile/abbigliamento/moda sub-sector only. Calzature, pelli, occhiali, giocattoli have separate salary tables not modelled.

!!! warning ""
    VV.PP. (Venditori Viaggiatori e Piazzisti) levels excluded; only Jan-2026 data available from primary sources, historical tranches not found.

!!! warning ""
    APPRENTICESHIP: not modelled (set to []). Primary source for post-2024 apprenticeship rules not identified.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Abbigliamento Moda Tessili PMI Uniontessile Confapi — KITech | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=501) |
| CCNL Tessili PMI (Uniontessile - Confapi) — lavoro-economia.it | tabella_retributiva | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=500) |
| CCNL Uniontessile Confapi: rinnovo 2025 — farecontrattazione.adapt.it | rivista | — | [↗](https://farecontrattazione.adapt.it/ccnl-uniontessile-confapi-relazioni-industriali-e-sostegno-ai-dipendenti-al-centro-del-rinnovo-2025/) |
| CCNL tessile PMI Confapi: tabelle retributive 2025-2027 — FISCOeTASSE | tabella_retributiva | — | [↗](https://www.fiscoetasse.com/approfondimenti/16754-ccnl-tessile-abbigliamento-moda-pmi-tabelle-retributive-2025-2027.html) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (single minimo mensile, no separate contingenza or EDR). Source: lavoro-economia.it explicitly divides monthly by 173 to derive hourly rate, no separate component columns.
    
    LEVEL 1: jumps to 1558.00 EUR/month at Jan 2025 (9.006 EUR/h, exceeds 9 EUR/h floor per CCNL art. 33bis). Frozen in Jan 2026 and Jan 2027 — excluded from standard tranche mechanism.
    
    LEVEL 8 IDF: indennità di funzione 51.65 EUR modelled as fixed_allowance (unverified for period before Jan 2026). Function-conditional, not automatic for all L8 workers.
    
    FONDAPI: employer rate 1.90% from contract start, increased +0.10% to 2.00% from Mar 2025 per Art. 33 (source: farecontrattazione.adapt.it).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tessile-pmi-uniontessile.json"
    ```

## Usage example

```python
--8 < --"docs/examples/contracts/tessile-pmi-uniontessile.py"
```
