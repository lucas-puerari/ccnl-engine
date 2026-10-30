# CCNL Occhiali e Occhialeria — Industria (ANFAO)

| | |
|---|---|
| **CNEL code** | `D271` |
| **Sector** | industria occhialeria e ottica |
| **Family** | `tessile-moda` |
| **Tax sector** | `industria` |
| **Last renewal** | 2023-12-04 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANFAO
    - Filctem-CGIL
    - Femca-CISL
    - UilTEC-UIL

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

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 77 verified / 11 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-12-04 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The Elemento Retributivo Nazionale (conglobated minimo, TEM) of the ten levels against the signed ipotesi of the 2023-2025 renewal (28 April 2023, ERN table for 1.05.2023, 1.03.2024, 1.02.2025) and of the 2026-2028 renewal (30 January 2026, ERN table for March 2026 to November 2028), both published by FILCTEM-CGIL, a signatory. | corrected | The two FILCTEM-CGIL scans (signed by ANFAO, Filctem, Femca, Uiltec) print the ERN per level for every tranche of the file: 2023 ipotesi PDF p. 22, 2026 ipotesi PDF p. 30 (All. 1). Both are image-only scans read on the page images (tesseract garbles the 2026 table). Level codes map one to one (Q, 6, 5S, 5, 4S, 4, 3S, 3, 2, 1); the 2023 table labels them by area and step professionale (e.g. '4° S Qualificata Consolidato').<br>The ERN is the conglobated tabular minimum and matches the file's base_salary meaning; the Q indennita di funzione is not in the ERN (Q ERN is only a few euro above level 6), consistent with the file's separate allowance.<br>Level 1 MAG.2027: the 2026 table prints 1.661,71, a transposition of 1.661,17 (1.622,04 + 39,13; 1.661,17 + 35,21 = 1.696,38 printed for MAG.28). The file's 1661.17 is kept as a derived value.<br>Level 4S 1.03.2024 and 1.02.2025: the 2023 table prints 2.014,69 and 2.074,05, but its own increments give 2.016,18 and 2.075,54, and the 2026 table (2.126,94 - 51,40) implies 2.075,54. The definitive text of 4 December 2023 reportedly corrected some minimi but is not published by a signatory; both periods are left unbacked.<br>One-cent residuals between the two signed tables remain for levels 6 and 5S (2025 ERN 2.448,66 and 2.323,28 vs 2.448,67 and 2.323,29 implied by the 2026 ERN minus the first 2026 tranche); each period is backed by the table that prints it.<br>Consistency check (base + printed increment) on both tables: 2023 table off by -0,01 for level 6 at 1.03.2024 (2.319,66 + 58,98 = 2.378,64 vs 2.378,63 printed) and by -1,49 for 4S; 2026 table consistent except the level 1 MAG.2027 transposition. Rule applied: a printed value stays a verified row unless a later signed table contradicts it by more than rounding (4S, unbacked); one-cent residuals are kept as printed and reported here.<br>The ruleset names a FILCTEM-CGIL document, a signatory: source_type contracting_party.<br>Corrected to the printed table: Q 2026-10-01: 2546.53 -> 2546.54; Q 2027-05-01: 2604.87 -> 2604.88; Q 2028-05-01: 2657.38 -> 2657.39; Q 2028-11-01: 2680.72 -> 2680.73; 6 2026-10-01: 2539.80 -> 2539.79; 6 2027-05-01: 2596.76 -> 2596.74; 6 2028-05-01: 2648.02 -> 2647.99; 6 2028-11-01: 2670.80 -> 2670.77; 5S 2027-05-01: 2467.76 -> 2467.75; 5S 2028-05-01: 2517.77 -> 2517.76; 5S 2028-11-01: 2540.00 -> 2539.99; 4S 2026-10-01: 2158.67 -> 2157.78; 4S 2027-05-01: 2211.56 -> 2209.18; 4S 2028-05-01: 2259.16 -> 2255.44; 4S 2028-11-01: 2280.32 -> 2276.00; 3S 2028-11-01: 2125.83 -> 2125.84; 2 2028-05-01: 1948.54 -> 1948.53; 2 2028-11-01: 1966.32 -> 1966.31; 1 2028-05-01: 1696.39 -> 1696.38; 1 2028-11-01: 1712.04 -> 1712.03. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — Lavoratori con responsabilita di direzione e coordinamento (Art. 2095 c.c.) | € 2,680.73 | 2028-11-01 |
| `6` | Livello 6 — Lavoratori con autonomia decisionale e competenze trasversali elevate | € 2,670.77 | 2028-11-01 |
| `5S` | Livello 5 Super — Lavoratori con funzioni tecniche o di supervisione avanzata | € 2,539.99 | 2028-11-01 |
| `5` | Livello 5 — Lavoratori con funzioni di controllo o alta specializzazione | € 2,453.48 | 2028-11-01 |
| `4S` | Livello 4 Super — Lavoratori con elevata specializzazione o coordinamento | € 2,276.00 | 2028-11-01 |
| `4` | Livello 4 — Lavoratori polivalenti o con responsabilita tecnica | € 2,187.96 | 2028-11-01 |
| `3S` | Livello 3 Super — Lavoratori specializzati di livello superiore | € 2,125.84 | 2028-11-01 |
| `3` | Livello 3 — Lavoratori specializzati con autonomia operativa | € 2,082.62 | 2028-11-01 |
| `2` | Livello 2 — Lavoratori qualificati con conoscenze specifiche | € 1,966.31 | 2028-11-01 |
| `1` | Livello 1 — Lavoratori addetti a mansioni semplici e ripetitive | € 1,712.03 | 2028-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.84 |
| `2` | € 7.36 |
| `3` | € 7.80 |
| `3S` | € 7.80 |
| `4` | € 8.26 |
| `4S` | € 8.26 |
| `5` | € 9.76 |
| `5S` | € 9.76 |
| `6` | € 11.65 |
| `Q` | € 11.65 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4S`, `5`, `5S`, `6`, `Q`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "occhiali-occhialeria-industria/shift_6x6_divisor_156 · overtime · impact yes · open"
    HOURLY DIVISOR: 173 (standard 40h/week). Shift workers on 6x6 turns use divisor 156; engine models the 173 case uniformly.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 156 divisor of the 6x6 shift workers (a work pattern input or an hourly_divisor by schedule), as the long-week divisors tracked elsewhere.

!!! warning "occhiali-occhialeria-industria/level_1_entry_rate · base_salary · impact yes · open"
    LEVEL 1 sub-level: the CCNL provides automatic advancement from entry sub-level (L1 ingresso) to L1 standard after 6 months. The file models only the post-advance minimum throughout, which is the relevant value for permanent workers and for workers beyond their 6th month. The entry sub-level undervaluation during the first 6 months is a deliberate structural simplification.

    **Applies when:** `base_salary` applies; level in 1.

    **Remediation:** Model the L1 ingresso minimum for the first 6 months of service (a level or a seniority-gated reduction), or record the limitation.

!!! warning "occhiali-occhialeria-industria/apprenticeship_full_pay · base_salary · impact yes · open"
    APPRENTICESHIP: 2026 rinnovo (signed 30/01/2026) explicitly 'abroga la ripartizione in percentuale in relazione agli step professionali' (edotto.com). Pre-2026 CCNL used a percentage system. Post-2026 replacement type is not confirmed from a D271 primary source — the cognate piccola industria (ccnlportatili.it) uses sotto-inquadramento (2 levels below for first 12m, 1 level below for next 12m, then destination). Modelled as 100% passthrough for all levels pending primary source confirmation; this is a conservative over-estimate for the 2026-2028 period.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Model the post-2026 under-classification apprenticeship from a D271 primary source.

!!! warning "occhiali-occhialeria-industria/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato of a month not worked in full without the pay of a whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive | altro | 2023-12-04 | [↗](https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive) |
| https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/ | altro | 2026-01-30 | [↗](https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/) |

??? note "Coverage notes"
    CCNL signed 04/12/2023 valid 01/01/2023-31/12/2025; renewed 30/01/2026 valid 01/01/2026-31/12/2028 (ANFAO+Filctem-CGIL+Femca-CISL+UilTEC-UIL).
    
    CONGLOBATED (since 01/01/2009): contingenza and EDR are inglobated into the tabular minimum. Single base_salary column per level; no separate contingenza allowance.
    
    Level Q (Quadro): indennita di funzione +82.63 EUR/month on top of the tabular minimum (all tranches). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level amounts (EUR): 1=6.84, 2=7.36, 3=3S=7.80, 4=4S=8.26, 5=5S=9.76, 6=Q=11.65.
    
    TRANCHES 01/10/2026 through 01/11/2028: L4 reference increments confirmed from primary source (CISL communique CCNL occhialeria 30/01/2026: +30, +50, +45, +20 EUR at L4). All-level amounts derived via the parametric ratio matrix from confirmed 01/03/2026 per-level deltas. The CCNL occhialeria uses a declared parametric system; parametric derivation is contractually consistent.
    

## Raw data

The contract file this page is generated from: [`agreement/occhiali-occhialeria-industria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/occhiali-occhialeria-industria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/occhiali-occhialeria-industria/example.py"
```
