# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | — |
| **Workers (est.)** | ~900k |
| **Ruleset version** | `2026.3` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

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
| **Limits of this contract** | base_salary, inps_employee, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,728.13 | 2026-01-01 |
| `D` | Level D — senior caregiver / household manager | € 1,658.80 | 2026-01-01 |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,438.67 | 2026-01-01 |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,362.40 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,291.33 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 1,215.07 | 2026-01-01 |
| `AS` | Level AS — domestic worker with seniority qualification | € 1,171.73 | 2026-01-01 |
| `A` | Level A — entry-level domestic worker (colf generica) | € 1,128.40 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 45.14 |
| `AS` | € 46.87 |
| `B` | € 48.60 |
| `BS` | € 51.65 |
| `C` | € 54.50 |
| `CS` | € 57.55 |
| `D` | € 66.35 |
| `DS` | € 69.13 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-non-convivente/tranches_from_2027 · base_salary · impact yes · open"
    SINGLE PERIOD 2026-01-01. Pre-2026 tranches out of scope. Post-2026 CCNL 2025-2028 tranches not yet modelled: +30 on BS from Jan 2027, +15 from Jan 2028, +15 from Sep 2028 (other levels proportional — exact amounts require official ASSINDATCOLF/DOMINA table for those periods).

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the 2027 and 2028 tranches from the official ASSINDATCOLF/DOMINA tables.

!!! warning "lavoro-domestico-non-convivente/seniority_frozen_at_2026 · seniority · impact unknown · open"
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amount_by_level will need manual update.

    **Applies when:** `seniority` applies; from 2027-01-01.

    **Remediation:** Update the seniority amounts with each ISTAT adjustment of the minimum tables.

!!! warning "lavoro-domestico-non-convivente/meal_indennity · base_salary · impact unknown · open"
    A non-convivente on 6 or more hours a day with continuous presence is owed the meal or, when it is not given, an indennita equal to its valore convenzionale (Art. 14 c. 8; Tabella F 2026: 2,33 per meal). The request carries no fact on daily hours, presence or meals given, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days owed a meal not given and pay the Tabella F value for them.

!!! warning "lavoro-domestico-non-convivente/extra_month_hours · inps_employee · impact unknown · open"
    INPS and Cas.Sa.Colf are charged on the contributable hours the run states, a tredicesima run too. No bundled source says whether the tredicesima carries contributable hours of its own, and a competence year gives it the hours of its default facts, those of a regular month.

    **Applies when:** `inps_employee` applies; run kind in thirteenth.

    **Remediation:** Source from the INPS rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA C - Lavoratori Non Conviventi, Art. 14 c. 1 lett. b CCNL 28/10/2025). Hourly rates from the official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026). Monthly base_salary = hourly rate x 40 x 52 / 12 (chiarimento a verbale 1). Source is signatory employer association - primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    HOURLY DIVISOR: 173.33 = 40 x 52 / 12 to the cent: 40 h/week contractual maximum for non conviventi (Art. 14 c. 1 lett. b CCNL 28/10/2025) and chiarimento a verbale 1. Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    BASE SALARY: computed as hourly_rate x 40 x 52 / 12, rounded to the cent. Dividing it by the hourly divisor 173.33 recovers the Tabella C hourly rate to the cent.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima.
    
    SENIORITY: biennale (24 months), maximum 7 scatti (Art. 37). Per-level amounts = 4% x the monthly minimum (hourly x 40 x 52 / 12). Amounts frozen at 2026 values - future ISTAT tranches require manual update.
    
    APPRENTICESHIP: none. Domestic workers excluded from D.lgs. 81/2015 Art. 47 apprenticeship.
    
    D/DS function allowance: not applicable for non-convivente (TABELLA C shows only hourly rates, no separate indennità column). D/DS hourly rates already reflect the seniority grade.
    
    CNEL code H501 confirmed: lavoro-economia.it explicitly lists 'CCNL Lavoro Domestico (Colf e Badanti) [Cnel: H501]'. Also confirmed via kitech.it. CNEL archive verification not attempted (had returned 404 previously).
    
    Livello Unico (hourly 5.83) is a special sub-under-18 level excluded from this model.
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/lavoro-domestico-non-convivente.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavoro-domestico-non-convivente.py"
```
