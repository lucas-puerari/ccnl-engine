# CCNL Gruppo ANAS

| | |
|---|---|
| **CNEL code** | `T511` |
| **Sector** | anas spa - personale non dirigente |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-12-18 |
| **Workers (est.)** | ~7k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANAS SpA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI
    - UGL Viabilità e Logistica

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 42 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-12-18 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 106 - Tredicesima mensilita' (p. 149): "il dipendente ha diritto a tanti dodicesimi della tredicesima mensilità per quanti sono i mesi di servizio prestati, computando come mese intero la frazione di mese pari o superiore a 15 giorni.". Match: at_least 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A | € 3,475.91 | 2027-07-01 |
| `A1` | Livello A1 | € 2,896.61 | 2027-07-01 |
| `B` | Livello B | € 2,462.15 | 2027-07-01 |
| `B1` | Livello B1 | € 2,244.84 | 2027-07-01 |
| `B2` | Livello B2 | € 2,027.55 | 2027-07-01 |
| `C` | Livello C | € 1,665.53 | 2027-07-01 |
| `C1` | Livello C1 | € 1,448.36 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `C1` | € 16.66 |
| `C` | € 19.16 |
| `B2` | € 23.32 |
| `B1` | € 25.82 |
| `B` | € 28.30 |
| `A1` | € 33.31 |
| `A` | € 39.97 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `C1`, `C`, `B2`, `B1`, `B`, `A1`, `A`  
percentage: 0.92

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "anas/apprentice_seniority · seniority · impact unknown · open"
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
| https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf | altro | 2025-12-18 | [↗](https://www.stradeanas.it/sites/default/files/Azienda/Lavora_con_noi/CCNL-2025-2027.pdf) |

??? note "Coverage notes"
    Split model: minimo tabellare + IIS (Indennita Integrativa Speciale, frozen). 7 levels C1-C-B2-B1-B-A1-A. Divisor 156, 13 months. 4 tranches: 01/03/2026, 01/09/2026, 01/03/2027, 01/07/2027.
    
    IIS months_per_year=13: confirmed equal to additional_months (ANAS CCNL: 13 mensilità standard; INPS/secondary sources confirm 13-month pay cycle).
    
    Seniority maximum_count=10 — confirmed: ANAS CCNL provides 10 biennial seniority increments (secondary source cross-reference, consistent with comparable PA-adjacent contracts).
    
    Apprenticeship 70/85/92% confirmed from CCNL ANAS 2025-2027 Art. 28 text. Last period (months_until=null at 92%) reflects the contractual open-ended formulation; upon qualification the worker moves to full pay at the destination level.
    
    Overtime base (Art. 101 CCNL ANAS): the official retribuzione oraria includes minimo tabellare + IIS (contingenza) + RIA + AEP + EDR. The file keeps hourly_base_method=minimo_tabellare without a verified hourly_base_provenance, so the engine derives no hourly base: an overtime event needs the caller's hourly rate, otherwise the run is rejected. Monthly/annual figures unaffected (review of 2026-10-30).
    
    Malattia: 100% mesi 1-12, 50% mesi 13+ — CCNL ANAS 2025-2027 Art. malattia. Modellato con SicknessTier (comporto standard). Il tasso si applica giorno per giorno secondo il mese di malattia (mesi di 30 giorni), anche nei periodi di paga a cavallo di soglia (review of 2026-10-30).
    

## Raw data

The contract file this page is generated from: [`agreement/anas.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/anas.json).

## Usage example

```python
--8<-- "docs/examples/agreement/anas/example.py"
```
