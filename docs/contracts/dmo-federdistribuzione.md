# Distribuzione Moderna Organizzata — Federdistribuzione

| | |
|---|---|
| **CNEL code** | `H008` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~460k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

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
| **Limits of this contract** | base_salary, seniority, sickness, territorial_supplement |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 77 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-13 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the Testo Unico of 29 September 2025 (Federdistribuzione, 99 pages), for the production tier. | corrected | 90 records verified; the work rules cited an aggregator and now cite the Testo Unico. The 2025/01 URL of the sources returns 404: replaced by the 2026/04 one.<br>Night overtime 50%, not 30% (Art. 132 c. 3); added the 20% beyond the 48th weekly hour (c. 1); the premiums are on the normale retribuzione of Art. 189 (hourly_base_method gross_incl_allowances).<br>Sickness: 75% for days 4-20 and 100% from day 21 of the net daily pay, carenza by event, apprentices excluded (Art. 170), not a flat 100%.<br>Seniority amounts in force since 1990 (Art. 188): the gap before 23 April 2024 removed.<br>Terzo elemento 2.07 due only without a provincial element (Art. 199): now gated.<br>Apprenticeship: second half of level VI at VII (Art. 46 c. 3); the 36-month end of levels II-V stated.<br>Added the payment days of the tredicesima and quattordicesima and Fon.Te. (Art. 95, 1.55% and 0.55%, apprentices 1.05%).<br>Night holiday overtime 0.50 stays derived: no clause sets it, Art. 132 c. 5 forbids cumulation.<br>No renewal after the Testo Unico through October 2026. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
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

## Apprenticeship

**standard_II_V** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`

**standard_VI** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dmo-federdistribuzione/provincial_elements_missing · territorial_supplement · impact yes · open"
    Terzo elemento nazionale (Art. 199, PDF p. 59): EUR 2.07 a month only for the workers of firms in provinces with no provincial terzo elemento in force (Art. 198, frozen since 1973): gated by EmployerProfile.provincial_pay_element. The provincial amounts themselves are set by provincial agreements outside the Testo Unico and are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the provincial terzi elementi of Art. 198 as a territorial supplement.

!!! warning "dmo-federdistribuzione/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "dmo-federdistribuzione/sickness_net_basis · sickness · impact yes · open"
    SICKNESS (Art. 170): the CCNL integrates up to a share of the net daily pay ('retribuzione giornaliera netta') without saying how the net pay is computed. The engine grosses up the INPS indemnity by the worker's INPS rate and tops it up to the measure of the gross daily quota, as for the Commercio file. The exempt events of c. 3 (hospital stay, prognosis of 12 days or more, the illnesses of Art. 175 c. 3, pregnancy) are not inputs: the carenza of such an event is paid at the reduced rate of its order.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the net daily pay of Art. 170 and the exempt events of c. 3.

!!! warning "dmo-federdistribuzione/dmo_unmodelled_elements · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the EDR of 0.30% of paga base and contingenza (14 months) owed when the employer does not pay E.Bi.Di.M. (Art. 18), the EUR 16.00 x 14 owed without Fondo EST (Art. 19) and the EUR 37.00 x 14 owed to quadri without Cassa QuAS (Art. 20); the worker shares of these funds; the indennità di cassa of 5% (Art. 202); the premiums on ordinary night (15%, Art. 134), Sunday (30%, Art. 136) and weekly rest day (30%, Art. 139) work; the pay rows of the operatori di vendita; the sostegno all'occupazione contract of Art. 70; the guarantee of the commission-paid staff (Art. 201). The una tantum of Art. 197 (July 2024 and 2025) is historic and outside the TFR base (c. 6).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the fund omission EDRs, the cashier allowance and the premiums on ordinary hours.

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
| — | — | 2025-09-29 | [↗](https://www.federdistribuzione.it/app/uploads/2026/04/Testo-Unico-CCNL-DMO.pdf) |

??? note "Coverage notes"
    Salary tables: 6 tranches from 01/04/2023 through 01/02/2027, Allegato 11 (PDF p. 98) of the Testo Unico CCNL DMO of 29/09/2025 (Federdistribuzione), Art. 196 for the tranche dates. Level IV on 01/04/2023 is printed 1112,46 in the PDF itself: the total 1646,68 less the contingenza 524,22, and 1192,46 less the 70,00 of Art. 196, give 1122.46, the value kept.
    
    Split model confirmed: total / 168 at L1 = 14.905, L4 = 10.605, L7 = 8.309 — all non-integer. Source: Art. 194 (divisore 168 for 40h/week), Allegato 11.
    
    Contingenza: frozen values from Allegato 11 column. EDR (lire 20,000 = 10.33 EUR) conglobated into contingenza on 01/01/1995 per Art. 190 — no separate EDR allowance modelled.
    
    Indennità di funzione Quadri (Art. 113): EUR 260.76/month for 14 months (cumulative increments: 51.65+77.47+51.65+70.00+10.00=260.77; 0.01 rounding from lire). Allegato 11 shows 260.76.
    
    Altri elementi of level VII: EUR 5.16/month (lire 10,000), column 'altri elementi' of Allegato 11 (PDF p. 98); the Testo Unico names no article for it.
    
    Seniority: 10 scatti triennali (Art. 188), amounts of the Art. 188 table, in force since 1 January 1990; paid from the month after the triennium (c. 4).
    
    Additional months: 14 (tredicesima Art. 204 + quattordicesima Art. 205).
    
    APPRENTICESHIP: under-classification of Art. 46 and durations of Art. 57 (Testo Unico 29/09/2025, PDF pp. 24-25). Destinations II-VI (Art. 55: I and Q excluded). Levels II-V: 36 months, two levels below in the first half, one below in the second. Level VI: 24 months at level VII, the first half by Art. 46 c. 5 and the second by c. 3 (one level below), as the Commercio file. The 42 and 48 month profiles of Art. 61 are not modelled.
    

## Raw data

The contract file this page is generated from: [`agreement/dmo-federdistribuzione.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dmo-federdistribuzione.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dmo-federdistribuzione/example.py"
```
