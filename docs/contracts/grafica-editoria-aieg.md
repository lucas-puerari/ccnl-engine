# CCNL Grafica e Editoria Industria (AIEG-Acigraf)

| | |
|---|---|
| **CNEL code** | `G011` |
| **Sector** | grafica-editoria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~70k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIEG
    - Acigraf
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

## Coverage

### Funzionalità

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2026-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — quadro, highest technical or managerial responsibility | € 2,882.11 | 2026-07-01 |
| `AS` | AS — special grade, senior technical-editorial manager | € 2,871.24 | 2026-07-01 |
| `A` | A — 6th category worker, production manager | € 2,504.43 | 2026-07-01 |
| `B1S` | B1S — upper 5th category worker, technical department head | € 2,425.41 | 2026-07-01 |
| `B1` | B1 — 5th category worker, highly qualified technician | € 2,371.11 | 2026-07-01 |
| `B2` | B2 — upper 4th category worker, complex equipment operator | € 2,252.04 | 2026-07-01 |
| `B3` | B3 — 4th category worker, expert graphic technician | € 2,126.85 | 2026-07-01 |
| `C1` | C1 — 3rd category worker, specialist graphic technician | € 2,002.49 | 2026-07-01 |
| `C2` | C2 — 3rd category worker, general graphic technician | € 1,827.37 | 2026-07-01 |
| `D1` | D1 — upper 2nd category worker, qualified operator | € 1,702.44 | 2026-07-01 |
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-12-20 | [↗](https://www.lexplain.it/tabelle-retributive-grafici-editoriali-industria-2024-2026/) |
| — | — | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

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

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/grafica-editoria-aieg.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/grafica-editoria-aieg.py"
```
