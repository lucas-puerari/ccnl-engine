# CCNL Terziario Distribuzione e Servizi — Confesercenti

| | |
|---|---|
| **CNEL code** | `H012` |
| **Sector** | Terziario distribuzione e servizi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-22 |
| **Workers (est.)** | ~230k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

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
| **Limits of this contract** | base_salary, bilateral_funds, seniority, sickness, una_tantum |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 75 verified / 0 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-22 |
| **Last review** | 2026-10-13 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the file read again in the signed texts, for the production tier: the Testo Unico of 12 December 2019, the renewal of 22 March 2024, its accordo integrativo of 28 March 2024 and the Protocollo of 12 December 2022. | corrected | 86 records verified against the Testo Unico of 12 December 2019 (text layer) and the Accordo integrativo of 28 March 2024 (CNEL 20279, scan read on the page image; quotes are the OCR-verbatim fragments).<br>Corrected 17 base_salary periods (Q 6, I 4, II 6, VI 1) by 1-5 cents: the file carried the ipotesi increases of 22 March 2024, the accordo integrativo of 28 March 2024 fixed their rounding and printed the official tables.<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, comporto in the calendar year, apprentices excluded (Artt. 186-187), not a flat 75%.<br>Added the terzo elemento nazionale of EUR 2.07, gated by the provincial element (Art. 215), the payment days of the tredicesima and quattordicesima (Artt. 220-221) and Fon.Te. (Art. 107, 1.55% and 0.55%, apprentices 1.05% by Art. 57).<br>Overtime premiums are on the normale retribuzione of Art. 206 (hourly_base_method gross_incl_allowances, was minimo_tabellare).<br>Apprenticeship: the second period closes at 36 months (II-V) and 24 months (VI), as Art. 53 pays the destination level at the end.<br>The una tantum of 2024-2025 is owed at every level, not only at level IV: limitation lump_sum_2024_2025 rescoped to July 2024 and July 2025.<br>The source documents had three ids and a tabella_retributiva kind for the same Testo Unico URL: unified. The 22 March 2024 ipotesi and the twin UGL texts (CNEL 20270, 19968) agree with the tables.<br>No renewal after the accordo integrativo of 28 March 2024 changes pay through October 2026 (CNEL H012 deposits through 20522 of 4 November 2024, training profiles only). |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations. | corrected | sickness_net_basis is recorded on every run with a sickness event (trigger run), not only documented. |

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

!!! warning "terziario-confesercenti/terziario_confesercenti_unmodelled · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the provincial terzi elementi of Art. 214 (amounts set by provincial agreements); the indennità di cassa e maneggio denaro of 5% (Art. 218); the minimi of the operatori di vendita I and II categoria (CNEL 20279 tables); the hourly divisors 182 and 195 of the 42 and 45 hour weeks (Art. 211); the 30% on Sunday overtime (Art. 149: OT_FESTIVO covers public holidays only); the apprentice sickness of Art. 54 (60% of the gross pay for the three days of carenza of six events a year and for hospital stays, while the file pays apprentices no integration); the 42 and 48 month apprenticeship profiles of Art. 68 Tabella B; the una tantum of the Protocollo 12/12/2022 (EUR 200 + 150 at level IV with the January and March 2023 pay, historic).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the fund omission EDRs, the cashier allowance, the operatori di vendita minimi, Sunday overtime and the apprentice sickness of Art. 54.

!!! warning "terziario-confesercenti/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH FUNDS: the Fondo ASTER (Art. 104 as renewed in 2024) and, for the quadri, the Cassa QuAS (Art. 106) are owed for every worker; an employer that does not pay them owes the worker instead an EDR of EUR 16.00 x 14 and EUR 37.00 x 14. Neither is modelled: the employer cost, and with the EDR the net pay, are short of them.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Model the contributions per worker, with a fact for an employer that pays the worker the alternative element instead, then remove this note.

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

### Without monetary impact

!!! note ""
    Grade I and the quadri are not apprenticeship destinations: Art. 62 admits the professionalizzante for levels II-VI only.

!!! note ""
    Track sesto-livello: Art. 53 (last paragraph) sets level VII for the first half of a level VI apprenticeship; the second half is one level below VI, again VII. Level VI from month 25.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2019-12-12 | [↗](https://www.confesercenti.it/wp-content/uploads/2023/01/CCNL_contratto-collettivo-nazionale.pdf) |
| — | — | 2024-03-22 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20260.pdf) |
| — | — | 2024-03-28 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20279.pdf) |
| — | — | 2022-12-12 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2022//19967.pdf) |

??? note "Coverage notes"
    Apprenticeship type b (professionalizzante). Durations (Art. 64): II-V 36 months, VI 24 months; half-period 18 and 12 months. The 42 and 48 month profiles of Art. 68 Tabella B are in the unmodelled note.
    
    TERZO ELEMENTO NAZIONALE (Art. 215, TU p. 157): EUR 2.07 a month due only in the provinces where no provincial third element is in force (Art. 214); paid when EmployerProfile.provincial_pay_element is false, left out with a missing_fact blocker when it is not stated.
    
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
