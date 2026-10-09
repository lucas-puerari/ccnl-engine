# CCNL Igiene Ambientale — Servizi Ambientali e di Igiene Urbana

| | |
|---|---|
| **CNEL code** | `K540` |
| **Sector** | servizi ambientali |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-12-09 |
| **Workers (est.)** | ~65k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Utilitalia — Federazione delle Imprese di Acqua, Ambiente, Energia
    - Cisambiente — Confindustria Cisambiente
    - FISE Assoambiente
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Produzione e Lavoro
    - FP-CGIL — Federazione Poteri e Funzioni Pubbliche
    - Fit-CISL — Federazione Italiana Trasporti
    - Uiltrasporti

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
| **Limits of this contract** | inps_employer, pension_fund_contribution, seniority |

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
| **Latest salary tranche** | 2027-12-01 |

### Semplificazioni note

5 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Livello Q — Quadri (dirigenti di secondo livello) | € 3,634.41 | 2027-12-01 |
| `A1` | Livello A1 — tecnici e impiegati con responsabilita autonome di primo livello | € 3,314.56 | 2027-12-01 |
| `A2s` | Livello A2S — tecnici e impiegati con responsabilita autonome di secondo livello, posizione superiore | € 3,065.21 | 2027-12-01 |
| `A2` | Livello A2 — tecnici e impiegati con responsabilita autonome di secondo livello | € 2,920.50 | 2027-12-01 |
| `B1s` | Livello B1S — operai e impiegati altamente specializzati di primo livello, posizione superiore | € 2,784.22 | 2027-12-01 |
| `B1` | Livello B1 — operai e impiegati altamente specializzati con mansioni di primo livello | € 2,661.29 | 2027-12-01 |
| `B2s` | Livello B2S — operai e impiegati altamente specializzati di secondo livello, posizione superiore | € 2,535.56 | 2027-12-01 |
| `B2` | Livello B2 — operai e impiegati altamente specializzati con mansioni di secondo livello | € 2,432.73 | 2027-12-01 |
| `C1s` | Livello C1S — operai e impiegati specializzati di primo livello, posizione superiore | € 2,332.13 | 2027-12-01 |
| `C1` | Livello C1 — operai e impiegati specializzati con mansioni di primo livello | € 2,264.77 | 2027-12-01 |
| `C2s` | Livello C2S — operai e impiegati specializzati di secondo livello, posizione superiore | € 2,196.19 | 2027-12-01 |
| `C2` | Livello C2 — operai e impiegati specializzati con mansioni di secondo livello | € 2,147.09 | 2027-12-01 |
| `D1s` | Livello D1S — operai e impiegati qualificati con mansioni esecutive, posizione superiore | € 2,143.89 | 2027-12-01 |
| `D1` | Livello D1 — operai e impiegati qualificati con mansioni esecutive di primo livello | € 1,955.19 | 2027-12-01 |
| `D2s` | Livello D2S — operai e impiegati con mansioni di base non qualificate, posizione superiore | € 1,779.25 | 2027-12-01 |
| `D2` | Livello D2 — operai e impiegati con mansioni di base non qualificate | € 1,555.36 | 2027-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 39.17 |
| `A1` | € 29.05 |
| `A2s` | € 26.04 |
| `A2` | € 26.04 |
| `B1s` | € 24.65 |
| `B1` | € 24.65 |
| `B2s` | € 21.83 |
| `B2` | € 21.83 |
| `C1s` | € 20.92 |
| `C1` | € 20.92 |
| `C2s` | € 19.11 |
| `C2` | € 19.11 |
| `D1s` | € 17.66 |
| `D1` | € 17.66 |
| `D2s` | € 15.24 |
| `D2` | € 15.24 |

## Apprenticeship

**30m-80-90** (type: `percentage`)  
Destination levels: `D2`, `D1`  
percentage: 0.90

**30m-75-85-90** (type: `percentage`)  
Destination levels: `C2`  
percentage: 0.90

**36m-85-90-95** (type: `percentage`)  
Destination levels: `C1`, `B2`, `B1`, `A2`, `A1`, `Q`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "igiene-ambientale-utilitalia/industria_rates_proxy · inps_employer · impact unknown · open"
    INPS RATES. INDUSTRIA rates from 2026-industria.json used as proxy (3 size tiers: ≤15, ≤50, >50 employees — selected via Employer.num_employees). For K540 (igiene ambientale), the applicable CIGO regime is standard industria (CIGO ordinaria) under D.Lgs. 148/2015; no sector-specific INPS circular found. The CIGO addizionale (0.60% ≤50 employees, 0.90% >50) is event-driven: charged only when hours are actually in CIG integrazione — correctly excluded from the standing monthly rate. Simplification: industria proxy, not a sector-specific file.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS rates of igiene ambientale against a sector-specific circular.

!!! warning "igiene-ambientale-utilitalia/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "igiene-ambientale-utilitalia/fund_paid_month · pension_fund_contribution · impact yes · open"
    Previambiente is due on the pay of the month (art. 65 c. 8): none for a month without pay, and 'commisurato alla retribuzione corrisposta' for a month with a paid absence, a rule the engine does not compute. A month paid in part (an unpaid absence, sickness, a partial month) keeps the full contributions of an enrolled worker.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source how the contributions are proportioned to the pay of a month paid in part, model it, then remove this note.

!!! warning "igiene-ambientale-utilitalia/contractual_fund_partial · pension_fund_contribution · impact unknown · open"
    The Previambiente contractual contribution (5 EUR, 15 EUR for a worker not enrolled voluntarily) is owed in full on a partly employed month; the CCNL states no rule for it.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source the rule of art. 65 for a partly employed month, model it, then remove this note.

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

### Without monetary impact

!!! note ""
    FIRST SALARY PERIOD. The 16-level classification (Q, A1, A2s, A2, B1s, B1, B2s, B2, C1s, C1, C2s, C2, D1s, D1, D2s, D2) took effect on 01/02/2026. The preceding period (01/01/2025-31/01/2026) used a different level structure. Only the post-reclassification system is modelled; queries for as_of dates before 2026-02-01 will return an out-of-range error.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-09 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=551) |
| — | — | 2025-12-09 | [↗](https://www.leggeinchiaro.it/ccnl/K540) |
| — | — | 2025-12-09 | [↗](https://www.wolterskluwer.com/it-it/solutions/oneline-lavoro) |

??? note "Coverage notes"
    CONGLOBATED SALARY. Salary amounts are modelled as a single conglobated figure (paga base parametrale inclusive of contingenza). No official hourly-rate column is published for K540 by the available sources; lavoro-economia.it returns a single Minimo column (not split Base/Contingenza as it does for contracts with split components). The conglobated model is consistent with the source format.
    
    APPRENTICESHIP OLD-TO-NEW LEVEL MAPPING. Art. 14 specifies tracks by old classification codes (1B-8, Q). New 16-level codes are mapped by parametric order: 1B to D2/D2s, 2B to D1/D1s, 3B to C2/C2s, 4B to C1/C1s, 5B to B2/B2s, 6B to B1/B1s, 7B to A2/A2s, 8 to A1, Q to Q. Three tracks are modelled with the exact periods and durations from the contract table.
    
    APPRENTICESHIP PERCENTAGE BASE. Art. 14 punto 8 (CCNL K540 testo consolidato 09/12/2025, fonte: utroppitu.eu) dispone che le indennità ex Art. 32 lett. D (indennità integrativa EUR 50.00) siano corrisposte per intero dal 1° periodo di formazione — pagamento a valore pieno, non soggetto alla percentuale. L'EDR (EUR 10.33, Art. 27 c.4 lett. d, Accordo interconfederale 31/07/1992) non è citato in Art. 14; per sua natura di elemento fisso interconfederale è trattato come esente dalla percentuale. Entrambi modellati con apprenticeship_pct_relevant=false.
    
    BILATERAL FUNDS. FASDA healthcare (Fondo Assistenza Sanitaria Dipendenti Aziende di Servizi Ambientali) contributions are not modelled. Previambiente is (art. 65 lett. A, with the TFR alone of c. 12); the conversion of the scatti into fund contributions of lett. A) bis, an option of the new hires is not.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/igiene-ambientale-utilitalia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/igiene-ambientale-utilitalia.py"
```
