# CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN

| | |
|---|---|
| **CNEL code** | `S305` |
| **Sector** | Pubblica Amministrazione |
| **Family** | `pubblico-impiego` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-07-01 |
| **Workers (est.)** | ~1,2M |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FSUR
    - FLC CGIL
    - UIL SCUOLA RUA
    - SNALS CONFSAL
    - GILDA UNAMS
    - ANIEF

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

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 60 verified / 45 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-07-01 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables of the seven scuola profiles, leave, sickness, seniority, overtime and the daily quota, against the signed ARAN texts of 2007, 2024, 2025 and 2026. | corrected | Every monthly tabellare was the annual amount over 13; the tables are per 12 mensilità plus the tredicesima: the values were about 7.7% low (e.g. Docente infanzia 2024: 1,724.65 -> 1,868.37).<br>The pre-2024 periods were back-calculated with the increments times 13 and started on 2022-01-01; they are now the tables of the CCNL 2019-2021, in force from 1 February 2023.<br>The CCNL 2025-2027 on the economic treatment, signed definitively on 1 July 2026, was missing: periods from 1.1.2025, 1.1.2026 and 1.1.2027 added.<br>Signatories: FLC CGIL did not sign the CCNL 2022-2024 (it signed the 2025-2027); ANIEF signed both and was missing.<br>Ferie: 32 days, 30 for the first 3 years (CCNL 2007 art. 13), not 28.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 17), not 270 days at 100%.<br>Overtime: the scuola pays fixed hourly amounts, not percentages: the 15/30/30/50% bands had no basis and are removed.<br>Daily quota: no scuola text fixes it; by_26 is now assumed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Overtime of the scuola ATA staff: Tabella E1.7 of the CCNL 2019-2021 and the overtime articles of the CCNL 2022-2024 and 2025-2027. | corrected | The ATA 'prestazioni aggiuntive' are paid at fixed hourly amounts by area from 1 January 2024 (Tabella E1.7): nine bands in EUR per hour by area and time of day, now paid by the engine.<br>The CCNL 2022-2024 (art. 23) and 2025-2027 (art. 11) update only the università overtime (Tabella B4): the scuola amounts stay those of 2024.<br>The docenti ore aggiuntive (Tabella E1.6) are by activity, not by time of day: left to the caller (limitation fixed_hourly_overtime, docenti levels). |
| 2026-10-12 | claude-opus-5-5 (ai) | Fasce stipendiali of the scuola staff, 2023-2027. | corrected | Every worker was paid the first fascia (0-8 years): the five higher fasce are now seniority steps, read on the tables of the three CCNL.<br>DOCENTE_SECONDARIA joined the scuola media and the laureato di II grado, equal in the first fascia only: split into DOCENTE_SECONDARIA (scuola media) and DOCENTE_LAUREATO_SECONDARIA_II. |
| 2026-10-12 | claude-opus-5-5 (ai) | Months from 1.1.2022 to 31.1.2023 (CCNL 2019-2021 Tabella C1). | corrected | The file started on 1.2.2023 (limitation before_february_2023): the tabellare dal 1.1.2021 and the elemento perequativo by fascia of Tabella C1 now cover 2022 and January 2023. |
| 2026-10-17 | claude-opus-5-5 (ai) | The number of instalments of the elemento perequativo of the CCNL 19/04/2018 the file pays until its conglobamento. | corrected | The 35 elemento perequativo records of the Scuola levels move from assumed to derived: INPS msg. 3224/2018 reads the element as paid 'con cadenza mensile', Tabella D2 of the CCNL 19/04/2018 gives 10 monthly instalments in 2018, and Tabella C1 of the CCNL 6/12/2022 (p. 244) prints the yearly amount as twelve monthly ones (308,04 = 12 x 25,67). No text puts it in the tredicesima. Art. 37 of the Scuola section was not read, so the records stay derived.<br>The absence rule stays assumed: no text of the comparto fixes the daily quota of an unpaid absence of the scuola staff. |
| 2026-11-15 | claude-opus-5-5 (ai) | RPD tables of the CCNL 2019-2021 (E1.2), 2022-2024 (A3) and 2025-2027 (A3), text layer, against the research of a separate model session. | corrected | Added the RPD of the docenti by seniority band, 2022-2027; it is not an indennità di funzione by order of school. |
| 2026-11-15 | claude-opus-5-5 (ai) | Tabella 2 IIS of the CCNL scuola 24 luglio 2003 (PDF p. 121), text layer. | corrected | The IIS conglobata of the docenti di scuola materna ed elementare is 6,384.11 a year at every position: left out of the ENAM base. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `FUNZIONARIO_ED_ESPERTO` | ATA: Funzionario ed esperto (ex dsga, direttori servizi generali) | € 2,249.26 | 2027-01-01 |
| `DOCENTE_LAUREATO_SECONDARIA_II` | Docente laureato degli istituti secondari di II grado | € 2,141.60 | 2027-01-01 |
| `DOCENTE_SECONDARIA` | Docente scuola secondaria di I grado (scuola media, educazione fisica) | € 2,141.60 | 2027-01-01 |
| `DOCENTE_DIPLOMATO_SECONDARIA` | Docente diplomato degli istituti secondari di II grado | € 1,978.53 | 2027-01-01 |
| `DOCENTE_INFANZIA_PRIMARIA` | Docente scuola dell'infanzia e primaria | € 1,978.53 | 2027-01-01 |
| `ASSISTENTE` | ATA: Assistente amministrativo, assistente tecnico, cuoco, infermiere | € 1,717.20 | 2027-01-01 |
| `OPERATORE` | ATA: Operatore scolastico (nuovo profilo dal 1/5/2024 CCNL 18/1/2024) | € 1,615.41 | 2027-01-01 |
| `COLLABORATORE_SCOLASTICO` | ATA: Collaboratore scolastico (ex bidello, ex commesso) | € 1,540.49 | 2027-01-01 |

## Seniority increments

**Cadence:** every 108 months  
**Maximum:** 5 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

### Without monetary impact

!!! note ""
    CNEL S305 confermato per comparto, include tutte le sezioni (scuola, università, ricerca, AFAM).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL 2025-2027 sui principali aspetti del trattamento economico, signed definitively on 1 July 2026 by ARAN and every union of the comparto. Tabella A2 (pp. 18-19): tabellare from 1.1.2025, 1.1.2026, 1.1.2027. | altro | 2026-07-01 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/07/2026_07_01_CCNL_C_IR_2025-2027.pdf) |
| CCNL 2022-2024 (FLC CGIL did not sign). Tabella A2 (pp. 50-51): tabellare from 1.1.2024. | altro | 2025-12-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/12/2025_12_23_COMP-IR_2022-2024.pdf) |
| CCNL 2019-2021. Tabelle C1 and E1.5 (pp. 246, 256): tabellare from 1.2.2023. | altro | 2024-01-18 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/01/2024_01_18_COMP-IR_2019-2021.pdf) |
| CCNL Scuola 2006-2009, still in force for ferie (art. 13), malattia (art. 17) and tredicesima (art. 80). | altro | 2007-11-29 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/07/CCNL-SCUOLA-2006-2009.pdf) |

??? note "Coverage notes"
    Platea ~1,2M: ~800k docenti (infanzia, primaria, secondaria I e II), ~230k ATA scuola, ~130k personale università e ricerca, ~80k AFAM (quifinanza.it).
    
    RPD (Retribuzione Professionale Docenti, art. 83 CCNL 2007; Tabella A3): the same for every order of school, by service seniority (0-14, 15-27, 28 and over years), on 12 monthly payments: 205.10 / 252.10 / 320.30 from 1 January 2025, 210.40 / 258.70 / 328.60 from 1 January 2027; the worker's recognised seniority (Employment.seniority) chooses the band.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Personale università, ricerca e AFAM: non modellato separatamente (trattamento retributivo distinto con sezioni specifiche nel CCNL). SIMPLIFICATION: unico JSON copre principalmente la scuola.
    
    Hourly divisor 156 = 36h/settimana × 52/12, the hourly rate of the ATA staff. The docenti (orario cattedra, 18 hours of teaching) need no INAIL daily base: the staff of the State schools takes no INAIL indemnity of temporary inability (gestione per conto dello Stato) and the school pays the whole pay of an injury (insured_absence.injury).
    
    PENSION FUND. Fondo Scuola Espero (1% + 1%); enrolment is a fact, the silenzio-assenso of the hires from 2019 is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    ASSICURAZIONE SOCIALE VITA. The employers of this CCNL are Amministrazioni dello Stato (the State schools; the forze di polizia), which INPS circ. 104/2014 leaves out of the Assicurazione Sociale Vita (ex ENPDEP): meta.public_life_insurance is false.
    
    LEVELS. The Tabelle A1 and A2 of the CCNL 2022-2024 (from 1.1.2024) list 'Docente scuola dell'infanzia ed elementare' and 'Docente diplomato istituti sec. II grado' as two rows with the same amounts (22,420.48 a year in the first band): two levels with the same minimum, DOCENTE_INFANZIA_PRIMARIA and DOCENTE_DIPLOMATO_SECONDARIA, since only the first owes the ENAM.
    
    ENAM (L. 93/1957 art. 3): 1% of 80% of the stipendio of a permanent teacher of the scuola dell'infanzia and primaria, the IIS conglobata in the tabellare left out: EUR 6,384.11 a year on 12 months (CCNL 24.7.2003 Tabella 2, PDF p. 121), 532.01 a month (parameters.enam_iis_monthly).
    
    The ore aggiuntive of the docenti are paid at fixed hourly amounts by activity (CCNL 2019-2021 Tabella E1.6: corsi di recupero 55,00, insegnamento 38,50, non di insegnamento 19,25): bands OT_CORSO_RECUPERO_DOC, OT_INSEGNAMENTO_DOC and OT_NON_INSEGNAMENTO_DOC on the overtime kinds corso_recupero, insegnamento_aggiuntivo and non_insegnamento_aggiuntivo. The ATA areas are paid by the bands of Tabella E1.7.
    
    FASCE STIPENDIALI: the six fasce of anzianità di servizio (0-8, 9-14, 15-20, 21-27, 28-34, da 35) are paid as five seniority steps after 9, 15, 21, 28 and 35 years, each the difference between the monthly tabellari of two fasce (CCNL 2019-2021 Tabelle C1 and E1.5, 2022-2024 and 2025-2027 Tabella A2). The seniority is the anzianità di servizio recognised for the fasce (ricostruzione di carriera), which the caller states; the engine does not reconstruct it. The scuola media and the laureato di II grado have the same first fascia and differ above it: two levels, DOCENTE_SECONDARIA and DOCENTE_LAUREATO_SECONDARIA_II.
    
    FROM 1.1.2022 TO 31.1.2023: the tabellare dal 1.1.2021 of Tabella C1 of the CCNL 2019-2021 (column 1) and, apart, the elemento perequativo by fascia (column 2, 12 instalments assumed), conglobated in the tabellare from 1.2.2023.
    
    SALARY TABLES: monthly tabellare = annual tabellare of the fascia 0-8 over 12 (the tables are 'per 12 mensilità cui aggiungere la 13^ mensilità'). 1.2.2023-31.12.2023: CCNL 2019-2021 Tabelle C1 and E1.5; 2024: CCNL 2022-2024 Tabella A2; 2025, 2026, 2027: CCNL 2025-2027 Tabella A2.
    
    CNEL S305 da kitech.it per comparto Istruzione e Ricerca personale docente. Confermato coerente con S325 (area dirigenza IR).
    

## Raw data

The contract file this page is generated from: [`agreement/istruzione-ricerca-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/istruzione-ricerca-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/istruzione-ricerca-aran/example.py"
```
