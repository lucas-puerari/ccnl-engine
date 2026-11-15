# Distribuzione Moderna Organizzata — Federdistribuzione

| | |
|---|---|
| **CNEL code** | `H008` |
| **Sector** | terziario |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-09-29 |
| **Workers (est.)** | ~460k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Federdistribuzione
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 109 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-09-29 |
| **Last review** | 2026-11-15 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the Testo Unico of 29 September 2025 (Federdistribuzione, 99 pages), for the production tier. | corrected | 90 records verified; the work rules cited an aggregator and now cite the Testo Unico. The 2025/01 URL of the sources returns 404: replaced by the 2026/04 one.<br>Night overtime 50%, not 30% (Art. 132 c. 3); added the 20% beyond the 48th weekly hour (c. 1). The premiums are on the normale retribuzione of Art. 189 (hourly_base_method gross_incl_allowances, which documents the rule: the caller states OvertimeEvent.hourly_rate).<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, apprentices excluded (Art. 170), not a flat 100%.<br>Seniority amounts in force since 1990 (Art. 188): the gap before 23 April 2024 removed.<br>Terzo elemento 2.07 due only without a provincial element (Art. 199): now gated.<br>Apprenticeship: second half of level VI at VII (Art. 46 c. 3); the 36-month end of levels II-V stated.<br>Added the payment days of the tredicesima and quattordicesima and Fon.Te. (Art. 95, 1.55% and 0.55%, apprentices 1.05%).<br>Night holiday overtime 0.50 stays derived: no clause sets it, Art. 132 c. 5 forbids cumulation.<br>No renewal after the Testo Unico through October 2026. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented. |
| 2026-10-17 | claude-opus-5-5 (ai) | The paga base, contingenza, terzo elemento, indennità di funzione and scatti of every level against the Testo Unico of 29 September 2025, and a year and a termination of a level IV worker against a hand oracle. | confirmed | Allegato 11 (PDF pp. 97-99): 47 of the 48 paghe base of the file are printed in the tables; the IV of 1 April 2023 prints 1112,46 in the paga base column, but its total 1646,68 less the contingenza 524,22 gives the 1122,46 of the file, which the CCNL Terziario Confesercenti also reaches (total 1646,68). The paga base column has a misprint; the file keeps 1122,46.<br>Contingenza + EDR of every level, the terzo elemento of 2,07 (Art. 195), the indennità di funzione of the Quadri (260,76) and of the VII (5,16) and the scatti (Quadri 25,46 to VII 19,47): match.<br>Art. 204 and 205 (PDF p. 59): tredicesima at Christmas, quattordicesima of the pay in force on 30 June paid on 1 July, in twelfths of the twelve months before. Match.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios dmo-year and dmo-june): a level IV impiegato hired on 1 January 2026 by an employer with 50 employees where a provincial element is in force; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, read in the Testo Unico of 29 September 2025 (Artt. 79, 141, 142, 191, 193, 194). | corrected | Art. 142 - Ferie, Chiarimento a verbale (p. 45): the indemnity of the ferie at the end of the employment is the retribuzione mensile di fatto divided by twenty-six: work_rules.leave_rules.termination; the accrual of the leave is not modelled, so the basis is not used yet. |
| 2026-10-31 | claude-opus-5-5 (ai) | The accrual of the ferie, the ex festività and the ROL read in the Testo Unico of 29 September 2025 (Artt. 141, 142, 145). | corrected | Art. 145 c.1 (p. 45): twelfths of the 26 days of Art. 142 per month of effective service, no month-fraction rule: work_rules.leave_rules.ferie_accrual.<br>Art. 141 cc.1, 3, 4, 7 (pp. 44-45): 32 hours of ex festività (4 festività in groups of 8 hours), 56 hours of permits up to 15 employees and 72 above, by whole months: work_rules.leave_rules.permits.<br>Art. 141 c.8 (p. 45): the 56/72 hours of a hire after 1 March 2011 at 0%, 50% after two years, 100% after four: permits[rol].ramp. |
| 2026-11-01 | claude-opus-5-5 (ai) | The indennità di cassa e maneggio denaro of Art. 202 (p. 59). | corrected | Art. 202 (p. 59): 5% of the paga base nazionale conglobata to the staff normally at the till with full responsibility for it: levels[*].fixed_allowances[IND_CASSA], role cassiere, one value per period of the base_salary. |
| 2026-11-01 | claude-opus-5-5 (ai) | The hourly divisors of the 42 and 45 hour weeks, Art. 194 - Quota oraria (p. 58). | corrected | Art. 194 - Quota oraria (p. 58): 168 for a normal week of 40 hours, 182 for 42, 195 for 45: work_rules.time_supplements.hourly_divisor_weekly_hours 40 and week_divisors 42/182, 45/195. |
| 2026-11-01 | claude-opus-5-5 (ai) | The notice of Artt. 231-236 (PDF pp. 64-66). | corrected | Artt. 231, 232, 233 c. 3, 236 c. 2 (pp. 64-66): calendar days by level and service for dismissal and resignation, from the 1st or the 16th, indemnity on the retribuzione di fatto with the 13th and 14th ratei, out of the TFR base: work_rules.notice. Found by a delegated search, checked again on the PDF text. |
| 2026-11-02 | claude-opus-5-5 (ai) | The premiums on ordinary hours of Artt. 134, 136, 138 and 139 and the hourly base of Artt. 189, 191 and 194 (PDF pp. 42-44 and 57-58). | corrected | Art. 134 (p. 43): ordinary night 15%; art. 136 c. 7 (p. 43): Sunday 30%; art. 139 (p. 44): weekly rest day 30%; art. 138 (p. 44): holidays as straordinario festivo 30% (art. 132), the hour paid apart: supplement_bands DMO_*, as Commercio artt. 151-156.<br>Art. 194 (p. 58) divisor 168 at 40 hours; art. 189 (p. 57, read on the page image) normale retribuzione: paga base, contingenza, terzi elementi, scatti, other bargained elements; art. 191 adds the continuative individual elements: hourly_base_provenance and individual_elements hour_only, as Commercio artt. 206-211. |
| 2026-11-05 | claude-opus-5-5 (ai) | Artt. 18-20 (PDF pp. 15-16), 191 and 233 of the Testo Unico of 29 September 2025, text layer. | corrected | The three funds and their alternative elements were not modelled: employer cost, worker shares and the EDR of an employer that does not pay them were missing. |
| 2026-11-06 | claude-opus-5-5 (ai) | Apprentice seniority: artt. 186 and 188 of the testo unico of 29 September 2025 (p. 56). | corrected | The apprentice is classified two then one level below with 'il conseguente trattamento economico'; 'il personale ha diritto a dieci scatti triennali' of fixed amounts per level, counting seniority 'dal giorno in cui il lavoratore è entrato a far parte dell'azienda, quali che siano le mansioni': the increments of the level the apprentice is paid at. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | gpt-6-sol (ai) | Open limitations claimed to be no longer gaps: one session read the clauses and the data, a second independent session checked the claim. | confirmed | cashier_allowance: All eight levels have IND_CASSA gated by role cassiere; all 48 dated amounts equal 5% of the corresponding stored base_salary rounded to cents. compensation/element/rules.py activates the allowance for that role. The employer must supply cassiere only when continuous cash assignm |
| 2026-11-08 | gpt-6-sol (ai) | Employer top-up of the INAIL indemnity, read from the signed text by a separate model session (audit of the injury rules); quote checked on the text layer or the page image. | corrected | The injury rule had no top-up of the INAIL indemnity; added: {"integration_bands": [{"day_from": 4, "rate": "0.90"}, {"day_from": 20, "rate": "1"}], "net_basis": true} |
| 2026-11-13 | claude-opus-5-5 (ai) | Art. 47 of the testo unico 2025 (printed p. 45, PDF p. 24), text layer. | corrected | Added work_rules.apprentice_sickness_rules: carenza at 60% for six events a year, 60% of the gross pay on the days of a hospital stay, after the probation; the apprentices were paid no employer treatment before. |
| 2026-11-13 | gpt-6-sol (ai) | Apprentice sickness clause, its encoding and the engine change, against the signed text, by a separate model session. | flagged | Confirmed: source, page and sha256; the 2024 renewal does not list the article among those changed.<br>Confirmed: 60% carenza for six events a year, 60% of the gross pay on hospital-stay days, nothing in the probation, gross basis, 180 days in the calendar year; hand amounts of the Commercio test case recomputed.<br>Flagged and corrected in the same change: quotes made verbatim; a relapse takes the rank of its event; no carenza past the comporto; missing-fact issues raised only when the fact can change the pay; the limitation states the 50-point difference of the alternative reading.<br>Flagged, kept as limitation apprentice_hospital_share: the text does not settle whether the hospital 60% adds to the INPS indemnity or is the total. |
| 2026-11-13 | gpt-6-sol (ai) | Sunday overtime outside the weekly rest day against the overtime, Sunday-work and rest-day articles, by a separate model session. | confirmed | Confirmed: overtime 'nei giorni festivi o la domenica' is paid 30% also when the weekly rest falls on another day; the 'salvo' clause reserves rest-day work, at the same 30% with a compensatory rest.<br>Confirmed: the Sunday-work article sends Sunday overtime to this article, so the two 30% do not add up; night overtime stays at 50%, the premiums are not cumulative.<br>Flagged and corrected: a typo in the transformation and the paragraph label of the unnumbered texts. |
| 2026-11-13 | claude-opus-5-5 (ai) | Allegato 11 (PDF p. 98) and allegato 3 artt. 1, 14 (PDF pp. 71, 74) of the TU 2025 | corrected | Added levels OV1 and OV2 of the operatori di vendita on their own ladder, six tables 2023-2027, and their seniority increments. |
| 2026-11-14 | claude-opus-5-5 (ai) | Artt. 189, 191, 198 and 199 of the Testo Unico 2025, PDF pp. 57-59. | confirmed | The provincial terzi elementi are frozen local amounts the national text does not print; the existing territorial second-level input carries them with the incidences of the normal pay, and provincial_pay_element removes the 2,07 national element. Closed the limitation, which asked for an input that exists. |
| 2026-11-14 | claude-opus-5-5 (ai) | Art. 141 c. 6 of the Testo Unico DMO 2025, deadline of the permits. | corrected | The file had the permit buckets but no deadline: the hours left at year end were never paid or carried. Added permit_deadline (30 June, ex festivita and ROL) as Art. 141 c. 6 sets it, the same clause as Commercio art. 158. |
| 2026-11-14 | claude-opus-5-5 (ai) | Weekly threshold of the overtime band beyond the 48th hour. | corrected | OvertimeEvent.weekly_hours_before counts all the hours worked in the week: the 20% band 'eccedenti la 48a ora settimanale' starts at 48, not at 8 (which paid the 41st-48th hours at 20% instead of 15% when the caller stated the hours before). |
| 2026-11-15 | claude-opus-5-5 (ai) | Travel allowance of Art. 162 cc. 2-5, quote located in the cited file by sha256 and read against the model. | corrected | The diaria is a share (twice) of the daily retribuzione di fatto, a third less without overnight stay, 10% less for long missions or habitual travel. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `OV1` | Operatore di vendita di I categoria | € 1,257.80 | 2027-02-01 |
| `OV2` | Operatore di vendita di II categoria | € 1,054.40 | 2027-02-01 |
| `Q` | Managers (Quadri) | € 2,313.29 | 2027-02-01 |
| `I` | First level | € 2,083.84 | 2027-02-01 |
| `II` | Second level | € 1,802.50 | 2027-02-01 |
| `III` | Third level | € 1,540.66 | 2027-02-01 |
| `IV` | Fourth level | € 1,332.46 | 2027-02-01 |
| `V` | Fifth level | € 1,203.83 | 2027-02-01 |
| `VI` | Sixth level | € 1,080.77 | 2027-02-01 |
| `VII` | Seventh level | € 925.31 | 2027-02-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `I` | € 24.84 |
| `II` | € 22.83 |
| `III` | € 21.95 |
| `IV` | € 20.66 |
| `V` | € 20.30 |
| `VI` | € 19.73 |
| `VII` | € 19.47 |
| `OV1` | € 15.50 |
| `OV2` | € 14.46 |

## Apprenticeship

**standard_II_V** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**standard_VI** (type: `under_classification`)  
Destination levels: `VI`

**tabella_b_48_mesi** (type: `under_classification`)  
Destination levels: `II`, `III`

**tabella_b_42_mesi** (type: `under_classification`)  
Destination levels: `IV`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dmo-federdistribuzione/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (Art. 170): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate and tops it up to the measure of the gross daily quota, as for the Commercio file. The exempt events of c. 3 are an input (SicknessEpisode.short_absence_exempt, read with carenza_by_event) (review of 2026-10-30).

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of Art. 170.

!!! warning "dmo-federdistribuzione/employment_support_contract · base_salary · impact yes · open"
    Art. 70: the sostegno all'occupazione contract.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the pay of the Art. 70 contract.

!!! warning "dmo-federdistribuzione/commission_guarantee · base_salary · impact yes · open"
    Art. 201: the guarantee of the commission-paid staff. The una tantum of Art. 197 (July 2024 and 2025) is historic and outside the TFR base (c. 6).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the guarantee of commission-paid staff.

!!! note "dmo-federdistribuzione/health_and_bilateral_funds · bilateral_funds · impact yes · resolved"
    HEALTH AND BILATERAL FUNDS (artt. 18-20, pp. 15-16): E.Bi.Di.M. 0.10% + 0.05% of paga base and contingenza on 14 months, Fondo EST EUR 10 (13 from April 2025) + 2 a month for the permanent non-quadri, Cassa QuAS EUR 350/370/390 + 56 a year for the quadri; the elements of an employer that does not pay them (0.30%, EUR 16 and 37 on 14 months) when it states so in EmployerProfile.contractual_funds.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Resolved: parameters.health_funds ebidim, fondo_est and quas, read on 2026-11-05.

!!! warning "dmo-federdistribuzione/apprentice_hospital_share · sickness · impact yes · unsourced"
    Art. 47 b): the employer pays 60% of the gross pay on the days of a hospital stay, read as added to the INPS indemnity ('oltre a quanto previsto dalla legislazione vigente'); the text does not say whether the 60% is instead the whole treatment the employer tops the INPS share up to, which would pay 50 points of the gross daily pay less on days 4-20 (60% in all against 50% + 60%). The INPS indemnity during the stay is not reduced to 2/5 for a worker without family dependants.

    **Applies when:** `sickness` applies; contract type in apprentice.

    **Remediation:** Source the reading of the hospital indemnity of the apprentice (a joint interpretation of the parties or a ruling) and apply it; then resolve this limitation.

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

!!! note "pension_extra_deduction_first_employed · pension_fund_contribution · impact unknown · resolved"
    A worker first employed after D.Lgs. 252/2005 came into force may deduct, in the twenty years after the fifth year of membership, the contributions above the annual cap within the room the first five years left, up to half the annual cap (art. 8 c. 6). The withholding agent applies it (AdE circ. 70/E/2007: the employer excludes the deductible contributions from the income of the ritenute): the worker states the deduction of the year as PensionFundEnrolment.extra_deduction, and contributions above the cap left with none stated carry the missing fact extra_deduction.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Resolved: the extra deduction is an input of the enrolment.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.federdistribuzione.it/app/uploads/2026/04/Testo-Unico-CCNL-DMO.pdf | altro | 2025-09-29 | [↗](https://www.federdistribuzione.it/app/uploads/2026/04/Testo-Unico-CCNL-DMO.pdf) |

??? note "Coverage notes"
    Salary tables: 6 tranches from 01/04/2023 through 01/02/2027, Allegato 11 (PDF p. 98) of the Testo Unico CCNL DMO of 29/09/2025 (Federdistribuzione), Art. 196 for the tranche dates. Level IV on 01/04/2023 is printed 1112,46 in the PDF itself: the total 1646,68 less the contingenza 524,22, and 1192,46 less the 70,00 of Art. 196, give 1122.46, the value kept.
    
    Split model confirmed: total / 168 at L1 = 14.905, L4 = 10.605, L7 = 8.309 — all non-integer. Source: Art. 194 (divisore 168 for 40h/week), Allegato 11.
    
    Contingenza: frozen values from Allegato 11 column. EDR (lire 20,000 = 10.33 EUR) conglobated into contingenza on 01/01/1995 per Art. 190 — no separate EDR allowance modelled.
    
    PROVINCIAL TERZI ELEMENTI (Art. 198 (Testo Unico 29 September 2025, PDF p. 59)): the provincial elements 'in atto alla data del 30 giugno 1973 [...] rimangono ancora congelati' and are paid 'in aggiunta ai nuovi livelli retributivi', also to the workers hired after 31 January 1983. The national text prints no province and no amount: they are the frozen figures of each provincial agreement. The caller states them as a territorial second-level element (EmployerProfile.second_level_elements, agreement 'territorial', monthly amount, levels, dates), which enters the extra months and the TFR by default, as the normal and de facto pay of Artt. 189 and 191 (p. 57) include the 'terzi elementi nazionali o provinciali ove esistenti'; with EmployerProfile.provincial_pay_element true the 2,07 national element of Art. 199 is left out.
    
    Indennità di funzione Quadri (Art. 113): EUR 260.76/month for 14 months (cumulative increments: 51.65+77.47+51.65+70.00+10.00=260.77; 0.01 rounding from lire). Allegato 11 shows 260.76.
    
    Altri elementi of level VII: EUR 5.16/month (lire 10,000), column 'altri elementi' of Allegato 11 (PDF p. 98); the Testo Unico names no article for it.
    
    Seniority: 10 scatti triennali (Art. 188), amounts of the Art. 188 table, in force since 1 January 1990; paid from the month after the triennium (c. 4).
    
    Additional months: 14 (tredicesima Art. 204 + quattordicesima Art. 205).
    
    APPRENTICESHIP PROFILES OF TABELLA B (Art. 61): 48 months for the listed profiles ending at levels II and III (track tabella_b_48_mesi), 42 months for those ending at level IV (tabella_b_42_mesi), two levels below for the first half and one below for the second. An apprentice of levels II, III and IV states Apprentice.track: standard_II_V for the 36 months of the other profiles.
    
    LEAVE, WEEKLY SCHEDULE: a 39-hour full-time week absorbs 36 hours of ROL and a 38-hour week 16 hours of ex festività and 56 of ROL, read from Employment.full_time_weekly_hours. The grandi magazzini, magazzini a prezzo unico, supermercati alimentari, cash&carry and ipermercati (Art. 119, EmployerProfile.subsector 'grande_distribuzione') on a 38-hour average absorb instead the 56 hours of Art. 141 c. 3 and the 16 of c. 4 and keep the ex festività.
    
    ORDINARY HOUR PREMIUMS (Testo Unico 29 September 2025, pp. 43-44): ordinary night 15% (art. 134), Sunday 30% (art. 136 c. 7, without a better second-level treatment), weekly rest day 30% (art. 139), holidays as straordinario festivo 30% with the hour paid apart (art. 138): work_rules.time_supplements.supplement_bands DMO_*.
    
    OPERATORI DI VENDITA (protocollo aggiuntivo, allegato 3 art. 14, TU 2025 PDF p. 74): ten three-year increments of 15,50 (I categoria) and 14,46 (II categoria) from 1 October 1986, the cadence and count of the other levels; levels OV1 and OV2, ladder operatori_vendita.
    
    LEAVE, DEADLINE (Art. 141 c. 6, TU 2025 p. 85): the permits not taken within the year are paid with the retribuzione di fatto of art. 191 at the deadline, or taken by 30 June of the next year, as the employer states (EmployerProfile.permit_carryover).
    

## Raw data

The contract file this page is generated from: [`agreement/dmo-federdistribuzione.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dmo-federdistribuzione.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dmo-federdistribuzione/example.py"
```
