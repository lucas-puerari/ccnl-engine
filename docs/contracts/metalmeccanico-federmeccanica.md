# CCNL Metalmeccanici e Installatori di Impianti (Federmeccanica-Assistal)

| | |
|---|---|
| **CNEL code** | `C011` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
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
| **Limits of this contract** | overtime, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 85 verified / 0 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-14 |
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

!!! warning "metalmeccanico-federmeccanica/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "metalmeccanico-federmeccanica/overtime_exempt_quota_supplement · overtime · impact yes · open"
    OVERTIME, QUOTE ESENTI: the 2025 ipotesi (p. 35) adds 8% to the overtime hours worked beyond the exempt quota of 40 or 48 hours a year; the engine does not count the overtime hours of the year, so it does not add it.

    **Applies when:** `overtime` applies.

    **Remediation:** Count the overtime hours of the year and add 8% past the exempt quota, or pass the multiplier on the overtime event.

!!! warning "metalmeccanico-federmeccanica/shift_and_multiweek_premiums · overtime · impact yes · open"
    SHIFT WORK AND MULTI-WEEK SCHEDULE: the shift column of Art. 7 (night overtime 40% for the first two hours and 45% after, night holiday overtime 65%; night shift work 20%, 60% and 35% from 1 June 2013, 25%, 65% and 40% from 22 to 6) and the premiums of the orario plurisettimanale of Art. 5 as renewed on 22 November 2025 (15% Monday to Friday and 25% on Saturday, 20% and 30% for sudden needs, raised by 8% from the 81st hour, p. 32 of the signed scan) are not modelled: an overtime event of a shift worker or of a multi-week schedule takes the non-shift bands.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the shift column of Art. 7 and the multi-week premiums of Art. 5 with a fact naming the schedule of the worker, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-11-22 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/11/20251122-CCNL-Federmeccanica-Assistal-Fim-Fiom-Uilm_Ipotesi-di-accordo-siglata.pdf) |
| — | — | 2026-06-16 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260616-CCNL-Federmeccanica-Assistal-IPCA-Minimi-giugno-2026-trasferta.pdf) |
| — | — | 2021-02-05 | [↗](https://www.fiom-cgil.it/images/CCNL/INDUSTRIA/2021_02_05-CCNL-federmeccanica.pdf) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: the values in base_salary are the 'consolidated table minimums' of the CCNL Federmeccanica-Assistal, which incorporate base pay, contingenza, and EDR into a single figure (Federmeccanica practice since 2001). For this reason fixed_allowances is empty for all levels.
    
    JUNE 2025 TRANCHE: values read in the signed minutes of 12 June 2025 (Federmeccanica, Assistal, Fim, Fiom, Uilm), all 9 levels.
    
    JUNE 2024 AND JUNE 2026 TRANCHES: June 2024 read in the signed minutes of 11 June 2024; June 2026 in the renewal of 22 November 2025 (ratified by the referendum of 18-20 February 2026), whose June 2026 tranche absorbs the IPCA share set by the minutes of 16 June 2026.
    
    SENIORITY INCREMENTS: the proposal to replace monthly increments with a one-off 'early settlement' was rejected in the 2025-2028 negotiations (renewal of 22 November 2025). Increments remain recurring monthly additions under Art. 6, Sez. Quarta Tit. IV, of the CCNL of 5 February 2021 (physical pp. 175-176), where the amounts by level are read.
    
    APPRENTICESHIP: professionalizzante (accordo integrativo 20/04/2021). Eligible levels: D2, C1, C2, C3, B1, B2, B3 (D1 and A1 excluded). Pay: 85% (first third), 90% (second third), 95% (third third), then classified at destination. Three duration tracks: 36m (standard), 30m (diploma EQF 4-7 consistent with profession), 24m (D2 serial repetitive production only). Source: accordo 20/04/2021 Federmeccanica art. 'Apprendistato professionalizzante', reproduced in MySolution circolare Marini 13/05/2021.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week × 52/12 = 173.33 rounded to 173, Federmeccanica standard).
    
    MONTHLY PAYMENTS: 13 (thirteenth month). The fourteenth month is not provided for in the Federmeccanica CCNL. The performance bonus/variable company element is not modelled (layer 3).
    
    INPS: the employer rates in 2026-industria.json are calculated for verified components (IVS 23.81% + DS 1.61% + CUAF 2.48% + CIGO D.Lgs.148/2015 + FIS/CIGS Circ.INPS 5/2025). Resulting totals: ≤15 employees = 30.13%, 16-50 employees = 30.20%, >50 employees = 30.50%. Does not include INAIL. The CIGS employee share (0.30% for >15 employees) is not yet modelled in employee_rate.
    
    JUN 2021, JUN 2022, JUN 2023 TRANCHES: read in the CCNL of 5 February 2021 and the signed minutes of 16 June 2023; four annual tranches (June 2021-2024) under the IPCA mechanism of the 2021 CCNL.
    
    OVERTIME/NIGHT/HOLIDAY: Art. 7 Sez. Quarta Titolo III of the CCNL of 5 February 2021 (physical pp. 160-161): for work not in shifts, overtime 25% for the first two hours and 30% after, night overtime 50%, holiday overtime 55%, night holiday overtime 75%, as the overtime bands model. The renewal of 22 November 2025 leaves the percentages of art. 7 ("Omissis", p. 35 of the signed scan) and adds only the 8% of the quote esenti (note below).
    
    SICKNESS (Sez. Quarta Titolo VI Art. 2): full pay for the first 122/153/214 days of the treatment chain and 80% after, by seniority band (up to 3 years, 3 to 6, over 6); comporto breve of 183/274/365 days over the sickness of the three years that end on the day; the chain restarts after 61 days of work; the first 3 days of the fourth short absence (at most 5 days) of a calendar year are paid 66%, of the fifth and later 50%. The history before the imported episodes, the seniority and the exemption of a short absence are facts: when they could change a sick day the run has a missing_fact blocker.
    
    TRAVEL AND ON-CALL ALLOWANCES (Art. 7 Trasferta p. 61, Art. 6 Reperibilità p. 158 of the CCNL 2021; adjusted each June by IPCA per the renewal of 22 November 2025, p. 2): event-driven, not modelled. From 1 June 2026 (minutes of 16 June 2026): trasferta intera 51.29, pasto 13.13, pernottamento 25.03; reperibilità by level group D1-D2-C1 / C2-C3 / B1+ per 16h worked day, 24h rest day, 24h holiday and per week. The engine takes no travel or on-call event, so these amounts are not paid.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-federmeccanica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-federmeccanica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-federmeccanica/example.py"
```
