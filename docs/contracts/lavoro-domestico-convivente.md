# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Family** | `lavoro-domestico` |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | 2026-01-01 |
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
| **Limits of this contract** | assistance_contribution, base_salary, inps_employer, seniority, sickness |

9 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 26 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-01-01 |
| **Last review** | 2026-10-16 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Every payable rule of the file: minimums, hourly divisor, additional months, seniority, Cas.Sa.Colf, overtime, absences, leave and the accrual of the tredicesima, read in the signed text of 28 October 2025 and its 2026 table (p. 59); the sickness rule of Art. 27 stays derived (readings in its transformation). | corrected | Overtime: the file held 10% and 20%; Art. 15 c. 3 sets 25% by day, 50% by night and 60% on a holiday or Sunday. The 20% of Art. 14 c. 6 is the supplement of ordinary night work, not of overtime.<br>accrual_rule was missing: chiarimento a verbale 4 counts a fraction of a month of at least 15 calendar days as a whole month.<br>Citations moved from the DOMINA table and section labels without page to the signed text with page and quote.<br>Seniority of levels D and D super: the file held 4% of the minimum without the indennità di funzione (56.18, 58.99); Art. 34 c. 2 a) makes the indennità part of the retribuzione minima contrattuale on which Art. 37 c. 1 computes the 4%: 64.49 and 67.30.<br>Tabella A, the indennità di funzione and Tabella F match the signed table (p. 59) and the DOMINA table of 2026. |
| 2026-10-16 | claude-opus-5-5 (ai) | Limitation hourly_inps_bracket_unvalidated: the band of the hourly INPS contribution up to 24 weekly hours against the worked quarters of a signatory of the CCNL (DOMINA) and INPS circ. 9/2026. | flagged | INPS circ. 9/2026 downloaded again on 2026-10-16: same sha256 as the bundle, no rectification in the text; the 2026 amounts of the file stand.<br>DOMINA states that the paga oraria effettiva includes the hourly share of the tredicesima and prints four quarters of 2026 (13 weeks): colf 10 h at 8.00 an hour, 1.70, 221.00 (worker 55.90); colf 10 h at 9.00, 1.92 because 9 x 13 / 12 = 9.75 is above 9.61, 249.60 (62.40); colf 25 h, 1.24, 403.00 (100.75); badante convivente 54 h, 1.24, 870.48 (217.62). The engine's effective pay and band match all four (tests/knowledge/ccnl_engine/contribution/domestic/services/test_effective_hourly_pay.py::test_the_band_of_the_published_quarters_of_a_signatory): the raise by 13/12 is validated.<br>Still unvalidated, so the limitation stays: the share of board and lodging in the effective pay of a convivente up to 24 weekly hours. DOMINA states it ('per chi ha vitto e alloggio, il loro valore convenzionale'), as the engine computes it, but prints no worked case with board and lodging, and no worked example of a convivente up to 24 hours was found. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DS` | Level DS — senior caregiver / household manager with seniority | € 1,474.73 | 2026-01-01 |
| `D` | Level D — senior caregiver / household manager | € 1,404.51 | 2026-01-01 |
| `CS` | Level CS — specialised domestic worker with seniority | € 1,193.84 | 2026-01-01 |
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 1,123.63 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 1,053.39 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 983.16 | 2026-01-01 |
| `AS` | Level AS — domestic worker with seniority qualification | € 958.55 | 2026-01-01 |
| `A` | Level A — entry-level domestic worker (colf generica) | € 908.10 | 2026-01-01 |

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
| `D` | € 64.49 |
| `DS` | € 67.30 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-convivente/tranches_from_2027 · base_salary · impact yes · open"
    SINGLE PERIOD 2026-01-01. Pre-2026 tranches out of scope. Post-2026 CCNL 2025-2028 tranches not yet modelled: +30 on BS convivente from Jan 2027, +15 from Jan 2028, +15 from Sep 2028 (other levels proportional — exact amounts require official ASSINDATCOLF/DOMINA table for those periods).

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the 2027 and 2028 tranches from the official ASSINDATCOLF/DOMINA tables.

!!! warning "lavoro-domestico-convivente/seniority_frozen_at_2026 · seniority · impact unknown · open"
    Seniority amounts frozen at 2026 base. Future ISTAT adjustments will raise base_salary but amounts_by_level will need manual update.

    **Applies when:** `seniority` applies; from 2027-01-01.

    **Remediation:** Update the seniority amounts with each ISTAT adjustment of the minimum tables.

!!! warning "lavoro-domestico-convivente/part_time_scaling · base_salary · impact unknown · open"
    REDUCED HOURS UNDER ART. 14 C. 1: a convivente may agree fewer than 54 weekly hours (art. 14 c. 1: 'con un massimo di [...] 54 ore settimanali'). The CCNL gives Tabella A as monthly values and no rule to proportion them to the agreed hours; the engine scales the pay linearly on the full time the employment states. The art. 14 c. 2 regime (levels C, B, B super up to 30 hours, Tabella B) is the separate file lavoro-domestico-convivente-orario-ridotto.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how the Tabella A minimum of a convivente with fewer than 54 agreed weekly hours is computed and model it, then remove this note.

!!! warning "lavoro-domestico-convivente/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    INPS BAND: the engine chooses the band of up to 24 weekly hours on the paga oraria effettiva of INPS (circ. 9/2026; INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore domestico): the monthly pay with board and lodging over the hours of the employment (weekly hours x 52 / 12), raised by the tredicesima (x 13 / 12). That reading of the circular is not yet checked against a worked example of the INPS domestic table (review of 2026-10-30).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table.

!!! warning "lavoro-domestico-convivente/board_lodging_substitute · base_salary · impact unknown · open"
    The cash indennita sostitutiva of board and lodging is not paid for the days the convivente does not take them: ferie (Art. 17 c. 7), sospensioni extraferiali (Art. 18 c. 1), congedo matrimoniale (Art. 24 c. 2), malattia and infortunio outside hospital (Art. 27 c. 9, Art. 29 c. 7). The request carries no fact on whether board and lodging were taken, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days without board and lodging and pay the Tabella F value for them.

!!! warning "lavoro-domestico-convivente/extra_month_hours · assistance_contribution · impact unknown · open"
    The INPS contributions of the tredicesima are paid on the hours of the year: INPS bands them on the paga oraria effettiva, which spreads the tredicesima over the hours, so the tredicesima run charges no INPS hours. The Cas.Sa.Colf contribution of Art. 54 c. 2 is charged on the contributable hours the run states, a tredicesima run too: no bundled source says whether the tredicesima carries hours of its own for it.

    **Applies when:** `assistance_contribution` applies; run kind in thirteenth.

    **Remediation:** Source from the Cas.Sa.Colf rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "lavoro-domestico-convivente/oncological_comporto · sickness · impact unknown · open"
    Art. 27 c. 6: the comporto is 50% longer for an oncological illness certified by the ASL. The episode can state a serious illness (SicknessEpisode.serious_illness), but the domestic sickness rules have no serious-illness rule, so the engine keeps the ordinary comporto (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the serious-illness rule of Art. 27 c. 6 (comporto 50% longer) to the sickness rules.

!!! warning "lavoro-domestico-convivente/sick_board_lodging · sickness · impact unknown · open"
    Art. 27 c. 9: the conventional value of board and lodging is part of the sick pay only when the worker is not in hospital or in the employer's home. The request does not say where the worker is, so the engine pays the monthly pay as stated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the days in hospital or in the employer's home and leave the board and lodging out of their sick pay.

!!! warning "lavoro-domestico-convivente/annual_minimi_not_updated · base_salary · impact yes · open"
    ANNUAL MINIMI: the minimi of the CCNL are updated every year from 1 January by the Commissione nazionale (Art. 38, ISTAT variation of the consumer prices); the bundle holds the table of 2026. From 1 January 2027 the amounts are those of 2026 until the 2027 table is published and added, so a 2027 run is not payable.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the minimi of 2027 set by the Commissione nazionale with their source, then remove this note.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded. A CCNL whose comporto the engine counts over the calendar year (Commercio Art. 186 and the others with comporto_calendar_year) is not affected.

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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf | tabella_retributiva | 2026-01-01 | [↗](https://associazionedomina.it/wp-content/uploads/2026/02/TABELLA-minimi-retributivi-2026.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione globale (TABELLA A — Lavoratori Conviventi, Art. 14 Co.1 lett. a CCNL). Values confirmed from official Domina salary table PDF (TABELLA-minimi-retributivi-2026.pdf, effective 01/01/2026, ISTAT +1.00%). Source is signatory employer association — primary source.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    HOURLY DIVISOR: 234 = 54 x 52 / 12: 54 h/week contractual maximum for conviventi (Art. 14 c. 1 lett. a CCNL 28/10/2025) and monthly pay = hourly pay x weekly hours x 52 / 12 (chiarimento a verbale 1). Convivente and non-convivente are independent pay scales (different tables, different hourly divisors).
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima for domestic workers.
    
    SENIORITY: biennale (24 months), maximum 7 scatti (Art. 37). Per-level amounts = 4% of the retribuzione minima contrattuale of Tabella A; for levels D and D super it includes the indennità di funzione (Art. 34 c. 2 a): 4% x (1,404.51 + 207.69) = 64.49 and 4% x (1,474.73 + 207.69) = 67.30. Amounts frozen at 2026 values: future ISTAT tranches require a manual update.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    D/DS INDENNITÀ DI FUNZIONE: 207.69 EUR/month (Art. 34 CCNL) for levels D and DS only. Modelled as fixed_allowance (no role restriction — applies to all workers at those levels). Confirmed from Domina official table.
    
    CNEL code H501 confirmed: lavoro-economia.it explicitly lists 'CCNL Lavoro Domestico (Colf e Badanti) [Cnel: H501]'. Also confirmed via kitech.it. CNEL archive verification not attempted (had returned 404 previously).
    
    Livello Unico (811.09) is a special sub-under-18 level excluded from this model — single-source, limited coverage.
    
    BOARD AND LODGING: every level carries the allowance vitto_alloggio, the valore convenzionale of board and lodging provided in kind (Art. 36 c. 3, Tabella F 2026: 2,33 + 2,33 + 2,00 per day, x 30 = 199,80 per month). A regular run pays no cash for it and counts it in the TFR base (Art. 41 c. 1); the tredicesima pays it in cash (Art. 39 c. 1, chiarimento a verbale 5). It is not reduced for reduced hours (Art. 14 c. 2: intera retribuzione in natura).
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    
    SICKNESS (Art. 27): INPS pays no indemnity to domestic workers; the employer pays 50% of the retribuzione globale di fatto up to the third day and 100% from the fourth, for at most 8, 10 or 15 days in the 365 days that end on the sick day, within a comporto of 10, 45 or 180 days, for up to 6 months of seniority, up to 2 years and over 2 years. A sick day is a thirtieth of the monthly pay (chiarimento a verbale 2).
    
    NIGHT WORK (Art. 14 c. 6): ordinary work between 22.00 and 6.00 is paid with a 20% supplement of the hourly retribuzione globale di fatto; the engine takes its amount as a NightShiftEvent stated by the caller. The overtime bands are those of Art. 15 c. 3 (25% by day, 50% by night, 60% on a holiday or Sunday); night overtime on a holiday has no band of its own and a run that states it is rejected.
    

## Raw data

The contract file this page is generated from: [`agreement/lavoro-domestico-convivente.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavoro-domestico-convivente.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavoro-domestico-convivente/example.py"
```
