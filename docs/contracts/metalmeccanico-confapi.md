# CCNL Metalmeccanici Piccola Industria (Unionmeccanica-Confapi)

| | |
|---|---|
| **CNEL code** | `C018` |
| **Sector** | metalmeccanico |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionmeccanica-Confapi
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
| **Limits of this contract** | base_salary, bilateral_funds, pension_fund_contribution |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 58 verified / 7 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read in the signed texts: the CCNL of 3 July 2017, the verbali on the minimi of 11 June 2024, 19 June 2025 and 17 June 2026, the accordo of 24 July 2025 and the renewal of 4 June 2026, for the production tier. | corrected | 70 records verified, 8 derived; the salary tables and the work rules cited aggregator pages and now cite the signatories' texts. The scans have no text layer: their quotes are OCR.<br>September 2025 minimi: the file re-parametrised the tranche; the signed accordo of 24 July 2025 prints 1603.45, 1770.79, 1964.74, 2195.87, 2354.36, 3054.74 for levels 1, 2, 3, 5, 6, 9 (one to five cents above).<br>Added the June 2027 and June 2028 tranches of the renewal of 4 June 2026 (ratified 23 July 2026); June 2026 closed at 2027-06-01.<br>Left derived: level 1 June 2024 and levels 1, 2, 4, 5, 9 June 2025, where the verbale that set the tranche and the later restated tables differ by one to five cents; the daily divisor 1/26 (no clause on absences); the leave tiers, whose 'oltre 10 anni' and 'oltre i 18 anni' are read as 120 and 216 completed months.<br>Overtime per Art. 29 column 'non a turni': 20% day, 50% night, 55% holiday and rest day, 75% night holiday (were 15/40/50/60); the base is the retribuzione globale di fatto (gross_incl_allowances).<br>Leave per Art. 33: 20 days, 21 over 10 years, 25 over 18 years (was 22 flat); left derived for the reading of the seniority thresholds.<br>Sickness per Art. 55: full pay for 2/3/4 months and half for 4/6/8 more over a 3-year window, comporto 6/9/12 months, net basis (was 60%/75%/180 days).<br>Fondapi 2.0%/1.2% from 2021-06-01 (Art. 50), not 2026-01-01; hourly divisor 173 from 2021-06-01 (Art. 40).<br>Apprenticeship: the 30- and 24-month tracks of Art. 10 added (limitation apprenticeship_36_months_assumed closed); no seniority during the apprenticeship (Art. 10 p. 49, limitation apprentice_seniority closed).<br>Not modelled pay clauses gathered in the limitation confapi_unmodelled_pay_elements; fondapi_base_elements narrowed to the indennità di funzione of the quadri. |
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi of 2025 and 2026 against the accordo of 24 July 2025 and the verbale of 17 June 2026, the derived minimi of 2024 and 2025, and a year and a termination of a 5th level impiegato against a hand oracle. | confirmed | 5th level (scans read by OCR): 2.195,87 from 1 September 2025 and 2.245,87 from 1 June 2026 in both documents. Match.<br>The 6 derived minimi of June 2024 and June 2025 stay derived: for each the verbale that set the tranche and the later accordo and renewal print amounts one to five cents apart (for example 1.752,96 against 1.752,97 at the 2nd level); the file keeps the verbale in force for the months it covers and records both. The derived absence and leave rules state their transformation of a cited text. No primary states any of them directly.<br>Hand oracle (tests/knowledge/ccnl_engine/period/sector, scenarios confapi-year and confapi-june): a 5th level impiegato hired on 1 January 2026 by an employer with 50 employees, across the tranche of June 2026; every payment and the year (gross, contributions, tax, net, TFR, employer cost) match the engine to the cent. The CCNL now covers every total of the definition of done. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | Level 9 — highly qualified quadro | € 3,263.42 | 2028-06-01 |
| `8` | Level 8 — highly specialised technician, quadro | € 2,934.46 | 2028-06-01 |
| `7` | Level 7 — high technical or managerial expertise | € 2,698.38 | 2028-06-01 |
| `6` | Level 6 — specialist technician, department head, senior technical employee | € 2,515.19 | 2028-06-01 |
| `5` | Level 5 — specialist worker 2nd category, senior white-collar employee (CCNL reference level) | € 2,345.87 | 2028-06-01 |
| `4` | Level 4 — specialist worker 1st category, white-collar employee | € 2,189.93 | 2028-06-01 |
| `3` | Level 3 — skilled worker, clerical employee | € 2,098.96 | 2028-06-01 |
| `2` | Level 2 — standardised operations, simple executive duties | € 1,891.75 | 2028-06-01 |
| `1` | Level 1 — auxiliary duties, simple and repetitive operations | € 1,712.98 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 18.49 |
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `9` | € 45.96 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

**professionalizzante_30** (type: `under_classification`)  
Destination levels: `3`, `4`, `5`, `6`, `7`, `8`, `9`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `3`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-confapi/fondapi_base_elements · pension_fund_contribution · impact yes · open"
    The Fondapi base ('retribuzione FONDAPI', Art. 50 p. 123) counts, besides the minimi conglobati, the EDR, the indennità di funzione of the quadri and the elemento retributivo of the 8th and 9th categories. The CCNL text sets no EDR amount and no elemento retributivo; the indennità di funzione (Art. 98 p. 182: 69.72 quadri A, 49.06 quadri B, 32.75 quadri B oreficeria) is not held by the bundle pay, so the fund contributions of an enrolled quadro are understated.

    **Applies when:** `pension_fund_contribution` applies.

    **Remediation:** Model the quadri of the 8th and 9th categories with the indennità di funzione of Art. 98 and add it to the Fondapi base, then remove this note.

!!! warning "metalmeccanico-confapi/confapi_unmodelled_pay_elements · base_salary · impact yes · open"
    NOT MODELLED PAY CLAUSES (CCNL of 3 July 2017 and renewal of 4 June 2026): elemento perequativo of 485 EUR a year with June pay in firms without second-level bargaining (Art. 48); indennità di funzione of the quadri (Art. 98); reperibilità (Art. 28, amounts by group of levels adjusted each June) and trasferta; ordinary night, holiday and compensatory-rest premiums (Art. 29 rows b, d, h, i, f, m); the shift-worker column of Art. 29 (night overtime 40%/45%, night holiday overtime 65%) and night holiday work within 8 hours (60%); flessibilità beyond 40 hours (15%/20%, Art. 23) and banca ore (50% of the overtime premium); festività on a Sunday (1/26) and the 1 h 20' of the ex operai; the superminimo ex Parte prima of 11 h 10' a year (Art. 38); leave on a 6-day week and the transitional extra day (Art. 33); sickness: comporto prolungato (9/13.5/18 months) and its treatment, short absences counted double from the eighth in the triennio, hospital stays over 10 days and sickness over 21 days left out of the limits (60/75/90 days, at most 120), the 2026 disability extension at 50% (renewal p. 27), the net-pay gross-up; child sickness indemnity from 2027 (Art. 58 bis) and oncological permits (Art. 55 bis); the 65% credit of the apprenticeship for the seniority increments of the worker kept on (Art. 10 p. 49); the IPCA top-up of June 2027 and 2028 above 2.653% and 2.729%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the perequativo, E.A.R., quadri allowance, standby, ordinary-hour premiums, shift-worker rates and the residual sickness rules of Art. 55.

!!! warning "metalmeccanico-confapi/bilateral_system_or_ear · bilateral_funds · impact yes · open"
    BILATERAL SYSTEM: a firm that adheres to the bilateral system pays its contributions for every worker, a firm that does not pays the worker an E.A.R. of 25 EUR x 13 (Art. 53). Neither is modelled: the employer cost, and with the E.A.R. the net pay, are short of it.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2017-07-03 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/CCNL-Unionmeccanica.pdf) |
| — | — | 2021-05-26 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/Ipotesi-CCNL-TESTO-firme-accordo-26-maggio-2021.pdf) |
| — | — | 2024-06-11 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2024/06/20240611-UNIONMECCANICA-Verbale-accordo-minimi-2024.pdf) |
| — | — | 2025-06-19 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/06/20250619-Unionmeccanica-Confapi-Verbale-di-accordo-adeguamento-IPCA-2024.pdf) |
| — | — | 2025-07-24 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2025/07/2025-07-24-CCNL-Unionmeccanica-accordo-aumenti-minini-2025-26.pdf) |
| — | — | 2026-06-04 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260604-CCNL-Unionmeccanica-Confapi-2025-2028.pdf) |
| — | — | 2026-06-17 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2026/06/20260617-Unionmeccanica-Confapi-Verbale-accordo-minimi-1-giugno-2026-IPCA-signed.pdf) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: base_salary holds the 'minimi tabellari conglobati della classificazione unica' (Art. 38 p. 112 and Art. 40 p. 113 of the CCNL of 3 July 2017), which absorb paga base, contingenza and EDR; fixed_allowances is empty for all levels.
    
    TRANCHES: June 2024 from the signed verbale of 11 June 2024; June 2025 from the verbale of 19 June 2025; September 2025 from the printed minimi of the accordo of 24 July 2025; June 2026 from the verbale of 17 June 2026 (IPCA 2025 absorbed); June 2027 and June 2028 from the renewal of 4 June 2026 (p. 5, ratified 23 July 2026), raised in those Junes only for the IPCA above 2.653% and 2.729%. The accordo of 24 July 2025 and the renewal restate the minimo at 31 December 2024 of level 1 as 1566.94 (verbale 1566.89) and the June 2025 minimi of levels 1, 2, 4, 5, 9 one to five cents apart from the verbale of 19 June 2025: the verbale values are kept, as derived.
    
    PRE-JUNE 2024 TRANCHES (CCNL in force since 26 May 2021) are outside the modelled window.
    
    SENIORITY INCREMENTS: Art. 41 (pp. 115-116 of the CCNL of 3 July 2017): five biennial increments, amounts in force from 1 January 2001 (1a=18.49 2a=21.59 3a=25.05 4a=26.75 5a=29.64 6a=32.43 7a=36.41 8a=40.95 9a=45.96), from the month after the biennio. None during the apprenticeship (Art. 10 p. 49).
    
    APPRENTICESHIP: Art. 10 (pp. 45-48). Destinations 3rd to 9th category (8th and 9th for high specialisation). Pay two levels below, then one below, then of the destination in three equal periods: 36 months (12/12/12), 30 months for holders of a relevant diploma (10/10/10), 24 months for assembly-line figures of the 3rd category (8/8/8). Choose the track by name.
    
    HOURLY DIVISOR: 173 (Art. 40 p. 113, Art. 38 p. 112; Art. 10 p. 48 for apprentices).
    
    MONTHLY PAYMENTS: 13 (Art. 42 p. 119). The CCNL provides no fourteenth month.
    
    INPS: industria rates (contribution/2026/industria.json); the CCNL sets no contribution regime of its own. Installation firms classified in another INPS sector are outside this file.
    
    SICKNESS (Art. 55 pp. 136-139): integration up to the normal net pay, full for 2/3/4 months and half for 4/6/8 more by seniority, over the sickness of the three years before each episode; comporto breve 6/9/12 months. The INPS share is grossed up by the worker's INPS rate (net_basis), a payroll practice the CCNL does not spell out.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-confapi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-confapi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-confapi/example.py"
```
