# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (non conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | ~900k |
| **Ruleset version** | `2026.3` |
| **Readiness** | 👁 Reviewed |

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

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | assistance_contribution, base_salary, seniority, sickness |

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 16 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-28 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Every payable rule of the file: minimums, hourly divisor, additional months, seniority, Cas.Sa.Colf, overtime, absences, leave and the accrual of the tredicesima, read in the signed text of 28 October 2025 and its 2026 table (p. 59); the sickness rule of Art. 27 stays derived (readings in its transformation). | corrected | Overtime: the file held 10% and 20%; Art. 15 c. 3 sets 25% by day, 50% by night and 60% on a holiday or Sunday. The 20% of Art. 14 c. 6 is the supplement of ordinary night work, not of overtime.<br>accrual_rule was missing: chiarimento a verbale 4 counts a fraction of a month of at least 15 calendar days as a whole month.<br>Citations moved from the DOMINA table and section labels without page to the signed text with page and quote.<br>Overtime of non conviventi: hours 41 to 44 by day at 10% (Art. 15 c. 4), beyond the 44th at 25% (hour_threshold_per_week 4). |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella C of the 2026 minimi (values from 1 January 2026) for the eight levels; the annual update of the minimi. | corrected | The eight hourly minimi of Tabella C (6,51 to 9,97) times 40 x 52 / 12 are the monthly amounts of the bundle.<br>The minimi are reset every 1 January (Art. 38): from 2027 the 2026 table would be paid as final. Declared as annual_minimi_not_updated on the three domestic CCNLs, review_due 2027-01-31. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL H501 matches (FIDALDO, which groups ASSINDATCOLF, and DOMINA with FILCAMS, FISASCAT, UILTUCS, FEDERCOLF).<br>Term: the ipotesi of 28 October 2025 applies from 1 November 2025; its expiry is reported as 31 October 2028 (CNEL filing) or 31 December 2028 (press); not read in the text, left open. |

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

!!! warning "lavoro-domestico-non-convivente/extra_month_hours · assistance_contribution · impact unknown · open"
    The INPS contributions of the tredicesima are paid on the hours of the year: INPS bands them on the paga oraria effettiva, which spreads the tredicesima over the hours, so the tredicesima run charges no INPS hours. The Cas.Sa.Colf contribution of Art. 54 c. 2 is charged on the contributable hours the run states, a tredicesima run too: no bundled source says whether the tredicesima carries hours of its own for it.

    **Applies when:** `assistance_contribution` applies; run kind in thirteenth.

    **Remediation:** Source from the Cas.Sa.Colf rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "lavoro-domestico-non-convivente/oncological_comporto · sickness · impact unknown · open"
    Art. 27 c. 6: the comporto is 50% longer for an oncological illness certified by the ASL. The request does not say whether an episode is oncological, so the engine keeps the ordinary comporto.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for an oncological sickness episode and lengthen its comporto by 50%.

!!! warning "lavoro-domestico-non-convivente/annual_minimi_not_updated · base_salary · impact yes · open"
    ANNUAL MINIMI: the minimi of the CCNL are updated every year from 1 January by the Commissione nazionale (Art. 38, ISTAT variation of the consumer prices); the bundle holds the table of 2026. From 1 January 2027 the amounts are those of 2026 until the 2027 table is published and added, so a 2027 run is not payable.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the minimi of 2027 set by the Commissione nazionale with their source, then remove this note.

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
    
    SICKNESS (Art. 27): INPS pays no indemnity to domestic workers; the employer pays 50% of the retribuzione globale di fatto up to the third day and 100% from the fourth, for at most 8, 10 or 15 days in the 365 days that end on the sick day, within a comporto of 10, 45 or 180 days, for up to 6 months of seniority, up to 2 years and over 2 years. A sick day is a thirtieth of the monthly pay (chiarimento a verbale 2).
    
    INPS BAND: the band of up to 24 weekly hours is chosen on the paga oraria effettiva of INPS (circ. 9/2026; INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore domestico): the monthly pay with board and lodging over the hours of the employment (weekly hours x 52 / 12), raised by the tredicesima (x 13 / 12).
    
    NIGHT WORK (Art. 14 c. 6): ordinary work between 22.00 and 6.00 is paid with a 20% supplement of the hourly retribuzione globale di fatto; the engine takes its amount as a NightShiftEvent stated by the caller. The overtime bands are those of Art. 15 c. 3 (25% by day, 50% by night, 60% on a holiday or Sunday); night overtime on a holiday has no band of its own and a run that states it is rejected.
    

## Raw data

The contract file this page is generated from: [`agreement/lavoro-domestico-non-convivente.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavoro-domestico-non-convivente.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavoro-domestico-non-convivente/example.py"
```
