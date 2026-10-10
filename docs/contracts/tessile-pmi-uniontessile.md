# CCNL Tessile-Abbigliamento-Moda PMI (Uniontessile-Confapi)

| | |
|---|---|
| **CNEL code** | `D018` |
| **Sector** | tessile abbigliamento moda PMI |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-18 |
| **Workers (est.)** | ~48k |
| **Ruleset version** | `2026.2` |
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

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | base_salary, pension_fund_contribution |

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
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

4 semplificazioni documentate.
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

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tessile-pmi-uniontessile/other_subsectors_tables · base_salary · impact yes · open"
    SCOPE: tessile/abbigliamento/moda sub-sector only. Calzature, pelli, occhiali, giocattoli have separate salary tables not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the calzature, pelli, occhiali and giocattoli salary tables with a sub-sector input.

!!! warning "tessile-pmi-uniontessile/fondapi_base_elements · pension_fund_contribution · impact yes · open"
    The Fondapi base ('retribuzione Fondapi' or 'elemento retributivo nazionale') counts the EDR besides the minimum; the bundle pay of this CCNL does not hold them, so the fund contributions of an enrolled worker are computed on the minimum alone and understated.

    **Applies when:** `pension_fund_contribution` applies.

    **Remediation:** Model the EDR in the pay of the CCNL and add them to the Fondapi base, then remove this note.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    VV.PP. (Venditori Viaggiatori e Piazzisti) levels excluded; only Jan-2026 data available from primary sources, historical tranches not found.

!!! note ""
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
    
    FONDAPI: the contributions are computed on the contractual minimum of the level; the Fondapi base also counts the EDR, not in the bundle pay.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/tessile-pmi-uniontessile.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tessile-pmi-uniontessile.py"
```
