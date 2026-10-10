# CCNL Autorimesse, Noleggio Automezzi e Parcheggi (ANIASA)

| | |
|---|---|
| **CNEL code** | `IC35` |
| **Sector** | Autorimesse e noleggio automezzi |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-12-09 |
| **Workers (est.)** | ~41k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIASA
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| **Limits of this contract** | base_salary, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-12-09 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-11-01 |

### Semplificazioni note

5 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Livello Q1 (Quadro di primo livello) | € 2,319.11 | 2027-11-01 |
| `Q2` | Livello Q2 (Quadro di secondo livello) | € 2,319.11 | 2027-11-01 |
| `A1` | Livello A1 | € 2,319.11 | 2027-11-01 |
| `A2` | Livello A2 | € 2,183.36 | 2027-11-01 |
| `B1` | Livello B1 | € 1,991.05 | 2027-11-01 |
| `B2` | Livello B2 | € 1,900.55 | 2027-11-01 |
| `B3` | Livello B3 | € 1,821.35 | 2027-11-01 |
| `C1` | Livello C1 | € 1,753.48 | 2027-11-01 |
| `C2` | Livello C2 | € 1,561.16 | 2027-11-01 |
| `C3` | Livello C3 | € 1,448.04 | 2027-11-01 |
| `C4` | Livello C4 | € 1,131.27 | 2027-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 9 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 33.10 |
| `Q2` | € 33.10 |
| `A1` | € 33.10 |
| `A2` | € 32.19 |
| `B1` | € 30.36 |
| `B2` | € 29.57 |
| `B3` | € 29.39 |
| `C1` | € 29.23 |
| `C2` | € 27.17 |
| `C3` | € 26.61 |
| `C4` | € 25.35 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `Q1`, `Q2`, `A1`, `A2`, `B1`, `B2`, `B3`, `C1`, `C2`, `C3`, `C4`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "autorimesse-ic35/apprenticeship_percentages_2019 · base_salary · impact unknown · open"
    SIMPLIFICATION: Apprenticeship article numbers from 2019 CCNL may have changed in the current consolidated text (Art. numbering in 2025 verbale differs from 2019 PDF). The 85/90/95 percentage structure is from the 2019 source and is assumed unchanged.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm the 85/90/95% apprenticeship percentages against the current consolidated text.

!!! warning "autorimesse-ic35/apprentice_seniority · seniority · impact unknown · open"
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
    SIMPLIFICATION: Sezione Appalti (Art. 81-89) excluded. The appalto sub-section defines a separate A1-SA to C4-SA level ladder with different tranche dates and amounts, for companies doing washing/shuttling/car prep on behalf of rental firms. Not modeled: out of scope for the main contract coverage.

!!! note ""
    SIMPLIFICATION: Ticket restaurant excluded. Art. 44/84 provides 8.00 EUR/day (from 01/01/2023), rising to 10.00 EUR/day from 01/04/2027, conditional on >= 5 hours worked. Per-day and conditional: not representable as a monthly fixed allowance.

!!! note ""
    SIMPLIFICATION: Hourly divisor 173 applies to standard 40h/week staff. The 2019 CCNL notes 182 (autisti/drivers) and 191 (custodi/security) in specific roles. Only 173 modeled here: dominant case. Verify per-role divisor for drivers and security classifications.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-09 | [↗](https://www.filtcgil.it/images/Contratti/Mobilita/ic35-verbale-accordo-09122025.pdf) |
| — | — | 2019-10-23 | [↗](https://www.comuneportofinomare.it/wp-content/uploads/CCNL-Autorimesse.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione tabellare (Allegato 1 of 2025-12-09 verbale); fixed_allowances = CONTINGENZA (per-level, frozen) + EDR (10.33 all levels, frozen since Protocollo Intesa 1992) + EAR (per-level, frozen; Art. 41 vigente CCNL; labeled 'E.A.S. CCNL 23/10/2019' in Allegato 1).
    
    Hourly divisor 173 confirmed from 2019 CCNL primary source. Cross-check: 40h/week x 52 / 12 = 173.33, consistent with 173.
    
    Additional months: 14. The 2025-12-09 verbale page 5 explicitly states 'tredicesima, la quattordicesima mensilita' for fixed-term workers, confirming both for all workers.
    
    Q1, Q2, A1 share parametro 205 and identical paga base and contingenza per Allegato 1. Allegato 1 gives no salary basis for ordering among the three; order Q1 > Q2 > A1 is conventional.
    
    Seniority: biennial (cadence_months=24), max 9 tranches from 2019 CCNL primary source. No seniority modifications found in the 2025 renewal text reviewed; amounts treated as unchanged (absence of evidence, not positive confirmation).
    
    Apprenticeship: percentage type, 85/90/95 percent by year of contract. Source: 2019 CCNL primary source. The 2025 renewal does not address apprenticeship provisions (absence of evidence, not positive confirmation).
    
    Source status: the 2025-12-09 document is a signed 'ipotesi di accordo' (conditional agreement). OO.SS. were to dissolve the reserve by 31/01/2026. As of 2026-09-05 the January 2026 tranches are in effect per public reporting; formal scioglimento not independently verified. Source is a signatory union PDF and sufficient as primary source.
    
    Headcount: 41,438 workers (contratticcnl.it, CNEL/INPS archive, IC35, 2025).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/autorimesse-ic35.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autorimesse-ic35.py"
```
