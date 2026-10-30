# CCNL per i dipendenti degli studi e delle attività professionali (Confprofessioni)

| | |
|---|---|
| **CNEL code** | `H442` |
| **Sector** | terziario |
| **Family** | `servizi-professionali` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-02-16 |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Confprofessioni
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, seniority, sickness |

13 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 51 verified / 0 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-02-16 |
| **Last review** | 2026-10-20 |
| **Latest salary tranche** | 2026-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the file read again in the CCNL of 16 February 2024 (integrale definitivo, 78 pages) and in its April 2026 testo ufficiale for Allegato B, with the D.I. of 21 May 2024 and the INPS circulars for the solidarity fund. | corrected | 60 records verified; the three document ids of the file are now one (ccnl-studi-professionali-2024-02-16), plus the 2026 testo ufficiale for Allegato B. The served integrale has sha256 89c22bb2..., not the hash recorded before.<br>Weekday overtime 15%, not 25%, and night overtime 30%, not 40% (Art. 95, p. 49), on the normale retribuzione of Art. 135 (hourly_base_method gross_incl_allowances).<br>Sickness: 75% for days 4-20 and 100% from day 21 (Art. 121), not a flat 75%.<br>Apprenticeship: Quadri are a destination of the professionalizzante (Allegato B Tabella 2, 30 months); split by duration (30 and 36 months); added the primo livello (45/55/65%) and alta formazione (40/50/60%) tracks. The limitation uniform_apprenticeship_percentages is closed: Tabella 3 is one table for every profile.<br>Added Fon.Te. (Art. 18: 1.55% employer, 0.55% worker minimum of the TFR base) and the payment day of the tredicesima (Art. 142).<br>INPS: the sector pays the Fondo di solidarietà per le attività professionali, not the FIS, and no CIGS: the terziario tier above 15 employees overcharges; declared as fsbap_rates_above_15.<br>Unmodelled clauses declared in one note (studi_unmodelled_elements); apprentice_seniority rewritten on Art. 129.<br>No renewal after 16 February 2024 found through October 2026 (the CCNL runs to 15 February 2027); the CNEL archive was not reachable. |
| 2026-10-13 | claude-opus-5-5 (ai) | Readiness of the file after the limitations gained a headcount scope. | confirmed | The INPS gap above 15 employees (fsbap_rates_above_15) is now recorded on every run of an employer with more than 15 employees (applies_when headcount_from 16): up to 15 employees the terziario rates coincide with the solidarity fund of the studi professionali, so the file moves to production. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-01: the minimi tabellari of every level and tranche, the scatti, the ENAC, the divisor and the extra months against the CCNL of 16 February 2024, the solidarity fund against the D.I. of 21 May 2024, and a year and a termination of a 4th level worker against a hand oracle. | confirmed | The 32 minimi of Art. 140 (eight levels, tranches of March 2024, October 2024, October 2025 and December 2026, pp. 71-72) match the file.<br>Scatti of Art. 134 (p. 68): eight triennial increments, Quadri 30, I 26, II 23, III Super and III 22, IV Super, IV and V 20. Match.<br>ENAC of Art. 141 (p. 73): 42,35 at the I, 102,53 at the II and 110,40 at the III Super level. Match.<br>Tredicesima at Christmas (Art. 142) and quattordicesima by 30 June of the pay in force on that date (Art. 143), both in twelfths for a hire within the year. Match with the fourteen payments of the file.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios studi-year and studi-june): a 4th level impiegato hired on 1 January 2026 by an employer with 10 employees; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent.<br>fsbap_rates_above_15 stays open: up to 15 employees the terziario rates equal the 0.80% of the solidarity fund (D.I. 21 May 2024 art. 6 c. 1 lett. b), above 15 they need a contribution sector of their own, an engine change outside this review.<br>bilateral_contribution_or_element stays open: the per-worker amount of Art. 13 needs an employer fact for the alternative element; it remains an owed amount on every run. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | confirmed | hourly_base_method gross_incl_allowances (was gross_incl_allowances), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: STUDI_FESTIVO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The bilateral contribution of Art. 13 (CADIPROF, EBIPRO and the element owed outside the bilateral system) against the CCNL of 16 February 2024, and the Fondo di solidarietà bilaterale per le attività professionali against the D.I. of 21 May 2024 art. 6 and INPS circ. 5/2025. | corrected | Art. 13 (p. 8): from March 2024 a unified contribution of 29 EUR a month for 12 months, 2 EUR of the worker, in full for part time: 20 EUR to CADIPROF, 7 + 2 EUR to EBIPRO. Modelled as the contractual funds cadiprof (health fund, 10% INPS solidarity) and ebipro; the owed limitation bilateral_contribution_or_element removed.<br>Art. 13 (p. 8): an employer outside the bilateral system owes 43 EUR for 14 months, in every institute including the TFR, not reproportioned for part time. Modelled as the element of cadiprof, which ebipro shares (alternative_in).<br>D.I. 21 May 2024 art. 6 c. 1 (pp. 6-7): 0.50% up to 5, 0.80% from 6 to 15, 1% above 15 employees, two thirds employer, on the INPS taxable pay. Modelled as a solidarity fund whose tier replaces the FIS and CIGS shares of the terziario rates; up to 15 employees they coincide, above 15 the worker pays 9.52% and the employer 29.65%. The owed limitation fsbap_rates_above_15 removed.<br>Art. 6 c. 4 and INPS circ. 5/2025 p. 3: the 0.50% falls to 0.30% for an employer without claims for 24 months, the same cut the terziario rates carry for the FIS (EmployerProfile.fis_reduction). |
| 2026-10-20 | claude-opus-5-5 (ai) | The renewal within the window of L. 199/2025 art. 1 c. 7 and the minimo in force before its first tranche. | corrected | Renewal signed on 2024-02-16, first tranche from 2024-03-01: parameters.renewals.<br>Minimo before the renewal = the column 'Minimo tabellare in vigore al 29 febbraio 2024' of the first tranche (Q 2,133.31 to 5 1,315.12). |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Art. 134 - Scatti di anzianità). | corrected | Art. 134 - Scatti di anzianità (p. 69): the earlier increments take the amounts of the new level from the change: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 135 - Normale retribuzione; Art. 95). | corrected | Art. 135 - Normale retribuzione; Art. 95: individual elements included in the hourly base: work_rules.time_supplements.individual_elements. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Manager (Quadro) — staff with managerial functions (Art. 2095 c.c., L. 190/1985) | € 2,436.76 | 2026-12-01 |
| `1` | 1st Level — staff with directive functions or highly specialised technical role | € 2,156.38 | 2026-12-01 |
| `2` | 2nd Level — senior concept-grade staff / highly specialised technicians | € 1,878.26 | 2026-12-01 |
| `3S` | 3rd Level Super — senior concept-grade staff with specialised expertise | € 1,742.20 | 2026-12-01 |
| `3` | 3rd Level — concept-grade staff with technical or administrative expertise | € 1,726.37 | 2026-12-01 |
| `4S` | 4th Level Super — qualified staff with higher-grade duties | € 1,674.10 | 2026-12-01 |
| `4` | 4th Level — qualified clerical staff | € 1,614.12 | 2026-12-01 |
| `5` | 5th Level — clerical staff performing routine tasks | € 1,502.19 | 2026-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.00 |
| `1` | € 26.00 |
| `2` | € 23.00 |
| `3S` | € 22.00 |
| `3` | € 22.00 |
| `4S` | € 20.00 |
| `4` | € 20.00 |
| `5` | € 20.00 |

## Apprenticeship

**professionalizzante_30** (type: `percentage`)  
Destination levels: `Q`, `1`, `2`  
percentage: 0.93

**professionalizzante_36** (type: `percentage`)  
Destination levels: `3S`, `3`, `4S`, `4`  
percentage: 0.93

**qualifica_diploma** (type: `percentage`)  
Destination levels: `Q`, `1`, `2`, `3S`, `3`, `4S`, `4`, `5`  
percentage: 0.65

**alta_formazione_ricerca** (type: `percentage`)  
Destination levels: `Q`, `1`, `2`, `3S`  
percentage: 0.60

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "studi-professionali-confprofessioni/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: Art. 129 CCNL 2024 (p. 68) applies the scatti of Art. 134 to apprentices from the hiring date, and Art. 28 I counts the apprenticeship for seniority; the text does not say whether the amount is the one of the destination level. The engine pays no scatto during the apprenticeship (apprentice_amount is one series, not per level). Only an apprenticeship prolonged under Art. 28 I past 36 months of service reaches a scatto (EUR 20-30).

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Let seniority_increments pay the level amount to apprentices (a flag such as apprentices_accrue_level_amount), then remove this note.

!!! warning "studi-professionali-confprofessioni/six_day_week_leave · leave · impact unknown · open"
    LEAVE: 22 working days for the settimana corta (Monday to Friday), 26 for a six-day week (Art. 99 CCNL 2024, p. 51). The file carries the 22 days; the engine cannot switch on the weekly schedule.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Accept the weekly schedule (days per week) and accrue 26 days on a six-day week, or record the limitation as rol_not_accrued does for ROL.

!!! warning "studi-professionali-confprofessioni/part_time_supplementary · overtime · impact yes · open"
    Art. 42: the lavoro supplementare of part-time at 40% of the quota oraria of the retribuzione di fatto, outside the deferred institutes and the TFR. OvertimeKind.SUPPLEMENTARY exists, but the file has no supplementary-hours band (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the OT_SUPPLEMENTARE band (40%) of Art. 42.

!!! warning "studi-professionali-confprofessioni/rolling_comporto_and_serious_illness · sickness · impact yes · open"
    Artt. 120-121: the comporto counted over the episodes of the 365 days before the last one, and the +90 days for serious illnesses paid 100% in months 7-8 and 70% in month 9.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the rolling comporto and the serious-illness extension.

!!! warning "studi-professionali-confprofessioni/holiday_during_sickness · sickness · impact yes · open"
    Art. 124: the 100% of festività during sickness.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the festività during sickness at 100%.

!!! warning "studi-professionali-confprofessioni/injury_integration · sickness · impact yes · open"
    Art. 123: the infortunio integration (100% on the day of the event, 60% days 1-3, 75% after).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the injury integration.

!!! warning "studi-professionali-confprofessioni/maternity_holiday_top_up · base_salary · impact yes · open"
    Art. 110 c. 8: the employer top-up to 100% of the holidays during compulsory maternity or paternity leave.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the top-up of Art. 110.

!!! warning "studi-professionali-confprofessioni/unused_leave_hours · base_salary · impact yes · open"
    Artt. 91, 92, 97 C, 98: the ROL (40 or 66 hours) and the 32 hours of ex festività paid when not taken, the festività falling on Sunday and the flexibility hours not recovered.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the unused ROL, ex festività and flexibility hours.

!!! warning "studi-professionali-confprofessioni/reemployment_entry_pay · base_salary · impact yes · open"
    Art. 56: the salario d'ingresso of the reimpiego, up to two levels below for 9 months and one for 6.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the entry pay of the reimpiego.

!!! warning "studi-professionali-confprofessioni/intermittent_availability · base_salary · impact yes · open"
    Art. 58: the indennità di disponibilità of the lavoro intermittente, 30%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the availability allowance.

!!! warning "studi-professionali-confprofessioni/travel_diaria · base_salary · impact yes · open"
    Art. 115: the diaria of the trasferte, EUR 15 or 30 a day.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the trasferta diaria.

!!! warning "studi-professionali-confprofessioni/fourteenth_exclusion · base_salary · impact yes · open"
    Art. 143: the exclusion of the quattordicesima for workers already paid extra months. The una tantum of EUR 400 (EUR 200 in May 2024 and May 2025, p. 73) is historic and outside the TFR base.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a worker fact for extra months already paid.

!!! warning "studi-professionali-confprofessioni/rol_not_accrued · leave · impact yes · open"
    LEAVE, ROL (Art. 91 cc.2-3): 40 hours a year on a five-day week, 66 on a six-day week, and for the hires under the 2024 CCNL 50% from the twelfth month, 75% from the twenty-fourth to the thirty-sixth, 100% after; the text is silent on the first twelve months. The weekly schedule is not an input and the first year is not sourced: the ROL is not accrued, and a leave taken from it is not decided.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the weekly schedule as an employment fact and source the first twelve months of the new-hire ramp.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato of a month not worked in full without the pay of a whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| https://confprofessioni.eu/wp-content/uploads/2025/11/CCNL-Studi-2024-integrale-definitivo.pdf | altro | 2024-02-16 | [↗](https://confprofessioni.eu/wp-content/uploads/2025/11/CCNL-Studi-2024-integrale-definitivo.pdf) |
| https://www.confprofessioni.eu/wp-content/uploads/2026/07/00274046_CCNL_Studi_Professionali_2026.04.10_completo.pdf | altro | 2024-02-16 | [↗](https://www.confprofessioni.eu/wp-content/uploads/2026/07/00274046_CCNL_Studi_Professionali_2026.04.10_completo.pdf) |

??? note "Coverage notes"
    CONGLOBATED MINIMUMS: the minimo tabellare includes the contingenza (up to 01/05/1992) and the EDR (Interconfederal Agreement 31/07/1992), merged under CCNL 10/12/1992 and reaffirmed by Art. 138 CCNL 2024. The only fixed allowance is the ENAC of levels 1, 2 and 3S (Art. 141), gated by a role.
    
    HOURLY DIVISOR: 170, daily divisor 26 (Art. 137 CCNL 2024: 'dividendo l'importo mensile per il divisore convenzionale 170'; Art. 45 for part-time).
    
    TRANCHES: four tranches, 01/03/2024, 01/10/2024, 01/10/2025, 01/12/2026 (Art. 140 CCNL 16/02/2024, tables pp. 71-73 of the integrale; the April 2026 testo ufficiale reproduces them). The CCNL runs to 15/02/2027.
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 142 + quattordicesima Art. 143 CCNL 2024).
    
    SENIORITY INCREMENTS: triennial (36-month cadence), max 8 increments. Fixed amounts per Art. 134 CCNL 2024 in force from 01/10/2011: Q=30, 1=26, 2=23, 3S=22, 3=22, 4S=20, 4=20, 5=20.
    
    ENAC (Art. 141 CCNL 2024): EUR 42.35 (level 1), EUR 102.53 (level 2), EUR 110.40 (level 3S) a month, only for the workers formerly under the Confedertecnica CCNL; the hires from 01/07/2004 get the minimi alone (p. 73). Modelled as an allowance with role 'confedertecnica_pre_2004' (compute(..., roles={'confedertecnica_pre_2004'})).
    
    APPRENTICESHIP (Artt. 28-31 and Allegato B CCNL 2024, read in the April 2026 testo ufficiale, PDF pp. 143-144): professionalizzante 70% months 1-12, 85% months 13-24, 93% after, of the minimo of the destination level, one table for every profile; 30 months for Q, 1, 2 (track professionalizzante_30) and 36 months for 3S, 3, 4S, 4 (professionalizzante_36); level 5 excluded (Art. 30 B). Primo livello (qualifica_diploma, every level): 45%, 55%, 65%. Alta formazione e ricerca (alta_formazione_ricerca, Q, 1, 2, 3S): 40%, 50%, 60%. The last band of each track is open-ended: the apprenticeship is prolonged by absences over 30 days (Art. 28 I). A level covered by several tracks needs Apprentice.track.
    
    SOLIDARITY FUND: the studi professionali pay the Fondo di solidarietà bilaterale per le attività professionali (D.I. 21 May 2024 art. 6) in place of the FIS and owe no CIGS (D.Lgs. 148/2015 art. 20 c. 3-bis): parameters.solidarity_fund replaces the FIS and CIGS shares of the terziario rates with the thirds of 0.50%, 0.80% and 1% by headcount. Up to 15 employees the rates coincide; above 15 the employer pays 0.46 points and the worker 0.24 points less than the terziario rates.
    
    CNEL code H442: confirmed from the CNEL archive 'Studi Professionali — Confprofessioni'. Workers covered: 317,554 (UNIEMENS 2022).
    
    BILATERAL CONTRIBUTION: EBIPRO and CADIPROF are paid with a unified contribution of EUR 29 a month for 12 months, EUR 2 of it by the worker (Art. 13), modelled as the contractual funds cadiprof (20 EUR, health fund) and ebipro (7 + 2 EUR); an employer outside the bilateral system owes the worker 43 EUR for 14 months instead. The CADIPROF enrolment of EUR 24 (Art. 16) stays a caller BilateralFundEvent.
    
    HOURLY RATE AND SUPPLEMENTS (artt. 93-97, 135, 137 of the CCNL of 16 February 2024): without a caller value the engine derives the hourly base (the art. 135 normale retribuzione over 170) and the 30% on festività hours paid as straordinario festivo (art. 97 lett. E with art. 95); art. 97 also pays the hours themselves, which the engine does not post: the run is provisional. Not derived, the caller states the amount: ordinary night work, which art. 93 leaves to the Area Professionale or second-level bargaining (the 30% of art. 95 is a night overtime rate); work on the weekly rest day ('la relativa sola maggiorazione', art. 97 lett. F, names no percentage).
    
    LEAVE AT TERMINATION (Art. 101): the ferie are paid at the 'normale retribuzione di fatto' during the leave; no clause states the basis of the indemnity at the end of the employment, so the engine pays no residual (termination_residual_leave incomplete).
    

## Raw data

The contract file this page is generated from: [`agreement/studi-professionali-confprofessioni.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/studi-professionali-confprofessioni.json).

## Usage example

```python
--8<-- "docs/examples/agreement/studi-professionali-confprofessioni/example.py"
```
