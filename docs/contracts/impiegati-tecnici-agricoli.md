# CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti

| | |
|---|---|
| **CNEL code** | `A021` |
| **Sector** | agricoltura |
| **Family** | `agricoltura` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-06-18 |
| **Workers (est.)** | ~80k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confagricoltura — Confederazione Generale dell'Agricoltura Italiana
    - CIA — Confederazione Italiana Agricoltori
    - Coldiretti — Confederazione Nazionale Coldiretti
    - FLAI-CGIL — Federazione Lavoratori Agroindustria
    - CONFEDERDIA — Confederazione Italiana dei Dirigenti e delle Alte Professionalità dell'Agricoltura
    - FAI-CISL — Federazione Agro Alimentare
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 12 verified / 8 derived / 0 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-06-18 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2024-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi nazionali di stipendio mensile conglobato of the seven categories against the signed CCNL of 18 June 2024. | confirmed | Art. 31, Tab. 1 (PDF p. 35, signed scan with text layer, read on the page image): the minimi nazionali di stipendio mensile conglobato from 01/07/2024 for Q and categories 1-6 match the 7 values of the file (file 1Q = Q, 1-6 = 1°-6°); they move to verified. Q is printed as 1.788,38 without the indennità di funzione, which Art. 18 lett. b (p. 24, 'una indennità mensile pari a 100 euro, da corrispondersi per 14 mensilità') grants on top, as the file models it.<br>Art. 31 (p. 34) applies the 5% from 1/04/2024 and 1.9% from 1/01/2025 to the stipendi contrattuali of the territorial contracts, not to the national minimi; Tab. 1 has a single date, 01/07/2024 (for territorial contracts renewed under the CCNL 7/07/2021 the minimi apply from the date of their next renewal and no later than 1/01/2027, p. 35). The coverage note that calls the 2025 tranche of the national table missing is wrong: there is no 2025 national minimo, and the open-ended period is correct.<br>The national minimo is conglobated (minimo base + contingenza + EDR, footnote p. 34 citing the Verbale 4.6.2008), matching the file's base_salary; territorial contracts may set higher stipendi contrattuali, and the minimo di stipendio integrativo is outside this table.<br>The ruleset names this source, published by FLAI-CGIL, a signatory: source_type contracting_party. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice clause (Art. 51 - Preavviso di risoluzione del rapporto, p. 47-48). | corrected | Notice bands by level, category and service checked against the PDF by a separate session (delegated search and independent verification): work_rules.notice. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | tranche_2025_01_missing: Art. 31 applies 5% (01/04/2024) and 1.9% (01/01/2025) to territorial contractual salaries, not a second national table. Tab. 1 has a single national minimum table dated 01/07/2024; all seven amounts match levels[*].base_salary, whose periods remain in force in 2025. The engine re |
| 2026-11-08 | gpt-6-sol (ai) | Allegato F (accordo 19 giugno 2018) of the CCNL 18 June 2024, pp. 85-88. Final encoding (dual_apprenticeship JSON) checked against the PDFs by a separate model session (.private flv2). | flagged | The third level (70% above 12 months, 80% up to 12) matches.<br>The first level follows 'l'anno scolastico/formativo di effettiva frequenza' (All. F p. 86) through the correspondence table of pp. 86-87, not the year of the contract the data keys it by: recorded as dual_apprenticeship_school_year.<br>Ambiguous in the text, kept as read: the base of the 10% training share ('di quella che gli sarebbe dovuta'). |
| 2026-11-15 | claude-opus-5-5 (ai) | Sick pay of art. 39 against the research of a separate model session; quote checked on the source. | corrected | Replaced 100% for 180 days of one episode with the 3+3, 5+5, 6+6 months of art. 39 summed over 12 months. |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: hourly_base, bands[0:night], bands[1:holiday], bands[3:night_holiday], none.shift_work.<br>Left out: bands[2:sunday]: quote quote_not_in_file; none.rest_day: skipped. |
| 2026-11-16 | claude-opus-5-5 (ai) | Parental leave by the hour (art. 32 c. 1-bis D.Lgs. 151/2001): the clause located in the cited file by sha256, read from the OCR of the page where the PDF is scanned. | corrected | Applied: work_rules.parental_hourly. |
| 2026-11-16 | claude-opus-5-5 (ai) | Number of monthly pays: the article on the additional months located in the cited file by sha256. | corrected | Sourced: 14 monthly pays. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | Livello 1Q — Quadri (dirigenti intermedi con autonomia gestionale) | € 1,788.38 | 2024-07-01 |
| `1` | Livello 1 — Funzionari e tecnici direttivi con responsabilita di settore | € 1,686.76 | 2024-07-01 |
| `2` | Livello 2 — Tecnici specializzati, impiegati di concetto superiore | € 1,541.41 | 2024-07-01 |
| `3` | Livello 3 — Tecnici e impiegati con funzioni di concetto di grado superiore | € 1,417.89 | 2024-07-01 |
| `4` | Livello 4 — Impiegati con mansioni di concetto o amministrative qualificate | € 1,335.93 | 2024-07-01 |
| `5` | Livello 5 — Impiegati d'ordine con compiti esecutivi | € 1,278.60 | 2024-07-01 |
| `6` | Livello 6 — Impiegati d'ordine di prima nomina, manovalanza di fatica | € 1,217.23 | 2024-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 33.05 |
| `1` | € 33.05 |
| `2` | € 29.44 |
| `3` | € 26.86 |
| `4` | € 24.79 |
| `5` | € 23.76 |
| `6` | € 22.21 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "impiegati-tecnici-agricoli/eban_agrifondo_missing · bilateral_funds · impact yes · open"
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and Agrifondo (supplementary pension) bilateral contributions are not modelled.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the EBAN and Agrifondo contributions as bilateral fund events, or model them.

!!! warning "impiegati-tecnici-agricoli/dual_apprenticeship_school_year · base_salary · impact yes · open"
    FIRST-LEVEL PERIOD (All. F, p. 86): 'la retribuzione, in ragione del titolo da conseguire e dell'anno scolastico/formativo di effettiva frequenza, è stabilita in percentuale'; the table of pp. 86-87 maps the school years of each course to the 45/55/60/70% rows. The data keys the rows by year of the contract, which differs for an apprentice hired after the first school year of the course.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Key the first-level rows by the course and the school year attended (Apprentice.school_year).

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

!!! note "inps_minimum_base_exempt_category · inps_employer · impact unknown · resolved"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Resolved: Tabella A gives the operai agricoli the 51.70, kept by art. 7 c. 5 from the 9.50% adjustment; circ. INPS 43/2026 recalls the legal minimums for the OTI and OTD and gives their part time 58.13 x 6/39 = 8.94. contribution/2026/agricoltura.json holds both as daily_by_category and hourly_categories. Tests: tests/mutation/ccnl_engine/contribution/minimum_base/test_rules.py.

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
| CNEL code A021, agreement date 18/06/2024, effective 01/07/2024. Contract covers impiegati, tecnici and quadri in agricultural sector. Expiry 31/12/2027. | altro | 2024-06-18 | [↗](https://www.contratticcnl.it/ccnl/a021/) |
| Salary levels: 1Q=1888.38 (base 1788.38 + IND_FUN 100.00), 1=1686.76, 2=1541.41, 3=1417.89, 4=1335.93, 5=1278.60, 6=1217.23. Hourly divisor 169. Daily divisor 26. Additional months 14 (tredicesima + quattordicesima). Seniority: biennale (24 months), 12 scatti, per-level amounts confirmed. Level 1Q listed as 1888.38 'with function allowance'; confirmed base 1788.38 + IND_FUN 100.00. | tabella_retributiva | 2024-06-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=3) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (levels 1-6). Single base_salary per level with no separate contingenza or EDR columns in the lavoro-economia.it table (consistent with A011 agricultural model). Level 1Q additionally carries an indennità di funzione of 100.00 EUR/month, additive to the base tabellare (source: lavoro-economia.it/ccnl/ccnl.aspx?c=3 showing 1Q total=1888.38 'with function allowance', decomposed as base 1788.38 + IND_FUN 100.00).
    
    RENEWAL: CCNL signed 18/06/2024 (quadriennio 2024-2027). One salary tranche modelled, effective 01/07/2024; the +1.9% tranche of 01/01/2025 is not modelled (tranche_2025_01_missing) (review of 2026-10-30)
    
    CNEL CODE: A021. Source: contratticcnl.it/ccnl/a021/.
    
    LEVELS: 7 levels (1Q, 1, 2, 3, 4, 5, 6). Level 1Q = Quadri (managerial cadre). Levels 1-6 = Impiegati/Tecnici from senior professional to entry-level clerk. Level 6 corresponds to first-year apprentice destination baseline.
    
    HOURLY DIVISOR: 169 hours/month. Formula: 39 h/week x 52 weeks / 12 = 169.00. Consistent with operai-agricoli-florovivaisti (A011) which also uses 169 for the 39h/week agricultural regime.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Standard for impiegati in the agricultural sector.
    
    SENIORITY: biennale (cadence 24 months), maximum 12 scatti. Per-level EUR amounts: 1Q and 1 = 33.05, 2 = 29.44, 3 = 26.86, 4 = 24.79, 5 = 23.76, 6 = 22.21. Levels 1Q and 1 share the same scatto amount.
    
    TAX SECTOR: AGRICOLTURA. INPS rates follow Gestione Previdenziale Speciale Agricola (impiegati OTI). Reuses 2026-agricoltura.json.
    
    APPRENTICESHIP. A021 specifica apprendistato professionalizzante per D.Lgs. 81/2015. Le percentuali retributive sono definite nel Piano Formativo Individuale (PFI) concordato tra le parti del singolo rapporto di lavoro e non pubblicate come tabella contrattuale. Non esiste una tabella fissa di percentuali nel testo del CCNL: l'array apprenticeship è vuoto per struttura contrattuale, non per omissione di modellazione. Analogo ai contratti pubblici dove l'apprendistato è escluso dall'ambito di applicazione. (Fonte: contratticcnl.it/ccnl/a021, leggeinchiaro.it CCNL A021.)
    
    INDENNITA DI FUNZIONE: level 1Q receives +100.00 EUR/month additive to base_salary 1788.38. Modelled as fixed_allowance code IND_FUN. Source: lavoro-economia.it/ccnl/ccnl.aspx?c=3 (total 1888.38 'with function allowance').
    
    INPS CONTRIBUTION BASE. The retribuzione convenzionale regime (INPS annual decree) applies to operai agricoli OTD/OTI (braccianti), NOT to impiegati agricoli. For impiegati OTI, contributions are computed on actual contractual salary pursuant to DL 338/1989 Art. 1 minimale (contribution base cannot fall below CCNL minimum). The engine applies rates to actual gross salary, which is correct for impiegati. Source: INPS Circ. 43/2026 covers operai only; standard regime applies to impiegati. (Confirmed by confagricolturapadova.it/wp-content/uploads/2020/02/Contributi_minimi_2020.pdf, laprevidenza.it.)
    
    APPRENTICE INPS RATES (contribution/2026/agricoltura.json): employer 10% plus NASpI 1.61% (INPS circ. 108/2018 par. 3.2, applied to the agricultural contribution by circ. 116/2013 par. 1) plus CISOA 1.50% (circ. 1/2023; 'CIS operai agricoli 1,5000' of circ. 43/2026 allegato 1) = 13.11% (4.61% and 6.11% in the first two years up to nine employees); worker 5.84%.
    
    FIRST- AND THIRD-LEVEL APPRENTICES (Allegato F): modelled in dual_apprenticeship (first level 45/55/60/70% by year at the conventional level, third level 70% or 80% by length; training at the employer 10% of the work pay, school hours unpaid). The contributions of these apprentices are the engine limitation dual_apprenticeship_contributions.
    
    SICKNESS (Art. 39 A, CCNL 18 giugno 2024, PDF pp. 39-40, https://www.flai.it/wp-content/uploads/2018/11/CCNL-quadri-e-impiegati-agricoli-2024-2027.pdf, sha256 94fba8a7cda3856266ed91ab8eec45264803a5396179772d67fbc995b7f7f076): comporto of 12 months; full pay for 3/5/6 months and half pay for 3/5/6 months by seniority (under 5 years, 5 to 10, over 10), the sick periods summed over 12 months. Modelled as sickness_rules.cumulation over a 1-year window, months of 30 days; how the comporto itself sums the episodes is not stated, and 365 days within one year end it only after a whole year of sickness.
    

## Raw data

The contract file this page is generated from: [`agreement/impiegati-tecnici-agricoli.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/impiegati-tecnici-agricoli.json).

## Usage example

```python
--8<-- "docs/examples/agreement/impiegati-tecnici-agricoli/example.py"
```
