# CCNL Marittimi — Industria Armatoriale (CONFITARMA)

| | |
|---|---|
| **CNEL code** | `I391` |
| **Sector** | navigazione marittima — personale di terra |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-11 |
| **Workers (est.)** | ~15k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFITARMA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority, una_tantum |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 2 verified / 39 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-11 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2026-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 17 - Tredicesima e Quattordicesima mensilità (p. 15): "il lavoratore non in prova, avrà diritto a tanti dodicesimi dell'ammontare delle mensilità accessorie e per quanti sono stati i mesi interi di servizio prestato, calcolando come mese intero la frazione di mese uguale o superiore a 15 giorni e trascurando invece quella inferiore a 15 giorni.". Match: at_least 15. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 26 (pp. 20-21) of the shore-staff section: the comporto is 10 months of one illness and 330 days of several within the last three years, with the whole pay; the carenza of the 4th-6th event of the year is paid 50%, from the 7th 30%. The file kept a comporto of 180 days of one illness with no event reduction: corrected (max_duration_days 304, a window of 36 months and 330 days, carenza_by_event). The 18 months of a serious illness are not modelled. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `VIIQ` | Livello VII Q — Quadri: VII minimo + INDENNITA_FUNZIONE EUR 225.00 (Art. 18 quinquies) | € 2,800.07 | 2026-07-01 |
| `VII` | Livello VII — Lavoratori con responsabilita direttive di alto livello | € 2,800.07 | 2026-07-01 |
| `VI` | Livello VI — Lavoratori con elevata autonomia e responsabilita gestionale | € 2,429.76 | 2026-07-01 |
| `V` | Livello V — Lavoratori altamente specializzati con coordinamento | € 2,108.93 | 2026-07-01 |
| `IV` | Livello IV — Lavoratori con qualifiche tecniche e responsabilita operative | € 1,989.32 | 2026-07-01 |
| `III` | Livello III — Lavoratori specializzati con autonomia operativa | € 1,755.00 | 2026-07-01 |
| `II` | Livello II — Lavoratori qualificati con mansioni esecutive | € 1,591.25 | 2026-07-01 |
| `I` | Livello I — Lavoratori addetti a mansioni di semplice esecuzione | € 1,509.42 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 23.74 |
| `II` | € 24.41 |
| `III` | € 25.76 |
| `IV` | € 29.35 |
| `V` | € 30.47 |
| `VI` | € 34.39 |
| `VII` | € 36.07 |
| `VIIQ` | € 36.07 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `III`, `IV`, `V`, `VI`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "marittimi-industria-armatoriale/level_superminimo_art_18 · base_salary · impact yes · open"
    SUPERMINIMO LIVELLO: Art. 18 provides additional EUR 7/month for L4 workers after 8 years in level, and EUR 7-11/month for L2-L3 workers under specific conditions. Individual-level amounts tied to personal history — not modellable in a standardised payroll engine (no per-worker tenure field). Out_of_scope structural limitation.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 18 superminimo (7 EUR for IV after 8 years in level, 7-11 EUR for II-III) as allowances gated on the time in level, or pay it as an IndividualElement and record the limitation.

!!! warning "marittimi-industria-armatoriale/una_tantum_2024_2025 · una_tantum · impact yes · open"
    UNA TANTUM: backpay EUR 200 paid Jul 2024 + EUR 180 paid Jan 2025, uniform all levels. Lump-sum, not recurring. Out_of_scope per engine design (una tantum payments are not included in periodic payroll computation).

    **Applies when:** `una_tantum` applies; from 2024-07-01.

    **Remediation:** Pay the una tantum (200 EUR in July 2024, 180 EUR in January 2025) outside the engine (ArrearsEvent) and record it as an open limitation.

!!! warning "marittimi-industria-armatoriale/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

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

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) but does not reduce the tax by the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4): the request does not state them, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Add the deductions the worker declares as unused for each year of the arrears and reduce the tax by them, then resolve this limitation.

### Without monetary impact

!!! note ""
    PRE-2024 HISTORY: prior CCNL signed 16/12/2020. Values before 01/07/2024 not modelled. From the 2020 contract PDF (usclac.it): terra salary tables were in Allegato 2 (tabelle retributive per il personale di terra, 2021-2023 tranches). Sezione 15 (uffici e terminals) specifically references Allegato 9 "in formato elettronico" — a separate electronic file not embedded in the scanned PDF. Neither Allegato 2 (scanned, image-only) nor Allegato 9 (separate file) is machine-readable. Engine history starts at 01/07/2024.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filtcgil.it/images/Contratti/Mare/15_-_SEZIONE_PERSONALE_DI_TERRA.pdf | altro | 2024-07-11 | [↗](https://www.filtcgil.it/images/Contratti/Mare/15_-_SEZIONE_PERSONALE_DI_TERRA.pdf) |

??? note "Coverage notes"
    CCNL 2024-2026 (CONFITARMA/FILT-CGIL/FIT-CISL/UILTRASPORTI), signed 11/07/2024, valid 01/07/2024-31/12/2026. Personale di terra (shore-based staff), Sezione 15 — Allegati 1 and 1bis.
    
    SPLIT model: minimo contrattuale (base_salary) + EAR Elemento Aggiuntivo della Retribuzione (per-level, omnicomprensivo) modelled as fixed_allowance. 3 tranches: 01/07/2024 (40%), 01/07/2025 (30%), 01/07/2026 (30%).
    
    VIIQ (Quadri): VII minimo + INDENNITA_FUNZIONE EUR 225.00/month fixed (since June 2007, not indexed). Included in TFR, 13th and 14th month, festivity. NOT included in overtime base.
    
    HOURLY DIVISOR: 173 (Art. 10 para 8). Daily divisor: 26. Verified on 3 levels: L1=1509.42/173=8.72, LIV=1989.32/173=11.50, LVII=2800.07/173=16.18.
    
    ADDITIONAL MONTHS: 14 — tredicesima (Christmas) and quattordicesima (Easter/summer). Art. 17: base = minimo + superminimo + scatti + contributo mensa + indennita funzione.
    
    SENIORITY: 24-month cadence (biennale), max 5 for workers hired from 1989 onwards. Per-level EUR from Allegato 1: I=23.74, II=24.41, III=25.76, IV=29.35, V=30.47, VI=34.39, VII=36.07.
    
    APPRENTICESHIP: professionalizzante, eligible levels III-VI only. Months 1-12: 70% of minimo; months 13-36: 80% of minimo. Minimum 6 months, maximum 36 months.
    
    SENIORITY MAX: CCNL provides 10 max increments for workers hired before 31/12/1988; modelled as max=5 (post-1988 hires, the prevailing case for the active workforce — no one hired before 1988 is still accumulating scatti). Structural engine limitation for the pre-1988 grandfathered cohort.
    
    EAR FOR VIIQ: Allegato 1bis lists EAR only for VII (not VIIQ separately). VIIQ workers receive the same EAR as VII; the distinguishing element is INDENNITA_FUNZIONE (additional allowance for quadri). Structural design: VIIQ base = VII base, VIIQ fixed_allowances includes INDENNITA_FUNZIONE.
    

## Raw data

The contract file this page is generated from: [`agreement/marittimi-industria-armatoriale.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/marittimi-industria-armatoriale.json).

## Usage example

```python
--8<-- "docs/examples/agreement/marittimi-industria-armatoriale/example.py"
```
