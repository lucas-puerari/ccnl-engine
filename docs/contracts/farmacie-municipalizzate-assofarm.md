# CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)

| | |
|---|---|
| **CNEL code** | `H124` |
| **Sector** | Farmacie municipalizzate e partecipate da enti locali |
| **Family** | `farmacie` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2022-07-07 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOFARM
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 74 verified / 16 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2022-07-07 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2029-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Articolo 20 - Tredicesima e quattordicesima mensilita' (p. 20): "Le frazioni di mese pari o superiori a 15 giorni vengono computate come mese intero e si trascurano quelle inferiori.". Match: at_least 15. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: art. 23 (p. 21, OCR) and Allegato F of the CCNL of 7 July 2022, with art. 41 c. 1 D.Lgs. 81/2015. | corrected | Art. 23 c. 1: 'Il lavoratore a tempo indeterminato ha diritto a 15 scatti biennali di anzianità'; apprenticeship 'è un contratto di lavoro a tempo indeterminato' (D.Lgs. 81/2015 art. 41 c. 1) and the CCNL excludes no apprentice: the increments of the level the apprentice is paid at. |
| 2026-11-07 | claude-opus-5-5 (ai) | Ipotesi Farmacie comunali 2027-2029 of 15 September 2026: art. 10 and Allegati B-E (pp. 10, 20-22, page images). | corrected | Four tranches of the retribuzione base mensile from October 2026 to July 2029; level 6 abolished into level 5; quadri allowances and seniority amounts unchanged; the base of level 1C at 31 December 2024 is printed 2,266.38 (the file has 2,266.37). |
| 2026-11-08 | gpt-6-sol (ai) | Monthly values on scanned pages, each read twice from the page image by two independent sessions of another model, the second without being told the expected value. | confirmed | 37 values read identically by both readings and equal to the file. |
| 2026-11-15 | claude-opus-5-5 (ai) | Sick pay and comporto against the research of a separate model session; quotes checked on the source. | corrected | Replaced 180 days of one episode with the chain of art. 32 reset after 60 days, comporto 16 or 24 months, 6 months in full and 6 at half pay. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | 1o livello Q - Direttore responsabile e area manager | € 2,712.11 | 2029-07-01 |
| `1S` | 1o livello super - Direttore responsabile con funzioni direttive | € 2,618.86 | 2029-07-01 |
| `1C` | 1o livello C - Farmacista collaboratore con funzioni speciali | € 2,501.78 | 2029-07-01 |
| `1_12` | 1o livello + 12 anni - Farmacista collaboratore con 12+ anni di servizio | € 2,329.97 | 2029-07-01 |
| `1_2` | 1o livello + 2 anni - Farmacista collaboratore con 24+ mesi di servizio | € 2,329.97 | 2029-07-01 |
| `1` | 1o livello - Farmacista collaboratore | € 2,329.97 | 2029-07-01 |
| `2` | 2o livello - Lavoratori con funzioni di coordinamento o tecnico-specialistiche | € 2,070.16 | 2029-07-01 |
| `3` | 3o livello - Lavoratori con conoscenze tecnico-pratiche qualificate | € 1,966.49 | 2029-07-01 |
| `4` | 4o livello - Lavoratori con compiti esecutivi e conoscenze tecnico-pratiche | € 1,850.81 | 2029-07-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze operative | € 1,719.37 | 2029-07-01 |
| `6` | 6o livello - Lavoratori con mansioni di pulizia e operazioni semplici | € 1,719.37 | 2029-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 26.50 |
| `1S` | € 25.82 |
| `1C` | € 25.31 |
| `1_12` | € 25.31 |
| `1_2` | € 25.31 |
| `1` | € 25.31 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.66 |
| `5` | € 20.14 |
| `6` | € 19.63 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "farmacie-municipalizzate-assofarm/terziario_rates_proxy · inps_employer · impact unknown · open"
    INPS RATES. Terziario proxy used. ASSOFARM entities operate as aziende speciali or società di gestione farmacia (private-law entities under municipal control); the contract is registered CNEL H124 and negotiated by UGL Terziario — standard private-sector INPS regime (terziario) is the expected classification. Note: CCNL text references "INPS Gestione ex INPDAP" in benefit provisions, suggesting legacy workers transferred from public-sector management may retain the ex-INPDAP pension regime — contribution rates for those workers differ. No sector-specific INPS circular identified; kitech.it does not list a dedicated contribution table for farmacie municipalizzate. Simplification retained.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification against a sector circular, including ex-INPDAP legacy workers.

!!! warning "farmacie-municipalizzate-assofarm/renewal_2027_2029 · base_salary · impact yes · open"
    RENEWAL 2027-2029 (ipotesi of 15 September 2026, Allegati B-E pp. 20-22; the parties report the definitive signature of 23 October 2026, whose text is not public): the retribuzione base mensile from 1 October 2026, 1 July 2027, 1 July 2028 and 1 July 2029 is modelled; level 6 is abolished and paid as level 5 from 1 October 2026 (art. 10). Not modelled: the una tantum of Allegato D (two instalments with the January and July 2027 pay, 290.00 to 190.00 EUR per instalment by level), and the seniority of a former level 6 worker, kept at the level 6 amounts already matured.

    **Applies when:** `base_salary` applies; from 2026-10-01.

    **Remediation:** Check the definitive text of 23 October 2026, model the una tantum of Allegato D as una tantum items, then remove this note.

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
| https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf | altro | 2022-07-07 | [↗](https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf) |
| Ipotesi di accordo di rinnovo CCNL Farmacie comunali 2027-2029, 15 settembre 2026 | associazione | 2026-09-15 | [↗](https://www.assofarm.it/wp-content/uploads/2026/09/CCNL-Assofarm-2027-2029-firmato.pdf) |

??? note "Coverage notes"
    Salary model: conglobated. Allegato B shows unified retribuzione di base with no separate contingenza or EDR columns. Back-calculation: L1=2109.97/173=12.20 EUR/h, L3=1777.29/173=10.27 EUR/h, L6=1421.48/173=8.22 EUR/h (all consistent with divisor 173).
    
    Hourly divisor 173: Art. 18 explicit: 'La quota oraria di retribuzione si ottiene dividendo la retribuzione mensile per 173'.
    
    Additional months: 14. Art. 20 explicit: quattordicesima (luglio) + tredicesima (dicembre).
    
    IQ (Indennita Quadri): Allegato C, effective 01/07/2022. Levels 1Q=160, 1S=150, 1C=145 EUR/month.
    
    IS (Indennita Speciale): Art. 19bis + Allegato A. Level 1+12anni=130, Level 1+2anni=100 EUR/month. Unchanged in 2022 renewal (Allegato C covers only IQ increments; Art. 19bis refers to Tabella A 2015 values).
    
    Seniority: 15 scatti biennali per Allegato E, decorrenza 1 gennaio 2014.
    
    Apprenticeship: Allegato F, under-classification. Farmacista collaboratore stays at Primo livello for all 36 months (levels_below=0). Non-pharmacist roles (Coadiutore, Capo settore, Addetto amministrativo): months 1-12 at Sesto, months 13-36 at Quinto, exit Quarto.
    
    Contract valid 07/07/2022-31/12/2024, ultrattivo since 01/01/2025 (no successor deposited at CNEL as of 2026-09-05). Third tranche (01/07/2024) modelled open-ended.
    
    Headcount: 6,389 workers, 335 employers (ASSOFARM primary source).
    
    Levels 1_12 and 1_2 (Farmacista Collaboratore with 12+ or 2+ years continuous service) are automatic time-in-grade progressions under Art. 19bis. Engine cannot model auto-advancement; implemented as static level codes distinguishable by IS allowance amount (1_12=130, 1_2=100 EUR/month). Structural engine limitation — correct payroll calculation requires knowing the worker's actual time-in-grade.
    
    Function and Tech-Prof allowances shown in kitech for L2/L3/quadri sub-levels are EXCLUDED. They appear in no allegato of the signed CCNL; Art. 17 defines retribuzione di base as Tabelle A+B only. Verification: 1Q base+IQ=2456.91+160=2616.91 vs kitech 2758.68; delta 141.77 = sum of the two extra kitech lines — confirming they are historical/personal elements outside the contractual minimum. Exclusion is correct.
    
    SICKNESS (Art. 32, CCNL 7 luglio 2022, PDF pp. 24-25; the renewal of 2026 leaves it unchanged): comporto 'mesi 16' up to three years of service and 'mesi 24' above; 'Si considera prosecuzione del periodo di malattia e/o infortunio quella che intervenga non oltre i 60 giorni dalla ripresa del servizio'; integration 'a partire dal primo giorno di malattia e per un massimo di 12 mesi', 100% for the first 6 and 50% for the next 6. Modelled as sickness_rules.cumulation over the chain; the 365 days in full of an oncological illness (c. 17) and the TBC rules (c. 4) are not modelled. Source: https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf, sha256 31dbf30a09f942830176634dff56320a55b830e07cee11f5629595192d852365.
    

## Raw data

The contract file this page is generated from: [`agreement/farmacie-municipalizzate-assofarm.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/farmacie-municipalizzate-assofarm.json).

## Usage example

```python
--8<-- "docs/examples/agreement/farmacie-municipalizzate-assofarm/example.py"
```
