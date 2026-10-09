# CCNL Istituzioni Formative Private (Scuole Private Religiose) — AGIDAE

| | |
|---|---|
| **CNEL code** | `T241` |
| **Sector** | istruzione privata |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~50k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGIDAE
    - FLC-CGIL
    - CISL-Scuola
    - UIL-Scuola

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
| **Limits of this contract** | — |

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
| **Latest salary tranche** | 2027-12-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L6` | Livello 6 — Personale direttivo (presidi, coordinatori didattici, direttori amministrativi) | € 2,205.27 | 2027-12-01 |
| `L5` | Livello 5 — Personale docente scuola secondaria, psicologi, psicoterapeuti, responsabili CED e amministrativi senior | € 1,987.80 | 2027-12-01 |
| `L4` | Livello 4 — Personale docente scuola infanzia/primaria, educatrici, assistenti sociali e sanitari, fisioterapisti, logopedisti | € 1,896.82 | 2027-12-01 |
| `L3` | Livello 3 — Personale amministrativo e tecnico specializzato (segretari, addetti amministrativi, capo-cuochi, capi-sala con diploma) | € 1,838.95 | 2027-12-01 |
| `L2` | Livello 2 — Personale tecnico-ausiliario (tecnici caldaie, autisti, centralinisti, cuochi, guardarobieri, camerieri specializzati) | € 1,784.67 | 2027-12-01 |
| `L1` | Livello 1 — Personale ausiliario non specializzato (addetti pulizie, bidelli, portieri, personale di fatica, accompagnatori) | € 1,731.18 | 2027-12-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `L1` | € 0.00 |
| `L2` | € 0.00 |
| `L3` | € 0.00 |
| `L4` | € 0.00 |
| `L5` | € 0.00 |
| `L6` | € 0.00 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    APPRENTICESHIP (Layer 2): apprendistato professionalizzante not modelled. Governed by Allegato 4 of the CCNL (Art. 25). Allegato 4 is not publicly accessible. Part-time and fixed-term (NASpI addizionale) function via generic engine rules without per-contract data. Layer 2 is therefore partial: apprenticeship gap is the only missing component.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-03 | [↗](https://www.terrazzini.it/wp-content/uploads/14bis-2024.pdf) |
| — | — | 2024-07-03 | [↗](https://www.terrazzini.it/wp-content/uploads/19bis-2026.pdf) |
| — | — | 2024-07-03 | [↗](https://ilccnl.it/ccnl/scuole-private-religiose/scuole-private-religiose---agidae-dal-010794) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (retribuzione tabellare comprensiva dell'indennità di contingenza maturata al 30/11/1991, per Art. 29 CCNL 2024). All base_salary values are the conglobated tabular minimums. Contingenza and EDR are fully absorbed. Source: Terrazzini & Partners circular 14bis/2024 (tranches 01/09/2024 and 01/09/2025) and circular 19bis/2026 (tranches 01/09/2026 through 01/12/2027).
    
    TRANCHE DATES: six tranches — 01/09/2024, 01/09/2025, 01/09/2026, 01/01/2027, 01/09/2027, 01/12/2027. CCNL signed 03/07/2024; economic validity 01/01/2024–31/12/2025 (first biennium), second biennium 01/01/2026–31/12/2027 signed 19/05/2026. No arrears for the 01/01/2024–31/08/2024 gap. First modelled period starts at the first salary tranche 01/09/2024.
    
    HOURLY DIVISOR: 164, derived from Art. 49 CCNL (38h/week for non-teaching staff at all levels). Formula: 38h/week × 52/12 = 164.67, truncated to 164 per Italian payroll convention. Source: ilccnl.it (aggregator); confirmed by Art. 49 working-hours article in the CCNL normative text (PDF page 29–30).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Confirmed by Art. 23.6 CCNL ('Al lavoratore assunto con contratto a tempo determinato spettano le ferie e la 13.ma mensilità, il T.F.R. e ogni altro trattamento in atto').
    
    SENIORITY: frozen at 31/12/2005. Art. 29 clause 1 of the CCNL 2024 lists 'salario di anzianità maturato al 31/12/2005' as a retributive element. Art. 32 governs this frozen amount. No new scatti di anzianità accrue after 2005. The current progression mechanism is POC (Progressione Orizzontale di Carriera), calculated as 100% of the 3-year average of PAP productivity awards (Art. 38, in force from 31/08/2024), which is merit-conditioned and excluded from Layer 1. Maximum_count set to 0; amount_by_level set to 0.00 EUR for all levels. Cadence_months set to 1 (minimum legal value; maximum_count=0 so no scatti ever apply; historical quinquennial cadence noted here only).
    
    INPS: reuses 2026-terziario.json (TERZIARIO sector). Private religious schools are private-sector employers; employer INPS classification follows the general terziario sector consistent with other private educational and social institutions (cf. UNEBA T141 which uses the same sector).
    
    HOURLY RATE — TEACHING STAFF: hourly_divisor=164 (38h/week) applies to ATA/non-teaching staff. L4 docenti (scuola infanzia/primaria) have 24h/week; L5 docenti (scuola secondaria) have 18–22h/week; L6 (presidi) differ. The engine hourly_rate for L4, L5, L6 is incorrect for the teaching components; this is a structural engine limitation (single divisor per contract). Base monthly salary and all annual financial figures (gross, net, INPS, TFR, IRPEF) are unaffected.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/scuole-private-agidae.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-private-agidae.py"
```
