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
| **Rule provenance** | 32 verified / 23 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the impiegati and quadri read in the ANCE minimi table of the CCNL of 21 February 2025, the CCNL of 19 April 2010 (FILLEA text), the Art. 92 apprenticeship text of 2019 and the ANCE provincial tables, for the production tier; new file split from edilizia-ance. | corrected | 47 records verified, 19 derived (contingenza, EDR, contractual fund, absence quota, seniority of levels 1-2, payment day of the premio annuo).<br>Split by category (Art. 77): the operai of levels 1-4 in edilizia-ance, the impiegati and quadri of levels 1-7 in edilizia-ance-impiegati.<br>base_salary is now the national minimo of the ANCE table; the ex contingenza and the EDR 10.33 are fixed allowances (derived, ANCE provincial tables), the EDR outside the TFR base. The previous consolidated values (minimo + contingenza + EDR) matched.<br>Aggregator sources (idealista, leggeinchiaro, businessonline, kitech) removed.<br>Absence quota: by_hourly 8 hours (1/173 of Art. 44 and Allegato A), not by_26, which no clause supports.<br>contractual_fund_uncovered closed: every operaio level has an hourly Prevedi amount and every impiegato or quadro level a monthly one.<br>No renewal changing the national minimi after the verbale of 21 February 2025 through October 2026.<br>Fourteen monthly payments: tredicesima (Art. 63, 20 December) and premio annuo (Art. 64, 30 June, stored 28 June).<br>Night overtime 47% (Art. 54), not the 40% of the operai.<br>Seniority 8.20 for levels 1-2 (printed 'Imp. 4ª 8,2'), not 8.22: derived.<br>Quadri indennità di funzione EUR 140 (Art. 76) added.<br>Sickness: 100% for 180 days without INPS (Art. 66 band up to two years); the longer bands declared. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | edilizia_impiegati_sickness (the art. 66 treatment beyond two years of service) is recorded on every sickness run of a worker with 24 months of seniority or more, or of unknown seniority. |
| 2026-10-17 | claude-opus-5-5 (ai) | A year and a termination of an impiegato of the 3rd level against a hand oracle, and the 23 derived rules of the file. | corrected | Engine corrected: at a termination the June pay settles the ratei of the tredicesima; the Prevedi contributo contrattuale, 'applicato anche per 13° e 14° mensilità', was not charged on them (6,50 EUR and its 10% solidarity contribution short), while an extra-month run of the same ratei charges it. The settled ratei now owe it (tests/knowledge/ccnl_engine/pension_fund/services/test_prevedi.py::test_a_termination_owes_the_ratei_it_settles).<br>Engine corrected: the ratei settled at a termination entered the TFR base whole, the EDR included, while the EDR stays out of the TFR base in the monthly pay and in an extra-month run (0,38 EUR of TFR too much here). The settled ratei now leave out the allowances outside the TFR base.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios edilizia-impiegati-year and edilizia-impiegati-june): an impiegato of the 3rd level hired on 1 January 2026 by an employer with 30 employees, across the tranche of March 2026; after the two corrections every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done.<br>The 23 derived rules stay derived: the contingenza and EDR of each level (14) are read from the ANCE provincial tables, not tabulated in the CCNL; the Prevedi amounts are rebuilt from two verbali and the fund scheda; two scatti differ between the table (8,2) and the secondary tables (8,22); the payment day of the quattordicesima and the absence divisor are stated transformations. No signatory text states them directly. |

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

!!! warning "edilizia-ance-impiegati/other_apprenticeship_types · base_salary · impact unknown · open"
    APPRENTICESHIP: Art. 92 (ANCE text of 4 April 2019): 72/72/78/78/85/90% by semester for 36 months towards levels 2-7; the apprendistato duale and the alta formazione are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the pay of the apprendistato duale and alta formazione, or refuse them by track.

!!! warning "edilizia-ance-impiegati/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "edilizia-ance-impiegati/edilizia_impiegati_sickness · sickness · impact yes · open"
    SICKNESS (Art. 66): the employer pays the whole treatment of the elements 1-10 of Art. 44 (INPS pays no indemnity to the impiegati and quadri of industry) for six months, the comporto of a worker with up to two years of service. Not modelled: from two to six years the comporto of nine months with the last three at 50%, over six years twelve months with three months at 75% and three at 50%; for several illnesses or relapses the comporto of 9, 12 or 15 months in 30, whose three extra months are paid in full for the first and at 50% after. The engine stops at day 180 (days past it are marked beyond the comporto).

    **Applies when:** `sickness` applies; seniority of at least 24 months.

    **Remediation:** Model the seniority bands of Art. 66 with equal full-pay days and the cumulated comporto in 30 months.

!!! warning "edilizia-ance-impiegati/provincial_evr · territorial_supplement · impact yes · open"
    Art. 46: the EVR set by the provincial agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial EVR as an input.

!!! warning "edilizia-ance-impiegati/loyalty_premium · base_salary · impact yes · open"
    Art. 65: the premio di fedeltà of one month a year after 20 years of service.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the premio di fedeltà on seniority.

!!! warning "edilizia-ance-impiegati/ordinary_hours_premiums · overtime · impact yes · open"
    Art. 54: the premiums on ordinary hours (lavoro festivo 45%, notturno 34% or 10% in shifts, festivo notturno 50%).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 54 premiums on ordinary hours.

!!! warning "edilizia-ance-impiegati/special_allowances · base_salary · impact yes · open"
    Art. 47, 50 and 52: the indennità speciale, di cassa and for alta montagna, cassoni and galleria.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the allowances of Artt. 47, 50 and 52.

!!! warning "edilizia-ance-impiegati/provincial_meals_transport_travel · territorial_supplement · impact yes · open"
    Mensa, trasporto and trasferta, set by the provincial agreements (verbale 2025).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial mensa, trasporto and trasferta as inputs.

!!! warning "edilizia-ance-impiegati/november_4_holiday · base_salary · impact yes · open"
    Art. 43: the 1/25 for the festività of 4 November.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the 1/25 of 4 November.

!!! warning "edilizia-ance-impiegati/quadri_absorption · base_salary · impact yes · open"
    Art. 76: the absorption of a superminimo into the quadri function allowance. The una tantum premio di ingresso of the verbale of 3 March 2022 and the riduzione contributiva edile concern the operai only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the absorption of Art. 76.

!!! warning "edilizia-ance-impiegati/provincial_production_premium · territorial_supplement · impact yes · open"
    PREMIO DI PRODUZIONE: the premio di produzione set by the provincial agreements (Art. 44 n. 5) is owed to every impiegato; the engine reads no provincial agreement. Not modelled: the net pay and the employer cost are short of it.

    **Applies when:** `territorial_supplement` applies.

    **Remediation:** Model the provincial premio di produzione with a fact naming the province, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! warning "notice_indemnity_tfr · termination_notice · impact unknown · open"
    The notice indemnity enters the TFR base as payroll practice holds; art. 2120 c. 2 c.c. counts the sums paid 'a titolo non occasionale' and no primary source read settles whether this indemnity is among them, so the TFR quota of the termination run may be overstated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the notice indemnity (case law of the Cassazione or a Ministry ruling) and apply it, then resolve this limitation.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

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
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-ance-impiegati.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-ance-impiegati.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-ance-impiegati/example.py"
```
