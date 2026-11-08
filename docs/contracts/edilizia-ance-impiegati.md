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

11 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 37 verified / 23 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-11-08 |
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
    Art. 65: the premio di fedeltà of one month a year after 20 years of service.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the premio di fedeltà on seniority.

!!! warning "edilizia-ance-impiegati/special_allowances · base_salary · impact yes · open"
    Art. 47, 50 and 52: the indennità speciale, di cassa and for alta montagna, cassoni and galleria.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the allowances of Artt. 47, 50 and 52.

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
    Art. 54: the 50% of lavoro festivo notturno excludes the work 'compreso in turni periodici', and the table states no rate for it; the engine does not tell a shift worker apart and pays the 50% (supplement_bands ANCE_IMP_FESTIVO_NOTTURNO). The other premiums on ordinary hours are modelled (ANCE_IMP_*).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Exclude the night holiday work in periodic shifts from the 50% of Art. 54 once a source sets its rate.

!!! warning "edilizia-ance-impiegati/dual_apprenticeship_prorogation · base_salary · impact yes · open"
    FIRST-LEVEL PROROGATION (Art. 92, ANCE text of 4 April 2019, p. 6): 'Per l'apprendista che invece non abbia conseguito il titolo di istruzione, in caso di proroga il trattamento economico è quello dell'anno precedente'. The engine pays the semester of Apprentice.months_elapsed: a prorogued apprentice who failed the title is paid the next semester's percentage.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state a failed title, and pay the previous year's percentage.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/mutation/ccnl_engine/sickness/base/test_rules_wiring.py, tests/mutation/ccnl_engine/sickness/base/test_rules.py.

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

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "notice_indemnity_partial · termination_notice · impact unknown · open"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source how the CCNL or case law measures the indemnity of a notice partly worked and apply it, then resolve this limitation.

!!! warning "notice_indemnity_extra_months · termination_notice · impact yes · open"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source whether the indemnity carries the rateo of the extra months (CCNL clause or case law) and add it, then resolve this limitation.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! note "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · resolved"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time; for a vertical part time the circular divides the pay of the month by its paid days, rest days included, which ExtraordinaryLeaveEvent.last_month_paid_days states. A vertical or mixed part time that does not state them is paid on the full-time measure, so its indemnity may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: ExtraordinaryLeaveEvent.last_month_paid_days divides the pay of a vertical part time by its paid days (INPS circ. 64/2001 par. 4); a leave that does not state them is paid on the full-time measure with the provisional issue extraordinary_paid_days_unknown, which names the fact.

!!! note "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · resolved"
    The NASpI contribution of the end of an employment that does not state its case (EmploymentPeriod.naspi_case) is read from the cause, the just cause and the contract type alone: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km would owe it (INPS circ. 44/2013 par. 1), a collective dismissal would owe 82% for an employer owing the CIGS contribution (L. 205/2017 art. 1 c. 137) and three times without union agreement (L. 92/2012 art. 2 c. 35), the changes of contractor with a social clause and the closures of a construction site of c. 34 would leave it out. The service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Resolved: EmploymentPeriod.naspi_case states the cases that owe, leave out or multiply the contribution; an end that could be one and does not state it is decided from its cause alone with the provisional issue naspi_dismissal_case_unknown, which names the fact.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** State ArrearsEvent.unused_deductions from the worker's declaration of the deductions used each year; for the una tantum, carry it into the events the engine generates.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid none, its treatment not being sourced.

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

!!! warning "dual_apprenticeship_contributions · inps_employer · impact unknown · open"
    A first- or third-level apprentice (D.Lgs. 81/2015 artt. 43 and 45) is paid by the CCNL dual_apprenticeship tracks, but the INPS contributions and the other rates of the run are those of the professionalising apprentice: the contribution regime of these apprentices is not sourced. On a final-settlement run that pays both its month and the ratei, Apprentice.hours splits both by one set of hours.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the INPS contribution regime of first- and third-level apprentices and apply it; give a final-settlement run separate hours for its month and its ratei.

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
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-ance-impiegati.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-ance-impiegati.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-ance-impiegati/example.py"
```
