# CCNL Logistica, Trasporto Merci e Spedizione (Confetra)

| | |
|---|---|
| **CNEL code** | `I100` |
| **Sector** | logistica |
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
| **Limits of this contract** | bilateral_funds, inps_employer, overtime, seniority |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 62 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-12-06 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2027-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (55 records) read again in the signed testo unico of the renewal of 6 December 2024 (Verbale di accordo 25 September 2025), published by Confetra; the URLs the file cited return 404. | corrected | Corrected: every one of the 36 salary periods. The base salary is the minimo plus the EPA of the tables of pp. 80-81 for non-travelling staff; the file held values about 88-110 EUR too high. The printed Totale of the 1 January 2027 table already includes the minimo increase of 1 June 2027; the Legacoop circular of 19 December 2024 (p. 2) confirms that January 2027 is an EPA-only step, so the period holds minimo plus EPA.<br>Corrected: the Quadri receive the indennità di funzione of 51.65 EUR a month (Art. 6 c. 4, p. 17), which the file lacked.<br>Corrected: the daily quota is 1/22 (Art. 61 c. 3, Sezione prima, p. 86), not 1/26, which applies to a six-day week of non-travelling staff and to Sezione seconda (Art. 73 c. 5).<br>Verified: 14 monthly payments (Artt. 18-19), the accrual of fractions over 15 days (Art. 18 c. 2, Art. 19 c. 2), seniority (Art. 17) and 22 days of leave (Art. 24). Pages are PDF page numbers, equal to the printed ones.<br>Assumed: sickness. Art. 63 A) c. 7-12 keeps the job 245 or 365 days and pays 3 months in full and 5 at half (up to 5 years of service) or 5 and 7, counted over 24 or 30 months; the cumulation model holds one window in whole years for every band, so the rule is not expressible and the file's 100% for 180 days is wrong.<br>Left derived: the overtime rates (30%, 50%, 65%, 75%, Art. 13 c. 6) match, but their start of 2023-05-01 is not stated; the level descriptions are paraphrases.<br>Not modelled: the EDR of Art. 60 c. 8 (10 EUR at level 3S, re-parametrised) for workers in service on 26 January 2011, which affects every entitlement, and level 6J and travelling staff. |
| 2026-10-12 | claude-opus-5-5 (ai) | Sickness rule of art. 63 A), now expressible with a window and steps per seniority band; readiness of the file. | corrected | The sickness rule was assumed (100% for 180 days, not the CCNL's): it is now 90 days in full and 150 at half within 24 months, comporto 245 days, up to 5 years of seniority; 150 in full and 210 at half within 30 months, comporto 365 days, above.<br>With no assumed or missing payable rule left and the salary tables, additional months, divisor and seniority verified on 2026-10-11, the file is promoted to reviewed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Malattie particolarmente gravi (art. 63 cc. 8 and 12). | corrected | The serious illnesses of INPS circ. 95/2016 were a limitation (grave_illness): now paid in full for 18 months and left out of the comporto when SicknessEpisode.serious_illness says so. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the salary tables of pp. 80-81 for every tranche, the overtime rates of Art. 13 c. 6 and the remaining derived records. | corrected | The minimo plus EPA of every level at 1.1.2025, 1.1.2026, 1.1.2027 and 1.6.2027 match the bundle.<br>Overtime 30/50/65/75%: verified from 1 January 2025 (the start of the salary series); the unsourced start of 2023-05-01 is dropped.<br>The 50% of the sixth day of a five-day week is not modelled: declared.<br>The EDR of 2011 (re-parametrisation by level not stated) and of 2021 (TFR treatment contradictory, pp. 54 and 83) stay derived. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL I100 matches; the report lists the same associations and FILT, FIT, UILTRASPORTI.<br>Term: 'Il presente contratto scadrà il 31 dicembre 2027' (testo unico), the same in the report. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi': the scatti and fixed allowances of the file against the text read in the P1 review. | confirmed | EDR ex accordo 18 maggio 2021 (p. 82, personale non viaggiante): the nine amounts match (Quadri 12,80 to 6° 8,26); 13 mensilità, no effect on other institutes (p. 83). Verified.<br>EDR of Art. 60 c. 8 (p. 85, 10 euro at 3° Super, staff in service on 26 January 2011): the eight amounts match (Quadro 12,89 to 6° 8,26) and the file gates it with in_service_on 2011-01-26. Verified. The 5-euro table of p. 93 belongs to another article and is not modelled here.<br>Scatti (Art. 17) were verified in the P1 review; IND_FUN verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | corrected | Tabella A (p. 75) matches the standard track. Tabella B, 90, 95 and 100% for the profili artigiani, was not modelled: added as a track; an apprentice now names it.<br>Part-time supplementary hours at 18% (40% past the annual limit, Art. 56, p. 71): declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | corrected | Priamo (Art. 50, pp. 63-64): 1% of the employer and 1% of the worker; no pension fund was modelled: added as an employer fund on the TFR base, derived because the text names the monthly pay.<br>Sanilog (150 euro a year, employer) and Ebilog (3,50 euro a month employer, 0,50 worker, or an EAR of 8 euro): declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour (DD 135 of 19 December 2025, impiegati non viaggianti, January 2026). | flagged | Impiegato 3S with 3 scatti, January 2026: minimo plus EPA 2000.37 ((23.644,44 + 360) / 12), scatti 74.37 and EDR 10.00 a month match the table (p. 9); the TFR of the month is the table's TFR base over 13.5 less the 0.5% IVS offset. Match.<br>Deviation: the table applies an employer INPS rate of 29.44%; the engine applies 29.06% from 16 to 50 employees and 29.36% from 51. Cause not established (the table does not state the class of employer and size); decision: flagged for the INPS review of the logistica contribution class. Sanilog (165 euro) and Ebilog (46,20 euro) of the table equal the declared 150 and 42 euro plus the 10% solidarity contribution. INAIL 0.404%: not computed by the engine. No independent net pay example. |
| 2026-10-15 | claude-opus-5-5 (ai) | Closure of the divergence left open by the review 2026-10-15-ai-cost-check: the employer INPS rate against the cost table of the Ministry of Labour (DD 135/2025). | flagged | The table prints 'Inps (29,44%)' on every row, operai and impiegati non viaggianti alike (30,68% for the personale viaggiante), with no composition and no class of employer. The 0.08 points above the 29.36% of the engine fit more than one composition (the whole 0.90% CIGS and a 0.24% maternità, for one), and a single rate for operai and impiegati does not fit the industria class of the file, where the operai pay the 2.22% malattia. The class is not established.<br>Divergence (source_context_missing): Employer INPS rate of an impiegato non viaggiante, January 2026: 29.44% in DD 135/2025 against 29.06% (16-50 employees) or 29.36% (51 and more) in the engine. Cause: The table does not state the INPS class of the employer nor the composition of its rate; the class of the file (industria) is not confirmed. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — quadro with high directional and managerial expertise | € 2,681.12 | 2027-06-01 |
| `1` | Level 1 — management role / area manager | € 2,496.84 | 2027-06-01 |
| `2` | Level 2 — operational unit manager / junior management role | € 2,302.61 | 2027-06-01 |
| `3S` | Level 3 Super — reference technical/operational expert or process manager | € 2,070.37 | 2027-06-01 |
| `3` | Level 3 — highly specialised operator / department coordinator | € 2,016.54 | 2027-06-01 |
| `4` | Level 4 — specialist operator (CED operator) | € 1,912.80 | 2027-06-01 |
| `4J` | Level 4 Junior — recently graded senior operator | € 1,865.27 | 2027-06-01 |
| `5` | Level 5 — qualified operator (specialist warehouse worker) | € 1,817.10 | 2027-06-01 |
| `6` | Level 6 — worker assigned to generic operational support tasks | € 1,703.67 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.99 |
| `1` | € 29.44 |
| `2` | € 26.86 |
| `3S` | € 24.79 |
| `3` | € 24.27 |
| `4` | € 23.24 |
| `4J` | € 22.34 |
| `5` | € 22.21 |
| `6` | € 20.66 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4J`, `5`, `6`  
percentage: 1.00

**profili_artigiani** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4J`, `5`, `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "logistica-trasporto-confetra/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "logistica-trasporto-confetra/sixth_day_overtime · overtime · impact yes · open"
    SIXTH DAY: Art. 13 c. 6 (p. 39) pays 50% for the overtime of the sixth day of a non-travelling worker whose normal week is spread over five days; the overtime bands have no such kind, so that overtime takes the 30% of the weekday band.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a sixth-day kind to the overtime event and a 50% band, then remove this note.

!!! warning "logistica-trasporto-confetra/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: supplementary hours are paid with 18% of the hourly quota of the retribuzione globale, 40% past the annual limit (Art. 56, testo unico p. 71). The request has no kind for supplementary hours: an overtime event of a part-time worker takes the overtime bands unless the caller passes the multiplier.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a supplementary-hours kind to the overtime event and a supplementare band with the CCNL rate.

!!! warning "logistica-trasporto-confetra/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH AND BILATERAL FUNDS: Sanilog (Art. 51, p. 64): 150 euro a year for each worker not in probation with a permanent contract or an apprenticeship, from the employer only, plus the 10% INPS solidarity contribution; Ebilog (Art. 52, p. 65): 3,50 euro a month from the employer and 0,50 euro from the worker, for 12 months, or an EAR of 8 euro a month paid to the worker by an employer outside the bilateral system. Not modelled.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the contributions as bilateral fund events, or model them per worker.

!!! warning "logistica-trasporto-confetra/inps_employer_class_unconfirmed · inps_employer · impact unknown · open"
    INPS CONTRIBUTION CLASS: the file applies the rates of the industria (impiegati 29.06% from 16 to 50 employees and 29.36% from 51, operai 31.28% and 31.58% with the 2.22% malattia). The cost table of the Ministry of Labour for this CCNL (DD 135 of 19 December 2025) applies 29.44% to operai and impiegati alike, and states neither the INPS class of the employer nor the composition of the rate: the class of a logistica employer is not confirmed, and the employer and worker contributions may differ.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Read the INPS classification (codice statistico contributivo) of the logistica, trasporto merci e spedizione employers and the composition of the 29.44% of DD 135/2025, then set the class of the file and remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-06 | [↗](https://www.confetra.com/wp-content/uploads/Nuovo-Testo-Unico-del-CCNL-logistica-trasporto-e-spedizione_pulito.pdf) |

??? note "Coverage notes"
    STAFF: tables for non-travelling staff (clerical employees and sedentary workers). The travelling staff (personale viaggiante, drivers and riders: letters C3 to L of pp. 25-26, tables pp. 81-82) is modelled in logistica-trasporto-confetra-viaggiante.
    
    CONGLOBATED MINIMUMS: base_salary values are the conglobated monthly minimum pay (minimum pay table + contingenza per Art. 61 note + EPA). Primary check: Art. 61 of the consolidated text September 2025 — 'From 1.1.2001 the indennità di contingenza has been conglobated into the minimum pay tables together with the EDR of EUR 10.33 per month'. fixed_allowances is empty for all levels.
    
    HOURLY DIVISOR: 168 hours/month. Primary source: Art. 61 para. 3 consolidated text September 2025 — 'The hourly pay is obtained by dividing the monthly pay by 168'.
    
    TRANCHES: four tranches for level 3S: 1.1.2025 +120 (minimo 90 + EPA 30), 1.1.2026 +40 (minimo), 1.1.2027 +30 (EPA), 1.6.2027 +40 (minimo 10 + EPA 30). Source: the tables of pp. 80-81 of the testo unico of 25 September 2025 and the Legacoop circular of 19 December 2024 (p. 2).
    
    ICE: the Indennità di Copertura Economica (ICE) was a provisional element in force until 31.12.2024. It ceases from 1.1.2025 with the renewal taking effect. base_salary values do not include ICE (ceased element). The consolidated text cites net increases of EUR 230 at 3S compared to the previous pay including ICE — the difference from the algebraic sum of the tranches (EUR 290 from base without ICE) corresponds to the pre-existing ICE value for that level.
    
    ADDITIONAL MONTHS: 14 (tredicesima Art. 18 + quattordicesima Art. 19 consolidated text September 2025).
    
    SENIORITY INCREMENTS: biennial (24-month cadence), max 5 biennial periods. Amounts from Art. 17 consolidated text September 2025. Non-travelling staff.
    
    LEVEL 6° JUNIOR: not modelled. The profile existed only in 2025 (1,464.53 a month from 1.1.2025, p. 80; seniority step 18.78, art. 17; EDR 2021 7.58, p. 82) and ended on 31.12.2025 (p. 25: 'Il presente profilo avrà termine inderogabilmente il 31 dicembre 2025'), its workers moving to level 6; a level of the bundle must cover the whole span of the ruleset. A 2025 run of a 6J worker uses level 6 with the 2025 amounts above as overrides.
    
    EPA: Elemento Professionale d'Area, a component introduced by the 6.12.2024 renewal. Included in base_salary values from 1.1.2025. Not shown separately because it forms an integral part of the minimum pay (it affects all contractual and statutory entitlements) — see Confetra circ283-2024.
    
    EDR: the EDR of EUR 10.33/month (agreement 26 Jan 2001) is conglobated into the minimum pay tables (Art. 61 note). The EDR of art. 60 c. 8 (workers in service on 26 January 2011) and the EDR of the agreement of 18 May 2021 (13 mensilità, no effect on other institutes) are paid as allowances; the 2021 EDR may still enter the daily base of absences and sickness, which 'nessuna incidenza su alcun istituto contrattuale' excludes.
    
    INPS: uses 2026-industria.json (TaxSector.INDUSTRIA). File already present — no changes to the tax file.
    
    APPRENTICESHIP: percentage type from TABELLA A consolidated text September 2025. 75% year 1 (m1-12), 85% year 2 (m13-24), 100% from m25. Eligible levels: 1, 2, 3, 3S, 4, 4J, 5, 6 (level Q excluded). Maximum duration 36 months. Source: Art. 106 + TABELLA A consolidated text 09/2025 (contrattotrasporti.it).
    
    APPRENTICESHIP TABELLA B (testo unico p. 75): the profili artigiani and equivalent profiles (addetti al magazzinaggio, alla manutenzione veicoli, alla movimentazione) are paid 90% in the first year, 95% in the second and 100% after, not the 75 and 85% of Tabella A. The profile, not the level, selects the table: track 'profili_artigiani' beside 'standard'; set Apprentice.track.
    

## Raw data

The contract file this page is generated from: [`agreement/logistica-trasporto-confetra.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/logistica-trasporto-confetra.json).

## Usage example

```python
--8<-- "docs/examples/agreement/logistica-trasporto-confetra/example.py"
```
