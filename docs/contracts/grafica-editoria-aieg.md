# CCNL Grafica e Editoria Industria (AIEG-Acigraf)

| | |
|---|---|
| **CNEL code** | `G011` |
| **Sector** | grafica-editoria |
| **Family** | `carta-grafica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-12-20 |
| **Workers (est.)** | ~70k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIEG
    - Acigraf
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 71 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-12-20 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Parte Terza (Impiegati), Art. 8 - Tredicesima mensilità (p. 98): "Nel caso di inizio o cessazione del rapporto durante il corso dell’anno, l’impiegato non in prova avrà diritto a tanti dodicesimi dell’ammontare della 13a mensilità per quanti sono i mesi di servizio prestato. La frazione di mese non superiore a 15 giorni non sarà considerata, mentre sarà considerata come mese intero la frazione di mese superiore a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-18 | claude-opus-5-5 (ai) | The base_salary (minimo + contingenza + EDR) of the twelve Grafici levels against the renewal of 19 December 2023 and the CCNL 19 January 2021 it amends. | corrected | No signatory text prints the 2024-2026 Grafici totals. The signed ipotesi of 19/12/2023 (PDF p. 17) sets the B3 increments (Marzo 24 € 90, Ottobre 24 € 30, Maggio 25 € 30, Ottobre 25 € 50, Luglio 26 € 52) to be riparametrati and keeps contingenza and EDR unchanged; p. 19 (also printed by SLC-FISTel-UILCOM national secretariats on 11/01/2024) gives the per-level increments; the CCNL 2021 printed text gives the minimi at 01/10/2022 (p. 172), contingenza (p. 176) and EDR 10,33 (p. 173). The file's base_salary is the total minimo + contingenza + EDR, so each value is derived as that sum.<br>The file's second tranche starts 2024-09-01, but the ipotesi and the increment table date it October 2024: the 12 periods of 2024-09-01 are left unbacked and should be moved to 2024-10-01.<br>Levels Q, B1S, B1, B2, B3, C1, C2, D1: the 32 periods of 2024-03-01, 2025-05-01, 2025-10-01 and 2026-07-01 are derived; the file values were 0-3 cents higher (aggregator rounding) and 25 are corrected.<br>Levels E, D2, A, AS: the file exceeds the derived sum by a constant 14.74-14.77 (E), 16.77-16.79 (D2), 30.81-30.83 (A), 36.47-36.49 (AS) at every tranche. These 16 periods are left unbacked pending a printed table; the derived values are in each reason.<br>The file's meta lists the signatories as AIEG and Acigraf; the texts are signed by Assografici, AIE and ANES with SLC-CGIL, FISTel-CISL and UILCOM-UIL (CNEL G011).<br>Corrected to the printed table: D1 2024-03-01: 1582.37 -> 1582.36; D1 2025-05-01: 1626.84 -> 1626.82; D1 2025-10-01: 1663.90 -> 1663.88; D1 2026-07-01: 1702.44 -> 1702.42; C2 2024-03-01: 1694.91 -> 1694.90; C2 2025-05-01: 1743.97 -> 1743.96; C2 2025-10-01: 1784.85 -> 1784.84; C2 2026-07-01: 1827.37 -> 1827.35; C1 2024-03-01: 1852.88 -> 1852.87; C1 2025-05-01: 1908.29 -> 1908.27; C1 2025-10-01: 1954.47 -> 1954.44; C1 2026-07-01: 2002.49 -> 2002.46; B3 2024-03-01: 1964.85 -> 1964.84; B3 2025-05-01: 2024.85 -> 2024.84; B3 2025-10-01: 2074.85 -> 2074.84; B3 2026-07-01: 2126.85 -> 2126.84; B2 2025-05-01: 2142.24 -> 2142.23; B2 2025-10-01: 2196.06 -> 2196.05; B2 2026-07-01: 2252.04 -> 2252.02; B1 2025-10-01: 2311.16 -> 2311.15; B1 2026-07-01: 2371.11 -> 2371.10; B1S 2025-10-01: 2363.93 -> 2363.92; B1S 2026-07-01: 2425.41 -> 2425.40; Q 2025-05-01: 2732.71 -> 2732.70; Q 2026-07-01: 2882.11 -> 2882.10. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — quadro, highest technical or managerial responsibility | € 2,882.10 | 2026-07-01 |
| `AS` | AS — special grade, senior technical-editorial manager | € 2,871.24 | 2026-07-01 |
| `A` | A — 6th category worker, production manager | € 2,504.43 | 2026-07-01 |
| `B1S` | B1S — upper 5th category worker, technical department head | € 2,425.40 | 2026-07-01 |
| `B1` | B1 — 5th category worker, highly qualified technician | € 2,371.10 | 2026-07-01 |
| `B2` | B2 — upper 4th category worker, complex equipment operator | € 2,252.02 | 2026-07-01 |
| `B3` | B3 — 4th category worker, expert graphic technician | € 2,126.84 | 2026-07-01 |
| `C1` | C1 — 3rd category worker, specialist graphic technician | € 2,002.46 | 2026-07-01 |
| `C2` | C2 — 3rd category worker, general graphic technician | € 1,827.35 | 2026-07-01 |
| `D1` | D1 — upper 2nd category worker, qualified operator | € 1,702.42 | 2026-07-01 |
| `D2` | D2 — 2nd category worker, machine operator | € 1,595.11 | 2026-07-01 |
| `E` | E — 1st category worker, simple and routine tasks | € 1,460.85 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 16.01 |
| `AS` | € 16.01 |
| `A` | € 16.01 |
| `B1S` | € 14.46 |
| `B1` | € 14.46 |
| `B2` | € 13.94 |
| `B3` | € 13.43 |
| `C1` | € 12.91 |
| `C2` | € 12.39 |
| `D1` | € 11.88 |
| `D2` | € 11.36 |
| `E` | € 10.33 |

## Apprenticeship

**triennale** (type: `percentage`)  
Destination levels: `C2`, `C1`, `B3`, `B2`, `B1`, `B1S`, `A`, `AS`, `Q`  
percentage: 1.00

**biennale** (type: `percentage`)  
Destination levels: `D2`, `D1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "grafica-editoria-aieg/pre_july_2026_amounts_missing · seniority · impact unknown · open"
    SENIORITY: 5 scatti biennali (24 months), amounts from kitech.it July 2026. The scatto amounts of the previous rinnovo were not recovered: each amount series declares a 'missing' gap from 2024-03-01 to 2026-07-01. A run before July 2026 with increments due raises MissingRuleError; a run with no increment due does not read the amount.

    **Applies when:** `seniority` applies; before 2026-07-01.

    **Remediation:** Recover the scatto amounts of the previous rinnovo for periods before July 2026.

!!! warning "grafica-editoria-aieg/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "grafica-editoria-aieg/grafica_levels_unreconciled · base_salary · impact yes · open"
    LEVELS E, D2, A, AS: the file values exceed the sum of the printed items (minimo of 01/10/2022 + contingenza + EDR + cumulative TEM increments, FISTel compendium pp. 172, 176, 173, 19) by a constant amount at every tranche: E +14.74, D2 +16.77, A +30.81, AS +36.47, about one 2022 tranche. No signatory prints the post-2024 totals, so the values are kept from the aggregator and not verified.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read a printed post-2024 table of the signatories (testo a stampa) and reconcile levels E, D2, A and AS.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.lexplain.it/tabelle-retributive-grafici-editoriali-industria-2024-2026/ | tabella_retributiva | 2024-12-20 | [↗](https://www.lexplain.it/tabelle-retributive-grafici-editoriali-industria-2024-2026/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156 | tabella_retributiva | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: the CCNL Grafica e Editoria Industria (G011) uses a split model with separate paga base (TEM), contingenza (frozen since 1992 per Prot. 31/07/1992), and EDR (10.33 EUR, all levels). The base_salary values in this file are the TOTAL (paga base + contingenza + EDR) per level and tranche, sourced from the official lexplain.it table (all 5 tranches) and kitech.it (July 2026 breakdown). Modeling the total as base_salary produces the same gross_monthly as the split representation. fixed_allowances is empty for all levels (no additional fixed components).
    
    CONGLOBATED CHECK: inter-level increase ratios are stable across all 5 tranches (e.g., Q/E = 1.937, C1/E = 1.357 at all dates), confirming a single parametric coefficient system. Contingenza is frozen per level (E=512.87, Q=539.99); EDR=10.33 uniform. Total values from lexplain cross-check with kitech July 2026 breakdown to within ±0.03 EUR (rounding difference).
    
    HOURLY DIVISOR: 173. G011 CCNL states orario normale 40 ore medie settimanali (confirmed conflavoro.it CCNL text and ilccnl.it). Formula 40×52/12=173.33→173. Daily divisore convenzionale 26 confirmed by lavoro-economia.it. The exact contractual divisore clause was not retrieved directly from primary text, but the 40h/week is unambiguous; divisor 173 is the correct derived value.
    
    TRANCHE DATES: 01.03.2024, 01.09.2024, 01.05.2025, 01.10.2025, 01.07.2026. Values from rinnovo 20.12.2024 (retroactive application). Fonte: lexplain.it (5 tranches, all 12 Grafici levels) and kitech.it (componenti breakdown July 2026).
    
    SECTOR SCOPE: models the GRAFICI (graphics workers) sector only (12 levels: E, D2, D1, C2, C1, B3, B2, B1, B1S, A, AS, Q). The EDITORI (publishers) sector (9 levels: 8°-0°/Q) with slightly different pay tables is NOT modelled. Coverage marked as layer_1=implemented for Grafici only.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Confirmed by secondary source (lavoro-economia.it / contratticcnl.it). A quattordicesima is not provided for by CCNL G011 Grafici.
    
    INPS: reuses 2026-industria.json (Confindustria). AIEG/Acigraf are members of Confindustria; CIGO applicable for the graphic arts industry sector (D.Lgs. 148/2015).
    
    APPRENTICESHIP (Art. 26e, Type 2, CCNL 19/01/2021, p.42; confirmed in force in the 20.12.2024 renewal): 'triennale' track (groups C,B,A,Q → levels C2,C1,B3,B2,B1,B1S,A,AS,Q): 36 months / 6 semesters, 70/75/80/85/90/95% then 100%. 'biennale' track (group D → levels D2,D1): 24 months / 6 four-month periods (4 months each), 70/75/80/85/90/95% then 100%. Level E not listed as an apprenticeship destination. EDITORI sector not modelled in this JSON. Source: fistelcisl.it PDF CCNL grafici-editoriali.pdf (p. 41-42).
    

## Raw data

The contract file this page is generated from: [`agreement/grafica-editoria-aieg.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/grafica-editoria-aieg.json).

## Usage example

```python
--8<-- "docs/examples/agreement/grafica-editoria-aieg/example.py"
```
