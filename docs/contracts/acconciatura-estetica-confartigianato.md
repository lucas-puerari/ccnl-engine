# CCNL Acconciatura ed Estetica — Confartigianato/CNA

| | |
|---|---|
| **CNEL code** | `H515` |
| **Sector** | acconciatura ed estetica |
| **Family** | `servizi-persona` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-05-20 |
| **Workers (est.)** | ~95k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Benessere-Acconciatori
    - CNA Unione Benessere e Sanità
    - Casartigiani
    - CLAAI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 21 verified / 9 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-05-20 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2026-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-08 | gpt-6-sol (ai) | Monthly values on scanned pages, each read twice from the page image by two independent sessions of another model, the second without being told the expected value. | confirmed | 20 values read identically by both readings and equal to the file. |
| 2026-11-08 | claude-opus-5-5 (ai) | FSBA ordinary contribution, art. 3 of the 2024 regulation, read on the text layer (analysis by a separate model session). | corrected | Added parameters.solidarity_fund FSBA: 0.45%+0.15% up to 15 employees, 0.75%+0.25% above, on the INPS base, fixed terms included. |
| 2026-11-14 | claude-opus-5-5 (ai) | INPS circ. 140/2012 par. 3.3 on the apprentice contribution, against the research of a separate model session. | confirmed | The cuneo reductions (0.91) do not apply to apprentices: the artigianato apprentice rates of the bundle are confirmed. |
| 2026-11-15 | claude-opus-5-5 (ai) | Holidays falling on a Sunday: the clause proposed by a separate model from the targeted research, its quote checked on the downloaded text. | confirmed | work_rules.sunday_holidays: 01-01, 01-06, 04-25, 05-01, 06-02, 08-15, 11-01, 11-04, 12-08, 12-25, 12-26, patron; divisor 26 |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Level 1 — technical director / senior supervisor | € 1,722.76 | 2026-10-01 |
| `2` | Level 2 — specialist worker / technical supervisor | € 1,573.78 | 2026-10-01 |
| `3` | Level 3 — qualified worker (hairdresser/beautician) | € 1,492.00 | 2026-10-01 |
| `4` | Level 4 — auxiliary worker / entry-level apprentice | € 1,406.73 | 2026-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `4` | € 7.23 |
| `3` | € 7.75 |
| `2` | € 8.26 |
| `1` | € 9.30 |

## Apprenticeship

**gruppo_1** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_1_ridotto** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_2** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3** (type: `percentage`)  
Destination levels: `2`  
percentage: 0.85

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "acconciatura-estetica-confartigianato/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

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

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
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

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confartigianatomarcatrevigiana.it/wp-content/uploads/2024/09/ccnl-benessere-app.prof-fino-30.9.24.pdf | altro | 2024-05-20 | [↗](https://www.confartigianatomarcatrevigiana.it/wp-content/uploads/2024/09/ccnl-benessere-app.prof-fino-30.9.24.pdf) |
| https://www.studiomion.it/tabelle-retributive/tabelle-retributive-acconciatura-estetica/ | tabella_retributiva | 2024-05-20 | [↗](https://www.studiomion.it/tabelle-retributive/tabelle-retributive-acconciatura-estetica/) |
| https://www.ilccnl.it/contratto/acconciatura-estetica/ | tabella_retributiva | — | [↗](https://www.ilccnl.it/contratto/acconciatura-estetica/) |
| CCNL Area Benessere (acconciatura, estetica, tricologia, tatuaggio, piercing, centri benessere), rinnovo 20 maggio 2024, scansione firmata | associazione | 2024-05-20 | [↗](https://confartigianatomarcatrevigiana.it/wp-content/uploads/2024/05/CCNL-AREA-BENESSERE-22.5.2024-NR.9-H515.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati — contingenza and EDR fully absorbed). Back-calculation: May 2024 L3=1379.00/173=7.97 EUR/h; L2=1454.58/173=8.41 EUR/h; L1=1592.29/173=9.20 EUR/h — consistent divisor confirms conglobated model (lexplain.it + ilccnl.it).
    
    TRANCHE DATES: four tranches — 2024-05-01 (retroactive, renewal signed 20 May 2024), 2025-01-01, 2026-01-01, 2026-10-01. Source: studiomion.it salary tables; cross-checked ilccnl.it for Jan 2026 values.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 12 CCNL). Formula: 40 h/week × 52/12 = 173.33, rounded to 173 per contract usage. Confirmed: 1379.00/7.97=173.0 (L3 May 2024).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it Art. 40; informaimpresa.it ('tredici mensilità' explicitly stated as basis for Responsabile Tecnico allowance calculation).
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level amounts: L1=9.30, L2=8.26, L3=7.75, L4=7.23 EUR/scatto. Source: ilccnl.it (current database), cross-checked CISL 2013 PDF (amounts unchanged by 2024 renewal, which only introduced a 6 EUR apprentice-specific scatto).
    
    APPRENTICESHIP Gruppo 1 (acconciatori, estetisti, tricologi, tatuatori → destination level 3, max 5 years), track 'gruppo_1'. Primary source: Confartigianato Marca Trevigiana PDF (ccnl-benessere-app.prof-fino-30.9.24.pdf) for the pre-Oct-2024 table; post-Oct-2024 update (filcams.cgil.it + fisascat.it) raised months 1-12 from 65% to 70%, making months 1-18 uniformly 70%. Modelled table: 0-18=70%, 18-24=78%, 24-36=85%, 36-48=90%, 48-54=95%, 54+=100%.
    
    APPRENTICE SENIORITY: apprentice-specific scatto of 6 EUR (Art. 25 of the 2024 renewal, from 2024-10-01) modelled as seniority_increments.apprentice_amount.
    
    RESPONSABILE TECNICO: 100 EUR x 13 mensilità for workers designated Responsabile Tecnico at level 1 or 2, modelled as a role-scoped allowance (role 'responsabile_tecnico').
    
    PRE-MAY-2024 SALARY: the final tranche of the 2022 renewal (from 2023-02-01: L1=1511.46, L2=1380.74, L3=1309.00, L4=1234.19) is modelled; earlier periods are not.
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    
    APPRENTICESHIP Gruppo 3 (impiegati amministrativi, destination level 2, 3 anni / 6 semestri): 70/70/70/78/85/85 per semester. Source: consulenza.it circolare acconciatura 2024; lexplain.it tabella apprendistato acconciatori (medium-high confidence: two concordant secondary sources; primary accordo tables not online).
    
    APPRENTICE INPS RATES (artigianato): 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI and integrativo, 11.61% for the employer (3.11% and 4.61% in the first two years of a firm up to 9 employees) and 5.84% for the worker. The 0.91 reduction of the artisan employers does not apply to apprentices: 'sul contributo per gli apprendisti non trovano applicazione le riduzioni del cuneo contributivo di cui alle leggi n. 388/2000 e n. 266/2005' (INPS circ. 140/2012 par. 3.3, https://servizi2.inps.it/servizi/Bussola/VisualizzaDoc.aspx?sVirtualURL=/Circolari/Circolare%20numero%20140%20del%2014-12-2012.htm, sha256 67d04317e66825fdb2cf6aa0b3106e644d76461e3e6ec17cd456b307948701a7). The wage-integration contribution of the sector is the FSBA, paid outside INPS (F24, code EBNA), not part of the INPS employer rate.
    
    APPRENTICESHIP from 1 October 2024 (renewal of 20 May 2024, scanned p. 6 read on the image), percentages by semester of the pay of the final level: Tabella 1, gruppo 1 (5 years) 70 70 70 78 85 85 90 90 95 100: track gruppo_1; Tabella 3, gruppo 1 with a post-compulsory school title or qualification (4 years and 6 months, p. 4) 70 70 70 78 85 85 90 90 100: track gruppo_1_ridotto; Tabella 2, gruppo 2 (18 months) 70 80 100: track gruppo_2; Tabella 4, gruppo 3 (3 years) 70 70 70 78 85 85: track gruppo_3. Level 3 is the destination of several tracks: state Apprentice.track. Not modelled: the 3-year cap of the apprentices of non-artisan small and medium firms and the extension of the duration by a suspension of 60 days or more (p. 4).
    

## Raw data

The contract file this page is generated from: [`agreement/acconciatura-estetica-confartigianato.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/acconciatura-estetica-confartigianato.json).

## Usage example

```python
--8<-- "docs/examples/agreement/acconciatura-estetica-confartigianato/example.py"
```
