# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)

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
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,724.81 | — |
| `D` | Level D — senior caregiver / household manager | € 1,655.61 | — |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,435.90 | — |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,359.78 | — |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,288.85 | — |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 1,212.73 | — |
| `AS` | Level AS — domestic worker with seniority qualification | € 1,169.48 | — |
| `A` | Level A — entry-level domestic worker (colf generica) | € 1,126.23 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 45.05 |
| `AS` | € 46.78 |
| `B` | € 48.51 |
| `BS` | € 51.55 |
| `C` | € 54.39 |
| `CS` | € 57.44 |
| `D` | € 66.22 |
| `DS` | € 68.99 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SINGLE PERIOD 2026-01-01. Pre-2026 tranches out of scope. Post-2026 CCNL 2025-2028 tranches not yet modelled: +30 on BS from Jan 2027, +15 from Jan 2028, +15 from Sep 2028 (other levels proportional — exact amounts require official ASSINDATCOLF/DOMINA table for those periods).

!!! warning ""
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amount_by_level will need manual update.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA C — Lavoratori Non Conviventi, Art. 14 Co.2 lett. b CCNL). Hourly rates from official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026). Monthly base_salary = hourly_rate × 173. Source is signatory employer association — primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026; withholding_exempt=true per Art. 4 D.P.R. 600/1973.
    
    HOURLY DIVISOR: 173, derived from 40 h/week (Art. 14 Co.2 CCNL). Formula: 40 × 52 / 12 = 173.33, rounded to 173. Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    BASE SALARY: computed as hourly_rate × 173. Engine divides gross_monthly / hourly_divisor to recover the contractual hourly rate exactly.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilità, Art. 27 CCNL). No quattordicesima.
    
    SENIORITY: biennale (24 months), maximum 7 scatti. Per-level amounts = 4% × non-convivente base (= hourly × 173 × 4%). Amounts frozen at 2026 values — future ISTAT tranches require manual update.
    
    APPRENTICESHIP: none. Domestic workers excluded from D.lgs. 81/2015 Art. 47 apprenticeship.
    
    D/DS function allowance: not applicable for non-convivente (TABELLA C shows only hourly rates, no separate indennità column). D/DS hourly rates already reflect the seniority grade.
    
    CNEL code H501 confirmed: lavoro-economia.it explicitly lists 'CCNL Lavoro Domestico (Colf e Badanti) [Cnel: H501]'. Also confirmed via kitech.it. CNEL archive verification not attempted (had returned 404 previously).
    
    Livello Unico (hourly 5.83) is a special sub-under-18 level excluded from this model.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lavoro-domestico-non-convivente.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavoro-domestico-non-convivente.py"
```
