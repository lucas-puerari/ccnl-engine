# CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)

| | |
|---|---|
| **CNEL code** | `B371` |
| **Sector** | gomma-plastica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federazione Gomma Plastica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2028-12-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — senior manager grade (quadro under L. 190/1985), highest responsibility | € 2,664.67 | 2028-12-01 |
| `A` | A — quadro, highly specialised technical or functional expert | € 2,508.94 | 2028-12-01 |
| `B` | B — technical or administrative manager, high professional grade | € 2,366.94 | 2028-12-01 |
| `C` | C — department head, white-collar employee with operational autonomy | € 2,335.85 | 2028-12-01 |
| `D` | D — team leader, qualified technical/administrative employee | € 2,306.50 | 2028-12-01 |
| `E` | E — highly skilled worker, expert technical employee | € 2,213.42 | 2028-12-01 |
| `F` | F — skilled worker, technical employee (CCNL reference level) | € 2,156.12 | 2028-12-01 |
| `G` | G — qualified worker 2nd category, white-collar employee | € 2,009.25 | 2028-12-01 |
| `H` | H — qualified worker 1st category, clerical staff | € 1,916.08 | 2028-12-01 |
| `I` | I — elementary tasks, simple operations with brief training | € 1,722.59 | 2028-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 20.14 |
| `A` | € 18.59 |
| `B` | € 16.53 |
| `C` | € 16.53 |
| `D` | € 16.53 |
| `E` | € 13.94 |
| `F` | € 13.94 |
| `G` | € 13.43 |
| `H` | € 11.88 |
| `I` | € 10.33 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `G`, `F`, `E`, `D`, `C`, `B`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "gomma-plastica-federazione-gomma-plastica/apprenticeship_period_boundaries · base_salary · impact unknown · open"
    APPRENTICESHIP under_classification (art. apprendistato professionalizzante CCNL Gomma e Plastica; rule from contratticcnl.it: the apprentice cannot be classified more than two levels below the destination). Track 'professionalizzante' for destinations G, F, E, D, C, B: 0-12 months two levels below, 12-24 one level below, then destination. The 12/12 boundaries are an approximation (no public monthly table). H (only one level below exists), I, A and Q are not modelled as destinations.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in B, C, D, E, F, G.

    **Remediation:** Source the monthly apprenticeship table and correct the 12/12 period boundaries.

!!! warning "gomma-plastica-federazione-gomma-plastica/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-gomma-plastica/) |
| — | — | 2025-12-10 | [↗](https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/) |
| — | — | 2026-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM — Trattamento Economico Minimo). All base_salary values incorporate paga base, contingenza, and EDR in a single figure. Evidence: the F/level coefficient ratio is stable to 4 decimal places across all 4 tranches (2023-2026), which is only possible in a fully parametric (conglobated) system. fixed_allowances is empty for all levels except Q.
    
    CONGLOBATED CHECK: coefficient ratios computed as level_value / F_value for all tranches. Q/F=1.2359, A/F=1.1636, B/F=1.0978, C/F=1.0834, D/F=1.0697, E/F=1.0266, G/F=0.9319, H/F=0.8887, I/F=0.7989 — identical across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026. This confirms conglobated model.
    
    TRANCHE DATES 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026 from lexplain.it and kitech.it. Future tranches 01.04.2027, 01.04.2028, 01.12.2028 from the rinnovo 10.12.2025 (ipotesi accordo PDF uniolex.com, confirmed by fiscoetasse.com, paserio.it, edotto.com): F +60, +60, +15. Other levels derived parametrically via the stable coefficients documented in CONGLOBATED CHECK — math verified ±0.01 EUR across all 3 tranches and all 10 levels.
    
    SENIORITY amounts unchanged across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026: the January 2023 rinnovo and December 2025 rinnovo both addressed only TEM (minimi tabellari) and left Art.23 (scatti di anzianità) untouched. Amounts at kitech.it/lavoro-economia.it apply from at least 01.01.2023 onward. Source: rinnovo 10.12.2025 full text (filctemcgil.it); rinnovo Jan 2023 summary (terzomillennio.uil.it); no source reports scatti change in either rinnovo.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Federazione Gomma Plastica is a member of Confindustria; CIGO applicable pursuant to D.Lgs. 148/2015.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Gomma e Plastica Industria.
    
    HOURLY DIVISOR 173 derived from the standard formula (40h/week x 52 / 12 = 173.33 rounded to 173); secondary sources (contratticcnl.it, fiscoetasse.com) confirm the 40h week but the contractual clause was not retrieved directly.
    
    Q LEVEL INDENNITA' DI FUNZIONE 50.00 EUR/month (quadri ex L. 190/1985), cross-verified at April 2025 (lexplain.it total 2473.68 vs contratticcnl.it TEM 2423.68). valid_from set to 2023-01-01 for consistency with the first modelled tranche; not verified whether the amount was already 50 EUR in 2023.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/gomma-plastica-federazione-gomma-plastica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/gomma-plastica-federazione-gomma-plastica.py"
```
