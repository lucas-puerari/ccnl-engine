# CCNL Impianti e Attività Sportive Profit e No-profit

| | |
|---|---|
| **CNEL code** | `H077` |
| **Sector** | impianti sportivi, palestre e attività sportive |
| **Family** | `sport` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-01-12 |
| **Workers (est.)** | 35533 |
| **Ruleset version** | `2024.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CUSI
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
| **Limits of this contract** | base_salary, overtime, sickness |

9 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 32 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-01-12 |
| **Last review** | — |
| **Latest salary tranche** | 2026-07-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,083.49 | 2026-07-01 |
| `I` | Primo livello | € 1,989.04 | 2026-07-01 |
| `II` | Secondo livello | € 1,807.04 | 2026-07-01 |
| `III` | Terzo livello | € 1,636.42 | 2026-07-01 |
| `IV` | Quarto livello | € 1,506.82 | 2026-07-01 |
| `V` | Quinto livello | € 1,413.42 | 2026-07-01 |
| `VI` | Sesto livello | € 1,336.82 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**apprendistato_II_III_IV_36mesi** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`  
under-level: `1`

**apprendistato_V_36mesi_semplificato** (type: `under_classification`)  
Destination levels: `V`  
under-level: `1`

**apprendistato_VI_24mesi_semplificato** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "impianti-sportivi-sport/pre_2015_superminimo_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Seniority. Il CCNL 2024 non contiene disposizioni su scatti di anzianita (parola 'scatti' assente dall'intero PDF). Regime transitorio: i lavoratori in forza al 22/12/2015 conservano un superminimo personale decrescente fino al 31/10/2029 (Art. 116 norma transitoria). Non modellato. Gli importi kitech (EUR 21.69-28.92) si riferiscono agli scatti ante-2015. Modellato: maximum_count=0. Allowances can depend on the date in service (Allowance.in_service_on, individual) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the decreasing personal superminimo of Art. 116 as an allowance with in_service_on 2015-12-22.

!!! warning "impianti-sportivi-sport/level_v_first_semester_overpaid · base_salary · impact yes · open"
    SIMPLIFICATION: Apprendistato livello V (Art. 30). Il livello V ha ordine 2 e il livello a ordine 0 non esiste; il primo semestre a 2 livelli sotto non e applicabile. SEMPLIFICAZIONE: primo semestre a 1 livello sotto (VI). L'apprendista percepisce piu del previsto contrattualmente nella prima meta. L'intera durata (36 mesi) e al livello VI.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in V.

    **Remediation:** Pay the first semester of the level V track at the contractual level once the classification allows it.

!!! warning "impianti-sportivi-sport/level_vi_whole_track_at_destination · base_salary · impact yes · open"
    SIMPLIFICATION: Apprendistato livello VI (Art. 30 + Art. 37). Art. 30 prevedeva il primo semestre al VII livello, che il rinnovo 2024 ha eliminato. SEMPLIFICAZIONE: l'intera durata apprendistato VI (24 mesi) e al livello di destinazione VI (levels_below=0). L'apprendista percepisce piu del previsto contrattualmente.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in VI.

    **Remediation:** Confirm the level VI track after the 2024 renewal and model its first semester.

!!! warning "impianti-sportivi-sport/overtime_over_48h_band_missing · overtime · impact yes · open"
    SIMPLIFICATION: Straordinario diurno. Art. 83 prevede 15% per ore 41-48 e 20% per ore oltre 48 settimanali. Modellato solo il 15% (caso dominante). Banda 20% (oltre 48h) non modellata.

    **Applies when:** `overtime` applies.

    **Remediation:** Model the 20% band over 48 weekly hours, or pass the multiplier on the overtime event.

!!! warning "impianti-sportivi-sport/integration_75_days_4_20 · sickness · impact yes · open"
    SIMPLIFICATION: Integrazione malattia (Art. 103). Struttura contrattuale: giorni 1-3 a carico del datore (100%), giorni 4-20 integrazione al 75%, giorni 21+ integrazione al 100%. Modellato: carenza_integration_rate=1.0, full_pay_integration_rate=1.0 (allineato alla fase finale). La finestra al 75% (gg. 4-20) non e modellata; il motore sovrastima la retribuzione per eventi di malattia breve. The sickness rules can hold day bands (sickness_rules.day_bands): the gap is in the data only (review of 2026-10-30).

    **Applies when:** `sickness` applies.

    **Remediation:** Add the day bands of Art. 103 (75% on days 4-20, 100% from day 21) to sickness_rules.day_bands, then resolve this limitation.

!!! note "impianti-sportivi-sport/long_week_divisor_195 · workplace_injury · impact unknown · resolved"
    SIMPLIFICATION: Divisore orario. Art. 120 prevede 173 (40h) e 195 (45h). Solo il divisore 173 e modellato. Le assunzioni a 45h settimanali non sono gestite.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: work_rules.time_supplements.week_divisors holds 195 for a full_time_weekly_hours of 45 (Art. 120 lett. b, p. 90).

!!! warning "impianti-sportivi-sport/night_overtime_cumulation · overtime · impact unknown · open"
    SIMPLIFICATION: Cumulo notturno. Art. 83 ult. comma: 'Le varie maggiorazioni previste dal presente articolo non sono cumulabili tra loro' — esclude la cumulabilita tra i soli supplementi interni all'Art. 83 (15%/20%/30%/50%). Il supplemento del 10% di Art. 84 e un articolo separato e non e esplicitamente escluso dalla cumulabilita. Il motore applica entrambi alle ore notturne straordinarie (60% totale). Se le parti intendono il 50% inclusivo del 10%, il motore sovrastima di 10 punti sulle ore OT notturne.

    **Applies when:** `overtime` applies.

    **Remediation:** Confirm with the parties whether the 50% night overtime band includes the 10% night supplement of Art. 84.

!!! warning "impianti-sportivi-sport/pre_2015_fourteenth_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Quattordicesima transitoria. Art. 116 norma transitoria: i lavoratori in forza al 22/12/2015 ricevono un superminimo personale assorbibile equivalente alla quattordicesima folded-in (rata mensile decrescente fino al 31/10/2029). Per la popolazione corrente (post-2015): 13 mensilita. La quattordicesima residuale per i lavoratori ante-2015 non e modellata; it may be the same element as pre_2015_superminimo_missing, which a reading of Art. 116 settles. Allowances can depend on the date in service (Allowance.in_service_on) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read Art. 116 and model the residual quattordicesima as an allowance with in_service_on 2015-12-22, or resolve it as part of pre_2015_superminimo_missing.

!!! warning "impianti-sportivi-sport/sickness_net_basis · sickness · impact unknown · open"
    SICKNESS (Art. 103): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate (the 'lordizzazione' of payroll practice, Ordine dei Consulenti del Lavoro di Salerno) and tops it up to the measure of the gross daily quota; IRPEF is left out, as it falls on both. Day bands, carenza by event, the yearly comporto and the exclusion of apprentices are modelled.

    **Applies when:** `sickness` applies.

    **Remediation:** Find a source (an interpretation of the parties, an INPS or Ministry text) that defines the net daily pay of Art. 103, align the computation, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabella retributiva completa 4 tranche (01/01/2024, 01/07/2024, 01/07/2025, 01/07/2026). Livelli Q–VI. Retribuzione conglobata (contingenza=0, terzo elemento=0). 13 mensilità (tredicesima). Modello confermato da ilccnl.it e kitech.it. | tabella_retributiva | 2024-01-12 | [↗](https://www.sindacato.it/il-ccnl-impianti-sportivi-o-lavoratori-dello-sport/) |
| CUSI PDF 2024-2026. Art. 116: retribuzione normale conglobata (componente a). Art. 119: divisore giornaliero 26. Art. 120: divisore orario 173 (40h settimanali) o 195 (45h settimanali) — solo 173 modellato. Art. 121: tabella livelli I–VI più quadro Q. Art. 125: tredicesima mensilità. Art. 30: apprendistato sotto-inquadramento (2 livelli primo semestre, 1 livello secondo semestre). Art. 37: durate apprendistato II–VI. Art. 83: straordinario 15%/20%/30%/50%. Art. 84: notturno ordinario 10%. Art. 85: ferie 26 giorni lavorativi. Art. 102: comporto 180 giorni. Art. 103: integrazione malattia 100%/75%/100%. | altro | 2024-01-12 | [↗](https://www.cusi.it/wp-content/uploads/2024/02/CCNL-Sport-2024-2026.pdf) |
| Kitech tabella 01/07/2026: conferma IND_FUN Q = EUR 60.00 (13 mensilità). Scatto anzianità da EUR 21.69 (VI) a EUR 28.92 (Q) — transitional amounts ante-22/12/2015; no new scatti under 2024 CCNL. | tabella_retributiva | 2024-01-12 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=13) |

??? note "Coverage notes"
    CCNL H077 Impianti Sportivi e Palestre, rinnovo 12/01/2024 (vigenza 01/01/2024-31/12/2026). 7 livelli: Q (quadro) + livelli I-VI. Art. 121 CCNL dice 'sei livelli' perche Q e categoria quadro sopra la scala ordinaria. Conglobato confermato da ilccnl.it (contingenza=0.00, terzo elemento=0.00 su 4 livelli). Divisore orario 173 da Art. 120 (40h settimanali).
    

## Raw data

The contract file this page is generated from: [`agreement/impianti-sportivi-sport.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/impianti-sportivi-sport.json).

## Usage example

```python
--8<-- "docs/examples/agreement/impianti-sportivi-sport/example.py"
```
