# CCNL per i dipendenti da aziende dei settori Pubblici Esercizi, Ristorazione Collettiva e Commerciale e Turismo

| | |
|---|---|
| **CNEL code** | `H05Y` |
| **Sector** | turismo |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~350k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FIPE-Confcommercio
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI-Servizi
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime, seniority |

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 58 verified / 5 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-11 | claude-opus-5-5 (ai) | Every payable rule of the file (72 records) and the hourly divisor read again in the signed texts: the CCNL of 8 February 2018, the renewal of 5 June 2024 and its accordo integrativo of 26 June 2024 with the final salary tables. | corrected | All 50 salary periods and the 10 level rows match the accordo integrativo of 26 June 2024 (pp. 1-2) and are verified, with the Quadri allowances (Art. 154), the 14 monthly payments (Artt. 183-184), seniority (Art. 182), overtime 30% and 60% (Art. 126), the daily quota 1/26 (Art. 159), leave (Art. 134) and the hourly divisor 172 (Art. 160). Pages are PDF page indexes.<br>Corrected: sickness (Art. 190, Art. 194). INPS pays 80% for the whole sickness in this sector (regime pubblici_esercizi, funded by the 0.77% supplement) and the CCNL adds no top-up, so the target is 80%; the three days of carenza are paid in full only when the sickness lasts more than five days; the comporto is 180 days a calendar year.<br>Assumed: the overtime bands for holidays (30%) and holiday nights (60%). The CCNL sets only 30% by day and 60% by night (Art. 126) and 20% for ordinary work on a holiday (Art. 132); the two bands are inferences, not cited values.<br>Left derived: the Fon.Te. rates, read in the fund's information sheet, not in the CCNL.<br>Not modelled: the quattordicesima excludes the seniority increments (Art. 184), the collective catering companies move the June 2025 and June 2026 tranches to September (accordo integrativo p. 3), and the conditions of Art. 190 beyond the carenza.<br>FIPE and the Turismo CCNLs are two agreements: FIPE was renewed on 5 June 2024 (level 4 at 1,692.69 from June 2026), the Turismo CCNL of Federalberghi and Faita on 5 July 2024 (1,695.69 from May 2026). |
| 2026-10-12 | claude-opus-5-5 (ai) | Quattordicesima and seniority, holiday overtime, September tranches of the ristorazione collettiva: follow-ups of the review of 2026-10-11. | corrected | Quattordicesima: art. 184 c. 1 excludes the matured seniority increments; the engine paid them. Now excluded.<br>Holiday overtime: the 30% and 60% are art. 126 itself (by time of day), not an analogy: derived from p. 99; whether art. 132's 20% is added is left open (outside_input note).<br>Ristorazione collettiva: the 2025 and 2026 tranches start in September for the companies of art. 1 c. 1 par. II (accordo integrativo 26.6.2024, p. 3); still the limitation contract_catering_tranche_dates. |
| 2026-10-12 | claude-opus-5-5 (ai) | Accrual of the tredicesima and quattordicesima (artt. 183 c. 2 and 184 c. 4). | corrected | The accrual rule was missing (engine default of 15 days per month): the CCNL cumulates the fractions of month, a rateo for each 30 days and one for a remainder of 15 days or more, now modelled (cumulated_fractions). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Qa` | Quadri A — managerial functions with a high level of management responsibility | € 2,578.07 | 2027-12-01 |
| `Qb` | Quadri B — managerial functions with continuous responsibility over a complex unit | € 2,375.56 | 2027-12-01 |
| `1` | Level 1 — staff with high professional content and operational autonomy | € 2,201.85 | 2027-12-01 |
| `2` | Level 2 — staff with initiative and operational autonomy (coordination) | € 1,999.36 | 2027-12-01 |
| `3` | Level 3 — staff with specialist technical knowledge (conceptual work) | € 1,877.00 | 2027-12-01 |
| `4` | Level 4 — staff with executive autonomy (specialised technical-administrative duties) | € 1,762.69 | 2027-12-01 |
| `5` | Level 5 — staff with qualified technical-practical knowledge and skills | € 1,643.50 | 2027-12-01 |
| `6s` | Level 6 super — staff with adequate technical-practical skills (formerly qualified commis or experienced staff) | € 1,574.42 | 2027-12-01 |
| `6` | Level 6 — staff with standard practical training and basic professional knowledge | € 1,549.78 | 2027-12-01 |
| `7` | Level 7 — general assistants, cleaning staff (simple manual tasks) | € 1,442.45 | 2027-12-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Qa` | € 40.80 |
| `Qb` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6s` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6s`, `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "pubblici-esercizi-fipe-angem/contract_catering_tranche_dates · base_salary · impact yes · open"
    CONTRACT CATERING: collective catering companies apply the June 2025 and June 2026 tranches from September (accordo integrativo 26 June 2024, p. 3); they are modelled in pubblici-esercizi-fipe-angem-ristorazione-collettiva. This file holds the June dates of the other sub-sectors.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Use pubblici-esercizi-fipe-angem-ristorazione-collettiva for a collective catering company.

!!! warning "pubblici-esercizi-fipe-angem/small_company_pay_reduction · base_salary · impact yes · open"
    SMALLER COMPANIES: Art. 162 provides for a reduction in base pay for smaller companies (from €2.58 to €5.68 per level). Not modelled — applicable only to the smaller pubblici esercizi of paragraph I Art. 1 (CCNL 2018, p. 118: "Per il personale delle aziende minori dei pubblici esercizi [...] si fa rinvio all'articolo 162"). Maximum impact: €5.68/month for Qa.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 162 base-pay reduction for micro-enterprises with an employer-size input.

!!! warning "pubblici-esercizi-fipe-angem/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "pubblici-esercizi-fipe-angem/holiday_overtime_cumulation · overtime · impact unknown · open"
    HOLIDAY OVERTIME: Art. 126 (PDF p. 99) gives 30% by day and 60% by night for every overtime hour; Art. 132 (p. 103) gives 20% for the hours worked on a festività. The CCNL states no cumulation rule between them (it does for night work, art. 126 c. 3, and for Sunday work, art. 130 c. 2). The engine pays holiday overtime at 30%/60% without the 20%.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Confirm whether the 20% of art. 132 is added to the overtime rate on a festività; if so set the bands to 0.5 and 0.8, else close this note.

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
    SALARY MODEL: the contractual pay structure provides for a separate national base pay and contingenza. For engine purposes they are consolidated into base_salary (monthly total per tranche). The totals are read in the accordo integrativo of 26 June 2024 (pp. 1-2), the same as the FIPE pay tables. fixed_allowances models the function allowance for quadri: Qa=75 EUR and Qb=70 EUR, from Art. 154 of the CCNL of 8 February 2018 (CCNL 2024-2027).

!!! note ""
    APPRENTICESHIP (Art. 68): professionalizzante apprenticeship 36 months, percentages 80%/85%/90% from lexplain.it (secondary, not checked on the signed text). Destination levels modelled as 1-6s and 6 (Qa/Qb excluded per D.Lgs. 81/2015 art. 41; level 7 excluded per tertiary CCNL convention, not verified against Art. 68 — fipe.it full text PDF not parseable: scanned without OCR). Art. 75 (apprenticeship for qualification/diploma) out of scope.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-26 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ACCORDO-INTEGRATIVO_Tabelle-Retributive_CCNL_P_E_Risto_Collettiva_Commerciale_Turismo.pdf) |
| — | — | 2024-06-05 | [↗](https://www.fipe.it/wp-content/uploads/2024/06/Contratto-CCNL-05_06_24.pdf) |
| — | — | 2018-02-08 | [↗](https://www.confcommerciomilano.it/export/sites/unione/doc/contratti_lavoro/contrattazione_collettiva/ccnl_ristorazione_2018.pdf) |

??? note "Coverage notes"
    2024 RENEWAL: CCNL signed 5 June 2024, validity 1 June 2024 – 31 December 2027 (CNEL H05Y, ~592,364 workers Uniemens 2022 / over 1 million according to FIPE). Pay table source: fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf.
    
    SENIORITY INCREMENTS: 6 quadrennial increments (48 months). Per-level amounts from FIPE pay tables (fipe.it/wp-content/uploads/2025/02/Tabelle-retributive-2024.pdf). Paid over 14 monthly instalments.
    
    MONTHLY PAYMENTS: 14, the tredicesima of Art. 183 and the quattordicesima of Art. 184 of the CCNL of 8 February 2018 (PDF pp. 127-128). The quattordicesima excludes the matured seniority increments (seniority_increments.excluded_from_extra_months).
    
    HOURLY DIVISOR: 172 for a 40-hour week (Art. 160 of the CCNL of 8 February 2018, PDF p. 116; 190 for a 44-hour week, not modelled).
    
    INPS: uses 2026-terziario.json (tax_sector terziario, same as commercio-confcommercio and turismo-federalberghi).
    

## Raw data

The contract file this page is generated from: [`agreement/pubblici-esercizi-fipe-angem.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/pubblici-esercizi-fipe-angem.json).

## Usage example

```python
--8<-- "docs/examples/agreement/pubblici-esercizi-fipe-angem/example.py"
```
