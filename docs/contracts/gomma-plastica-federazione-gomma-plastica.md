# CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)

| | |
|---|---|
| **CNEL code** | `B371` |
| **Sector** | gomma-plastica |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federazione Gomma Plastica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, sickness |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 70 verified / 7 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2028-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The TEM minimi of the ten levels against the minimi tables of the renewals of 26 January 2023 (2023-2025) and 10 December 2025 (2026-2028), both published by FILCTEM-CGIL. | corrected | Rinnovo 26 gennaio 2023 (signed scan with the integration of 2 February 2023, PDF p. 15, read on the page image): Art. 17 c. 3 prints the minimi of levels I-Q from 1/1/2023, 1/1/2024 and 1/4/2025. The 30 values of the file match.<br>Rinnovo 10 dicembre 2025: the signed ipotesi (45-page scan, PDF p. 31) states only the level F increment (60 from 1/01/2026, 60 from 1/04/2027, 60 from 1/04/2028, 15 from 1/12/2028); FILCTEM-CGIL publishes the per-level table of Art. 17 as a separate one-page file, which prints the minimi of the ten levels on the four dates and the per-level increments. The 40 values of the file were derived parametrically from level F; 11 differ by one or two cents from the printed table and are corrected.<br>The file's base_salary is the conglobated TEM (Art. 17 Paragrafo A), the same item the tables print. The ruleset names a source published by FILCTEM-CGIL, a signatory: source_type contracting_party.<br>Corrected to the printed table: I 2027-04-01: 1662.67 -> 1662.66; I 2028-04-01: 1710.60 -> 1710.59; I 2028-12-01: 1722.59 -> 1722.57; G 2028-04-01: 1995.28 -> 1995.27; E 2027-04-01: 2136.42 -> 2136.43; E 2028-04-01: 2198.02 -> 2198.03; E 2028-12-01: 2213.42 -> 2213.43; D 2028-04-01: 2290.45 -> 2290.44; D 2028-12-01: 2306.50 -> 2306.49; B 2028-04-01: 2350.47 -> 2350.48; B 2028-12-01: 2366.94 -> 2366.95. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: art. 2 par. A c. 9 and art. 19 c. 1 of the stesura of 12 April 2021 (pp. 13, 30). | corrected | Apprentices are paid the minimo contrattuale of their level alone; the scatti are a separate element of the pay: none during the apprenticeship. |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto of several illnesses, against the research of a separate model session; quote checked on the OCR of the source. | corrected | Added the comporto window; the pay bands of the CCNL are recorded as a limitation. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — senior manager grade (quadro under L. 190/1985), highest responsibility | € 2,664.67 | 2028-12-01 |
| `A` | A — quadro, highly specialised technical or functional expert | € 2,508.94 | 2028-12-01 |
| `B` | B — technical or administrative manager, high professional grade | € 2,366.95 | 2028-12-01 |
| `C` | C — department head, white-collar employee with operational autonomy | € 2,335.85 | 2028-12-01 |
| `D` | D — team leader, qualified technical/administrative employee | € 2,306.49 | 2028-12-01 |
| `E` | E — highly skilled worker, expert technical employee | € 2,213.43 | 2028-12-01 |
| `F` | F — skilled worker, technical employee (CCNL reference level) | € 2,156.12 | 2028-12-01 |
| `G` | G — qualified worker 2nd category, white-collar employee | € 2,009.25 | 2028-12-01 |
| `H` | H — qualified worker 1st category, clerical staff | € 1,916.08 | 2028-12-01 |
| `I` | I — elementary tasks, simple operations with brief training | € 1,722.57 | 2028-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 20.14 |
| `A` | € 18.59 |
| `B` | € 16.53 |
| `C` | € 16.53 |
| `D` | € 16.53 |
| `E` | € 13.94 |
| `F` | € 13.94 |
| `G` | € 13.43 |
| `H` | € 11.88 |
| `I` | € 10.33 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `G`, `F`, `E`, `D`, `C`, `B`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "gomma-plastica-federazione-gomma-plastica/q_allowance_2023_unverified · base_salary · impact unknown · resolved"
    Q LEVEL INDENNITA' DI FUNZIONE (p. 40 of the 2021 stesura): 'Ai lavoratori con qualifica di quadro è riconosciuto con decorrenza 1.9.2008 un nuovo elemento retributivo denominato "Indennità di funzione", pari a euro 50,00 lordi': the 50 EUR are in force from 2008, through the first modelled tranche of 2023; the renewal of 26 January 2023 does not amend it.

    **Applies when:** `base_salary` applies; level in Q; before 2025-04-01.

    **Remediation:** Resolved: 50 EUR from 1 September 2008 (2021 stesura, p. 40); read on 2026-11-06.

!!! warning "gomma-plastica-federazione-gomma-plastica/apprenticeship_period_boundaries · base_salary · impact unknown · open"
    APPRENTICESHIP under_classification (art. apprendistato professionalizzante CCNL Gomma e Plastica; rule from contratticcnl.it: the apprentice cannot be classified more than two levels below the destination). Track 'professionalizzante' for destinations G, F, E, D, C, B: 0-12 months two levels below, 12-24 one level below, then destination. The 12/12 boundaries are an approximation (no public monthly table). H (only one level below exists), I, A and Q are not modelled as destinations.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in B, C, D, E, F, G.

    **Remediation:** Source the monthly apprenticeship table and correct the 12/12 period boundaries.

!!! warning "gomma-plastica-federazione-gomma-plastica/sickness_pay_bands · sickness · impact yes · open"
    SICKNESS PAY BANDS (art. 39): 100% net for the first 3, 4 or 5 months by seniority (up to 3, up to 6, over 6 years), then 2/3 for 3, 5 or 7 months while INPS pays, 50% otherwise within the comporto; the file pays 100% for 180 days of an episode.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 100%, 2/3 and 50% bands of art. 39 by seniority.

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

!!! warning "parental_extra_month_share · parental_leave · impact unknown · unsourced"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour follows the national CCNL rule on the hours of a day of leave (art. 32 c. 1-bis D.Lgs. 151/2001, work_rules.parental_hourly), or without one the general criterion of art. 32 c. 1-ter: half the average daily hours a day, two such days a day of leave, no cumulation with the nursing rests on the same day (INPS circ. 152/2015 par. 2.1-2.2). The run records this limitation while the bundle does not record the rule of the CCNL; a company or territorial agreement is the fact local_hourly_agreement of the event.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

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

!!! warning "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · unsourced"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6, as amended by L. 199/2025 from 1 July 2026). The request has no field for the first employment or the room left, and the sources searched set no rule for the withholding agent: a run whose contributions exceed the cap left deducts within the ordinary cap, and the worker may claim the rest in the tax return.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source whether and how the withholding agent grants the extra deduction at the conguaglio, add the worker's statement as an optional input and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.lexplain.it/tabelle-retributive-gomma-plastica/ | tabella_retributiva | — | [↗](https://www.lexplain.it/tabelle-retributive-gomma-plastica/) |
| https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/ | tabella_retributiva | 2025-12-10 | [↗](https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156 | tabella_retributiva | 2026-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM — Trattamento Economico Minimo). All base_salary values incorporate paga base, contingenza, and EDR in a single figure. Evidence: the F/level coefficient ratio is stable to 4 decimal places across all 4 tranches (2023-2026), which is only possible in a fully parametric (conglobated) system. fixed_allowances is empty for all levels except Q.
    
    CONGLOBATED CHECK: coefficient ratios computed as level_value / F_value for all tranches. Q/F=1.2359, A/F=1.1636, B/F=1.0978, C/F=1.0834, D/F=1.0697, E/F=1.0266, G/F=0.9319, H/F=0.8887, I/F=0.7989 — identical across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026. This confirms conglobated model.
    
    TRANCHE DATES 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026 from lexplain.it and kitech.it. Future tranches 01.04.2027, 01.04.2028, 01.12.2028 from the rinnovo 10.12.2025 (ipotesi accordo PDF uniolex.com, confirmed by fiscoetasse.com, paserio.it, edotto.com): F +60, +60, +15. Other levels derived parametrically via the stable coefficients documented in CONGLOBATED CHECK — math verified ±0.01 EUR across all 3 tranches and all 10 levels.
    
    SENIORITY amounts unchanged across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026: the January 2023 rinnovo and December 2025 rinnovo both addressed only TEM (minimi tabellari) and left Art.23 (scatti di anzianità) untouched. Amounts at kitech.it/lavoro-economia.it apply from at least 01.01.2023 onward. Source: rinnovo 10.12.2025 full text (filctemcgil.it); rinnovo Jan 2023 summary (terzomillennio.uil.it); no source reports scatti change in either rinnovo.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Federazione Gomma Plastica is a member of Confindustria; CIGO applicable pursuant to D.Lgs. 148/2015.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Gomma e Plastica Industria.
    
    COMPORTO OF SEVERAL ILLNESSES (Art. 39, chiarimento a verbale 2° (testo definitivo 2021, scanned), PDF p. 67, https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/138012, sha256 2ec73cf8b46366b973eb3e1a6f5067071f6c070208969fd55a0c5183f61120d4): 'I periodi di conservazione del posto di cui al 8° comma, nel caso di più assenze, si intendono riferiti ad un arco temporale di 36 mesi' Modelled as sickness_rules.comporto_windows (6, 9 and 12 months as 183, 274 and 365 days; the 'arco temporale' read as the 36 months before the day).
    
    HOURLY DIVISOR 173 derived from the standard formula (40h/week x 52 / 12 = 173.33 rounded to 173); secondary sources (contratticcnl.it, fiscoetasse.com) confirm the 40h week but the contractual clause was not retrieved directly.
    

## Raw data

The contract file this page is generated from: [`agreement/gomma-plastica-federazione-gomma-plastica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/gomma-plastica-federazione-gomma-plastica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/gomma-plastica-federazione-gomma-plastica/example.py"
```
