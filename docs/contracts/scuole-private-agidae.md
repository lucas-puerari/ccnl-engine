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

[← Contracts index](index.md)

??? note "Signatories"
    - AGIDAE
    - FLC-CGIL
    - CISL-Scuola
    - UIL-Scuola

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ⚠️ partial |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L6` | Livello 6 — Personale direttivo (presidi, coordinatori didattici, direttori amministrativi) | € 2,205.27 | — |
| `L5` | Livello 5 — Personale docente scuola secondaria, psicologi, psicoterapeuti, responsabili CED e amministrativi senior | € 1,987.80 | — |
| `L4` | Livello 4 — Personale docente scuola infanzia/primaria, educatrici, assistenti sociali e sanitari, fisioterapisti, logopedisti | € 1,896.82 | — |
| `L3` | Livello 3 — Personale amministrativo e tecnico specializzato (segretari, addetti amministrativi, capo-cuochi, capi-sala con diploma) | € 1,838.95 | — |
| `L2` | Livello 2 — Personale tecnico-ausiliario (tecnici caldaie, autisti, centralinisti, cuochi, guardarobieri, camerieri specializzati) | € 1,784.67 | — |
| `L1` | Livello 1 — Personale ausiliario non specializzato (addetti pulizie, bidelli, portieri, personale di fatica, accompagnatori) | € 1,731.18 | — |

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

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    HOURLY RATE — TEACHING STAFF: hourly_divisor=164 (38h/week) applies only to ATA/non-teaching staff. L4 docenti (scuola infanzia/primaria) have 24h/week contracted hours; L5 docenti (scuola secondaria) have 18–22h/week; L6 (presidi) contractual duties also differ. hourly_rate computed by the engine for L4, L5, and the docenza component of L6 is therefore incorrect for those roles. Base monthly salary and all annual figures are unaffected.

!!! warning ""
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
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/scuole-private-agidae.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-private-agidae.py"
```
