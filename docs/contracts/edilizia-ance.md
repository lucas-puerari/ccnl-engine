# CCNL Edilizia — Industria (ANCE), operai

| | |
|---|---|
| **CNEL code** | `F012` |
| **Sector** | edilizia |
| **Family** | `edilizia` |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-02-21 |
| **Workers (est.)** | ~550k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCE
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Produzione e Lavoro
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
| **Limits of this contract** | base_salary, bilateral_funds, overtime, sickness, territorial_supplement |

12 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 47 verified / 7 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-11-09 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the operai read again in the ANCE minimi table of the CCNL of 21 February 2025, the CCNL of 19 April 2010 (FILLEA text), the Art. 92 apprenticeship text of 2019 and the ANCE provincial tables, for the production tier. | corrected | 26 records verified, 12 derived (contingenza, EDR, contractual fund, absence quota, sickness mapping).<br>Split by category (Art. 77): the operai of levels 1-4 in edilizia-ance, the impiegati and quadri of levels 1-7 in edilizia-ance-impiegati.<br>base_salary is now the national minimo of the ANCE table; the ex contingenza and the EDR 10.33 are fixed allowances (derived, ANCE provincial tables), the EDR outside the TFR base. The previous consolidated values (minimo + contingenza + EDR) matched.<br>Aggregator sources (idealista, leggeinchiaro, businessonline, kitech) removed.<br>Absence quota: by_hourly 8 hours (1/173 of Art. 44 and Allegato A), not by_26, which no clause supports.<br>contractual_fund_uncovered closed: every operaio level has an hourly Prevedi amount and every impiegato or quadro level a monthly one.<br>No renewal changing the national minimi after the verbale of 21 February 2025 through October 2026.<br>Twelve monthly payments, not 13: the gratifica natalizia and the ferie are the 18.5% of Art. 18 through the Cassa Edile (declared).<br>No scatti for the operai (Art. 49 is for the impiegati; APE through the Cassa Edile, Art. 29): seniority removed, the apprentice seniority note closed.<br>Sickness: the coefficients of Art. 26, not 100% for 180 days; comporto 270 days (derived mapping, declared).<br>Night overtime 40% (Art. 19) confirmed; sources now the CCNL text.<br>Notes corrected: the TFR is paid by the employer (Art. 33), not the Cassa Edile; the INPS rates are the verified 2026 edilizia table. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations and readiness. | demoted | The 18.5% Cassa Edile accrual and the 4.95% riposi annui are missing from every operaio payslip: declared as cassa_edile_riposi_missing on every run, so the file goes back to reviewed.<br>edilizia_operai_sickness is recorded on every run with a sickness event. |
| 2026-10-13 | claude-opus-5-5 (ai) | The hourly pay of the operai (Allegato A), the riposi annui of Art. 5 B, the Cassa Edile percentage of Art. 18 with the conventional net of Allegato D and the TFR base of Art. 33, read in the CCNL of 19 April 2010 (FILLEA text), for the production tier. | corrected | hourly_pay added: the operai are paid the monthly elements over 173 times the ordinary hours worked (Allegato A, p. 164); without the hours the run has a missing_fact ordinary_hours_worked blocker.<br>RIPOSI_ANNUI 4.95% (Art. 5 B, p. 27) paid with the pay and CASSA_EDILE 18.5% (Art. 18, pp. 37-38) accrued net of the withholdings: 14.2% withheld from the net pay (Allegato D, p. 172); both on the paga base and the ex contingenza (Art. 24 point 3-4, p. 49), in the INPS, IRPEF and TFR bases (Art. 33, p. 56).<br>No renewal changes the rates: the OCR of the verbali of 1 July 2014, 18 July 2018, 3 March 2022 and 21 February 2025 has no hit for 4,95, 18,5 or 14,2; the ANCE Ragusa table of 1 March 2026 prints 4,95%, 18,50% and 14,20%.<br>The ANCE Sassari table of 1 February 2025 computes the 18.5% and the 4.95% on a sub-total with the hourly EDR (0,06); the CCNL base of Art. 24 does not list the EDR and the data follow the CCNL.<br>cassa_edile_riposi_missing closed; the festività of Art. 17, the capisquadra maggiorazione, the Allegato D sickness and injury percentages and its point 4 exception declared.<br>Promoted to production. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the minimi of the operai for the tranches of 1 February 2025, 1 March 2026 and 1 March 2027 against the ANCE national table; the remaining derived records. | confirmed | The 12 monthly minimi of the four operai levels match the impiegati column of the national table, and each over 173 is the hourly minimo the table prints for the operai.<br>Contingenza and EDR stay derived: Art. 11 of the CCNL of 19 April 2010 refers to the interconfederal agreements and no national signed table prints the amounts; the ANCE provincial tables do.<br>Prevedi stays derived (fund information sheet); the accrual rule is a placeholder the operai do not read (no extra month paid by the employer). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | corrected | CNEL F012 matches. Signatory names corrected to the report: Legacoop Produzione e Servizi (was Legacoop Costruzioni) and AGCI Produzione e Lavoro.<br>Term: expiry 30/06/2028 from the report; valid_from is the first tranche of the renewal of 21 February 2025, the start of its term was not read. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi': the scatti and fixed allowances of the file against the text read in the P1 review. | confirmed | Ex contingenza 512,87 / 516,43 / 519,16 / 521,25 and EDR 10,33 of levels I-IV match the ANCE table of 1 February 2025 (ANCE is a signatory). The same table prints the operai hourly amounts 2,96 / 2,99 / 3,00 / 3,01 and 0,06, which are the monthly amounts divided by the hourly divisor 173: the monthly records are consistent with the hourly pay. Verified.<br>No scatti for the operai: the anzianità professionale edile is paid by the Cassa Edile (Art. 29), as the file states. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | flagged | Part-time supplementary hours at 20% and the 10% of the flexible clauses (pp. 105-106): declared. The apprenticeship track was verified in P1. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour for the CCNL (D.Lgs. 36/2023 art. 41 c. 13). | flagged | Operaio di 1° livello, January 2026 (the tranche of the table of May 2025), 30 employees, 173 hours: minimo 6,17, ex contingenza 2,96 and EDR 0,06 an hour equal the monthly amounts over 173; riposi annui 4,95% and the Cassa Edile accrual 18,50% are the table's rates on minimo and contingenza; the employer INPS rate 34.28% (15-50 employees) matches. Match.<br>Deviations, with cause and decision: the EVR, the indennità territoriale di settore and the transport and meal indemnities are provincial and declared (NOT MODELLED AMOUNTS); the Cassa Edile contribution (5,47% in the table) was not declared: declared; INAIL 11% is not computed by the engine (documented). No independent net pay example: not compared. |
| 2026-10-17 | claude-opus-5-5 (ai) | The rate of the supplementary hours of the part-time workers. | corrected | Art. 78 (pp. 90-91): the operai are paid the supplementary hours with the hourly quota raised by 20%, which 'avrà incidenza su tutti gli istituti retributivi legali e contrattuali, indiretti e differiti, compresi le contribuzioni e gli accantonamenti in Cassa Edile'. The 20% band is added; its incidence on the TFR and the Cassa Edile accruals is not modelled (the engine keeps an overtime pay out of the TFR base), so part_time_supplementary_rate stays open, narrowed to it. The 10% of the flexible clauses is not modelled either. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 26 (pp. 50-51): the comporto is 270 days of one illness and 'nove mesi nell’arco di 20 mesi consecutivi' of several, 365 days and '12 mesi nell’arco di 24 mesi consecutivi' past three and a half years of seniority; coefficient (e) pays days 181-365. The file kept a comporto of 270 days of one illness: corrected to the windows of 20 and 24 months (comporto_windows) with one illness paid up to day 365. The coefficients were confirmed. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice of the operai, Art. 32 (p. 55). | corrected | Art. 32 (p. 55): 7 calendar days up to three years, 10 beyond, from any day, indemnity at the pay of the period: work_rules.notice. Found by a delegated search, checked on the PDF text. |
| 2026-11-02 | claude-opus-5-5 (ai) | The premiums on ordinary hours of Art. 19 (PDF p. 40) and the hourly base of Art. 24 point 3 (p. 49). | corrected | Art. 19 nn. 2, 4-8, 12: supplement_bands ANCE_* (festivo 45%, night 28%, guardiano 8%, continuous night 16%, day shift 9%, night shift 12%, Sunday with compensatory rest 8%).<br>Art. 24 point 3: the base of the premiums is paga base di fatto, ex contingenza and indennità territoriale di settore: the EDR was in the hourly base of the overtime bands and is now excluded (hourly_base_excluded); the superminimo enters (individual_elements included). |
| 2026-11-02 | claude-opus-5-5 (ai) | Art. 19 n. 10 (PDF p. 40). | corrected | Art. 19 n. 10: festivo notturno 50% (HolidayWorkKind.NIGHT_HOLIDAY). |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity. |
| 2026-11-08 | claude-opus-5-5 (ai) | Saturday premium of the signed text, found verbatim in the source (analysis by a separate model session, quote rechecked). | corrected | Added supplement band ANCE_SABATO_SEI_GIORNI. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 92 in the ANCE text of 4 April 2019 (pp. 4-8), applied to contracts from 1 April 2019. Final encoding (dual_apprenticeship JSON) checked against the PDFs by a separate model session (.private flv2). | flagged | Semesters, conventional levels 2 and 1 and the third-level table match. The base also names the indennità territoriale, the premio di produzione and the elemento variabile, which the bundle does not hold (limitations territorial_sector_allowance and provincial_evr).<br>A failed-title prorogation keeps the pay of the previous year (p. 6): not expressible, recorded as dual_apprenticeship_prorogation.<br>Ambiguous in the text, kept as read: the base of the 10% training share ('di quella che gli sarebbe dovuta'). |
| 2026-11-08 | claude-opus-5-5 (ai) | Caposquadra (printed p. 89, PDF p. 103) and Art. 24 points 3-4 of the CCNL 19 April 2010, via a research report, quotes checked on the text layer. | corrected | Added the role allowance CAPOSQUADRA (10% of paga base and ex contingenza) in the base of the hourly percentages. |
| 2026-11-08 | claude-opus-5-5 (ai) | Caposquadra percentage base and qualified-worker floor, CCNL 2010 PDF pp. 49 and 103. | corrected | Calculate the national supplement dynamically and lift base pay to the level 2 ordinary pay where required. Provincial, individual and piecework components remain unavailable. |
| 2026-11-08 | claude-opus-5-5 (ai) | Caposquadra qualified-worker remuneration integration and Art. 24 points 2–4, signed CCNL 2010 PDF pp. 49 and 103. | corrected | The level-2 shortfall is a separate earning, not a contractual base-pay increase; own individual elements reduce it and enter the special supplement and Art. 17–18 bases. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 17(3), Art. 18 and Art. 5 B holiday treatment in the cached 2010 CCNL, checked against the hourly pay model. | corrected | Eight hours per eligible holiday, including rest-day holidays; percentages also apply to the holiday treatment. Eligibility remains caller-stated. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 78 proportional part-time pay and Art. 17 holiday treatment, verified on cached 2010 PDF pages 104 and 37. | corrected | Horizontal part-time holiday hours are proportional to agreed weekly hours; unknown eligible days cannot mean zero. Vertical or mixed holiday placement and discontinuous work remain unresolved. |
| 2026-11-09 | claude-opus-5-5 (ai) | Direct hourly sickness integration and episode-length waiting tiers under Art. 26 of the signed 2010 agreement, PDF pp. 50–51; weekly hours under Art. 5, PDF p. 26. | corrected | The employer pays direct coefficients on a separate hourly base, not a target net of INPS. Waiting coefficients depend on the full episode; six payable days exclude holidays. Cassa Edile accruals and short-episode annual rest remain unmodelled. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 92 first-level failed-title extension, cached ANCE PDF p. 6, both first-level tracks. | confirmed | The maximum extension is one year; failure to obtain the title retains the previous year's pay, while competence consolidation progresses normally. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 19 n. 12 Sunday shift-worker exclusion, PDF page 40 | corrected | The 8% Sunday compensatory-rest premium excludes shift workers. |
| 2026-11-09 | claude-opus-5-5 (ai) | Art. 78 scope of the supplementary rate for manual and clerical workers. | corrected | Art. 78, printed pp. 90-91: 'Per il personale operaio, le eventuali ore di lavoro supplementare ... maggiorata di una percentuale del 20%'; the subsequent paragraph gives clerical workers a distinct Art. 44 base and excludes TFR. Restricted the existing direct-pay band to manual workers; clerical base and manual-worker accrual incidence remain open. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `4` | Livello 4: operai di quarto livello (art. 77) | € 1,634.31 | 2027-03-01 |
| `3` | Livello 3: operai specializzati (art. 77) | € 1,517.56 | 2027-03-01 |
| `2` | Livello 2: operai qualificati (art. 77) | € 1,365.81 | 2027-03-01 |
| `1` | Livello 1: operai comuni (art. 77) | € 1,167.36 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`  
percentage: 1.00

**lavorazioni_artistiche** (type: `percentage`)  
Destination levels: `2`, `3`, `4`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-ance/provincial_evr · territorial_supplement · impact yes · open"
    Art. 46: the EVR set by the provincial agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial EVR as an input.

!!! warning "edilizia-ance/capisquadra_supplement · base_salary · impact yes · open"
    CAPISQUADRA (classification, p. 103; Art. 24 point 4): the 10% maggiorazione of the operaio put in charge of at least five operai is the allowance CAPOSQUADRA (role 'caposquadra'), in the base of the riposi annui and Cassa Edile percentages. Not modelled: provincial EET/ITS and piecework minimum in the percentage base; assignment duration is supplied by the role input.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Supply provincial and piecework components of the percentage base and assignment duration.

!!! warning "edilizia-ance/holiday_hours · base_salary · impact yes · open"
    Art. 17 point 3: eight hours of pay, with 4.95% and 18.5% on the holiday treatment, are included when the caller supplies paid_holiday_days; horizontal part time scales the hours by agreed weekly hours. An unknown count raises a missing-fact issue; zero confirms none. Not modelled: 9.6 hours for discontinuous workers, the separate 4 November treatment and holiday placement in vertical or mixed part-time schedules. The caller must resolve local patron saint dates, employment eligibility and any suspension; no automatic holiday calendar is applied.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolve eligible holiday dates, discontinuous work and vertical or mixed schedules; supply the eligible count after checking employment and suspension conditions. Model the distinct 4 November treatment.

!!! warning "edilizia-ance/entry_premium_2022 · base_salary · impact yes · open"
    Verbale of 3 March 2022, Allegato 5: the una tantum premio di ingresso of EUR 100 to operai under 29.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the premio di ingresso with the age of the worker.

!!! warning "edilizia-ance/ape_cassa_edile · base_salary · impact yes · open"
    Art. 29: the APE paid by the Cassa Edile.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the APE as a Cassa Edile payment.

!!! warning "edilizia-ance/hardship_allowances · base_salary · impact yes · open"
    Art. 20-21: the indennità for lavori speciali disagiati, alta montagna and cantiere ferroviario.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the allowances of Artt. 20-21.

!!! warning "edilizia-ance/provincial_meals_transport_travel · territorial_supplement · impact yes · open"
    Mensa, trasporto and trasferta, set by the provincial agreements (verbale 2025).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial mensa, trasporto and trasferta as inputs.

!!! warning "edilizia-ance/contribution_reduction · base_salary · impact yes · open"
    Art. 29 L. 341/1995: the riduzione contributiva edile on the employer INPS contributions of full-time operai.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the riduzione contributiva edile of the year.

!!! warning "edilizia-ance/territorial_sector_allowance · territorial_supplement · impact yes · open"
    INDENNITÀ TERRITORIALE DI SETTORE: set by the provincial agreements (Art. 12) and owed to every operaio, also in the base of the 4.95% and 18.5% and in the TFR base of Art. 33. Not modelled: the net pay and the employer cost are short of it.

    **Applies when:** `territorial_supplement` applies.

    **Remediation:** Model the indennità territoriale di settore with a fact naming the province, then remove this note.

!!! warning "edilizia-ance/cassa_edile_contribution · bilateral_funds · impact yes · open"
    CASSA EDILE CONTRIBUTION: the contribution to the Cassa Edile, set by the provincial agreements and shared by employer and worker (5,47% on the hourly elements in the Agrigento table of the Ministry of Labour of May 2025), is not modelled; only the 18.5% accrual for ferie and gratifica is. The worker's share lowers the net pay.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the provincial Cassa Edile contribution as a bilateral fund event, or model the provincial rates.

!!! warning "edilizia-ance/edilizia_operai_sickness · sickness · impact yes · open"
    SICKNESS (Art. 26): direct employer integration uses hourly minimum and ex contingenza (plus territorial allowance where available), excluding EDR, times one sixth of contracted weekly hours on six days a week excluding holidays. Waiting days 1-3 are unpaid for episodes of at most six days, paid at 0.5495 above six and 1.0495 above twelve; INPS-covered days 4-20 use 0.3795 and days 21-180 use 0.1565; non-INPS-covered days 181-365 use 0.5495. Not modelled: the 4.95% annual-rest payment for waiting days of episodes up to six days and on the injury day (60% on injury days 1-3); Cassa Edile sickness and injury accruals (18.5% gross, 14.2% net for sickness waiting days and from day 4; 7.4% and 5.7% on injury days 4-90; 4.6% and 3.6% from day 91) and the no-direct-pay exception of Allegato D point 4. Provincial territorial pay and actual site hours are not bundled, so only known components enter the base. Sick hours do not deduct from hourly worked pay.

    **Applies when:** `sickness` applies.

    **Remediation:** Model the short-episode annual-rest payment and Cassa Edile accruals on sickness and injury, including site-hour and no-direct-pay rules.

!!! warning "edilizia-ance/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: Art. 78 pays horizontal part-time operai 20% on the direct hourly remuneration up to 40 weekly hours. OT_SUPPLEMENTARE applies only to operai; the engine does not apply its incidence to deferred pay, TFR or Cassa Edile accruals. For impiegati Art. 78 also sets 20%, but on different Art. 44 elements, all-inclusive and without TFR incidence; that base is not derived here. The 10% for flexible clauses is separate and not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the operai incidence on deferred pay, TFR and Cassa Edile accruals, and the distinct impiegati hourly base before resolving this note.

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

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid as a private one (art. 5 names the "Stato, enti pubblici e datori privati").

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

!!! warning "dual_apprenticeship_contributions · inps_employer · impact unknown · open"
    A first- or third-level apprentice (D.Lgs. 81/2015 artt. 43 and 45) is paid by the CCNL dual_apprenticeship tracks, but the INPS contributions and the other rates of the run are those of the professionalising apprentice: the contribution regime of these apprentices is not sourced. On a final-settlement run that pays both its month and the ratei, Apprentice.hours splits both by one set of hours.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the INPS contribution regime of first- and third-level apprentices and apply it; give a final-settlement run separate hours for its month and its ratei.

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
    
    OPERAI: twelve monthly payments; paid by the hour worked (Allegato A, parameters.hourly_pay; state PeriodFacts.ordinary_hours_worked); ferie and gratifica natalizia are the 18.5% of the paga base and ex contingenza accrued with the Cassa Edile net of the withholdings (Art. 16 and 18, Allegato D: 14.2% withheld from the net pay), not extra months; the riposi annui are the 4.95% paid with the pay (Art. 5 B). No scatti di anzianità: the operai receive the APE through the Cassa Edile (Art. 29). The TFR is paid by the employer under L. 297/1982 (Art. 33). Prevedi: the contractual contribution of an operaio is an amount per ordinary hour worked (state PeriodFacts.ordinary_hours_worked).
    
    FIRST- AND THIRD-LEVEL APPRENTICES (Art. 92, ANCE text of 4 April 2019): modelled in dual_apprenticeship (first level at the conventional level 2 or 1, 65-90% by semester; third level 70-90% by semester for six semesters; on minimo, ex contingenza and EDR; training at the employer 10% of the work pay, school hours unpaid). Not modelled: the provincial elements of the base (indennità territoriale, premio di produzione, elemento variabile). The contributions of these apprentices are the engine limitation dual_apprenticeship_contributions.
    
    FIRST-LEVEL FAILED-TITLE EXTENSION (Art. 92, p. 6): for up to one year after failing the qualification, use the previous year's apprenticeship pay phase. Set Apprentice.failed_title_extension_start_month to the first month of the extension; leave it unset for ordinary or competence-consolidation pay.
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-ance.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-ance.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-ance/example.py"
```
