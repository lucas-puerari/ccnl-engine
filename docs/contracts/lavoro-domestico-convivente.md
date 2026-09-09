# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | — |
| **Workers (est.)** | ~900k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - DOMINA — Associazione Nazionale Famiglie Datori di Lavoro Domestico
    - FIDALDO — Federazione Italiana Datori di Lavoro Domestico
    - ASSINDATCOLF — Associazione Nazionale dei Datori di Lavoro Domestico
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL
    - FEDERCOLF

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
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,474.73 | — |
| `D` | Level D — senior caregiver / household manager | € 1,404.51 | — |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,193.84 | — |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,123.63 | — |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,053.39 | — |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 983.16 | — |
| `AS` | Level AS — domestic worker with seniority qualification | € 958.55 | — |
| `A` | Level A — entry-level domestic worker (colf generica) | € 908.10 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 36.32 |
| `AS` | € 38.34 |
| `B` | € 39.33 |
| `BS` | € 42.14 |
| `C` | € 44.95 |
| `CS` | € 47.75 |
| `D` | € 56.18 |
| `DS` | € 58.99 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CNEL code H501 sourced from kitech.it page title; unverified against CNEL archive (archive not accessible via HTTP at time of extraction). Update if CNEL confirms a different code.

!!! warning ""
    Single period 2026-01-01; pre-2026 tranches are out of scope. Prior renewal tranches (2021–2025) exist but are not modelled.

!!! warning ""
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amounts_by_level will need manual update.

!!! warning ""
    This file models TABELLA A only — full-time conviventi at 54 h/week (Art. 14 Co.1 lett. a CCNL). TABELLA B (conviventi ad orario ridotto, Art. 14 Co.2: B=702.25, BS=737.39, C=814.60) is out of scope. Callers must use a TABELLA B file (not yet modelled) for reduced-hours conviventi.

!!! warning ""
    Dividing TABELLA A monthly base by hourly_divisor 234 yields the cash-only rate (excludes board and lodging in kind). The hourly-wage INPS bracket lookup for weekly_hours <= 24 has not been validated for this file; the wage-bracket path is not exercised by the golden cases shipped with this file.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA A — Lavoratori Conviventi, Art. 14 Co.1 lett. a CCNL). Values confirmed from official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026, ISTAT +1.00%). Source is signatory employer association — primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026; withholding_exempt=true per Art. 4 D.P.R. 600/1973 (family employers are not sostituti d'imposta).
    
    HOURLY DIVISOR: 234, derived from 54 h/week contractual maximum for conviventi (Art. 10 CCNL). Formula: 54 × 52 / 12 = 234. Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilità, Art. 27 CCNL). No quattordicesima for domestic workers.
    
    SENIORITY: biennale (24 months), maximum 7 scatti. Per-level euro amounts = 4% × 2026 base (confirmed: kitech.it amounts match Domina base × 4% exactly at every level). Amounts frozen at 2026 base — will not automatically recompute at future ISTAT tranches.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    D/DS INDENNITÀ DI FUNZIONE: 207.69 EUR/month (Art. 34 CCNL) for levels D and DS only. Modelled as fixed_allowance (no role restriction — applies to all workers at those levels). Confirmed from Domina official table.
    
    Livello Unico (811.09) is a special sub-under-18 level excluded from this model — single-source, limited coverage.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lavoro-domestico-convivente.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavoro-domestico-convivente.py"
```
