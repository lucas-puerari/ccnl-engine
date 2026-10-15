# CCNL Lavoro Domestico — DOMINA/FIDALDO/ASSINDATCOLF (conviventi a orario ridotto, art. 14 c. 2)

| | |
|---|---|
| **CNEL code** | `H501` |
| **Sector** | lavoro domestico |
| **Tax sector** | `lavoro-domestico` |
| **Last renewal** | — |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.3` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - DOMINA — Associazione Nazionale Famiglie Datori di Lavoro Domestico
    - FIDALDO — Federazione Italiana Datori di Lavoro Domestico
    - ASSINDATCOLF — Associazione Nazionale dei Datori di Lavoro Domestico
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL
    - FEDERCOLF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | assistance_contribution, base_salary, inps_employer, overtime, sickness |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🧑 Manual | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 13 verified / 2 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | — |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Every payable rule of the file: minimums, hourly divisor, additional months, seniority, Cas.Sa.Colf, overtime, absences, leave and the accrual of the tredicesima, read in the signed text of 28 October 2025 and its 2026 table (p. 59); the sickness rule of Art. 27 stays derived (readings in its transformation). | corrected | Overtime: the file held 10% and 20%; Art. 15 c. 3 sets 25% by day, 50% by night and 60% on a holiday or Sunday. The 20% of Art. 14 c. 6 is the supplement of ordinary night work, not of overtime.<br>accrual_rule was missing: chiarimento a verbale 4 counts a fraction of a month of at least 15 calendar days as a whole month.<br>Citations moved from the DOMINA table and section labels without page to the signed text with page and quote.<br>Tabella B, level B: the file held 702,35 as printed in the signed text; the DOMINA table of 2026 and the table of the Commissione of 11 February 2026 print 702,25. Corrected to 702,25 and left derived; the seniority step (4%) is 28,09 either way. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `C` | Level C — specialised domestic worker / assistant caregiver (badante) | € 814.60 | 2026-01-01 |
| `BS` | Level BS — qualified domestic worker with seniority | € 737.39 | 2026-01-01 |
| `B` | Level B — qualified domestic worker (colf qualificata) | € 702.25 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `B` | € 28.09 |
| `BS` | € 29.50 |
| `C` | € 32.58 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavoro-domestico-convivente-orario-ridotto/hourly_inps_bracket_unvalidated · inps_employer · impact unknown · open"
    INPS BAND: the band of up to 24 weekly hours is chosen on the paga oraria effettiva of INPS (circ. 9/2026; INPS page Contributi e agevolazioni fiscali per chi assume un lavoratore domestico): the monthly pay with board and lodging over the hours of the employment (weekly hours x 52 / 12), raised by the tredicesima (x 13 / 12).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Validate the hourly INPS bracket lookup for weekly hours up to 24 against the INPS domestic table.

!!! warning "lavoro-domestico-convivente-orario-ridotto/board_lodging_substitute · base_salary · impact unknown · open"
    The cash indennita sostitutiva of board and lodging is not paid for the days the convivente does not take them: ferie (Art. 17 c. 7), sospensioni extraferiali (Art. 18 c. 1), congedo matrimoniale (Art. 24 c. 2), malattia and infortunio outside hospital (Art. 27 c. 9, Art. 29 c. 7). The request carries no fact on whether board and lodging were taken, so the engine pays none.

    **Applies when:** `base_salary` applies; run kind in regular, termination.

    **Remediation:** Add a fact for the days without board and lodging and pay the Tabella F value for them.

!!! warning "lavoro-domestico-convivente-orario-ridotto/extra_month_hours · assistance_contribution · impact unknown · open"
    The INPS contributions of the tredicesima are paid on the hours of the year: INPS bands them on the paga oraria effettiva, which spreads the tredicesima over the hours, so the tredicesima run charges no INPS hours. The Cas.Sa.Colf contribution of Art. 54 c. 2 is charged on the contributable hours the run states, a tredicesima run too: no bundled source says whether the tredicesima carries hours of its own for it.

    **Applies when:** `assistance_contribution` applies; run kind in thirteenth.

    **Remediation:** Source from the Cas.Sa.Colf rules whether the tredicesima carries contributable hours and set them for extra-month runs.

!!! warning "lavoro-domestico-convivente-orario-ridotto/oncological_comporto · sickness · impact unknown · open"
    Art. 27 c. 6: the comporto is 50% longer for an oncological illness certified by the ASL. The request does not say whether an episode is oncological, so the engine keeps the ordinary comporto.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for an oncological sickness episode and lengthen its comporto by 50%.

!!! warning "lavoro-domestico-convivente-orario-ridotto/sick_board_lodging · sickness · impact unknown · open"
    Art. 27 c. 9: the conventional value of board and lodging is part of the sick pay only when the worker is not in hospital or in the employer's home. The request does not say where the worker is, so the engine pays the monthly pay as stated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the days in hospital or in the employer's home and leave the board and lodging out of their sick pay.

!!! warning "lavoro-domestico-convivente-orario-ridotto/hours_within_arrangement · overtime · impact yes · open"
    Art. 14 c. 2: hours beyond the agreed ones within the agreed time arrangement are paid at the plain hourly retribuzione globale di fatto, only those outside it with the supplements of Art. 15. The request does not say where an hour falls, so the overtime bands of Art. 15 apply to every overtime hour stated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a fact for the extra hours within the agreed time arrangement and pay them without a supplement.

!!! warning "lavoro-domestico-convivente-orario-ridotto/annual_minimi_not_updated · base_salary · impact yes · open"
    ANNUAL MINIMI: the minimi of the CCNL are updated every year from 1 January by the Commissione nazionale (Art. 38, ISTAT variation of the consumer prices); the bundle holds the table of 2026. From 1 January 2027 the amounts are those of 2026 until the 2027 table is published and added, so a 2027 run is not payable.

    **Applies when:** `base_salary` applies; from 2027-01-01.

    **Remediation:** Add the minimi of 2027 set by the Commissione nazionale with their source, then remove this note.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-28 | [↗](https://lavorodomestico.assindatcolf.it/wp-content/uploads/2026/04/CCNL.pdf) |

??? note "Coverage notes"
    SALARY MODEL: TABELLA B of the CCNL of 28/10/2025, conviventi hired under art. 14 c. 2 (levels C, B and B super, up to 30 weekly hours, written act of c. 3). The monthly minimum is paid 'qualunque sia l'orario di lavoro osservato nel limite massimo delle 30 ore settimanali', so it is not proportioned to the hours and more than 30 weekly hours are rejected; board and lodging are due in full ('fermo restando l'obbligo di corresponsione dell'intera retribuzione in natura'). Values of 2026: B 702,25 (the signed text prints 702,35, the DOMINA and Commissione tables 702,25), BS 737,39, C 814,60.
    
    HOURLY DIVISOR: 130 = 30 x 52 / 12 in the file; a run uses the weekly hours of the employment x 52 / 12 (flat_pay_max_weekly_hours), since the Tabella B pay does not change with the hours: B super at 10 weekly hours is 737,39 / 43,33 = 17,02 an hour. Work beyond the agreed hours is paid at the hourly retribuzione globale di fatto (art. 14 c. 2), with the art. 15 supplements outside the agreed time arrangement; the overtime bands are those of the convivente file.
    
    SENIORITY: biennale, 4% of the Tabella B minimum (art. 37 c. 1: 'sulla retribuzione minima contrattuale'), maximum 7 scatti: B 28,09, BS 29,50, C 32,58.
    
    NOT MODELLED: students aged 16 to 40 (art. 14 c. 2) at levels other than C, B and B super, for whom Tabella B has no value; the Tabella H indennita of the baby sitter of level B super for children under six (art. 34 c. 3), 97,06 a month for Tabella B workers; the Tabella L indennita of art. 34 c. 7 for certified workers. None of them is paid.
    
    TAX SECTOR: lavoro-domestico (TaxSector.LAVORO_DOMESTICO). Flat per-hour INPS contributions from INPS Circ. 9/2026. A household employer is not a withholding agent: it is not among the sostituti d'imposta of art. 23 c. 1 D.P.R. 600/1973 (art. 33 c. 1 D.Lgs. 33/2025 from 2027), so the engine withholds no IRPEF or surtax and pays no trattamento integrativo, ulteriore detrazione or somma esente.
    
    ADDITIONAL MONTHS: 13 (tredicesima mensilita, Art. 39 CCNL 28/10/2025). No quattordicesima for domestic workers.
    
    APPRENTICESHIP: none. Domestic workers are excluded from D.lgs. 81/2015 Art. 47 apprenticeship provisions.
    
    BOARD AND LODGING: every level carries the allowance vitto_alloggio, the valore convenzionale of board and lodging provided in kind (Art. 36 c. 3, Tabella F 2026: 2,33 + 2,33 + 2,00 per day, x 30 = 199,80 per month). A regular run pays no cash for it and counts it in the TFR base (Art. 41 c. 1); the tredicesima pays it in cash (Art. 39 c. 1, chiarimento a verbale 5). It is not reduced for reduced hours (Art. 14 c. 2: intera retribuzione in natura).
    
    CAS.SA.COLF: contributi di assistenza contrattuale of Art. 54 c. 2, 0,06 EUR per paid hour, 0,02 withheld from the worker and 0,04 paid by the employer, charged on the contributable hours of the run.
    
    SICKNESS (Art. 27): INPS pays no indemnity to domestic workers; the employer pays 50% of the retribuzione globale di fatto up to the third day and 100% from the fourth, for at most 8, 10 or 15 days in the 365 days that end on the sick day, within a comporto of 10, 45 or 180 days, for up to 6 months of seniority, up to 2 years and over 2 years. A sick day is a thirtieth of the monthly pay (chiarimento a verbale 2).
    
    NIGHT WORK (Art. 14 c. 6): ordinary work between 22.00 and 6.00 is paid with a 20% supplement of the hourly retribuzione globale di fatto; the engine takes its amount as a NightShiftEvent stated by the caller. The overtime bands are those of Art. 15 c. 3 (25% by day, 50% by night, 60% on a holiday or Sunday); night overtime on a holiday has no band of its own and a run that states it is rejected.
    

## Raw data

The contract file this page is generated from: [`agreement/lavoro-domestico-convivente-orario-ridotto.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavoro-domestico-convivente-orario-ridotto.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavoro-domestico-convivente-orario-ridotto/example.py"
```
