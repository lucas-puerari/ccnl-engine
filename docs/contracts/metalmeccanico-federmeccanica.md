# CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)

| | |
|---|---|
| **CNEL code** | `C011` |
| **Sector** | metalmeccanico |
| **Family** | `metalmeccanica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-11-22 |
| **Workers (est.)** | ~1,7M |
| **Ruleset version** | `2026.3` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - Federmeccanica
    - Assistal
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, sickness |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 90 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-11-22 |
| **Last review** | 2026-11-14 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-10 | claude-opus-5-5 (ai) | Whole file. The values checked were not recorded; no value was marked verified. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (94 records) read again in the signed texts: the CCNL of 5 February 2021, the renewal of 22 November 2025 and the minutes of June 2023, 2024, 2025 and 2026 on the minimi. | corrected | 91 records match their source and are verified, and the corrected divisor below is verified too. All 72 salary periods match in amount and dates. Pages are physical PDF pages (the printed page of the 2021 CCNL is four lower).<br>Ratified: the workers' referendum of 18-20 February 2026 approved the renewal of 22 November 2025 (93.13% in favour); the minutes of 16 June 2026 call it the Accordo di rinnovo 22 novembre 2025. No consolidated final text is published; the minimi of the signed hypothesis are in force.<br>June 2026: the IPCA share is absorbed in the June 2026 tranche of the renewal, so the minimi already in the file stand; the minutes of 16 June 2026 also set travel and on-call allowances, not modelled.<br>Corrected: the hourly divisor 173 (Art. 5, Sez. Quarta Tit. IV) is undated in the 2021 CCNL, so it applies from 2021-06-01, not from 2024-06-01.<br>Left derived: the Cometa rates (2%, 1.2%, 2.2% under 35, Art. 15) match but start on 1 June 2017 and 1 June 2022, not on 2026-01-01; the leave tiers start 'oltre 10 anni' and 'oltre i 18 anni', which the file reads as 120 and 216 months.<br>Wrong page citations corrected: divisor p. 175, seniority pp. 175-176, daily quota 1/26 p. 164, annual leave p. 165. |
| 2026-10-12 | claude-opus-5-5 (ai) | Cometa contribution dates, leave citation, travel and on-call allowances: follow-ups of the review of 2026-10-11. | corrected | Cometa: rates confirmed (art. 15 not amended in 2025); the periods started on 2026-01-01, now 1 June 2017 (2% and 1.2%) and, for young members, 2% from 6 February 2021 and 2.2% from 1 June 2022.<br>Leave: the clause is on p. 165, not p. 158; the norme transitorie on p. 167.<br>Trasferta and reperibilità (June 2026 amounts) are per event: documented, not paid, as the engine takes no such event. |
| 2026-10-12 | claude-opus-5-5 (ai) | Standby (reperibilità): art. 6 Sez. Quarta Titolo III and the IPCA verbali of June 2025 and June 2026. | corrected | Standby was documented and not paid: the engine now takes a StandbyEvent and the rates of the three bands from 1 June 2025 and 1 June 2026, read on the page images of the two signed verbali.<br>Art. 6 excludes the standby pay from the TFR base and pays 5.00 euro for each call with an intervention. |
| 2026-10-12 | claude-opus-5-5 (ai) | Hospital stays in the sickness treatment (Sez. Quarta Titolo VI art. 2). | corrected | Hospital stays of more than 10 consecutive days are paid in full instead of 80%, up to 61 days: modelled with SicknessEpisode.hospital_stays (hospital_stay of the cumulation). |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: minimi of every level for June 2026, 2027 and 2028; Cometa rates (art. 15); overtime percentages (art. 7) against the renewal of 22 November 2025. | corrected | The 27 minimi of the table (9 levels from 1 June 2026, 2027 and 2028, p. 2 of the signed scan) match the bundle to the cent.<br>Cometa: 2% of the employer and 1.2% of the worker from 1 June 2017, 2.2% from 1 June 2022 for members joining after 5 February 2021 under 35: verified.<br>Overtime: the note cited Art. 14 and 15/20/30% and expected the renewal to change them; the bands follow Art. 7 (25/30/50/55/75%) and the renewal leaves them. Note corrected.<br>Shift column of Art. 7 and multi-week premiums of Art. 5: not modelled, now declared (shift_and_multiweek_premiums). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL C011 matches (Federmeccanica, Assistal with FIM, FIOM, UILM; the report also lists the confederations and CISAL Metalmeccanici as depositors).<br>Term: the renewal 'decorre dal 22 novembre 2025 ed avrà vigore fino a tutto il 30 giugno 2028' (renewal text, p. 4); the report, older, still shows 30/06/2024. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | flagged | Part-time supplementary hours at an all-inclusive 10% (p. 58): declared. The apprenticeship tracks of the accordo of 20 April 2021 were not re-read. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | flagged | Cometa verified in P1. mètaSalute (156 euro a year plus the 10% solidarity contribution, Ministry of Labour DD 82/2026) is not modelled: declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour for the CCNL (D.Lgs. 36/2023 art. 41 c. 13). | corrected | Impiegato C3 with 3 scatti, June 2026, 51 employees: tabellare 2211.43 and scatti 88.92 a month equal the table (26.537,16 and 1.067,04 a year over 12); the employer INPS rate 29.36% and the tredicesima on tabellare and scatti match; the TFR of the month 158.90 is the table's (tabellare + scatti) / 13.5 less the 0.5% IVS contribution the employer offsets (art. 3 L. 297/1982), which the table does not deduct. Match.<br>Deviations, with cause and decision: INAIL 4.417% and the health fund (171,60 a year) are capabilities the engine does not compute (documented); Cometa at a 40% enrolment is the table's average, the engine pays it on enrolment; the elemento perequativo (485 euro) and the flexible benefits (250 euro) were neither modelled nor declared: declared. The stale INPS note (30.13/30.20/30.50%) is corrected. No independent net pay example: not compared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova', re-read on the full text published by a party. | confirmed | Apprenticeship tracks 36, 30 and 24 months at 85/90/95% (p. 271) and their durations (pp. 267-268) match the three tracks of the file. |
| 2026-10-17 | claude-opus-5-5 (ai) | The rate of the supplementary hours of the part-time workers. | corrected | Lavoro supplementare (Sez. Quarta, Titolo I, PDF p. 58): 10% onnicomprensiva up to 40 weekly hours and 50% of the yearly part-time hours, 20% beyond that yearly limit. The 10% band is added for OvertimeKind.SUPPLEMENTARY; the 20% past the yearly limit needs the yearly count of supplementary hours and is not modelled. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | corrected | hourly_base_method gross_incl_allowances (was minimo_tabellare), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: FED_FESTIVO, FED_FESTIVO_RIPOSO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS.<br>work_rules.absence_rules was verified on the 1/26 of art. 9, which pays a festività falling on a Sunday and sets no absence divisor: now derived, with the reading stated. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Sez. Quarta, Titolo IV, Art. 6 - Aumenti periodici di anzianità). | corrected | Sez. Quarta, Titolo IV, Art. 6 - Aumenti periodici di anzianità (p. 176): the earlier increments take the amounts of the new level from the change: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Sez. Quarta, Titolo IV, Art. 3 - Mensilizzazione; Titolo III, Art. 7). | corrected | Sez. Quarta, Titolo IV, Art. 3 - Mensilizzazione; Titolo III, Art. 7: individual elements included in the hourly base: work_rules.time_supplements.individual_elements. |
| 2026-10-31 | claude-opus-5-5 (ai) | The basis of the indemnity for the leave not taken at the end of the employment, searched for a divisor of the daily pay in the CCNL of 5 February 2021 (Sez. IV, Tit. III, Artt. 9, 10; Tit. IV, Art. 3) and in the OCR of the ipotesi of 22 November 2025. | confirmed | Art. 10 pays a day of ferie not taken at the 'retribuzione giornaliera globale di fatto' and no text read divides the monthly pay into it: the 1/26 of Art. 9 is limited to a festività on a Sunday. No termination basis is recorded. |
| 2026-11-08 | gpt-6-sol (ai) | CCNL top-ups of maternity and work injury, read from the signed text by a separate model session; every quote found on the PDF text layer. | confirmed | Added work_rules.insured_absence.maternity.<br>Added work_rules.insured_absence.injury. |
| 2026-11-08 | gpt-6-sol (ai) | The conto ore of the PAR not taken, the hourly pay of Tit. IV art. 3 and the leave settlement code path, by a separate model session in two rounds. | flagged | Round 1 found the payout blocked by the missing termination basis: the deadline now values the hours by the hour (PermitDeadline.permits_hourly), the termination path unchanged.<br>Round 2 confirmed the year offset (December of the second year after), the hourly valuation as the general hourly pay 'ai fini dei vari istituti contrattuali', and the test amounts (C3 131.27, level 5 132.42).<br>Flagged: the hourly pay of Tit. IV art. 3 adds the hourly elements (incentivi, cottimo), which the engine leaves out; kept under par_conto_ore_hourly_elements. |
| 2026-11-08 | gpt-6-sol (ai) | Sez. IV Tit. III art. 9 against the holiday target in sickness, by a separate model session. | flagged | Confirmed: the holidays of letters b and c in a sickness compensated with reduced pay reach 100%; excluded_days leaves exactly the national letter b days (04-25, 05-01, 06-02 and 10-04 out); Easter Monday 2026 adds 16.60.<br>Flagged: 29 June (Rome only) and the patron saint are outside the national calendar; injury and pregnancy holidays not topped up. |
| 2026-11-08 | gpt-6-sol (ai) | Sez. IV Tit. III art. 9 (PDF pp. 164-165) against the holiday target in a work injury, by a separate model session. | flagged | Confirmed: the holidays of letter b in an injury compensated with reduced pay reach the whole daily pay; letter a (25 April, 1 May, 2 June) and 4 October excluded; the extra nets the INAIL share and the employer integration of the day; the waiting days and the injury day are not paid twice.<br>Flagged: 29 June (Rome) and the letter c holidays (patron saint, substitute) are outside the national calendar. |
| 2026-11-08 | gpt-6-sol (ai) | Art. 5 sez. IV tit. III (PDF pp. 164-165), patron saint day of letter c against the sickness and injury holiday target, by a separate model session. | confirmed | Confirmed: letter c (patron of the place of work) is in the absence top-up of p. 165, letter a is not.<br>Confirmed: a stated patron_saint_day adds one weekday holiday; a day coinciding with a national holiday or a Sunday adds nothing.<br>Kept as limitation: the substitute holiday agreed in place of the patron is not modelled. |
| 2026-11-09 | gpt-6-sol (ai) | Part-time supplementary work (Sez. IV Tit. I C, PDF pp. 57-58), by a separate model session. | confirmed | Confirmed: 10% up to 50% of the normal annual part-time hours and 20% beyond, only up to 40 weekly hours, on the overtime-premium pay elements.<br>Confirmed: the engine derives only the 10% band; the 20% excess is a caller-supplied multiplier, and the annual count is outside the engine.<br>Flagged and added to the limitation: the elastic clauses (10% and 15%) and the conditions of supplementary work. |
| 2026-11-10 | gpt-6-sol (ai) | Tit. IV art. 3 hourly pay and the conto ore deadline: expired PAR paid at the monthly pay over 173 plus the stated hourly elements. | confirmed | CONFIRMED: the hourly pay of the clause includes the hourly elements (incentives, hourly allowances, piecework) and the expired PAR are paid at it; divisor 173.<br>CONFIRMED: quotes verbatim; December 2027 example 10 x (2271.01 / 173 + 2.50) = 156.27 and an independent case recomputed.<br>CONFIRMED: payout at termination before the deadline is not regulated by the cited passages and stays a limitation. |
| 2026-11-13 | gpt-6-sol (ai) | PAR of the Federmeccanica renewal of 22 November 2025 (scanned pp. 8-9, 33) against the settore siderurgico tier, by a separate model session. | flagged | Confirmed: 124 hours in place of the 104 for the settore siderurgico ('sono invece previsti [...] 124 ore'), with the same 32 hours of ex festività; the sector is that of the plants of Disciplina generale pp. 8-9.<br>Confirmed: the 8 hours of the turnisti on 15 or more weekly shifts including the night shift, the weekend wording struck out by the renewal; the 2027 and 2028 shift extras do not change the base tiers.<br>Flagged and corrected: the siderurgico turnisti have the 8 hours paid with the 13th, not accrued; the historical sottosettore hour needs service at 31 December 2012. |
| 2026-11-14 | gpt-6-sol (ai) | Art. 7 quote esenti of the ipotesi of 22 November 2025 (PDF p. 35) and art. 2 decorrenza (PDF p. 4), read on the rendered scans by a separate model session. | confirmed | Confirmed: 8% more per overtime hour of the quote esenti past 40 hours a year (shift workers, firms above 200 employees) or 48 (non-shift workers in firms up to 200), absorbing better company terms; no separate decorrenza from the contract's 22 November 2025. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Level 8 — quadro, maximum professional grade | € 3,070.61 | 2028-06-01 |
| `B3` | Level 7 — high technical or managerial expertise | € 2,998.76 | 2028-06-01 |
| `B2` | Level 6 — specialist technician, department head, technical employee | € 2,686.08 | 2028-06-01 |
| `B1` | Level 5 Super — highly specialised worker, technician | € 2,503.72 | 2028-06-01 |
| `C3` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,335.88 | 2028-06-01 |
| `C2` | Level 4 — specialist worker 1st category, white-collar employee | € 2,181.09 | 2028-06-01 |
| `C1` | Level 3 — skilled worker, clerical employee | € 2,135.89 | 2028-06-01 |
| `D2` | Level 2 — standardised operations, simple white-collar duties | € 2,090.76 | 2028-06-01 |
| `D1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,885.37 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.05 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 40.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_30** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

**professionalizzante_24** (type: `percentage`)  
Destination levels: `D2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-federmeccanica/overtime_exempt_quota_supplement · overtime · impact yes · open"
    OVERTIME, QUOTE ESENTI (art. 7, ipotesi of 22 November 2025 p. 35): 8% more per overtime hour of the regime past 40 hours a year (shift workers, firms above 200 employees) or 48 (workers not on shifts in firms up to 200) is added when the event states the hours of the regime worked earlier in the year (OvertimeEvent.exempt_quota_hours_before) and, in a firm up to 200 employees, whether the worker is on shifts (OvertimeEvent.in_periodic_shift). Without those facts the premium is not added and the run carries this limitation.

    **Applies when:** `overtime` applies; the run takes the engine code path.

    **Remediation:** State OvertimeEvent.exempt_quota_hours_before (and in_periodic_shift in a firm up to 200 employees) on the overtime of the quote esenti.

!!! warning "metalmeccanico-federmeccanica/shift_and_multiweek_premiums · overtime · impact yes · open"
    SHIFT WORK AND MULTI-WEEK SCHEDULE: the shift column of Art. 7 (night overtime 40% for the first two hours and 45% after, night holiday overtime 65%; night shift work 20%, 60% and 35% from 1 June 2013, 25%, 65% and 40% from 22 to 6) and the premiums of the orario plurisettimanale of Art. 5 as renewed on 22 November 2025 (15% Monday to Friday and 25% on Saturday, 20% and 30% for sudden needs, raised by 8% from the 81st hour, p. 32 of the signed scan) are not modelled: an overtime event of a shift worker or of a multi-week schedule takes the non-shift bands.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the shift column of Art. 7 and the multi-week premiums of Art. 5 with a fact naming the schedule of the worker, then remove this note.

!!! warning "metalmeccanico-federmeccanica/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: work up to 40 weekly hours earns an all-inclusive 10% on the overtime-premium pay elements until supplementary hours exceed 50% of agreed annual part-time hours; the excess earns 20% (CCNL 5 February 2021, PDF p. 58). OT_SUPPLEMENTARE derives only 10%. A caller may split hours at the boundary and explicitly supply multiplier 1.20 for the excess; the engine cannot count year-to-date supplementary hours or split an event that crosses the boundary. The elastic clauses of the same section (PDF p. 57: 10% for a rearranged placement of hours, 15% for an increase in duration up to 25% of the normal annual part-time hours) and the conditions of supplementary work (specific needs, notice to the RSU, no proven individual impediment) are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Supply agreed annual part-time hours and prior supplementary hours to split crossing events and derive the 20% rate on the excess without a caller override.

!!! warning "metalmeccanico-federmeccanica/elemento_perequativo · base_salary · impact yes · open"
    ELEMENTO PEREQUATIVO (Sez. Quarta Tit. IV Art. 13, pp. 177-178): 485 euro a year with the June pay to the worker in service on 1 January of a company without second-level bargaining (EmployerProfile.second_level_premium false), for the months of the year before over twelve; the engine pays it (parameters.equalisation_element). Left open: the pay above the CCNL the worker received in the year before (superminimi, premi annui, other pay subject to contributions) has no field in the request; the engine reads it from the individual elements of the run, each amount on 31 December of the year before at the part-time fraction, for each month served, on twelve monthly payments, so an element agreed since, the share of the extra months or a yearly premium of the year before is not seen. A run without the employment period pays none; a second-level element the employer states counts when in force in the year before.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** State the pay above the CCNL of the year before as a fact of the run, or pass the element as a bonus and leave the employer flag true.

!!! warning "metalmeccanico-federmeccanica/par_sector_and_shift_hours · leave · impact yes · open"
    LEAVE, PAR (Sez. Quarta, Titolo III, Art. 5, renewal of 22 November 2025 p. 33): the settore siderurgico (EmployerProfile.subsector steel) accrues 124 hours in place of 104, and the turnisti on 15 or more weekly shifts including the night shift (Employment.qualifying_shifts) 8 hours more. Not modelled: the 8 hours of the siderurgico turnisti, paid with the 13th; the further 4 hours from 2027 at 18 or more weekly shifts and 4 more from 2028 at 21 for the non siderurgico workers; and the hour of the sottosettori of the accordo of 16 July 1979 for the workers in service at 31 December 2012.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add employment facts for 18 and 21 weekly shifts with night work and for the historical sottosettore, accrue their hours, and pay the siderurgico shift hours with the 13th.

!!! warning "metalmeccanico-federmeccanica/par_conto_ore_hourly_elements · leave · impact yes · open"
    LEAVE, CONTO ORE: the hourly elements of Tit. IV art. 3 are included in the PAR payout at expiry when the caller states hourly_pay_elements (zero confirms none; missing blocks payment). PAR left when employment ends before expiry remain unpaid: Tit. III art. 5 specifies liquidation at expiry but no termination basis.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Source the payment basis and timing for PAR left when employment ends before the conto ore expires.

!!! warning "metalmeccanico-federmeccanica/holiday_outside_calendar · sickness · impact yes · open"
    Art. 9 (Sez. IV Tit. III): the holidays of letters b and c in a sickness or a work injury reach 100% (sickness_rules.holiday and insured_absence.injury.holiday). Not calculated: the holiday top-up during pregnancy and puerperium, the patron saint substitute and 29 June, a letter b holiday in Rome only, outside the national calendar.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Top up pregnancy and puerperium holidays, the substitute patron holiday and Rome-only 29 June when the applicable local facts are stated.

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

!!! note "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · resolved"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time; for a vertical part time the circular divides the pay of the month by its paid days, rest days included, which ExtraordinaryLeaveEvent.last_month_paid_days states. A vertical or mixed part time that does not state them is paid on the full-time measure, so its indemnity may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Resolved: ExtraordinaryLeaveEvent.last_month_paid_days divides the pay of a vertical part time by its paid days (INPS circ. 64/2001 par. 4); a leave that does not state them is paid on the full-time measure with the provisional issue extraordinary_paid_days_unknown, which names the fact.

!!! note "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · resolved"
    The NASpI contribution of the end of an employment that does not state its case (EmploymentPeriod.naspi_case) is read from the cause, the just cause and the contract type alone: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km would owe it (INPS circ. 44/2013 par. 1), a collective dismissal would owe 82% for an employer owing the CIGS contribution (L. 205/2017 art. 1 c. 137) and three times without union agreement (L. 92/2012 art. 2 c. 35), the changes of contractor with a social clause and the closures of a construction site of c. 34 would leave it out. The service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Resolved: EmploymentPeriod.naspi_case states the cases that owe, leave out or multiply the contribution; an end that could be one and does not state it is decided from its cause alone with the provisional issue naspi_dismissal_case_unknown, which names the fact.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) and reduces the tax by ArrearsEvent.unused_deductions, the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4). An arrears event that does not state them, among which the una tantum the engine pays itself, is taxed without the reduction, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** State ArrearsEvent.unused_deductions from the worker's declaration of the deductions used each year; for the una tantum, carry it into the events the engine generates.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

!!! warning "sunday_holiday_ccnl_clause · sunday_holiday · impact yes · open"
    L. 260/1949 art. 5 pays the workers with a fixed salary a further daily quota only for the civil holidays (25 April, 1 May, 2 June) falling on a Sunday; the other holidays of art. 2 (1 January, 6 January, Easter Monday, 15 August, 4 October, 1 November, 8 December, 25 and 26 December) give it only by CCNL clause, and the payment of 4 November is a CCNL institute. A run of a month with such a holiday on a Sunday, in a CCNL whose clause is not sourced (work_rules.sunday_holidays), pays the statutory holidays only; a public employment is paid none, its treatment not being sourced.

    **Applies when:** `sunday_holiday` applies; the run takes the engine code path.

    **Remediation:** Source the CCNL clause on the holidays falling on a Sunday and record it as work_rules.sunday_holidays.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.uilmnazionale.it/wp-content/uploads/2025/11/20251122-CCNL-Federmeccanica-Assistal-Fim-Fiom-Uilm_Ipotesi-di-accordo-siglata.pdf | altro | 2025-11-22 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/11/20251122-CCNL-Federmeccanica-Assistal-Fim-Fiom-Uilm_Ipotesi-di-accordo-siglata.pdf) |
| https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260616-CCNL-Federmeccanica-Assistal-IPCA-Minimi-giugno-2026-trasferta.pdf | altro | 2026-06-16 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260616-CCNL-Federmeccanica-Assistal-IPCA-Minimi-giugno-2026-trasferta.pdf) |
| https://www.fiom-cgil.it/images/CCNL/INDUSTRIA/2021_02_05-CCNL-federmeccanica.pdf | altro | 2021-02-05 | [↗](https://www.fiom-cgil.it/images/CCNL/INDUSTRIA/2021_02_05-CCNL-federmeccanica.pdf) |
| Ipotesi di accordo di rinnovo del CCNL Federmeccanica-Assistal, 22 novembre 2025 (scansione firmata, UILM) | associazione | 2025-11-22 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/11/20251122-CCNL-Federmeccanica-Assistal-Fim-Fiom-Uilm_Ipotesi-di-accordo-siglata.pdf) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the 'consolidated table minimums' of the CCNL Federmeccanica-Assistal, which incorporate base pay, contingenza, and EDR into a single figure (Federmeccanica practice since 2001). For this reason fixed_allowances is empty for all levels.
    
    JUNE 2025 TRANCHE: values read in the signed minutes of 12 June 2025 (Federmeccanica, Assistal, Fim, Fiom, Uilm), all 9 levels.
    
    JUNE 2024 AND JUNE 2026 TRANCHES: June 2024 read in the signed minutes of 11 June 2024; June 2026 in the renewal of 22 November 2025 (ratified by the referendum of 18-20 February 2026), whose June 2026 tranche absorbs the IPCA share set by the minutes of 16 June 2026.
    
    SENIORITY INCREMENTS: the proposal to replace monthly increments with a one-off 'early settlement' was rejected in the 2025-2028 negotiations (renewal of 22 November 2025). Increments remain recurring monthly additions under Art. 6, Sez. Quarta Tit. IV, of the CCNL of 5 February 2021 (physical pp. 175-176), where the amounts by level are read.
    
    APPRENTICESHIP: professionalizzante (accordo integrativo 20/04/2021). Eligible levels: D2, C1, C2, C3, B1, B2, B3 (D1 and A1 excluded). Pay: 85% (first third), 90% (second third), 95% (third third), then classified at destination. Three duration tracks: 36m (standard), 30m (diploma EQF 4-7 consistent with profession), 24m (D2 serial repetitive production only). Source: accordo 20/04/2021 Federmeccanica art. 'Apprendistato professionalizzante', reproduced in MySolution circolare Marini 13/05/2021.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12 = 173.33 rounded to 173, Federmeccanica standard).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Federmeccanica CCNL. The performance bonus/variable company element is not modelled (layer 3).
    
    INPS: the employer rates of contribution/2026/industria.json for an impiegato are IVS 23.81% plus 4.65% up to 15 employees (28.46%), plus 5.25% from 16 to 50 (29.06%) and plus 5.55% from 51 (29.36%); the cost table of the Ministry of Labour of June 2026 (DD 82 of 5 October 2026) applies 29.36%. INAIL (4.417% in that table) is not computed by the engine (review of 2026-10-30)
    
    JUN 2021, JUN 2022, JUN 2023 TRANCHES: read in the CCNL of 5 February 2021 and the signed minutes of 16 June 2023; four annual tranches (June 2021-2024) under the IPCA mechanism of the 2021 CCNL.
    
    OVERTIME/NIGHT/HOLIDAY: Art. 7 Sez. Quarta Titolo III of the CCNL of 5 February 2021 (physical pp. 160-161): for work not in shifts, overtime 25% for the first two hours and 30% after, night overtime 50%, holiday overtime 55%, night holiday overtime 75%, as the overtime bands model. The renewal of 22 November 2025 leaves the percentages of art. 7 ("Omissis", p. 35 of the signed scan) and adds only the 8% of the quote esenti (note below).
    
    SICKNESS (Sez. Quarta Titolo VI Art. 2): full pay for the first 122/153/214 days of the treatment chain and 80% after, by seniority band (up to 3 years, 3 to 6, over 6); comporto breve of 183/274/365 days over the sickness of the three years that end on the day; the chain restarts after 61 days of work; the first 3 days of the fourth short absence (at most 5 days) of a calendar year are paid 66%, of the fifth and later 50%. The history before the imported episodes, the seniority and the exemption of a short absence are facts: when they could change a sick day the run has a missing_fact blocker.
    
    TRAVEL AND ON-CALL ALLOWANCES (Art. 7 Trasferta p. 61, Art. 6 Reperibilità p. 158 of the CCNL 2021; adjusted each June by IPCA per the renewal of 22 November 2025, p. 2): event-driven. From 1 June 2026 (minutes of 16 June 2026): trasferta intera 51.29, pasto 13.13, pernottamento 25.03; reperibilità by level group D1-D2-C1 / C2-C3 / B1+ per 16h worked day, 24h rest day, 24h holiday and per week. A StandbyEvent is paid at the rates of work_rules.standby_rules (from 1 June 2025; the earlier rates are not extracted) plus 5.00 for each call; a TravelAllowanceEvent pays the daily_amount the caller states, since the file holds no trasferta amounts (review of 2026-10-30)
    
    APPRENTICESHIP TRACKS (CCNL 5 February 2021, accordo sull'apprendistato, pp. 267-271): 36 months, reduced by 6 months for a diploma of level 4 QEQ or above (30), 24 for the D2 figures on assembly lines; each third at 85, 90 and 95% of the destination level.
    
    HOURLY RATE AND SUPPLEMENTS (Art. 7 Sez. Quarta Tit. III of the CCNL of 5 February 2021, rates untouched by the renewal of 22 November 2025): without a caller value the engine derives the hourly base (minimi, scatti and fixed allowances over 173) and the supplements on holiday hours (50%) and on holiday hours with a compensatory rest (10%), equal in both columns. Whether those hours are also paid on top of the monthly pay is not settled: a derived holiday supplement is provisional. Not derived, the caller states the amount: ordinary night work (20% until 22 and 30% after; shift workers 15%, 20% from June 2013, 25% from 22 to 6 in the impiantistica), because its window starts 12 hours after the morning shift of each work group and its rate depends on the hour and on the shift column, facts the request does not carry; night holiday work and Sunday work. Individual elements (merito, superminimi, cottimi) are not in the hourly base. Absences: no clause sets the divisor of an absence deduction; the 1/26 of art. 9 (festività on a Sunday) is taken by analogy (work_rules.absence_rules derived, was verified on the wrong clause): the caller states AbsenceEvent.hourly_rate.
    
    LEAVE AT TERMINATION (Sez. IV, Tit. III, Art. 10, p. 166 of the CCNL of 5 February 2021): 'L’indennità dovuta al lavoratore per le giornate di ferie non godute è costituita dalla retribuzione giornaliera globale di fatto'. No clause of the 2021 text or of the ipotesi of 22 November 2025 (OCR) defines that daily pay as a fraction of the monthly pay: the only daily quota stated (1/26 of the retribuzione mensile fissa, Art. 9, p. 164) is the pay of a festività falling on a Sunday, and the divisor 173 (Tit. IV, Art. 3, p. 173) gives the hourly pay. The engine pays no residual (termination_residual_leave incomplete, termination_basis_not_sourced).
    
    APPRENTICE SENIORITY (Disciplina dell'apprendistato professionalizzante, Art. 13, p. 272 of the CCNL 5 February 2021): the apprenticeship counts for the aumenti periodici of the worker kept in service for 65% of its length; no increment during it (seniority_increments.apprentice_amount 0.00).
    
    LEAVE, CONTO ORE (Sez. IV Tit. III Art. 5, p. 156): the PAR not taken in their year are carried 24 more months and the residual is paid with the December pay of the second year after, at the pay of that run (work_rules.leave_rules.permit_deadline, carry_years 2).
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-federmeccanica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-federmeccanica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-federmeccanica/example.py"
```
