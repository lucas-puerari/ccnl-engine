# CCNL Logistica, Trasporto Merci e Spedizione (Confetra) - Personale viaggiante

| | |
|---|---|
| **CNEL code** | `I100` |
| **Sector** | logistica |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-12-06 |
| **Workers (est.)** | ~430k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - AITI
    - ASSOESPRESSI
    - ASSOLOGISTICA
    - FEDESPEDI
    - FEDIT
    - FISI
    - TRASPORTOUNITO FIAP
    - ANITA
    - Confetra
    - FILT-CGIL
    - FIT-CISL
    - UILTrasporti

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | absence, base_salary, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 53 verified / 30 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-12-06 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2027-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-11 | claude-opus-5-5 (ai) | Inherited from logistica-trasporto-confetra, of which this file is a copy: the review covered that file's levels; here it stands for the shared rules (work rules, parameters) only. Every payable rule of the file (55 records) read again in the signed testo unico of the renewal of 6 December 2024 (Verbale di accordo 25 September 2025), published by Confetra; the URLs the file cited return 404. | corrected | Corrected: every one of the 36 salary periods. The base salary is the minimo plus the EPA of the tables of pp. 80-81 for non-travelling staff; the file held values about 88-110 EUR too high. The printed Totale of the 1 January 2027 table already includes the minimo increase of 1 June 2027; the Legacoop circular of 19 December 2024 (p. 2) confirms that January 2027 is an EPA-only step, so the period holds minimo plus EPA.<br>Corrected: the Quadri receive the indennità di funzione of 51.65 EUR a month (Art. 6 c. 4, p. 17), which the file lacked.<br>Corrected: the daily quota is 1/22 (Art. 61 c. 3, Sezione prima, p. 86), not 1/26, which applies to a six-day week of non-travelling staff and to Sezione seconda (Art. 73 c. 5).<br>Verified: 14 monthly payments (Artt. 18-19), the accrual of fractions over 15 days (Art. 18 c. 2, Art. 19 c. 2), seniority (Art. 17) and 22 days of leave (Art. 24). Pages are PDF page numbers, equal to the printed ones.<br>Assumed: sickness. Art. 63 A) c. 7-12 keeps the job 245 or 365 days and pays 3 months in full and 5 at half (up to 5 years of service) or 5 and 7, counted over 24 or 30 months; the cumulation model holds one window in whole years for every band, so the rule is not expressible and the file's 100% for 180 days is wrong.<br>Left derived: the overtime rates (30%, 50%, 65%, 75%, Art. 13 c. 6) match, but their start of 2023-05-01 is not stated; the level descriptions are paraphrases.<br>Not modelled: the EDR of Art. 60 c. 8 (10 EUR at level 3S, re-parametrised) for workers in service on 26 January 2011, which affects every entitlement, and level 6J and travelling staff. |
| 2026-10-12 | claude-opus-5-5 (ai) | Inherited from logistica-trasporto-confetra, of which this file is a copy: the review covered that file's levels; here it stands for the shared rules (work rules, parameters) only. Sickness rule of art. 63 A), now expressible with a window and steps per seniority band; readiness of the file. | corrected | The sickness rule was assumed (100% for 180 days, not the CCNL's): it is now 90 days in full and 150 at half within 24 months, comporto 245 days, up to 5 years of seniority; 150 in full and 210 at half within 30 months, comporto 365 days, above.<br>With no assumed or missing payable rule left and the salary tables, additional months, divisor and seniority verified on 2026-10-11, the file is promoted to reviewed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Travelling staff: levels, salary tables of the four tranches, seniority, EDR 2011 and 2021, apprenticeship, overtime, against the signed testo unico (Verbale 25 September 2025). | corrected | This file was created from logistica-trasporto-confetra for the travelling staff, which that file left out: same rules and review history, with the travelling levels, seniority amounts, EDR and apprenticeship tracks.<br>51 of the 52 salary values equal minimo plus EPA and the printed Totale of pp. 81-82; F2 prints a Totale 0.06 above the sum at every tranche. The Legacoop circular of December 2024 confirms the F2 minimo (1.791,51 + 87,63), so the Totale is the misprint: F2 takes the sum and stays derived.<br>Saturday and Sunday overtime of the travelling staff is 30% (art. 13 c. 6); the engine has one holiday band, left as a limitation.<br>Tabella B (p. 75) reads by year: drivers A3-C3 over 5 years and D2-F2 over 4, 90% the first year, 95% the second, 100% after. |
| 2026-10-12 | claude-opus-5-5 (ai) | Weekend overtime and working time of the travelling staff (artt. 11, 11 bis, 13). | corrected | Sunday overtime of the travelling staff is 30% (art. 13 c. 6), not the 65% of the holiday band: new band OT_RIPOSO on the rest_day overtime kind.<br>The 47-hour regime of art. 11 bis changes the overtime threshold, not the pay: the hourly divisor is 168 under every regime (art. 13 c. 8); the limitation travelling_working_time is closed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Malattie particolarmente gravi (art. 63 cc. 8 and 12). | corrected | The serious illnesses of INPS circ. 95/2016 were a limitation (grave_illness): now paid in full for 18 months and left out of the comporto when SicknessEpisode.serious_illness says so. |
| 2026-10-12 | claude-opus-5-5 (ai) | Indennità di trasferta of the travelling staff (art. 62). | corrected | The allowance amounts of art. 62 c. 3 from 1.1.2025 and the TFR rule of c. 7 are now CCNL data: a TravelAllowanceEvent without daily_amount takes the amount of its hours away. |
| 2026-10-16 | claude-opus-5-5 (ai) | The employer INPS rate of the personale viaggiante in the cost table of the Ministry of Labour (DD 135 of 19 December 2025) against the INPS rate tables and the classes of the bundle. | flagged | DD 135/2025 prints 'Inps (30,68%)' on every table of the personale viaggiante, with no composition, no class of employer and no number of employees.<br>30.68% is, to the cent, the employer rate of an INPS class industria employer up to 15 employees for operai and intermedi: IVS 23.81 + NASpI 1.61 + CUAF 0.68 + CIG ordinaria 1.70 + Fondo garanzia TFR 0.20 + malattia 2.22 + maternità 0.46 (INPS tables of January 2023 reproduced by GIA Parma, row 'Industria, aziende fino a 15 dipendenti, Operai - Intermedi'). The engine applies the same 30.68% to an operaio viaggiante of an employer up to 15 employees, and 31.28% from 16 to 50 and 31.58% above (CIG straordinaria 0.90 and the higher CIG ordinaria): match for the smallest band, no evidence for the others.<br>Not established: whether the Ministry assumes an employer up to 15 employees or a class other than industria. A press article (Euroconference, 24 November 2021) classifies a road haulage employer in the INPS sector terziario, CSC 7.04.01, which would give other rates; the class is a fact of the employer, so it is not decided here. |
| 2026-10-17 | claude-opus-5-5 (ai) | The INPS sector of the employers of the CCNL against the INPS classification manual, after the review 2026-10-16-ai-inps-composition left the class of the employer open. | corrected | The Manuale di classificazione dei datori di lavoro of INPS (May 2021, ATECO 2007) classifies the activities of this CCNL in two sectors: autotrasporto, traslochi, movimento merci and corrieri in the industria (CSC 11501, 11505, 11507), magazzini di custodia, spedizionieri, intermediari dei trasporti and servizi logistici in the terziario (CSC 70401). The file applied the industria to every employer.<br>Corrected: meta.inps_sectors lists industria and terziario; EmployerProfile.inps_sector states the sector of the employer and the run reads its INPS rates, sickness cover and every rule that follows the sector; a run without it reads the industria with a missing_fact inps_sector blocker.<br>INPS circ. 71/2025 adopted ATECO 2025 from 1 April 2025 and announced a new edition of the manual; that edition was not found: the classification above is the one of the 2021 edition. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `C3` | Qualifica 3, lettera C (parametro 133.5): driver of the highest qualification | € 2,131.65 | 2027-06-01 |
| `B3` | Qualifica 3, lettera B (parametro 133): driver | € 2,100.37 | 2027-06-01 |
| `A3` | Qualifica 3, lettera A (parametro 132.5): driver | € 2,079.11 | 2027-06-01 |
| `F2` | Qualifica 2, lettera F (parametro 129.5): driver | € 2,017.83 | 2027-06-01 |
| `E2` | Qualifica 2, lettera E (parametro 129): driver | € 2,016.61 | 2027-06-01 |
| `D2` | Qualifica 2, lettera D (parametro 128.5): driver | € 2,015.34 | 2027-06-01 |
| `H1` | Qualifica 1, lettera H (parametro 124.5): driver | € 1,951.23 | 2027-06-01 |
| `G1` | Qualifica 1, lettera G (parametro 124): driver | € 1,938.72 | 2027-06-01 |
| `L119` | Lettera L, parametro 119: rider on a moped or motorcycle, after further 9 months | € 1,821.92 | 2027-06-01 |
| `L116` | Lettera L, parametro 116: rider on a moped or motorcycle, after 6 months | € 1,777.23 | 2027-06-01 |
| `I116` | Lettera I, parametro 116: rider on a bicycle, after 6 months | € 1,757.24 | 2027-06-01 |
| `L110` | Lettera L, parametro 110: rider on a moped or motorcycle, first 6 months | € 1,687.91 | 2027-06-01 |
| `I110` | Lettera I, parametro 110: rider on a bicycle, first 6 months | € 1,667.91 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `C3` | € 24.79 |
| `B3` | € 24.79 |
| `A3` | € 24.79 |
| `F2` | € 24.27 |
| `E2` | € 24.27 |
| `D2` | € 24.27 |
| `H1` | € 23.24 |
| `G1` | € 23.14 |
| `I110` | € 22.18 |
| `I116` | € 22.18 |
| `L110` | € 21.62 |
| `L116` | € 21.62 |
| `L119` | € 21.62 |

## Apprenticeship

**drivers_g_h** (type: `percentage`)  
Destination levels: `H1`, `G1`  
percentage: 1.00

**drivers_a_f** (type: `percentage`)  
Destination levels: `C3`, `B3`, `A3`, `F2`, `E2`, `D2`  
percentage: 1.00

**riders** (type: `percentage`)  
Destination levels: `I110`, `I116`, `L110`, `L116`, `L119`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "logistica-trasporto-confetra-viaggiante/travelling_allowances · base_salary · impact yes · open"
    NOT MODELLED: the night allowance of art. 16 for a trasferta under 18 hours overlapping the night hours (paid only from 18 hours), the 50% on the Sunday and holiday work within the ordinary hours (art. 12 c. 4), and the 4.5 days of paid leave of art. 11 c. 11. The trasferta of art. 62 and the night allowance of a trasferta of 18-24 hours are paid by TravelAllowanceEvent.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the night allowance of art. 16 and the Sunday or holiday work within the ordinary hours outside the engine.

!!! warning "logistica-trasporto-confetra-viaggiante/edr_2021_in_daily_base · absence · impact unknown · open"
    EDR: the EDR of EUR 10.33/month (agreement 26 Jan 2001) is conglobated into the minimum pay tables (Art. 61 note). The EDR of art. 60 c. 8 (workers in service on 26 January 2011) and the EDR of the agreement of 18 May 2021 (13 mensilità, no effect on other institutes) are paid as allowances; the 2021 EDR may still enter the daily base of absences and sickness, which 'nessuna incidenza su alcun istituto contrattuale' excludes.

    **Applies when:** `absence` applies.

    **Remediation:** Exclude EDR_2021 from the daily base of absences and sickness (a relevance flag on the allowance), or source that it enters it.

!!! warning "logistica-trasporto-confetra-viaggiante/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.confetra.com/wp-content/uploads/Nuovo-Testo-Unico-del-CCNL-logistica-trasporto-e-spedizione_pulito.pdf | altro | 2024-12-06 | [↗](https://www.confetra.com/wp-content/uploads/Nuovo-Testo-Unico-del-CCNL-logistica-trasporto-e-spedizione_pulito.pdf) |

??? note "Coverage notes"
    STAFF: travelling staff (personale viaggiante) of the CCNL Logistica: drivers of qualifiche 3 (C, B, A), 2 (F, E, D) and 1 (H, G) and riders of letters I (bicycle) and L (moped or motorcycle), art. 2 pp. 25-26, tables pp. 81-82. The non-travelling staff is logistica-trasporto-confetra. Every level is an operaio.
    
    RIDER PARAMETERS: letter I starts at parametro 110 and moves to 116 after 6 months; letter L starts at 110, moves to 116 after 6 months and to 119 after further 9 months (art. 2, p. 26). Each parametro is a level (I110, I116, L110, L116, L119): the request names the parametro reached, the engine does not move the worker.
    
    TRANCHES: four tranches: 1.1.2025, 1.1.2026, 1.1.2027 (EPA), 1.6.2027 (minimo and EPA), +260.00 at B3 in all (140 minimo, 120 EPA, p. 82). base_salary is minimo plus EPA.
    
    SENIORITY INCREMENTS: biennial, at most 5 bienni, amounts of the travelling column of art. 17 c. 2 (p. 41).
    
    APPRENTICESHIP: Tabella A (p. 75): drivers G1 and H1 75%, 85%, then 100%; riders I and L 100% throughout. Tabella B: drivers A3, B3, C3 (5 years) and D2, E2, F2 (4 years) 90%, 95%, then 100%.
    
    WORKING TIME: drivers work 39 hours a week (art. 11 c. 1) over up to 6 days, averaged over 4 weeks; the discontinuous drivers of art. 11 bis (qualifiche 3 A-C and 2 D-F, after the verification procedure) work 47 hours ordinary. The regime moves only the threshold beyond which an hour is overtime: the monthly pay is the same and the hourly pay divides it by 168 under every regime (art. 13 c. 8), so the request declares the overtime hours beyond the worker's own regime.
    
    TRAVELLING WEEKEND OVERTIME: Saturday and Sunday overtime of the travelling staff is 30% (art. 13 c. 6, p. 39): Saturday as weekday overtime, Sunday as rest_day overtime (OT_RIPOSO). Overtime on the festività of artt. 60 and 71 is holiday overtime at 65%, 75% at night. The rates do not add up and the higher absorbs the lower (c. 7): a weekend overtime hour at night is night overtime (50%), reported as night.
    
    CONGLOBATED MINIMUMS: base_salary values are the conglobated monthly minimum pay (minimum pay table + contingenza per Art. 61 note + EPA). Primary check: Art. 61 of the consolidated text September 2025 — 'From 1.1.2001 the indennità di contingenza has been conglobated into the minimum pay tables together with the EDR of EUR 10.33 per month'. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 168 hours/month. Primary source: Art. 61 para. 3 consolidated text September 2025 — 'The hourly pay is obtained by dividing the monthly pay by 168'.
    
    ICE: the Indennità di Copertura Economica (ICE) was a provisional element in force until 31.12.2024. It ceases from 1.1.2025 with the renewal taking effect. base_salary values do not include ICE (ceased element). The consolidated text cites net increases of EUR 230 at 3S compared to the previous pay including ICE — the difference from the algebraic sum of the tranches (EUR 290 from base without ICE) corresponds to the pre-existing ICE value for that level.
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 18 + quattordicesima Art. 19 consolidated text September 2025).
    
    EPA: Elemento Professionale d'Area, a component introduced by the 6.12.2024 renewal. Included in base_salary values from 1.1.2025. Not shown separately because it forms an integral part of the minimum pay (it affects all contractual and statutory entitlements) — see Confetra circ283-2024.
    
    INPS: meta.inps_sectors lists industria (contribution/2026/industria.json) and terziario (contribution/2026/terziario.json); EmployerProfile.inps_sector chooses, and without it the run reads the industria with a missing_fact inps_sector blocker (see the INPS SECTOR OF THE EMPLOYER note) (review of 2026-10-30)
    
    INPS SECTOR OF THE EMPLOYER: INPS classifies an employer by the activity it carries out (art. 49 L. 88/1989), not by the CCNL it applies. The Manuale di classificazione dei datori di lavoro of May 2021 (ATECO 2007, PDF pp. 199-206) gives CSC 11501 (industria, trasporti) to 49.41.00 trasporto di merci su strada and 49.42.00 traslochi, 11505 (industria) to 52.24 movimento merci and 52.21.90, 11506 to 52.21.40 interporti, 11507 to 53.20.00 corrieri, and 70401 (terziario, intermediari) to 52.10.10 magazzini di custodia e deposito, 52.29.10 spedizionieri, 52.29.21 intermediari dei trasporti and 52.29.22 servizi logistici. The employers of this CCNL are therefore in the industria or in the terziario: meta.inps_sectors lists both and EmployerProfile.inps_sector chooses; without it the run reads the industria and has a missing_fact inps_sector blocker. INPS circ. 71/2025 moved the classification to ATECO 2025 from 1 April 2025 and announced a new edition of the manual, not found in this review: the CSC above are those of the 2021 edition.
    

## Raw data

The contract file this page is generated from: [`agreement/logistica-trasporto-confetra-viaggiante.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/logistica-trasporto-confetra-viaggiante.json).

## Usage example

```python
--8<-- "docs/examples/agreement/logistica-trasporto-confetra-viaggiante/example.py"
```
