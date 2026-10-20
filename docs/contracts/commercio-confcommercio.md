# CCNL Terziario, Distribuzione e Servizi (Confcommercio)

| | |
|---|---|
| **CNEL code** | `H011` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-22 |
| **Workers (est.)** | ~800k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Confcommercio
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
| **Limits of this contract** | bilateral_funds, leave, seniority, sickness |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 71 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-22 |
| **Last review** | 2026-10-19 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-10 | claude-opus-5-5 (ai) | Whole file. The values checked were not recorded; no value was marked verified. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (80 records) read again in the signed texts: the Testo Unico of 30 July 2019 and the renewal of 22 March 2024 with the accordo integrativo of 28 March 2024. | confirmed | 64 records match their source and are verified; no amount differs. Pages are PDF page indexes (the printed page of the 2019 text is one higher).<br>Wrong page citations corrected: Artt. 210-211 on p. 197, Art. 159 on p. 157, Artt. 186-187 on pp. 178-180.<br>The 16 contingenza and terzo elemento records match in amount, but no source states their valid_from 1993-11-01: they stay derived. No effect on periods from 2024-04-01.<br>The Fon.Te. rates are read in Art. 107 (and Art. 57 for apprentices) of the 2019 text instead of the fund's information sheet.<br>Not modelled: the two one-off payments of the 2024 renewal (level IV 175 EUR on 1 July 2024 and on 1 July 2025, 2024 text p. 50).<br>Pages 1-62 of the 2024 text are image-only and were read by OCR; the expiry clause of Art. 259 is illegible. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the 16 contingenza and terzo elemento records left derived on 2026-10-11, and the tranche tables of pp. 64-65 of the 2024 renewal. | corrected | The six tranche tables (1/4/2023 to 1/2/2027) print the paga base, 'Altri el.' and 'Contingenza + EDR' of the bundle for every level, with the same dates.<br>Contingenza + EDR and terzo elemento: the amounts were already right; their start moves from the unsourced 1993-11-01 to 2023-04-01, the first date a bundled source states them, and they are verified.<br>The renewal of 22 March 2024 (pp. 1-62 read by OCR) does not cite Art. 215. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | confirmed | CNEL H011 matches (Confcommercio with Filcams, Fisascat, Uiltucs); the report also lists UGL Terziario as a depositor, not a signatory of the renewal of 22 March 2024.<br>Term: 31/03/2027 from the report; the first tranche of the renewal is 1 April 2023. The first paragraph of Art. 259 is unreadable in the scan, so the dates rest on the report and the tranche table. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | flagged | Fon.Te. verified in P1. The EBT (0,10% + 0,05%), Quadrifor (50 + 25 euro a year for the quadri), Fondo Est and Qu.A.S. contributions are not modelled: declared. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the amounts of the declared contributions, read on the full text published by a party. | confirmed | Fondo Est 10 + 2 euro a month (Art. 104, p. 101) and Qu.A.S. 350 + 56 euro a year (Art. 105, p. 103) read: the declared limitation now states every amount. |
| 2026-10-15 | claude-opus-5-5 (ai) | Closure of the difference on the annual deductions of the observed termination payslip p25 (Terziario level 3, August 2026), shared with every CCNL of the terziario tax sector. | corrected | p25 prints 1.621,58 of annual deductions, other_deductions 1.042,62 and 242 days (gg_detrazioni). The art. 13 deduction proportioned to 242 days is 977.62 or 977.63 (1.474,52 x 242 / 365 = 977.6267), the ulteriore detrazione 578.96, and the payroll adds the 65 euro of art. 13 c. 1.1 whole: circolare 4/E/2022, par. 1.2.1, p. 7, 'deve essere corrisposto [...] per intero nel corso dell'anno [...] senza effettuare alcun ragguaglio al periodo di lavoro nell'anno'. The engine proportioned the 65 euro to the days: corrected in irpef.deduction.rules.work_income_deduction.<br>Divergence (engine_bug): Annual deductions of p25: 1.621,58 printed against 1.606,30 computed by the engine before the fix (243 days, 65 euro proportioned). Cause: The engine proportioned the 65 euro of art. 13 c. 1.1 TUIR to the days of work; circolare AdE 4/E/2022 grants it whole.<br>Divergence (accepted_external_variance): Art. 13 deduction of p25 for 242 days: 977.62 printed against 977.63 computed (1.474,52 x 242 / 365 = 977.6267). Cause: No source states how the proportioned deduction is rounded: the payroll of p25 truncates, the engine rounds half-up. One cent. Two payslips printed by other payroll packages, p26 (969.4658 printed 969.47) and p27 (74.9863 printed 74.99), round half-up as the engine does: the rounding varies by package. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,313.29 | 2027-02-01 |
| `1` | 1st level | € 2,083.84 | 2027-02-01 |
| `2` | 2nd level | € 1,802.50 | 2027-02-01 |
| `3` | 3rd level | € 1,540.66 | 2027-02-01 |
| `4` | 4th level | € 1,332.46 | 2027-02-01 |
| `5` | 5th level | € 1,203.83 | 2027-02-01 |
| `6` | 6th level | € 1,080.77 | 2027-02-01 |
| `7` | 7th level | € 925.31 | 2027-02-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `1` | € 24.84 |
| `2` | € 22.83 |
| `3` | € 21.95 |
| `4` | € 20.66 |
| `5` | € 20.30 |
| `6` | € 19.73 |
| `7` | € 19.47 |

## Apprenticeship

**livelli_2_5** (type: `under_classification`)  
Destination levels: `2`, `3`, `4`, `5`

**livello_6** (type: `under_classification`)  
Destination levels: `6`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "commercio-confcommercio/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "commercio-confcommercio/sickness_net_basis · sickness · impact unknown · open"
    SICKNESS (Art. 187): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate (the 'lordizzazione' of payroll practice, Ordine dei Consulenti del Lavoro di Salerno) and tops it up to the measure of the gross daily quota; IRPEF is left out, as it falls on both. Day bands, carenza by event, the yearly comporto and the exclusion of apprentices are modelled.

    **Applies when:** `sickness` applies.

    **Remediation:** Find a source (an interpretation of the parties, an INPS or Ministry text) that defines the net daily pay of Art. 187, align the computation, then resolve this limitation.

!!! warning "commercio-confcommercio/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH AND BILATERAL FUNDS (testo unico 2019): Fondo Est (Art. 104, p. 101), for the permanent workers other than the quadri, 10 euro a month from the employer and 2 euro from the worker, or an elemento distinto of 16 euro for 14 months when the employer does not enrol them; Qu.A.S. (Art. 105, p. 103), for the quadri, 350 euro a year from the employer and 56 euro from the worker from June 2011, plus an enrolment fee; Quadrifor (p. 108), 50 euro a year from the employer and 25 from the quadro; Ente Bilaterale Territoriale (p. 48), 0,10% from the employer and 0,05% from the worker on paga base and contingenza. Not modelled: the worker's shares lower the net pay.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the contributions as bilateral fund events, or model them per worker.

!!! warning "commercio-confcommercio/rol_schedule_absorption · leave · impact yes · open"
    LEAVE, WEEKLY SCHEDULE (Artt. 133-134): an employer on a 39-hour week absorbs 36 hours of ROL, on a 38-hour week 72 hours (16 of ex festività and 56 of ROL), and the grandi magazzini, supermercati, cash&carry and ipermercati on a 38-hour average absorb 72 hours of ROL. The engine accrues the hours of a 40-hour week (Art. 133 a).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the weekly schedule of Artt. 133-134 and absorb the hours it uses.

!!! warning "commercio-confcommercio/permit_deadline_payout · leave · impact yes · open"
    LEAVE, DEADLINE (Art. 158): the permits not taken within the year of accrual lapse and are paid with the retribuzione di fatto, or are carried and taken by 30 June of the following year; the text leaves the choice open. The engine carries the balances and pays the residual only at the end of the employment.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the alternative of Art. 158 and pay the residual permits at its deadline.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
| CCNL Terziario Distribuzione e Servizi, Ipotesi di accordo 22 marzo 2024 e Accordo integrativo 28 marzo 2024 (scansione firmata) | associazione | 2024-03-28 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/Ccnl_Tds_Confcommercio_2023-2027_e_accordo_integrativo.pdf) |
| CCNL per i dipendenti da aziende del Terziario della Distribuzione e dei Servizi, Testo Unico 30 luglio 2019 | associazione | 2019-07-30 | [↗](https://uiltucs.it/wp-content/uploads/2022/02/testo-unico-CCNL-TDS-Confcommercio-2019.pdf) |

??? note "Coverage notes"
    'contingenza_edr' is the tables' 'Contingenza + EDR' column (contingenza frozen since November 1993 per L. 438/1992 plus EDR 10,33); 'terzo_elemento_nazionale' is the 2,07 EUR element of Art. 215.
    
    Indennità di funzione Quadri 260,76 EUR (Art. 129, 14 mensilità; the literal sum of the increments is 260,77, the tables carry 260,76); VII livello 'altri elementi' 5,16 EUR.
    
    INPS: see tax/data/2026-terziario.json notes.
    
    CNEL code H011 confirmed by Il Sole 24 Ore / INPS UNIEMENS reference.
    
    TERZO ELEMENTO NAZIONALE (Art. 215): 2.07 EUR a month due only in the provinces where no provincial third element is in force; paid when EmployerProfile.provincial_pay_element is false, left out with a missing_fact blocker when it is not stated.
    
    Salary tables: five tranches of the rinnovo 22/03/2024 (paga base dal 1/4/2024, 1/3/2025, 1/11/2025, 1/11/2026, 1/2/2027) taken from the official tabelle retributive as perfected by the Accordo integrativo 28/03/2024 (rounding fixes on Q, I, II, VI vs the 22/03 ipotesi), read in the signed text published by Uiltucs (pp. 63-65 of the 2024 PDF).
    
    Seniority (Art. 205): ten triennial scatti; amounts Q 25,46, I 24,84, II 22,83, III 21,95, IV 20,66, V 20,30, VI 19,73, VII 19,47 (dal 1/1/1990, unchanged by the 2024 renewal).
    
    Apprenticeship (Art. 53 TU 2019, unchanged in 2024): sottoinquadramento, two levels below the destination for the first half and one level below for the second half; eligible destinations II-VI (Art. 62); durations II-V 36 months, VI 24 months (Art. 64). Track 'livelli_2_5' (18+18 months), track 'livello_6' (VII for the first 12 months; the second half stays at VII by the general one-level-below rule, lexplain.it reads it as VI: adopted the literal text). Art. 68 Tabella B profiles with 42/48-month durations and the farmacista di parafarmacia derogation (Accordo 31/10/2024) are profile-specific and not modelled.
    

## Raw data

The contract file this page is generated from: [`agreement/commercio-confcommercio.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/commercio-confcommercio.json).

## Usage example

```python
--8<-- "docs/examples/agreement/commercio-confcommercio/example.py"
```
