# CCNL Industria Chimica e Farmaceutica (Federchimica-Farmindustria-Assistal)

| | |
|---|---|
| **CNEL code** | `B011` |
| **Sector** | chimica |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-04-15 |
| **Workers (est.)** | ~210k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Federchimica
    - Farmindustria
    - Assistal
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, sickness, workplace_injury |

14 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 116 verified / 6 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-15 |
| **Last review** | 2026-10-20 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the signed texts: the ipotesi di rinnovo of 15 April 2025, the Intesa of 8 January 2024, the testo definitivo of 10 May 2006 and the renewals of 18 December 2009 and 19 July 2018, for the production tier. | corrected | 134 records verified, 4 derived. The tables cited an aggregator re-typing; they now cite the signed scan (read by OCR and on the page images) and the Intesa of 8 January 2024.<br>The first table is the TEM of 1 July 2024 (Intesa 8/1/2024), not of 1 June 2025: valid_from 2024-07-01 for the 15 levels.<br>The EDR from 1 July 2027 was inside base_salary; it is now the allowance EDR, outside the TFR base (art. 15 B 2): base_salary 2027-07 and 2028-06 lowered by 18 to 39 EUR.<br>Overtime: night 50/60/75% (not 35%), weekday 35% beyond the 48th hour, holiday 70% from the 45th hour, the 25% band from the 45th hour (threshold 4, not 8); categories A and B excluded.<br>Absences are deducted at 1/175 an hour (art. 20), not by 26: by_hourly with an 8-hour day (derived).<br>Sickness: 100% of the net pay for 3/4/5 months and 50% after, comporto 8/10/12 months over 36, not a flat 100% for 365 days (derived: the 2022 and 2025 texts differ on the hospital restart day).<br>Apprenticeship: one category below then the destination, at the minimo without IPO: not expressible, track removed and declared.<br>Fonchim: employer 2.3% from 1 January 2027 (2025 renewal p. 47), 2.55% with the fund's insurance share (derived).<br>Hourly divisor and additional months from the 2006 text (valid_from 2006-05-10); payment day of the tredicesima added.<br>No renewal or inflation verification after 15 April 2025 through October 2026 (CNEL B011 listing). |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-01: the trattamento economico minimo of every category and tranche of the renewal of 15 April 2025, and a year and a termination of a D1 impiegato against a hand oracle. | confirmed | Allegato TEM (p. 48, scan read by OCR): the previgente minimo and IPO of the 15 categories plus the increments of July 2025, December 2025, July 2026, July 2027 and June 2028 rebuild the 75 amounts of the file; the A1 to A3 and B1 to B2 amounts add the EAR of 190 and 100 euro (art. 15 B 3), as their transformations state. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios chimica-year and chimica-june): a D1 impiegato hired on 1 January 2026 by an employer with 50 employees, across the tranche of July 2026; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. No owed amount blocks these runs.<br>The 5 derived rules stay derived: each reads its value from a cited text through a stated transformation, and this review found no primary text that states them directly. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | corrected | hourly_base_method minimo_e_anzianita (was minimo_tabellare), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: CHIM_FESTIVO, CHIM_TURNO_DIURNO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The renewal within the window of L. 199/2025 art. 1 c. 7 and the minimo before its first tranche. | corrected | Ipotesi of 15 April 2025, first tranche from 1 July 2025: parameters.renewals.<br>p. 46: the July 2025 tranche also pays the last 20 EUR (D1) of the renewal of 13 June 2022, signed outside the window: the minimo before the renewal at D1 is 2239.26 + 20 = 2259.26. The 2022 tranche of the other categories is not printed in the 2025 text (its tables are announced, not attached): their increment stays unmeasured. |
| 2026-10-20 | claude-opus-5-5 (ai) | The treatment of the compulsory maternity leave and of a work injury. | corrected | work_rules.insured_absence added from the articles cited in its provenance; statutory measures in absence/insured/rates.json (D.Lgs. 151/2001 artt. 22-23, D.P.R. 1124/1965 artt. 68, 73, 116-117). |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 15 punto 1 - Elementi della retribuzione; Art. 9). | corrected | Art. 15 punto 1 - Elementi della retribuzione; Art. 9: individual elements included in the hourly base: work_rules.time_supplements.individual_elements. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | A (Quadri) — QA/HSE/IT manager, senior scientist, plant manager, 1st grade | € 3,643.48 | 2028-06-01 |
| `A2` | A (Quadri) — laboratory manager, complex systems expert, 2nd grade | € 3,362.59 | 2028-06-01 |
| `A3` | A (Quadri) — area coordinator, department head, 3rd grade | € 3,292.22 | 2028-06-01 |
| `B1` | B — ISF, product manager, safety officer, 1st grade | € 3,048.98 | 2028-06-01 |
| `B2` | B — researcher, maintenance manager, senior programmer, 2nd grade | € 2,938.61 | 2028-06-01 |
| `C1` | C — shift supervisor, administrative coordinator, specialist technician, 1st grade | € 2,680.65 | 2028-06-01 |
| `C2` | C — specialist clerk, QC officer, senior accountant, 2nd grade | € 2,576.86 | 2028-06-01 |
| `D1` | D — team leader, senior multi-skilled operator, 1st grade | € 2,496.26 | 2028-06-01 |
| `D2` | D — distribution operator, QA inspector, 2nd grade | € 2,384.77 | 2028-06-01 |
| `D3` | D — clerical employee / multi-skilled worker, 3rd grade | € 2,318.76 | 2028-06-01 |
| `E1` | E — GMP production operator, 1st grade | € 2,204.28 | 2028-06-01 |
| `E2` | E — basic production operator, 2nd grade | € 2,085.14 | 2028-06-01 |
| `E3` | E — generic specialised operator, 3rd grade | € 2,010.29 | 2028-06-01 |
| `E4` | E — generic operator, 4th grade | € 1,959.04 | 2028-06-01 |
| `F` | F — simple executive and service duties | € 1,873.46 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "chimica-farmaceutica-federchimica/apprenticeship_minimo_without_ipo · base_salary · impact yes · open"
    APPRENTICESHIP (stesura 22/9/2012, art. 3 A, CNEL n. 468 pp. 16 and 22, unchanged by the later renewals): the contract of 6 months to 3 years is split in two halves; in the first the apprentice is one category below the destination, in the second at the destination, both paid the minimo contrattuale without IPO (nor EAR or EDR). The engine counts levels, not categories, pays the whole base_salary of a level and splits at fixed months, so no track is modelled and an apprentice run fails closed (no track).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model an under-classification by category paid at the minimo without IPO, with periods of half the contract duration.

!!! warning "chimica-farmaceutica-federchimica/excess_hours · overtime · impact yes · open"
    Art. 9 punto 1: the lavoro eccedente from 37h45 to 40 weekly hours at 5%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a band for the lavoro eccedente at 5%.

!!! warning "chimica-farmaceutica-federchimica/ordinary_hours_premiums · overtime · impact yes · open"
    Art. 9 punti 3-6, 9-11: the premiums on ordinary hours not yet modelled: night work outside shifts 50%, night shifts 34% and 46% (3x7), Sunday 3x7 33%, pluriperiodale and Saturday 10%, the first 120 hours past 2,024 a year 30%. The holiday premium (50%) and the day-shift premium (4%) are modelled (supplement_bands CHIM_FESTIVO, CHIM_TURNO_DIURNO) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the remaining Art. 9 premiums on ordinary hours.

!!! warning "chimica-farmaceutica-federchimica/night_shift_indemnity · base_salary · impact yes · open"
    Renewal of 2025, p. 47: the night-shift indemnity in cifra, outside the TFR base (EUR 13.50 per 8 hours, EUR 15.50 from 1/7/2027).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the night-shift indemnity per shift.

!!! warning "chimica-farmaceutica-federchimica/easter_and_sunday_holiday · base_salary · impact yes · open"
    Art. 12 and Art. 20: the Easter payment of 1/25 and the holiday falling on a Sunday at 1/25.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the Easter 1/25 and the Sunday holiday at 1/25.

!!! warning "chimica-farmaceutica-federchimica/participation_premiums · base_salary · impact yes · open"
    Artt. 48-50: the premio di partecipazione, the premio variabile and the elemento perequativo.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the premi of Artt. 48-50 with the employer facts they need.

!!! warning "chimica-farmaceutica-federchimica/una_tantum_withholding_2025 · base_salary · impact yes · open"
    Renewal of 2025, p. 45: the una tantum contribution of EUR 25 withheld in July 2025 from non-member workers.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the withholding of July 2025 for non-member workers.

!!! warning "chimica-farmaceutica-federchimica/overtime_base_and_categories · overtime · impact yes · open"
    The CCNL applies the overtime premiums to the art. 15 punto 1 elements, superminimi included, and categories A and B get none. The overtime bands are limited to levels F to C1 and the individual elements count in the hourly base; still open: the hourly quota of art. 20 excludes the EAR, which base_salary holds for category B, and the holiday and shift supplement bands apply to every level (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Exclude the EAR of category B from the hourly base and limit the supplement bands to the levels the CCNL pays them to.

!!! warning "chimica-farmaceutica-federchimica/edr_absences · base_salary · impact yes · open"
    The EDR is paid whatever the absences of the month and has no effect on other institutes, while the engine reduces it with the month and counts it in the sickness quota.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Keep the EDR whole in partial months and out of the sickness quota.

!!! warning "chimica-farmaceutica-federchimica/absence_hours · base_salary · impact yes · open"
    Absences are deducted at 1/175 an hour, a day taken as 8 hours whatever the company schedule.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Take the company daily schedule for the hours of an absent day.

!!! warning "chimica-farmaceutica-federchimica/sickness_scales_and_comporto · sickness · impact yes · open"
    Sickness: the scales of fixed-term contracts and apprentices (75/60/45/30 days in full, as many at half), the comporto 30% longer for disabled workers (L. 68/1999), the therapies of oncological and degenerative illnesses outside the comporto, the restart of an exhausted treatment on a hospital stay of more than 10 days; hospital stays are left out of the comporto over the whole window, the CCNL does it within one continuous event.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the fixed-term and apprentice scales and the comporto rules of the sickness article.

!!! warning "chimica-farmaceutica-federchimica/other_sector_tables · base_salary · impact yes · open"
    Scope: the tables of the Fibre, Abrasivi, Lubrificanti e GPL and Ceramica sectors differ and are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the tables of the other sectors.

!!! warning "chimica-farmaceutica-federchimica/rol_shift_workers · leave · impact yes · open"
    LEAVE, ROL OF THE TURNISTI (Art. 13 A): the turnisti 3x5 and 3x6 have 76 hours in the 2006 text (a secondary source states 88 under the current text, not verified on a primary text), the turnisti on a continuous cycle have no hour bucket (232.5 days a year) and the semicontinui on night shift 2 more rest days. The shift pattern is not an input: the engine accrues the 68 hours of the giornalieri and the turnisti 2x5 and 2x6.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source the current hours of the turnisti 3x5 and 3x6 and add the shift pattern as an employment fact.

!!! warning "chimica-farmaceutica-federchimica/injury_full_pay_periods · workplace_injury · impact yes · open"
    INSURED ABSENCES: compulsory maternity leave (top-up to 100% of the gross retribuzione globale di fatto for five months, Art. 41) and work injury (full net pay with the INAIL indemnity advanced, Art. 40 C) as work_rules.insured_absence. The full pay of an injury lasts three, four or five months by seniority and halves after: the engine tops up every injury day to 100%.

    **Applies when:** `workplace_injury` applies.

    **Remediation:** Count the injury days against the full-pay and half-pay periods of Art. 40 C, with the sickness of the same window.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filctemcgil.it/images/download/CONTRATTI/chimico_farmaceutico/250415-_CHIMICO-FARMACEUTICO_RINNOVO%20CCNL_%201-7-2025__30-6-2028.pdf | altro | 2025-04-15 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/chimico_farmaceutico/250415-_CHIMICO-FARMACEUTICO_RINNOVO%20CCNL_%201-7-2025__30-6-2028.pdf) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/178786 | cnel | 2024-01-08 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/178786) |
| https://www.filctemcgil.it/images/download/CONTRATTI/chimico_farmaceutico/180719_CHIMICO-FARMACEUTICO_RINNOVO%20CCNL_%202019-GIUGNO%202022.pdf | altro | 2018-07-19 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/chimico_farmaceutico/180719_CHIMICO-FARMACEUTICO_RINNOVO%20CCNL_%202019-GIUGNO%202022.pdf) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/579 | cnel | 2006-05-10 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/579) |

??? note "Coverage notes"
    SALARY MODEL: base_salary is the Trattamento Economico Minimo (minimo contrattuale + IPO of the position, art. 15 punto 1) plus, for categories A and B, the Elemento Aggiuntivo della Retribuzione (EUR 190 for A, EUR 100 for B since 1/7/2010, art. 15 B 3, renewal 19/7/2018 p. 14), which is in the TFR base. The Elemento Distinto della Retribuzione (art. 15 B 2) is the fixed allowance EDR from 1/7/2027 (A1 39, A2 34, A3 33, B1 32, B2 30, C1 28, C2 27, D1 26, D2 25, D3 24, E1 22, E2 20, E3 19, E4 19, F 18; 2025 renewal p. 49), outside the TFR base ('ivi compreso il Trattamento di fine rapporto').
    
    SOURCES: tables of the ipotesi di rinnovo 15/4/2025 (signed scan published by FILCTEM-CGIL, pp. 46-49, read by OCR and on the page images; the same text is deposited at CNEL n. 221298); the TEM of 1/7/2024 from the Intesa 8/1/2024 (CNEL n. 178786, p. 2); the rules from the testo definitivo 10/5/2006 (CNEL n. 579), the latest full text public, with the renewals of 2009, 2015, 2018, 2022 and 2025.
    
    MODELLED TRANCHES: 1/7/2024 (Intesa 8/1/2024, in force until the first tranche of the 2025 renewal: the June 2025 tranche of the 2022 renewal is paid with July 2025, 2025 renewal p. 46), 1/7/2025, 1/12/2025, 1/7/2026, 1/7/2027 and 1/6/2028 (2025 renewal p. 48).
    
    IPO VARIES BY TRANCHE: the IPO of each position takes its own increments at every tranche (2025 renewal p. 48); the table reconciles with the increments for all 15 levels.
    
    SENIORITY INCREMENTS abolished from 1 January 2010 (renewal 18/12/2009 p. 37); the amounts accrued by 31/12/2009 are a frozen, non-absorbable personal element, passed as Employment.individual_elements (IndividualElement with absorbable false). maximum_count=0 and amount_by_level={}.
    
    HOURLY DIVISOR: 175 (art. 20 punto 4). The 173 divisor applies only to Ceramica e Abrasivi.
    
    ADDITIONAL MONTHS: 13, the tredicesima paid on Christmas Eve (art. 21). The quattordicesima of the Lubrificanti e GPL sectors is outside this file.
    
    INPS: tax_sector industria (CNEL B011, ATECO C20 and C21).
    
    FONCHIM: employer 2.35% of the TFR base (2.10% plus the 0.25% insurance contribution) and worker minimum 1.20%, from the fund's opuscolo 2026; from 1/1/2027 the employer rate is 2.3% (2025 renewal p. 47), 2.55% with the insurance share (derived).
    
    HOURLY RATE AND SUPPLEMENTS (artt. 9, 15 punto 1, 20 of the 2006 text): without a caller value the engine derives the hourly base (minimo + IPO + scatti over 175), the 50% on holiday hours (art. 9 punto 3) and the 4% on rotating day shifts (punto 5 a). Not derived, the caller states the amount: ordinary night work of non-shift workers (50%, punto 4), whose 9-hour window the company fixes between 20 and 8 (art. 8 H); Sunday work (50% with compensatory rest, 33% for 3x7 continuous cycles under punto 6, a fact the request does not carry); night shifts (34%, 46% for 3x7, punto 5 b-c), because the fixed amount per 8 hours of art. 9 H in force after the 2022 renewal is unconfirmed (6.50 EUR from 2007, 13.50 from 1 April 2019, 15.50 from 1 July 2027). Art. 9 does not say whether the holiday hours themselves are paid on top of the monthly pay: a derived holiday supplement is provisional. Not modelled: the 5% on hours 37h45m to 40 and the 30% beyond 2,024 annual hours (punti 1 and 11). Absences: art. 20 punti 2-3 deduct 1/175 of the same elements per hour, but work_rules.absence_rules stays derived (its 8-hour day is not in the text), so the engine derives no absence deduction: the caller states AbsenceEvent.hourly_rate.
    
    LEAVE AT TERMINATION (Art. 14): the indemnity is the 'retribuzione globale di fatto in atto al momento della liquidazione' for the days of ferie not taken; its daily divisor is not stated in the text read, so the engine pays no residual (termination_residual_leave incomplete). The ferie taken in excess are repaid (not modelled); Art. 13 sets no deadline for the residual ROL and ex festività.
    

## Raw data

The contract file this page is generated from: [`agreement/chimica-farmaceutica-federchimica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/chimica-farmaceutica-federchimica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/chimica-farmaceutica-federchimica/example.py"
```
