# CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)

| | |
|---|---|
| **CNEL code** | `K051` |
| **Sector** | industria |
| **Family** | `energia-utilities` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-11 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Elettricita Futura
    - Utilitalia
    - Enel SpA
    - GSE
    - Sogin SpA
    - Terna SpA
    - FILCTEM-CGIL
    - FLAEI-CISL
    - UILTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

0 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 58 verified / 22 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-11 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2027-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 40 - Tredicesima e Quattordicesima mensilità (p. 96): "Nel caso di inizio o di cessazione del rapporto di lavoro durante l’anno o nel caso di assenza non retribuita, il lavoratore, non in prova, ha diritto a tanti dodicesimi dell’ammontare di tali mensilità quanti sono i mesi interi di servizio prestato, computando come mese intero la frazione di mese superiore a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi contrattuali integrati of the 14 levels on the four tranches of the ipotesi di accordo of 11 February 2025 (1/4/2025, 1/4/2026, 1/4/2027, 1/10/2027), against the table printed in the signed text deposited at CNEL. | corrected | The signed ipotesi of 11 February 2025 (CNEL K051, deposito 216334, 44-page scan without text layer, read on the page image of PDF p. 37) prints the table 'Minimi contrattuali integrati' with the parameter, the increment and the minimo of the 14 levels QS-C1 on 1/4/2025, 1/4/2026, 1/4/2027 and 1/10/2027 ('Aumento medio a regime €290 su parametro medio 179,76 valore punto 29,80'). The table level labels are the file codes.<br>41 of the 56 file values match; 15 (all on 1/4/2027 or 1/10/2027) differ by one cent and are corrected to the printed table.<br>Art. 38 c. 1 (PDF p. 34) defines the monthly pay as the minimo contrattuale integrato (minimi tabellari conglobated with the ex indennità di contingenza from 1 April 2013) and c. 3 adds the EDR of EUR 10,33 separately: the file's base_salary (minimo) with the EDR as a fixed allowance matches.<br>The appendix table on PDF p. 42 (5 categories, 'Aumento medio a regime € 220 su parametro medio 134,19') belongs to the separate area contrattuale in the appendix and is not used.<br>The ruleset now names the CNEL deposit of the text signed by the contracting parties (Elettricità Futura, Utilitalia, Energia Libera, Enel, GSE, Terna, Sogin, Filctem-CGIL, Flaei-CISL, Uiltec-UIL): source_type contracting_party.<br>Corrected to the printed table: Q 2027-04-01: 3858.47 -> 3858.48; Q 2027-10-01: 3947.60 -> 3947.61; ASS 2027-04-01: 3405.74 -> 3405.73; ASS 2027-10-01: 3484.42 -> 3484.41; AS 2027-04-01: 3187.64 -> 3187.65; AS 2027-10-01: 3261.27 -> 3261.28; A1 2027-04-01: 2913.65 -> 2913.66; A1 2027-10-01: 2980.96 -> 2980.97; BSS 2027-04-01: 2774.62 -> 2774.63; BS 2027-04-01: 2656.36 -> 2656.35; BS 2027-10-01: 2717.73 -> 2717.72; B1 2027-04-01: 2417.48 -> 2417.49; B2S 2027-04-01: 2257.70 -> 2257.71; CS 2027-04-01: 1862.65 -> 1862.64; CS 2027-10-01: 1905.68 -> 1905.67. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: artt. 15, 39 of the CCNL of 18 July 2022 (pp. 31, 94) and art. 38 of the ipotesi of 11 February 2025 (p. 34, OCR). | corrected | Apprentices accrue the level increments at their percentage: art. 15 c. 5 (p. 31 of the CCNL of 18 July 2022) pays 'una retribuzione in misura percentuale e proporzionata all'anzianità di servizio'; art. 38 c. 1 (p. 34 of the ipotesi of 11 February 2025) makes the retribuzione mensile of the minimo contrattuale integrato 'e dai corrispettivi eventualmente spettanti a titolo di aumenti periodici di anzianità'; art. 39 (p. 94 of 2022) owes an increment each biennio of service. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | gpt-6-sol (ai) | Employer top-up of the INAIL indemnity, read from the signed text by a separate model session (audit of the injury rules); quote checked on the text layer or the page image. | corrected | The injury rule had no top-up of the INAIL indemnity; added: {"integration_rate": "1", "carenza_rate": "1"} |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto and sick pay against a second research of a separate model session; quotes checked on the source. | corrected | Comporto of one illness 360 days (12 months of 30 days) and 540 within 36 months, hospital stays left out. |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: bands[0:night], travel.<br>Left out: bands[1:holiday]: quote quote_not_in_file; bands[2:rest_day]: quote quote_not_in_file; bands[3:night_holiday_compensatory_rest]: quote quote_not_in_file; bands[4:sunday]: quote quote_not_in_file; bands[5:sunday]: quote quote_not_in_file; bands[6:night_shift]: quote quote_not_in_file; bands[7:day_shift]: quote quote_not_in_file; bands[8:day_shift]: more day_shift bands the engine cannot tell apart; bands[9:day_shift]: quote quote_not_in_file. |
| 2026-11-16 | claude-opus-5-5 (ai) | Number of monthly pays: the article on the additional months located in the cited file by sha256. | corrected | Sourced: 14 monthly pays. |
| 2026-11-16 | claude-opus-5-5 (ai) | Apprentice pay (Art. 15, Inquadramento e trattamento retributivo, PDF p. 50): the elements the percentage applies to, read in the cited file by sha256. | corrected | apprenticeship_pct_relevant EDR = false: EDR corrisposto in aggiunta alla retribuzione mensile contrattuale e non compreso nel minimo contrattuale integrato percentualmente ridotto: dovuto intero.<br>Clause: 5. L’apprendista viene inquadrato nella categoria corrispondente alla qualifica-
    zione da conseguire al termine dell’apprendistato con una retribuzione in mi-
    sura percentuale e proporzionata all’anzianità di servizio. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QS` | Senior Quadro | € 4,399.12 | 2027-10-01 |
| `Q` | Quadro | € 3,947.61 | 2027-10-01 |
| `ASS` | Senior Senior Specialist Area | € 3,484.41 | 2027-10-01 |
| `AS` | Senior Specialist Area | € 3,261.28 | 2027-10-01 |
| `A1S` | Area 1 Senior | € 3,124.14 | 2027-10-01 |
| `A1` | Area 1 | € 2,980.97 | 2027-10-01 |
| `BSS` | Area B Senior Senior | € 2,838.72 | 2027-10-01 |
| `BS` | Area B Senior | € 2,717.72 | 2027-10-01 |
| `B1S` | Area B1 Senior | € 2,589.64 | 2027-10-01 |
| `B1` | Area B1 | € 2,473.33 | 2027-10-01 |
| `B2S` | Area B2 Senior | € 2,309.87 | 2027-10-01 |
| `B2` | Area B2 | € 2,149.26 | 2027-10-01 |
| `CS` | Area C Senior | € 1,905.67 | 2027-10-01 |
| `C1` | Area C1 | € 1,724.71 | 2027-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `QS` | € 49.01 |
| `Q` | € 46.33 |
| `ASS` | € 43.07 |
| `AS` | € 39.82 |
| `A1S` | € 37.86 |
| `A1` | € 35.74 |
| `BSS` | € 33.72 |
| `BS` | € 31.97 |
| `B1S` | € 30.16 |
| `B1` | € 28.46 |
| `B2S` | € 26.13 |
| `B2` | € 23.81 |
| `CS` | € 20.30 |
| `C1` | € 17.66 |

## Apprenticeship

**gruppo_c** (type: `percentage`)  
Destination levels: `CS`  
percentage: 1.00

**gruppo_b** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_a_bss** (type: `percentage`)  
Destination levels: `BSS`, `A1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.contratticcnl.it/elettrico/tabelle-retributive/ | tabella_retributiva | 2025-02-11 | [↗](https://www.contratticcnl.it/elettrico/tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92 | tabella_retributiva | 2025-02-11 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92) |

??? note "Coverage notes"
    Salary model is split. base_salary = paga base (time-series, 4 tranches from the 2025-02-11 renewal); fixed_allowances = EDR (Elemento Distinto della Retribuzione) frozen at EUR 10.33/month since 1988, same for all levels.
    
    hourly_divisor 173.33 as stated by the contract (40h/week statutory base: 40 x 52 / 12). Actual weekly hours are 38 (non-shift) or 40 (shift); the divisor is contractually fixed on the 40h base.
    
    Seniority cadence 24 months (biennale), maximum 5 scatti (10 years of service per contract text). Amounts vary by level (kitech.it, April 2026).
    
    APPRENTICESHIP (Art. 15 CCNL 2025-02-11, apprendistato professionalizzante). Three tracks by qualification group. Gruppo C (dest CS, 36m): yr1=86%, yr2=90%, yr3=96%, then 100%. Gruppo B excl. BSS (dest B1, 36m): same progression. BSS + Gruppo A (dest BSS and A1, 24m): yr1=86%, yr2=96%, then 100%. Source: Art. 15 para.5 table (CCNL full text PDF filctemcgil.it, 2025-02-11). Note: only the four qualification levels explicitly cited in Art.15 (CS, B1, BSS, A1) are modelled; S-suffix variants (B1S, A1S, etc.) are senior-grade levels not addressed in the apprenticeship article.
    
    APR 2027 VALUES: confirmed via parametric derivation. The CCNL elettrici system applies a fixed valore-punto increase each tranche (same absolute amount per parametro per tranche). Apr 2026 and Apr 2027 increments are equal across all 14 levels (ratio=1.000 verified); A1S reference level gets +65.50 EUR matching the search-confirmed '+65 EUR average TEM' for Apr 2027 (fiscoetasse.com, pmi.it). October 2027 values verified against contratticcnl.it (all 14 levels match).
    
    Workers covered: approximately 63,000 in 687 companies (Enel SpA, Terna SpA, GSE, Sogin, Energia Libera and affiliated). Agreement signed 2025-02-11; valid until 2027-12-31.
    
    INPS rates from 2026-industria.json (industria sector, 50 employees tier). IRPEF 2026 brackets applied (L. 199/2025).
    
    COMPORTO (Art. 21 cc. 1-2, CCNL 11 febbraio 2025 (CNEL K051), PDF p. 49, https://pub-44429b7b330a431e94aea589bd6b8bed.r2.dev/K051/221685.pdf, sha256 6e317dea1b74d55618e655abc6477c5e006fbf960c2cacb8dc37ad61218ce8e3): 'il lavoratore, non in prova, ha diritto alla conservazione del posto per un periodo di 12 mesi. Si considera prosecuzione del periodo di malattia quella che intervenga non oltre 30 giorni dalla cessazione della malattia precedente'; 'raggiunga il limite di 18 mesi di assenza [...] entro l'arco massimo di 36 mesi consecutivi. Nel computo dei predetti limiti non si tiene conto dei periodi di degenza ospedaliera'. Modelled as max_duration_days 360 and sickness_rules.comporto_windows (540 days within 36 months, hospital stays left out); months of 30 days as the article states. The 32 months of the named serious illnesses and the apprentice and fixed-term limits are not modelled.
    
    contratticcnl.it shows data alignment errors for BSS, BS, B1 in the April 2026 and April 2027 columns; kitech.it April 2026 values used as authoritative for all 14 levels.
    

## Raw data

The contract file this page is generated from: [`agreement/elettrico-elettricita-futura.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/elettrico-elettricita-futura.json).

## Usage example

```python
--8<-- "docs/examples/agreement/elettrico-elettricita-futura/example.py"
```
