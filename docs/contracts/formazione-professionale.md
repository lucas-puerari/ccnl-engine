# CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)

| | |
|---|---|
| **CNEL code** | `T261` |
| **Sector** | formazione professionale |
| **Family** | `istruzione-formazione` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-01 |
| **Workers (est.)** | ~19.8k |
| **Ruleset version** | `2026.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNOS-FAP
    - CIOFS-FP
    - FORMA
    - CNF
    - FLC-CGIL
    - FLC-CISL (CISL Scuola)
    - UIL Scuola RUA
    - SNALS-CONFSAL
    - ANIEF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 34 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-01 |
| **Last review** | 2026-11-08 |
| **Latest salary tranche** | 2025-09-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-08 | gpt-6-sol (ai) | Allegato 13 of the CCNL 2024-2027 signed 1 March 2024 (CNEL 236584), pp. 177-181. Final encoding (dual_apprenticeship JSON) checked against the PDFs by a separate model session (.private flv2). | flagged | The first-level and third-level percentages by year on the tabellare match.<br>Third level (p. 181): 'la percentuale retributiva di ingresso non può essere inferiore a quella percepita al termine dell'apprendistato professionalizzante'; not expressible, recorded as dual_apprenticeship_entry_floor.<br>Ambiguous in the text, kept as read: the base of the 10% training share ('di quella che gli sarebbe dovuta'). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `IX` | Livello IX — dirigente o quadro con massima responsabilita gestionale | € 3,222.79 | 2025-09-01 |
| `VIII` | Livello VIII — quadro superiore, direttore di centro o responsabile senior | € 2,627.71 | 2025-09-01 |
| `VII` | Livello VII — coordinatore didattico o responsabile di progetto complesso | € 2,440.58 | 2025-09-01 |
| `VI` | Livello VI — formatore senior o responsabile di area | € 2,331.43 | 2025-09-01 |
| `V` | Livello V — formatore o tecnico con autonomia operativa | € 2,057.63 | 2025-09-01 |
| `IV` | Livello IV — impiegato di concetto o tecnico qualificato | € 1,975.16 | 2025-09-01 |
| `III` | Livello III — operatore specializzato, mansioni tecnico-pratiche | € 1,834.59 | 2025-09-01 |
| `II` | Livello II — operatore qualificato, mansioni esecutive | € 1,730.71 | 2025-09-01 |
| `I` | Livello I — personale ausiliario e addetto a mansioni generiche | € 1,635.99 | 2025-09-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 30.00 |
| `II` | € 30.00 |
| `III` | € 30.00 |
| `IV` | € 40.00 |
| `V` | € 55.00 |
| `VI` | € 60.00 |
| `VII` | € 60.00 |
| `VIII` | € 60.00 |
| `IX` | € 60.00 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "formazione-professionale/dual_apprenticeship_entry_floor · base_salary · impact yes · open"
    THIRD-LEVEL ENTRY (Allegato 13, punto b, PDF p. 181): after a professionalising apprenticeship 'la percentuale retributiva di ingresso non può essere inferiore a quella percepita al termine dell'apprendistato professionalizzante'. The engine pays 70% in the first year whatever came before.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state the last professionalising percentage and pay the higher one.

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

!!! note "dual_apprenticeship_contributions · inps_employer · impact unknown · resolved"
    A first- or third-level apprentice (D.Lgs. 81/2015 artt. 43 and 45) is paid by the CCNL dual_apprenticeship tracks. The INPS contributions of a third-level apprentice are those of the professionalising one (L. 296/2006 art. 1 c. 773); a first-level one pays the employer 5% (D.Lgs. 150/2015 art. 32 c. 1 lett. b, made structural by L. 205/2017 art. 1 c. 110), the 1.5% and 3% of a firm with up to nine employees staying in the first two years, with no NASpI, no 0.30% (lett. c) and no dismissal contribution (lett. a): INPS circ. 108/2018 par. 3.4 (HTML sha256 6704846f...).

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the first-level rates of INPS circ. 108/2018 par. 3.4 (first_level_employer_rate) and no dismissal contribution; the hours of the final settlement are dual_final_settlement_hours (review of 2026-11-16).

!!! note "dual_final_settlement_hours · base_salary · impact unknown · resolved"
    A final-settlement run of a first- or third-level apprentice pays its month at Apprentice.hours and the ratei of the extra months at Apprentice.ratei_hours, the hours of the period they accrued over; a run liquidating ratei without them raises a missing-fact error.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice; run kind in termination.

    **Remediation:** Resolved: the ratei of the final settlement are weighed by Apprentice.ratei_hours.

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.cislscuola.it/download/ccnl-formazione-professionale-2024-2027/ | altro | 2024-03-01 | [↗](https://www.cislscuola.it/download/ccnl-formazione-professionale-2024-2027/) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2024-03-01 (CNEL-registered). Original text drafted 18/12/2023. Validity 01/01/2024-31/12/2027. Biennio economico 01/01/2024-31/12/2025.
    
    CONGLOBATED MINIMUMS (Art. 25): Art. 25-A lists 'stipendio tabellare' as the sole fundamental salary component. No contingenza or EDR column. Art. 29 defines hourly rate as 'retribuzione mensile/156' — the tabellare IS the total conglobated amount. fixed_allowances=[] for all levels.
    
    SALARY TABLE 1 (Art. 20): three tranches from primary CCNL PDF (cislscuola.it, signatory union). Tranche 0: 31/12/2023 carry-over from 01/01/2024. Tranche 1: +01/06/2024. Tranche 2 (secondo biennio): +01/09/2025. Second biennium negotiations collapsed 27/05/2026 — no further increase. valid_until=null on 2025-09-01 period is correct.
    
    HOURLY DIVISOR (Art. 29 para 6): 'retribuzione mensile/156'. Art. 29 para 4 states part-time pay is 'tanti trentaseiesimi' (36ths) of full pay, confirming 36h/week. 36x52/12=156. hourly_divisor=156 verified from contract text.
    
    ADDITIONAL MONTHS (Art. 27): tredicesima only, paid by 20 December each year. additional_months=13.
    
    SENIORITY — P.E.O.I. (Art. 21, Table 2): Progressione Economica Orizzontale Individuale. 5 quadrennial increments (cadence_months=48, maximum_count=5). Monthly amounts by level from Table 2: I=30, II=30, III=30, IV=40, V=55, VI=60, VII=60, VIII=60, IX=60. All from primary PDF.
    
    APPRENTICESHIP (Art. 7): Art. 7 para 3 delegates profile and salary definitions entirely to EBiNFoP within 30 days of signing. No specific salary model (percentage or under-classification) is defined in the CCNL text. apprenticeship=[] is correct — no under-classification or percentage model is established by the contract. SIMPLIFICATION: if EBiNFoP has since issued a framework, it is not captured here.
    
    INDENNITA (Art. 25 F-G): regional-bargaining indennita minima (700/1400 EUR) and sanita integrativa (7 EUR/month 'dalla data di attivazione dell accordo nazionale specifico'). These are not level-attached fixed allowances; excluded from fixed_allowances. No evidence the national sanita agreement has been activated.
    
    OVERTIME (Art. 39): three rates — diurno +15%, notturno or festivo +30%, notturno+festivo +50%. The combined notturno+festivo band (50%) is not in overtime_bands, although the engine supports it (OvertimeKind.NIGHT_HOLIDAY): such an event needs the caller's multiplier. Art. 41 para 3 (15% supplement for ordinary work at night or on holidays) is not modelled as a supplement band (supplement_bands): such an event needs the caller's amount (review of 2026-10-30)
    
    LEAVE (Art. 43, p. 30): 32 giorni lavorativi of ferie plus 4 giornate di ferie in place of the festività soppresse, 36 days counted on a 6-day week (on a 5-day week each day of ferie is 1.2 working days); twelfths, a month over 15 calendar days counting whole. The text sets no payment of the days not taken.
    
    DAILY DIVISOR (Art. 29 c. 5, p. 23): 'La quota giornaliera si determina convenzionalmente, dividendo la retribuzione mensile per 26'; the hourly quota is the monthly pay over 156 (c. 6, Art. 37: 36 hours a week, 156 a month).
    
    FIRST- AND THIRD-LEVEL APPRENTICES (Allegato 13): modelled in dual_apprenticeship (first level 50/55/60/70%, third level 70/80/90/100% of the tabellare by year; training at the employer 10% of the work pay, school hours unpaid).
    

## Raw data

The contract file this page is generated from: [`agreement/formazione-professionale.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/formazione-professionale.json).

## Usage example

```python
--8<-- "docs/examples/agreement/formazione-professionale/example.py"
```
