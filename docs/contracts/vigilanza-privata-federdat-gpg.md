# CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG

| | |
|---|---|
| **CNEL code** | `HV51` |
| **Sector** | vigilanza privata — guardie particolari giurate (GPG) |
| **Family** | `vigilanza` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2026-07-09 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERDAT
    - CIU Unionquadri
    - FLAITS
    - CONSIL
    - CONFIAL

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

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 30 verified / 6 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-07-09 |
| **Last review** | 2026-11-16 |
| **Latest salary tranche** | 2026-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-11-06 | claude-opus-5-5 (ai) | FEDERDAT CCNL of 4 May 2023 (CNEL 167336) and of 9 July 2026 (CNEL 245848): artt. 102/119 pay (p. 63, page images), 124 seniority (p. 64), 86/103 sickness (pp. 51), 32-33 apprenticeship, 4 validity. | corrected | The file held the HV17 tables (six tranches 2023-2026): FEDERDAT pays one table from May 2023 and the renewal's two from July and December 2026.<br>Six increments, not ten; sickness 100% days 1-3, 75% days 4-20, 100% from day 21 (the file had 75% throughout). |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: artt. 32, 123-124 and 157 of the CCNL of 9 July 2026 (pp. 23, 64, 76, OCR). | corrected | Apprentices accrue the level increments in full: art. 32 c. 1 (p. 23 of the CCNL of 9 July 2026) sets their pay 'in applicazione del principio di parità di trattamento' (no percentage), art. 123 (p. 64) counts seniority 'dal giorno in cui il lavoratore inizia di fatto la prestazione lavorativa nell'Istituto, quali che siano le mansioni', and the six triennial increments are fixed per level (art. 124; art. 157 for the servizi fiduciari). |
| 2026-11-13 | claude-opus-5-5 (ai) | Arts. 21 and 64 of the renewal of 9 July 2026 (CNEL 245848, PDF pp. 16, 34-35) and arts. 21 and 48 of the text of 4 May 2023 (CNEL 167336, PDF pp. 17, 34), scanned pages read on the images. | corrected | Added health_funds ebilav (0,20% + 0,10%, alternative 25 EUR) and ebilav_sanitario (12 EUR, alternative 15 EUR), the same HV51 clauses as the FEDERDAT SF file; the substitutes are paid on the 14 monthly payments of this file. |
| 2026-11-15 | claude-opus-5-5 (ai) | Comporto over the calendar year and paid days, against the research of a separate model session; quotes checked on the source. | corrected | Comporto of 240 days over the calendar year; pay ends after 180 days. |
| 2026-11-15 | claude-opus-5-5 (ai) | Hourly base, night, holiday and shift supplements, travel allowance: quotes located in the cited files by sha256, values read against the quotes. | corrected | Applied: hourly_base, bands[2:sunday], bands[3:holiday], none.shift_work.<br>Left out: bands[0:night]: more night bands the engine cannot tell apart; bands[1:night]: more night bands the engine cannot tell apart; bands[4:rest_day]: more rest_day bands the engine cannot tell apart; bands[5:rest_day]: more rest_day bands the engine cannot tell apart; travel: kind share applied by hand. |
| 2026-11-16 | claude-opus-5-5 (ai) | Number of monthly pays: the article on the additional months located in the cited file by sha256. | corrected | Sourced: 14 monthly pays. |
| 2026-11-16 | claude-opus-5-5 (ai) | Holidays falling on a Sunday: the clause located in the cited file by sha256 (or the law where the CCNL is silent). | corrected | Applied: work_rules.sunday_holidays. |
| 2026-11-16 | claude-opus-5-5 (ai) | Arts. 104, 105, 111 and 82 of the CCNL of 4 May 2023 (CNEL 167336) and arts. 100, 121 of the renewal of 9 July 2026 (CNEL 245848), read from the OCR of the scans by sha256. | corrected | Extended the Sunday and holiday bands to June 2023; added the daily night allowance by service and the travel share. |
| 2026-11-16 | claude-opus-5-5 (ai) | The clause on the fraction of a month of the extra-month ratei, located in the cited file by sha256. | corrected | Sourced: parameters.accrual_rule. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Livello Q (Quadro) | € 2,434.74 | 2026-12-01 |
| `I` | Livello I | € 2,086.89 | 2026-12-01 |
| `II` | Livello II | € 1,946.09 | 2026-12-01 |
| `III` | Livello III | € 1,723.31 | 2026-12-01 |
| `IV` | Livello IV | € 1,528.88 | 2026-12-01 |
| `V` | Livello V | € 1,450.44 | 2026-12-01 |
| `VI` | Livello VI (convenzionale) | € 1,350.44 | 2026-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `VI` | € 19.66 |
| `V` | € 20.52 |
| `IV` | € 21.13 |
| `III` | € 22.46 |
| `II` | € 23.83 |
| `I` | € 26.12 |
| `Q` | € 31.30 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `VI`, `V`, `IV`, `III`, `II`, `I`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "vigilanza-privata-federdat-gpg/leave_days_by_rota · leave · impact yes · resolved"
    LEAVE (Art. 89, 2026 text): 25 days with the 5+1 rota, 23 with 6+1+1, 22 with 5+2, read by Employment.rota; without it the 25 days of the 5+1 rota.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: leave_rules.rota_annual_days with Employment.rota, read on 2026-11-06.

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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

### Without monetary impact

!!! note ""
    COMPORTO OF ONE ILLNESS: up to 300 days of the same illness in the calendar year when certified as such before the 240 days; the engine ends the comporto at 240 days. The days past 180 are unpaid either way.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Vigilanza privata e servizi fiduciari FEDERDAT, 9 luglio 2026 (archivio CNEL HV51, accordo 245848) | cnel | 2026-07-09 | [↗](https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/245848) |
| CCNL Vigilanza privata e servizi fiduciari FEDERDAT, 4 maggio 2023 (archivio CNEL HV51, accordo 167336) | cnel | 2023-05-04 | [↗](https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/167336) |

??? note "Coverage notes"
    CCNL FEDERDAT (CNEL HV51), guardie particolari giurate. Conglobated pay, 14 months, hourly divisor 173, daily 26. The CCNL of 4 May 2023 pays one table (art. 102) until the renewal of 9 July 2026, in force 'da luglio 2026' (art. 4: read as 1 July), whose art. 119 gives the amounts in force and those of December 2026. The pay tables of the main CCNL (HV17) the file held before are those of vigilanza-privata-assiv.
    
    APPRENTICESHIP (Art. 32, 2026 text): 'La retribuzione, l'inquadramento e l'orario di lavoro dell'apprendista sono disciplinati [...] in applicazione del principio di parità di trattamento': modelled as 100% of the level; three years at most (art. 33).
    
    COMPORTO AND PAID DAYS (Artt. 101 and 105 (CNEL archive, PDF in base64), PDF p. 51, https://az-apim-cne-sa-0002-lgc-we.azure-api.net/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/245848, sha256 6a3c337847f6be1a3bae390eff58b7d95b9ec2f7a21d79130cb6ae1519de3a29): 'ha diritto alla normale retribuzione netta mensile [...] per un periodo massimo di 180 giorni'; 'ha diritto alla conservazione del posto di lavoro per i seguenti periodi: - fino a 240 (duecentoquaranta) giorni di malattia riferibile a più episodi morbosi, nell'arco di un anno solare'. Modelled as sickness_rules.comporto_calendar_year with max_duration_days 240; day_bands end the pay on day 180 (day 181 on at 0) of the relapse chain.
    

## Raw data

The contract file this page is generated from: [`agreement/vigilanza-privata-federdat-gpg.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/vigilanza-privata-federdat-gpg.json).

## Usage example

```python
--8<-- "docs/examples/agreement/vigilanza-privata-federdat-gpg/example.py"
```
