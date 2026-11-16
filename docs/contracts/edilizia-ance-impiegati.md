# CCNL Edilizia — Industria (ANCE), impiegati e quadri

| | |
|---|---|
| **CNEL code** | `F012` |
| **Sector** | edilizia |
| **Family** | `edilizia` |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-02-21 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCE
    - Legacoop Costruzioni
    - Confcooperative Lavoro e Servizi
    - AGCI
    - Fillea-CGIL
    - Filca-Cisl
    - Feneal-Uil

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime, seniority, sickness, territorial_supplement |

10 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 44 verified / 23 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-11-09 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the impiegati and quadri read in the ANCE minimi table of the CCNL of 21 February 2025, the CCNL of 19 April 2010 (FILLEA text), the Art. 92 apprenticeship text of 2019 and the ANCE provincial tables, for the production tier; new file split from edilizia-ance. | corrected | 47 records verified, 19 derived (contingenza, EDR, contractual fund, absence quota, seniority of levels 1-2, payment day of the premio annuo).<br>Split by category (Art. 77): the operai of levels 1-4 in edilizia-ance, the impiegati and quadri of levels 1-7 in edilizia-ance-impiegati.<br>base_salary is now the national minimo of the ANCE table; the ex contingenza and the EDR 10.33 are fixed allowances (derived, ANCE provincial tables), the EDR outside the TFR base. The previous consolidated values (minimo + contingenza + EDR) matched.<br>Aggregator sources (idealista, leggeinchiaro, businessonline, kitech) removed.<br>Absence quota: by_hourly 8 hours (1/173 of Art. 44 and Allegato A), not by_26, which no clause supports.<br>contractual_fund_uncovered closed: every operaio level has an hourly Prevedi amount and every impiegato or quadro level a monthly one.<br>No renewal changing the national minimi after the verbale of 21 February 2025 through October 2026.<br>Fourteen monthly payments: tredicesima (Art. 63, 20 December) and premio annuo (Art. 64, 30 June, stored 28 June).<br>Night overtime 47% (Art. 54), not the 40% of the operai.<br>Seniority 8.20 for levels 1-2 (printed 'Imp. 4ª 8,2'), not 8.22: derived.<br>Quadri indennità di funzione EUR 140 (Art. 76) added.<br>Sickness: 100% for 180 days without INPS (Art. 66 band up to two years); the longer bands declared. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | edilizia_impiegati_sickness (the art. 66 treatment beyond two years of service) is recorded on every sickness run of a worker with 24 months of seniority or more, or of unknown seniority. |
| 2026-10-17 | claude-opus-5-5 (ai) | A year and a termination of an impiegato of the 3rd level against a hand oracle, and the 23 derived rules of the file. | corrected | Engine corrected: at a termination the June pay settles the ratei of the tredicesima; the Prevedi contributo contrattuale, 'applicato anche per 13° e 14° mensilità', was not charged on them (6,50 EUR and its 10% solidarity contribution short), while an extra-month run of the same ratei charges it. The settled ratei now owe it (tests/mutation/ccnl_engine/pension_fund/services/test_prevedi.py::test_a_termination_owes_the_ratei_it_settles).<br>Engine corrected: the ratei settled at a termination entered the TFR base whole, the EDR included, while the EDR stays out of the TFR base in the monthly pay and in an extra-month run (0,38 EUR of TFR too much here). The settled ratei now leave out the allowances outside the TFR base.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios edilizia-impiegati-year and edilizia-impiegati-june): an impiegato of the 3rd level hired on 1 January 2026 by an employer with 30 employees, across the tranche of March 2026; after the two corrections every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done.<br>The 23 derived rules stay derived: the contingenza and EDR of each level (14) are read from the ANCE provincial tables, not tabulated in the CCNL; the Prevedi amounts are rebuilt from two verbali and the fund scheda; two scatti differ between the table (8,2) and the secondary tables (8,22); the payment day of the quattordicesima and the absence divisor are stated transformations. No signatory text states them directly. |
| 2026-11-02 | claude-opus-5-5 (ai) | The premiums on ordinary hours of Art. 54 (PDF p. 71) and their base of Art. 44 (pp. 66-67). | corrected | Art. 54: supplement_bands ANCE_IMP_* (night 34%, night in periodic shifts 10%, festivo 45%); festivo notturno 50% left as the narrowed limitation.<br>Art. 44 points 1-6, 8, 9 over 173: hourly_base_provenance verified, individual elements included (point 3).<br>A separate session without the reasoning of the extraction re-read art. 54 (p. 71) and art. 44 (pp. 66-67) on the PDF and confirmed the table (34%, 10%, 45%, festivo notturno 50%), the elements 1-6, 8, 9 and the divisor 173; it found the EDR named in neither article: its place in point 9 stays a reading. |
| 2026-11-02 | claude-opus-5-5 (ai) | Art. 54 (PDF p. 71). | corrected | Art. 54 (p. 71): 'lavoro festivo notturno escluso quello compreso in turni periodici' 50%, confirmed by a separate session without the reasoning of the extraction; no other row covers ordinary night holiday work, and none gives the rate of the periodic shifts it excludes (kept as the ordinary_hours_premiums limitation). |
| 2026-11-08 | gpt-6-sol (ai) | Art. 92 in the ANCE text of 4 April 2019 (pp. 4-8), applied to contracts from 1 April 2019. Final encoding (dual_apprenticeship JSON) checked against the PDFs by a separate model session (.private flv2). | flagged | Semesters, conventional levels 2 and 1 and the third-level table match. The base also names the premio di produzione and the elemento variabile, which the bundle does not hold (limitations provincial_production_premium and provincial_evr).<br>A failed-title prorogation keeps the pay of the previous year (p. 6): recorded as dual_apprenticeship_prorogation.<br>Ambiguous in the text, kept as read: the base of the 10% training share ('di quella che gli sarebbe dovuta'). |
| 2026-11-08 | gpt-6-sol (ai) | Art. 66 of the CCNL edilizia industria 2010 (PDF p. 78). A separate model session rejected a first encoding (pay counted over the 30-month window); the merged per-illness encoding was checked again by a separate session (.private flv2), which confirmed the bands and kept the three extra months of several illnesses as unmodelled. | flagged | Replaced the six-month rule with the seniority bands of one illness and the 30-month comporto of art. 66.<br>The separate session read the 30-month periods as job retention only: the pay of the three extra months of several illnesses is left as a limitation. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 43 (PDF p. 66) and art. 61 (PDF p. 75) of the CCNL 19 April 2010, the renewals of 2014, 2018, 2022 and 2025 for amendments, and the Sunday-holiday code of the engine, by a separate model session. | flagged | Confirmed: the quota of '11-04' at 1/25 is paid on the first Sunday of every November, a second quota when 1 November is that Sunday (art. 61 and art. 43); no renewal amends art. 43.<br>Flagged, kept under november_4_holiday: a worker not employed on the first Sunday of November gets no quota; the 'retribuzione stessa' is read as the monthly pay of the chain. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 65, 44, 63, 72 and 76 of the CCNL 19 April 2010 against the loyalty premium encoding, by a separate model session. | flagged | Confirmed: one month of the art. 44 elements 1-15 on the hire anniversary after 20 years of uninterrupted actual service, then every year; impiegati and quadri (art. 76, with the function allowance); in the TFR base (art. 72); out of the 13th (art. 63, item 18 of art. 44).<br>Flagged, kept in the limitation loyalty_premium: the run chain stands for the elements 1-15, the employment start for the qualifying service, the anniversary month for the date; the pro rata at a non-disciplinary dismissal is not paid. |
| 2026-11-09 | gpt-6-sol (ai) | Art. 92 (PDF pp. 4-6), extension of a first-level apprenticeship after a failed qualification, by a separate model session. | corrected | Confirmed: the employer may extend the contract up to one year; only when the title is not obtained does the pay stay at the previous contract year (p. 6).<br>Confirmed: the previous year is read by semester (85% at month 36, 90% at month 42 for the qualifica track).<br>Corrected: an extension starting before the end of the original contract of the track (p. 4) was accepted and could underpay; it is now rejected. |
| 2026-11-09 | gpt-6-sol (ai) | Art. 50 (PDF p. 70), cash-handling allowance, and arts. 44, 47, 52, 63-64, 76 for the remaining limitations, by a separate model session. | confirmed | Confirmed: 8% of the monthly minimum and the ex-contingenza for an impiegato who normally handles money with liability for errors; no allowance without the attested role.<br>Confirmed: the allowance enters the thirteenth and the annual premium (art. 44 item 12, arts. 63-64).<br>Flagged: 1 February 2025 is the first salary tranche in the data, not the clause start; earlier eligibility is not encoded.<br>Confirmed: the art. 47, art. 52, art. 76 and provincial premium limitations stay open. |
| 2026-11-09 | gpt-6-sol (ai) | Art. 54 (PDF p. 71), night-holiday work in periodic shifts against the 50% band, by a separate model session. | corrected | Confirmed: the 50% night-holiday band excludes the hours comprised in periodic shifts; ordinary holiday and other bands are unaffected.<br>Flagged and corrected: an excluded hour is now provisional, not final at zero, since no combined night-holiday periodic-shift rate is printed; the 10% night-shift band of the same page stays as encoded.<br>Confirmed: a missing in_periodic_shift fact blocks only the restricted band. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7` | Livello 7: quadri e impiegati di 1a categoria super (art. 77) | € 2,334.71 | 2027-03-01 |
| `6` | Livello 6: impiegati di 1a categoria (art. 77) | € 2,101.23 | 2027-03-01 |
| `5` | Livello 5: impiegati di 2a categoria (art. 77) | € 1,751.02 | 2027-03-01 |
| `4` | Livello 4: impiegati di quarto livello (art. 77) | € 1,634.31 | 2027-03-01 |
| `3` | Livello 3: impiegati di 3a categoria (art. 77) | € 1,517.56 | 2027-03-01 |
| `2` | Livello 2: impiegati di 4a categoria (art. 77) | € 1,365.81 | 2027-03-01 |
| `1` | Livello 1: impiegati di 4a categoria primo impiego (art. 77) | € 1,167.36 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.20 |
| `2` | € 8.20 |
| `3` | € 8.99 |
| `4` | € 9.62 |
| `5` | € 10.46 |
| `6` | € 12.85 |
| `7` | € 13.94 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6`, `7`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-ance-impiegati/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "edilizia-ance-impiegati/edilizia_impiegati_sickness · sickness · impact yes · open"
    SICKNESS (Art. 66, PDF p. 78): the employer pays the elements 1-10 of Art. 44 (INPS pays no indemnity to the impiegati of industry). Modelled per illness: up to two years of seniority six months in full; from two to six years nine months, the last three at 50%; over six years twelve months, three at 75% and three at 50%; several illnesses or relapses keep the job 9, 12 or 15 months in 30. Not modelled: the pay of the three extra months of several illnesses ('intero trattamento economico per il primo mese e del 50% per i mesi restanti'): the text does not say whether they follow the aggregate of the illnesses or each illness's own period, so each illness takes its own schedule.

    **Applies when:** `sickness` applies.

    **Remediation:** Settle how the three extra months of art. 66 are counted across illnesses, then pay them.

!!! warning "edilizia-ance-impiegati/provincial_evr · territorial_supplement · impact yes · open"
    Art. 46: the EVR set by the provincial agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial EVR as an input.

!!! warning "edilizia-ance-impiegati/loyalty_premium · base_salary · impact yes · open"
    Art. 65: the annual loyalty award is paid on the hire-anniversary month after 20 years of uninterrupted actual service, using the run-chain monthly pay as an approximation of Art. 44 items 1-15. Not modelled: the whole-month twelfths due after a non-disciplinary dismissal, conventional seniority and interruptions or group-company service not represented by the hire date, and the exact Art. 44 elements (including territorial and individual components) actually summed in the award.

    **Applies when:** `base_salary` applies; category in impiegato, quadro; seniority of at least 240 months.

    **Remediation:** Represent qualifying actual service and the Art. 44 items 1-15 individually, and pay whole-month twelfths on eligible non-disciplinary dismissal.

!!! warning "edilizia-ance-impiegati/special_allowances · base_salary · impact yes · open"
    Artt. 47 and 52: the 25% special allowance for directors with responsibility for a company or department also depends on the unmodelled provincial production premium (and the option to deduct it from a superminimo set for those duties); the mountain and compressed-air caisson treatment depends on the operai's territorial rates; the EUR 25.82 monthly tunnel allowance is absorbed by same-purpose payments and by existing superminimi not granted for merit or another specific reason. Art. 50 cash handling with liability for errors is paid at 8% of minimum plus ex-contingenza when the role is attested.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source the provincial production premium and the operai's rates, and represent the specified superminimo absorption before paying the remaining allowances of Artt. 47 and 52.

!!! warning "edilizia-ance-impiegati/provincial_meals_transport_travel · territorial_supplement · impact yes · open"
    Mensa, trasporto and trasferta, set by the provincial agreements (verbale 2025).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial mensa, trasporto and trasferta as inputs.

!!! warning "edilizia-ance-impiegati/november_4_holiday · base_salary · impact yes · open"
    Art. 43: the 1/25 for the festività of 4 November is paid with every November pay, as the quota of '11-04' on the first Sunday of November (work_rules.sunday_holidays, divisor 25), in addition to a holiday of art. 61 on the same Sunday. Approximated: the text owes it 'per il mese di novembre'; the engine pays it to a worker employed on the first Sunday of November, not to one hired after it or leaving before it.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the 1/25 of art. 43 to every impiegato employed in November, whatever the first Sunday.

!!! warning "edilizia-ance-impiegati/quadri_absorption · base_salary · impact yes · open"
    Art. 76: the absorption of a superminimo into the quadri function allowance. The una tantum premio di ingresso of the verbale of 3 March 2022 and the riduzione contributiva edile concern the operai only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the absorption of Art. 76.

!!! warning "edilizia-ance-impiegati/provincial_production_premium · territorial_supplement · impact yes · open"
    PREMIO DI PRODUZIONE: the premio di produzione set by the provincial agreements (Art. 44 n. 5) is owed to every impiegato; the engine reads no provincial agreement. Not modelled: the net pay and the employer cost are short of it.

    **Applies when:** `territorial_supplement` applies.

    **Remediation:** Model the provincial premio di produzione with a fact naming the province, then remove this note.

!!! warning "edilizia-ance-impiegati/ordinary_hours_premiums · overtime · impact yes · open"
    Art. 54 excludes turnisti from the 50% night-holiday band; this exclusion is enforced. The same page states a 10% premium for night work in periodic shifts, covered by the existing ANCE_IMP_TURNO_NOTTURNO night_shift band (requested separately). No distinct combined night-holiday periodic-shift rate or stacking rule is stated: zero under the excluded 50% band is provisional, not total remuneration.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Determine whether the existing 10% periodic night-shift rate applies to these hours and how it combines with holiday pay before settling total remuneration.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

!!! warning "provisional_ruleset · irpef · impact unknown · awaiting_publication"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · awaiting_publication"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

!!! note "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · resolved"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8 and no Fondo di garanzia exemption: the 10% apprentice rate of L. 296/2006 art. 1 c. 773 is split by the D.M. 28 marzo 2007 among FPLD 9.01, CUAF 0.11, malattia 0.53, maternità 0.05 and INAIL 0.30, with no Fondo di garanzia share to exempt.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the apprentice rate holds no Fondo di garanzia share, so none is exempted.

!!! note "maternity_daily_base · maternity_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! note "paternity_daily_base · paternity_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! note "parental_daily_base · parental_leave · impact unknown · resolved"
    The INPS indemnity of the leave is computed on the pay of the month before, as the sickness base (art. 23 D.Lgs. 151/2001): an operaio's pay over the days worked or paid with the monthly share of the extra months over 25, a month not worked in full over its days worked or paid; the pay of the month before, its days and the pay of a whole month are facts of the leave, missing when not stated. The run keeps its own pay only when the category or the monthly payments of the CCNL are unknown.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the base of an operaio and of a partial month is the sickness base of the month before.

!!! warning "parental_income_condition · parental_leave · impact unknown · awaiting_publication"
    The days of parental leave beyond the indemnified months are paid 30% when the parent's individual income (ParentalLeaveEvent.individual_income) is below 2.5 times the yearly trattamento minimo di pensione (art. 34 c. 3 D.Lgs. 151/2001); a year whose minimum the INPS has not published yet (2027) pays them nothing.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Add the trattamento minimo of each new year to the parental rates when the INPS circular publishes it.

!!! note "parental_month_split · parental_leave · impact unknown · resolved"
    When a rate band or the indemnified months of the parental leave end inside a calendar month, the days of that month are paid in order at the rate of the period each falls in, one day of counter each, the last day what is left of the thirty. INPS attributes the rates to the periods of leave by day, within a month too: circ. 57/2024, example A, gives 30% to 21-31 December 2023 and 80% to 1-20 January 2024, and counts '10 giorni residui' of the further month after 20 days taken.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: the rates follow the days of each period, as INPS circ. 57/2024.

!!! note "parental_extra_month_share · parental_leave · impact unknown · resolved"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge: the leave does not reduce them (art. 34 c. 5 D.Lgs. 151/2001), and no source sets a netting of the share the INPS indemnity holds in its base (art. 23 c. 2); by the maintainer's decision of 2026-11-15 the employer pays the whole rateo, as the text reads.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the employer pays the whole rateo of the extra months.

!!! note "disability_permit_tfr · disability_permits · impact unknown · resolved"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base. Art. 33 c. 4 refers to art. 43 D.Lgs. 151/2001, which applies art. 34 c. 5: the days are paid and counted in the seniority; no primary source states their TFR base, and by the maintainer's decision of 2026-11-15 they stay in it, as payroll practice holds.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the permit days stay in the TFR base.

!!! note "notice_indemnity_partial · termination_notice · impact unknown · resolved"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 2118 c. 2 c.c. (https://www.normattiva.it/atto/caricaArticolo?art.versione=1&art.idGruppo=267&art.flagTipoArticolo=2&art.codiceRedazionale=042U0262&art.idArticolo=2118&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1942-04-04&art.progressivo=0&, sha256 834213e542e77f0f1079835b14c444432e208be59a9d3d4c859ff5ede6c8e11d): 'un'indennità equivalente all'importo della retribuzione che sarebbe spettata per il periodo di preavviso'; a notice partly worked owes the pay of the days left, as the engine computes. How a day of that pay is measured stays the declared residual notice_indemnity_day_measure. Read on 2026-11-15.

!!! note "notice_indemnity_extra_months · termination_notice · impact yes · resolved"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 2121 c. 1 c.c. (Normattiva, https://www.normattiva.it/atto/caricaArticolo?art.versione=2&art.idGruppo=267&art.flagTipoArticolo=2&art.codiceRedazionale=042U0262&art.idArticolo=2121&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1942-04-04&art.progressivo=0, sha256 d0e0175efc4dd4c7e4cc4d8431ed107547531932ccfc6dc5e078b94f0a45e7ec): 'L'indennità di cui all'articolo 2118 deve calcolarsi computando [...] ogni altro compenso di carattere continuativo'. The indemnity carries the rateo of the extra months; read on 2026-11-15.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! note "notice_indemnity_day_measure · termination_notice · impact unknown · resolved"
    A notice in calendar days is paid at the monthly pay over 30 for each calendar day ('la retribuzione che sarebbe spettata', art. 2118 c. 2 c.c.): no law sets a daily measure, and by the maintainer's decision of 2026-11-15 a calendar day is a thirtieth of the month unless the CCNL sets its own. A CCNL whose daily quota differs records its own limitation.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: a calendar day of notice is a thirtieth of the monthly pay.

!!! note "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · resolved"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time; for a vertical part time the circular divides the pay of the month by its paid days, rest days included, which ExtraordinaryLeaveEvent.last_month_paid_days states. A vertical or mixed part time that does not state them is paid on the full-time measure, so its indemnity may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: ExtraordinaryLeaveEvent.last_month_paid_days divides the pay of a vertical part time by its paid days (INPS circ. 64/2001 par. 4); a leave that does not state them is paid on the full-time measure with the provisional issue extraordinary_paid_days_unknown, which names the fact.

!!! note "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · resolved"
    The NASpI contribution of the end of an employment that does not state its case (EmploymentPeriod.naspi_case) is read from the cause, the just cause and the contract type alone: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km would owe it (INPS circ. 44/2013 par. 1), a collective dismissal would owe 82% for an employer owing the CIGS contribution (L. 205/2017 art. 1 c. 137) and three times without union agreement (L. 92/2012 art. 2 c. 35), the changes of contractor with a social clause and the closures of a construction site of c. 34 would leave it out. The service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Resolved: EmploymentPeriod.naspi_case states the cases that owe, leave out or multiply the contribution; an end that could be one and does not state it is decided from its cause alone with the provisional issue naspi_dismissal_case_unknown, which names the fact.

!!! note "personal_withholding_same_kind · personal_withholdings · impact unknown · resolved"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 553 c. 1 c.p.c. (Normattiva, https://www.normattiva.it/atto/caricaArticolo?art.versione=4&art.idGruppo=93&art.flagTipoArticolo=1&art.codiceRedazionale=040U1443&art.idArticolo=553&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.dataPubblicazioneGazzetta=1940-10-28&art.progressivo=0&, sha256 b41bf831e63fcaacfe95231f9595da5d0e5619c162cc455a80632bba90c147cd): the judge 'le assegna in pagamento [...] ai creditori concorrenti' and 'L'obbligo di pagamento decorre, per il terzo, dalla notifica dell'ordinanza di assegnazione'. The amount each garnishment takes is the fact of its ordinanza: PersonalWithholding.installment, and two garnishments of one kind without it give the missing-fact issue personal_withholding_unassigned. Read on 2026-11-15.

!!! note "mid_month_level_change · base_salary · impact unknown · resolved"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component, as a month of hire or termination; the hourly quotas of the month read the same split chain. No source sets the split (art. 2103 c.c. gives the higher pay from the assignment): by the maintainer's decision of 2026-11-15 the partial-month rule of the CCNL applies.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Resolved by the decision of 2026-11-15: the month is split by the partial-month rule of the CCNL.

!!! note "arrears_unused_deductions · contract_renewal_arrears · impact yes · resolved"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Resolved: art. 21 c. 4 TUIR (Normattiva, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art21!vig=, sha256 aafc3e5d5cd7254c7eb52e74051e86f1243b3a7b3cbadcd951daf7bc5e113fc6): 'Gli aventi diritto agli arretrati devono dichiarare al soggetto che li corrisponde l'ammontare delle detrazioni fruite per ciascuno degli anni cui si riferiscono'. The deductions are a fact the worker declares: ArrearsEvent.unused_deductions, and PriorYearTaxFacts.arrears_unused_deductions for the una tantum the engine pays as arrears; unstated, the run carries the missing-fact issue arrears_unused_deductions_unknown. Read on 2026-11-14.

!!! note "dual_apprenticeship_contributions · inps_employer · impact unknown · resolved"
    A first- or third-level apprentice (D.Lgs. 81/2015 artt. 43 and 45) is paid by the CCNL dual_apprenticeship tracks. The INPS contributions of a third-level apprentice are those of the professionalising one (L. 296/2006 art. 1 c. 773); a first-level one pays the employer 5% (D.Lgs. 150/2015 art. 32 c. 1 lett. b, made structural by L. 205/2017 art. 1 c. 110), the 1.5% and 3% of a firm with up to nine employees staying in the first two years, with no NASpI, no 0.30% (lett. c) and no dismissal contribution (lett. a): INPS circ. 108/2018 par. 3.4 (HTML sha256 6704846f...).

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the first-level rates of INPS circ. 108/2018 par. 3.4 (first_level_employer_rate) and no dismissal contribution; the hours of the final settlement are dual_final_settlement_hours (review of 2026-11-16).

!!! warning "dual_final_settlement_hours · base_salary · impact unknown · open"
    A final-settlement run of a first- or third-level apprentice pays both its month and the ratei of the extra months: Apprentice.hours weighs both by one set of hours, while the ratei accrued over the year at its own share of school, training and work.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice; run kind in termination.

    **Remediation:** Give a final-settlement run separate hours for its month and its ratei.

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://ance.it/wp-content/uploads/allegati/Tabella_nuovi_minimi_orari-_CCNL_2025.pdf | tabella_retributiva | 2025-02-21 | [↗](https://ance.it/wp-content/uploads/allegati/Tabella_nuovi_minimi_orari-_CCNL_2025.pdf) |
| https://ance.it/wp-content/uploads/allegati/20250221_Verbale_accordo_rinnovo_CCNL_firmato.pdf | altro | 2025-02-21 | [↗](https://ance.it/wp-content/uploads/allegati/20250221_Verbale_accordo_rinnovo_CCNL_firmato.pdf) |
| https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL_EDILIZIA_INDUSTRIA_2010_TESTO_COMPLETO.pdf | altro | 2010-04-19 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL_EDILIZIA_INDUSTRIA_2010_TESTO_COMPLETO.pdf) |
| https://ance.it/wp-content/uploads/archive/37937-Art%20%2092%20Apprendistato-Nota%20a%20verbale.pdf | altro | 2019-04-04 | [↗](https://ance.it/wp-content/uploads/archive/37937-Art%20%2092%20Apprendistato-Nota%20a%20verbale.pdf) |

??? note "Coverage notes"
    RENEWAL: verbale di accordo of 21 February 2025 (ANCE, Legacoop Produzione e Servizi, Confcooperative Lavoro e Servizi, AGCI Produzione e Lavoro, Feneal-Uil, Filca-Cisl, Fillea-Cgil) renewing the CCNL of 3 March 2022 to 30 June 2028; three tranches of the minimi from 1 February 2025, 1 March 2026 and 1 March 2027 (ANCE table of the new minimi, the same as Allegato 10 of the verbale). Normative text: CCNL of 19 April 2010 (FILLEA text), as amended by the verbali of 2014, 2018, 2022 and 2025. The testo coordinato signed on 24 March 2026 is in the ANCE members' area and was not read.
    
    STRUCTURE: the CCNL treats operai and impiegati differently (extra months, seniority, sickness, night overtime), so the bundle splits it: edilizia-ance holds the operai of levels 1-4, edilizia-ance-impiegati the impiegati of levels 1-7 and the quadri of level 7 (Art. 77).
    
    PAY ELEMENTS: base_salary is the national minimo of the ANCE table; the ex indennità di contingenza and the EDR of EUR 10.33 (frozen national elements of the Protocollo of 31 July 1992) are fixed allowances read from the ANCE provincial tables. The EDR is outside the TFR base (Art. 33 and 72). hourly_divisor 173: Allegato A and Art. 44 last comma.
    
    INPS: the rates of contribution/2026/edilizia.json, by category of the worker.
    
    IMPIEGATI E QUADRI: fourteen monthly payments, the tredicesima (Art. 63, by 20 December) and the premio annuo of one month (Art. 64, paid on 30 June for the service from 1 July to 30 June, stored as 28 June). Five biennial scatti (Art. 49). Quadri: indennità di funzione of EUR 140 a month (Art. 76), by Employment.roles 'quadro'. Prevedi: a monthly contractual contribution by level, also on the extra months.
    
    FIRST- AND THIRD-LEVEL APPRENTICES (Art. 92, ANCE text of 4 April 2019): modelled in dual_apprenticeship (first level at the conventional level 2 or 1, 65-90% by semester; third level 70-90% by semester for six semesters; on minimo, ex contingenza and EDR; training at the employer 10% of the work pay, school hours unpaid). Not modelled: the provincial elements of the base (indennità territoriale, premio di produzione, elemento variabile). The contributions of these apprentices are the engine limitation dual_apprenticeship_contributions.
    
    FIRST-LEVEL FAILED-TITLE EXTENSION (Art. 92, p. 6): for up to one year after failing the qualification, use the previous year's apprenticeship pay phase. Set Apprentice.failed_title_extension_start_month to the first month of the extension; leave it unset for ordinary or competence-consolidation pay.
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-ance-impiegati.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-ance-impiegati.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-ance-impiegati/example.py"
```
