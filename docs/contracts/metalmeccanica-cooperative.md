# CCNL Metalmeccanica - Cooperative

| | |
|---|---|
| **CNEL code** | `C016` |
| **Sector** | metalmeccanico cooperativo |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGI Produzione e Lavoro
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

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
| **Latest salary tranche** | 2028-06-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A1 — quadro superiore, massima responsabilita gestionale | € 3,177.92 | 2028-06-01 |
| `B3` | Livello B3 — quadro intermedio, caposquadra o coordinatore di gruppo | € 2,883.46 | 2028-06-01 |
| `B2` | Livello B2 — specialista senior o responsabile di funzione | € 2,651.95 | 2028-06-01 |
| `B1` | Livello B1 — specialista o tecnico con responsabilita di progetto | € 2,471.90 | 2028-06-01 |
| `C3` | Livello C3 — tecnico o impiegato di concetto con autonomia operativa | € 2,306.18 | 2028-06-01 |
| `C2` | Livello C2 — operatore polivalente, mansioni di concetto | € 2,153.36 | 2028-06-01 |
| `C1` | Livello C1 — operatore specializzato, mansioni tecnico-pratiche | € 2,108.77 | 2028-06-01 |
| `D2` | Livello D2 — operatore qualificato, mansioni esecutive | € 2,064.18 | 2028-06-01 |
| `D1` | Livello D1 — operatore comune, mansioni semplici e ripetitive | € 1,861.42 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.90 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 45.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanica-cooperative/apprenticeship_from_federmeccanica · base_salary · impact unknown · open"
    APPRENTICESHIP: percentages (85/90/95% over 36 months) modelled as C011 Federmeccanica (accordo 20/04/2021). No independent C016-specific source found in 2025 renewal documentation. Checked: ecnews.it (renewal article), dottrinalavoro.it, ilccnl.it (two URL paths), kitech.it CodiceCateg=48. Destination levels D2-B3 mirror C011; D1 and A1 excluded as in C011.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm the apprenticeship percentages against a C016-specific source.

!!! warning "metalmeccanica-cooperative/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-07-22 | [↗](https://geps.it/rinnovo-ccnl-metalmeccanica-cooperative-2025-2028-10377/) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=48) |
| — | — | 2025-07-22 | [↗](https://www.fiom-cgil.it/net/cooperative/trattativa-coop/11211-ccnl-cooperative-incrementi-salariali-e-nuovi-minimi-retributivi) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2025-07-22 by Legacoop Produzione e Servizi, Confcooperative Lavoro e Servizi, AGI Produzione e Lavoro with FIM-CISL, FIOM-CGIL and UILM-UIL. Validity 17/06/2025-30/06/2028. First tranche retroactive to 2025-06-01.
    
    CONGLOBATED MINIMUMS: base_salary values are the consolidated 'minimi contrattuali', incorporating all salary components (paga base, contingenza, EDR) into a single figure, consistent with the metalmeccanici industry practice adopted since 1993. No separate contingenza or EDR column appears in any source table.
    
    FIXED ALLOWANCES: A1 (+180 EUR indennita di funzione) and B3 (+120 EUR indennita di funzione) are paid in addition to base_salary, per kitech.it (CodiceCateg=48), which lists them as separate columns. C011 (Federmeccanica) omits these from its JSON; C016 models them explicitly for accuracy.
    
    SENIORITY: biennali scatti (cadence 24 months), maximum 5 per level. Amounts per level confirmed on kitech.it CodiceCateg=48.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). No quattordicesima in any source. Consistent with C011 federmeccanica structure.
    
    HOURLY DIVISOR: 173 h/month (40 h/week standard, same as C011). Confirmed on kitech.it.
    
    INPS: employer rates from 2026-industria.json (same tax sector as C011). Cooperative employers may have different INPS addizionale rates; this is a SIMPLIFICATION — verify against INPS circular for cooperative sector if precise employer cost is critical.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanica-cooperative.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanica-cooperative.py"
```
