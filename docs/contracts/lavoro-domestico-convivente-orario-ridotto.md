# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | — |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.3` |
| **Extraction** | 🧑 Manual |
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
| **Limits of this contract** | base_salary, inps_employee, inps_employer |

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

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 814.60 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 737.39 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 702.35 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `B` | € 28.09 |
| `BS` | € 29.50 |
| `C` | € 32.58 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-convivente-orario-ridotto/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    Dividing TABELLA B monthly base by the monthly hours of the employment yields the cash-only rate: the INPS hourly bracket for weekly_hours <= 24 is selected on it, without the board and lodging the INPS retribuzione oraria effettiva counts. The hourly-wage INPS bracket lookup has not been validated for this file; the wage-bracket path is not exercised by the golden cases shipped with this file.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table.

!!! warning "lavoro-domestico-convivente-orario-ridotto/board_lodging_substitute · base_salary · impact unknown · open"
    The cash indennita sostitutiva of board and lodging is not paid for the days the convivente does not take them: ferie (Art. 17 c. 7), sospensioni extraferiali (Art. 18 c. 1), congedo matrimoniale (Art. 24 c. 2), malattia and infortunio outside hospital (Art. 27 c. 9, Art. 29 c. 7). The request carries no fact on whether board and lodging were taken, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days without board and lodging and pay the Tabella F value for them.

!!! warning "lavoro-domestico-convivente-orario-ridotto/extra_month_hours · inps_employee · impact unknown · open"
    INPS and Cas.Sa.Colf are charged on the contributable hours the run states, a tredicesima run too. No bundled source says whether the tredicesima carries contributable hours of its own, and a competence year gives it the hours of its default facts, those of a regular month.

    **Applies when:** `inps_employee` applies; run kind in thirteenth.

    **Remediation:** Source from the INPS rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-28 | [↗](https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/CCNL.pdf) |

??? note "Coverage notes"
    SALARY MODEL: TABELLA B of the CCNL of 28/10/2025, conviventi hired under art. 14 c. 2 (levels C, B and B super, up to 30 weekly hours, written act of c. 3). The monthly minimum is paid 'qualunque sia l'orario di lavoro osservato nel limite massimo delle 30 ore settimanali', so it is not proportioned to the hours and more than 30 weekly hours are rejected; board and lodging are due in full ('fermo restando l'obbligo di corresponsione dell'intera retribuzione in natura'). Values from the Tabella minimi retributivi decorrenza 1 gennaio 2026 annexed to the CCNL: B 702,35, BS 737,39, C 814,60.
    
    HOURLY DIVISOR: 130 = 30 x 52 / 12 in the file; a run uses the weekly hours of the employment x 52 / 12 (flat_pay_max_weekly_hours), since the Tabella B pay does not change with the hours: B super at 10 weekly hours is 737,39 / 43,33 = 17,02 an hour. Work beyond the agreed hours is paid at the hourly retribuzione globale di fatto (art. 14 c. 2), with the art. 15 supplements outside the agreed time arrangement; the overtime bands are those of the convivente file.
    
    SENIORITY: biennale, 4% of the Tabella B minimum (art. 37 c. 1: 'sulla retribuzione minima contrattuale'), maximum 7 scatti: B 28,09, BS 29,50, C 32,58.
    
    NOT MODELLED: students aged 16 to 40 (art. 14 c. 2) at levels other than C, B and B super, for whom Tabella B has no value; the Tabella H indennita of the baby sitter of level B super for children under six (art. 34 c. 3), 97,06 a month for Tabella B workers; the Tabella L indennita of art. 34 c. 7 for certified workers. None of them is paid.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima for domestic workers.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    BOARD AND LODGING: every level carries the allowance vitto_alloggio, the valore convenzionale of board and lodging provided in kind (Art. 36 c. 3, Tabella F 2026: 2,33 + 2,33 + 2,00 per day, x 30 = 199,80 per month). A regular run pays no cash for it and counts it in the TFR base (Art. 41 c. 1); the tredicesima pays it in cash (Art. 39 c. 1, chiarimento a verbale 5). It is not reduced for reduced hours (Art. 14 c. 2: intera retribuzione in natura).
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lavoro-domestico-convivente-orario-ridotto.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavoro-domestico-convivente-orario-ridotto.py"
```
