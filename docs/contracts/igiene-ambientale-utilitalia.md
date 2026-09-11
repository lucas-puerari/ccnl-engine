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

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Livello Q — Quadri (dirigenti di secondo livello) | € 3,634.41 | — |
| `A1` | Livello A1 — tecnici e impiegati con responsabilita autonome di primo livello | € 3,314.56 | — |
| `A2s` | Livello A2S — tecnici e impiegati con responsabilita autonome di secondo livello, posizione superiore | € 3,065.21 | — |
| `A2` | Livello A2 — tecnici e impiegati con responsabilita autonome di secondo livello | € 2,920.50 | — |
| `B1s` | Livello B1S — operai e impiegati altamente specializzati di primo livello, posizione superiore | € 2,784.22 | — |
| `B1` | Livello B1 — operai e impiegati altamente specializzati con mansioni di primo livello | € 2,661.29 | — |
| `B2s` | Livello B2S — operai e impiegati altamente specializzati di secondo livello, posizione superiore | € 2,535.56 | — |
| `B2` | Livello B2 — operai e impiegati altamente specializzati con mansioni di secondo livello | € 2,432.73 | — |
| `C1s` | Livello C1S — operai e impiegati specializzati di primo livello, posizione superiore | € 2,332.13 | — |
| `C1` | Livello C1 — operai e impiegati specializzati con mansioni di primo livello | € 2,264.77 | — |
| `C2s` | Livello C2S — operai e impiegati specializzati di secondo livello, posizione superiore | € 2,196.19 | — |
| `C2` | Livello C2 — operai e impiegati specializzati con mansioni di secondo livello | € 2,147.09 | — |
| `D1s` | Livello D1S — operai e impiegati qualificati con mansioni esecutive, posizione superiore | € 2,143.89 | — |
| `D1` | Livello D1 — operai e impiegati qualificati con mansioni esecutive di primo livello | € 1,955.19 | — |
| `D2s` | Livello D2S — operai e impiegati con mansioni di base non qualificate, posizione superiore | € 1,779.25 | — |
| `D2` | Livello D2 — operai e impiegati con mansioni di base non qualificate | € 1,555.36 | — |

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

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    FIRST SALARY PERIOD. The 16-level classification (Q, A1, A2s, A2, B1s, B1, B2s, B2, C1s, C1, C2s, C2, D1s, D1, D2s, D2) took effect on 01/02/2026. The preceding period (01/01/2025-31/01/2026) used a different level structure. Only the post-reclassification system is modelled; queries for as_of dates before 2026-02-01 will return an out-of-range error.

!!! warning ""
    INPS RATES. INDUSTRIA rates from 2026-industria.json used as proxy (3 size tiers: ≤15, ≤50, >50 employees — selected via Employer.num_employees). For K540 (igiene ambientale), the applicable CIGO regime is standard industria (CIGO ordinaria) under D.Lgs. 148/2015; no sector-specific INPS circular found. The CIGO addizionale (0.60% ≤50 employees, 0.90% >50) is event-driven: charged only when hours are actually in CIG integrazione — correctly excluded from the standing monthly rate. Simplification: industria proxy, not a sector-specific file.

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
    
    BILATERAL FUNDS. FASDA healthcare (Fondo Assistenza Sanitaria Dipendenti Aziende di Servizi Ambientali) and Previambiente supplementary pension fund contributions are not modelled.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/igiene-ambientale-utilitalia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/igiene-ambientale-utilitalia.py"
```
