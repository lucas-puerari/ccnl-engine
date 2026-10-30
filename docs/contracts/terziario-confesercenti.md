# CCNL Terziario Distribuzione e Servizi — Confesercenti

| | |
|---|---|
| **CNEL code** | `H012` |
| **Sector** | Terziario distribuzione e servizi |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-22 |
| **Workers (est.)** | ~230k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Confesercenti
    - Filcams-CGIL
    - Fisascat-CISL
    - UILTuCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, overtime, seniority, sickness, territorial_supplement, una_tantum |

14 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 83 verified / 3 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-22 |
| **Last review** | 2026-10-20 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the file read again in the signed texts, for the production tier: the Testo Unico of 12 December 2019, the renewal of 22 March 2024, its accordo integrativo of 28 March 2024 and the Protocollo of 12 December 2022. | corrected | 86 records verified against the Testo Unico of 12 December 2019 (text layer) and the Accordo integrativo of 28 March 2024 (CNEL 20279, scan read on the page image; quotes are the OCR-verbatim fragments).<br>Corrected 17 base_salary periods (Q 6, I 4, II 6, VI 1) by 1-5 cents: the file carried the ipotesi increases of 22 March 2024, the accordo integrativo of 28 March 2024 fixed their rounding and printed the official tables.<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, comporto in the calendar year, apprentices excluded (Artt. 186-187), not a flat 75%.<br>Added the terzo elemento nazionale of EUR 2.07, gated by the provincial element (Art. 215), the payment days of the tredicesima and quattordicesima (Artt. 220-221) and Fon.Te. (Art. 107, 1.55% and 0.55%, apprentices 1.05% by Art. 57).<br>Overtime premiums are on the normale retribuzione of Art. 206 (hourly_base_method gross_incl_allowances, was minimo_tabellare).<br>Apprenticeship: the second period closes at 36 months (II-V) and 24 months (VI), as Art. 53 pays the destination level at the end.<br>The una tantum of 2024-2025 is owed at every level, not only at level IV: limitation lump_sum_2024_2025 rescoped to July 2024 and July 2025.<br>The source documents had three ids and a tabella_retributiva kind for the same Testo Unico URL: unified. The 22 March 2024 ipotesi and the twin UGL texts (CNEL 20270, 19968) agree with the tables.<br>No renewal after the accordo integrativo of 28 March 2024 changes pay through October 2026 (CNEL H012 deposits through 20522 of 4 November 2024, training profiles only). |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented. |
| 2026-10-19 | claude-opus-5-5 (ai) | Hourly base of the time supplements and the supplements of ordinary night, holiday, Sunday, rest-day and shift work, read in the cited articles of the national text (text layer, or OCR of the scanned pages). AI review only: the same model extracted and checked the values. | confirmed | hourly_base_method gross_incl_allowances (was gross_incl_allowances), now verified: the engine reads it to derive the hourly rate of an event without one.<br>Supplement bands added: CONF_NOTTURNO, CONF_FESTIVO, CONF_DOMENICA, CONF_DOMENICA_AUTOSTRADE, CONF_RIPOSO.<br>Bands left out where the rate depends on facts the request does not carry or the text is unconfirmed; listed in the coverage note HOURLY RATE AND SUPPLEMENTS. |
| 2026-10-19 | claude-opus-5-5 (ai) | Leave accrual: the ferie twelfths and month rule, the hours of each permit bucket (ROL, ex festività or the pooled PAR), the new-hire ramps and the basis of the indemnity for the residual leave at termination, read on the text cited by each rule. An AI review: the extractor is also the verifier. | confirmed | The values stated are those of the quoted clauses; what the texts leave open (month fractions, termination divisors, schedules and shift patterns) is not modelled and is recorded in the coverage notes. |
| 2026-10-20 | claude-opus-5-5 (ai) | The pricing of the seniority increments matured before a change of level (Art. 205 - Scatti di anzianità). | corrected | Art. 205 - Scatti di anzianità (p. 153): the earlier increments are repriced at the new level when the next one matures: seniority_increments.on_promotion. |
| 2026-10-20 | claude-opus-5-5 (ai) | Whether the individual elements of the worker (superminimi, aumenti di merito, assegni ad personam) enter the hourly base of overtime and supplements (Art. 149 - Maggiorazione lavoro straordinario; Artt. 206 and 208). | corrected | Art. 149 - Maggiorazione lavoro straordinario; Artt. 206 and 208: individual elements hour only in the hourly base: work_rules.time_supplements.individual_elements. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Senior Manager (Quadro) | € 3,114.42 | 2027-02-01 |
| `I` | First Level | € 2,621.36 | 2027-02-01 |
| `II` | Second Level | € 2,335.04 | 2027-02-01 |
| `III` | Third Level | € 2,068.56 | 2027-02-01 |
| `IV` | Fourth Level | € 1,856.68 | 2027-02-01 |
| `V` | Fifth Level | € 1,725.77 | 2027-02-01 |
| `VI` | Sixth Level | € 1,600.53 | 2027-02-01 |
| `VII` | Seventh Level | € 1,447.98 | 2027-02-01 |

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

## Apprenticeship

**standard** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**sesto-livello** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "terziario-confesercenti/lump_sum_2024_2025 · una_tantum · impact yes · open"
    One-off lump sum of the renewal of 22/03/2024 (CNEL 20260, pp. 49-50): EUR 350 at level IV, reparametrised for every level, paid in two instalments with the July 2024 and July 2025 pay (per instalment Q 303.81, I 273.67, II 236.73, III 202.34, IV 175.00, V 158.11, VI 141.95, VII 121.53), to the workers in force on 22/03/2024, pro rata over 1/1/2022-31/3/2023, outside the TFR and every other institute. Not modelled.

    **Applies when:** `una_tantum` applies; level in I, II, III, IV, Q, V, VI, VII; from 2024-07-01; before 2025-08-01.

    **Remediation:** Pay the una tantum as a one-off earning with the July 2024 and July 2025 pay: per instalment Q 303.81, I 273.67, II 236.73, III 202.34, IV 175.00, V 158.11, VI 141.95, VII 121.53, pro rata over 1/1/2022-31/3/2023.

!!! warning "terziario-confesercenti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "terziario-confesercenti/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (Art. 187): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate and tops it up to the measure of the gross daily quota, as for the Commercio file. The events exempt from the carenza reduction (hospital stay, day hospital, dialysis, prognosis of 12 days or more, the illnesses of Art. 192, pregnancy) are not inputs: the carenza of such an event is paid at the reduced rate of its order.

    **Applies when:** `sickness` applies.

    **Remediation:** Model the net daily pay of Art. 187 and the exempt events of its second paragraph.

!!! warning "terziario-confesercenti/provincial_third_elements · territorial_supplement · impact yes · open"
    Art. 214: the provincial terzi elementi, amounts set by provincial agreements.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial terzi elementi as inputs.

!!! warning "terziario-confesercenti/cashier_allowance · base_salary · impact yes · open"
    Art. 218: the indennità di cassa e maneggio denaro of 5%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the cashier allowance with a role.

!!! warning "terziario-confesercenti/sales_operators · base_salary · impact yes · open"
    The minimi of the operatori di vendita I and II categoria (CNEL 20279 tables).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the operatori di vendita levels.

!!! warning "terziario-confesercenti/long_week_divisors · base_salary · impact yes · open"
    Art. 211: the hourly divisors 182 and 195 of the 42 and 45 hour weeks.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pick the divisor by the weekly hours.

!!! warning "terziario-confesercenti/sunday_overtime · overtime · impact unknown · open"
    Art. 149: the 30% on Sunday overtime. Overtime declared as OvertimeKind.REST_DAY takes OT_FESTIVO, 30% (working_time/overtime/policies.py, tests/integration/ccnl_engine/working_time/overtime/test_rest_day.py::test_rest_day_band[terziario_sunday_30]); Sunday overtime of a worker whose weekly rest falls on another day is weekday overtime, 15%, and whether Art. 149 pays it 30% is not confirmed (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read Art. 149 on Sunday overtime of a worker whose weekly rest is not Sunday; if it pays 30%, add a Sunday band, else resolve this limitation.

!!! warning "terziario-confesercenti/apprentice_sickness · sickness · impact yes · open"
    Art. 54: the apprentice sickness, 60% of the gross pay for the three days of carenza of six events a year and for hospital stays, while the file pays apprentices no integration.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the apprentice sickness of Art. 54.

!!! warning "terziario-confesercenti/long_apprenticeship_profiles · base_salary · impact yes · open"
    Art. 68 Tabella B: the 42 and 48 month apprenticeship profiles. The una tantum of the Protocollo 12/12/2022 (EUR 200 + 150 at level IV with the January and March 2023 pay) is historic.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 42 and 48 month tracks.

!!! warning "terziario-confesercenti/rol_schedule_absorption · leave · impact yes · open"
    LEAVE, WEEKLY SCHEDULE (Artt. 133-134): an employer on a 39-hour week absorbs 36 hours of ROL, on a 38-hour week 72 hours (16 of ex festività and 56 of ROL), and the grandi magazzini, supermercati, cash&carry and ipermercati on a 38-hour average absorb 72 hours of ROL. The engine accrues the hours of a 40-hour week (Art. 133 a).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the weekly schedule of Artt. 133-134 and absorb the hours it uses.

!!! warning "terziario-confesercenti/permit_deadline_payout · leave · impact yes · open"
    LEAVE, DEADLINE (Art. 158): the permits not taken within the year of accrual lapse and are paid with the retribuzione di fatto, or are carried and taken by 30 June of the following year; the text leaves the choice open. The engine carries the balances and pays the residual only at the end of the employment.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add an employer fact for the alternative of Art. 158 and pay the residual permits at its deadline.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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

### Without monetary impact

!!! note ""
    Grade I and the quadri are not apprenticeship destinations: Art. 62 admits the professionalizzante for levels II-VI only.

!!! note ""
    Track sesto-livello: Art. 53 (last paragraph) sets level VII for the first half of a level VI apprenticeship; the second half is one level below VI, again VII. Level VI from month 25.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Testo Unico 12 dicembre 2019 (sha256 18a2f10c...). Art. 53, 57, 64 (apprendistato), Art. 107 (Fon.Te), Artt. 186-187 (malattia), Art. 205 (scatti), Art. 210-211 (quote giornaliera e oraria), Art. 215 (terzo elemento), Artt. 220-221 (tredicesima e quattordicesima), Tabella I (p. 347) vigente dal 01.01.2020. | altro | 2019-12-12 | [↗](https://www.confesercenti.it/wp-content/uploads/2023/01/CCNL_contratto-collettivo-nazionale.pdf) |
| Ipotesi di accordo 22 marzo 2024 (CNEL 20260, scansione firmata), validità 2023-04-01/2027-03-31. Art. 213 aumenti in 6 tranche (01/04/2023, 01/04/2024, 01/03/2025, 01/11/2025, 01/11/2026, 01/02/2027). Una tantum EUR 350 at level IV, reparametrised for every level, paid 175+175 with the July 2024 and July 2025 pay: not modelled. | altro | 2024-03-22 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20260.pdf) |
| Accordo integrativo 28 marzo 2024 (CNEL 20279, scansione firmata): Art. 213 increases with the rounding fixed and the official tabelle retributive 2023-2027 (pp. 2-3), the source of every 2023-2027 base_salary period. | altro | 2024-03-28 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20279.pdf) |
| Protocollo straordinario 12 dicembre 2022 (CNEL 19967): acconto EUR 30 at level IV from 1 April 2023 (first 2023-2027 tranche) and una tantum EUR 350 at level IV (January and March 2023), not modelled. | altro | 2022-12-12 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2022//19967.pdf) |

??? note "Coverage notes"
    Apprenticeship type b (professionalizzante). Durations (Art. 64): II-V 36 months, VI 24 months; half-period 18 and 12 months. The 42 and 48 month profiles of Art. 68 Tabella B are in the unmodelled note.
    
    TERZO ELEMENTO NAZIONALE (Art. 215, TU p. 157): EUR 2.07 a month due only in the provinces where no provincial third element is in force (Art. 214); paid when EmployerProfile.provincial_pay_element is false, left out with a missing_fact blocker when it is not stated.
    
    HOURLY RATE AND SUPPLEMENTS (Testo Unico 12 December 2019, unchanged by the 2024 renewal, artt. 149-157, 206-211): without a caller value the engine derives the hourly base (the normale retribuzione of art. 206 over 168), the 15% on ordinary night hours from 22 to 6 (art. 151), the 30% on festività hours paid as straordinario festivo (art. 155 with art. 149), the 30% on ordinary Sunday hours (art. 153; 10% at the motorway fuel stations of art. 157, role impianto_carburante_autostradale: Employment.roles must be stated) and the 30% on the hours of the weekly rest day (art. 156). Art. 155 also pays the festività hours themselves: the engine posts the 30% only and the run is provisional. Second-level agreements may replace the Sunday and night rules (art. 153). Not derived: the divisors 182 and 195 of the 42- and 45-hour weeks; shift work, left to second-level bargaining.
    
    Base salary table effective from 01.01.2020 (Table I, CCNL 12.12.2019, confesercenti.it PDF).
    
    Salary tables 2023-2027: the official tabelle retributive of the Accordo integrativo 28/03/2024 (CNEL 20279, pp. 2-3), which perfected the Art. 213 increases of the ipotesi 22/03/2024 (CNEL 20260) 'con la sistemazione degli arrotondamenti' (Q, I, II and VI differ by 1-5 cents from the ipotesi). Tranches 01/04/2023 (the acconto of the Protocollo 12/12/2022, CNEL 19967), 01/04/2024, 01/03/2025, 01/11/2025, 01/11/2026, 01/02/2027. base_salary is the 'Totale mensile' column: paga base + contingenza/EDR + altri elementi (Q 260.76 indennità di funzione, VII 5.16).
    
    Seniority increment amounts from Art. 205 CCNL 2019, effective from 01.01.1990 (triennial, max 10).
    
    Hourly divisor 168 from Art. 211 CCNL 2019 (40h/week).
    
    14 monthly payments from Art. 220 (thirteenth) and Art. 221 (fourteenth) CCNL 2019.
    
    Apprenticeship from Art. 53 (under-classification) and Art. 64 (durations: II-V 36 months, VI 24 months) of the Testo Unico 2019, unchanged by the 2024 renewal: at the end of the apprenticeship the worker is paid at the destination level (Art. 53).
    

## Raw data

The contract file this page is generated from: [`agreement/terziario-confesercenti.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/terziario-confesercenti.json).

## Usage example

```python
--8<-- "docs/examples/agreement/terziario-confesercenti/example.py"
```
