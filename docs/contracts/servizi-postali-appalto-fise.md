# CCNL Servizi Postali in Appalto (FISE-ARE)

| | |
|---|---|
| **CNEL code** | `K721` |
| **Sector** | Servizi postali in appalto e recapito |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-12-21 |
| **Workers (est.)** | ~1k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FISE-ARE
    - SLC-CGIL
    - SLP-CISL
    - UILPOSTE-UIL

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
| **Last renewal** | 2023-12-21 |
| **Last verified** | — |
| **Latest salary tranche** | 2025-12-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 (Par. 166) | € 1,875.95 | 2025-12-01 |
| `2` | Livello 2 (Par. 139) | € 1,650.74 | 2025-12-01 |
| `3S` | Livello 3 Super (Par. 127) | € 1,549.72 | 2025-12-01 |
| `3` | Livello 3 (Par. 122) | € 1,509.09 | 2025-12-01 |
| `4S` | Livello 4 Super (Par. 116) | € 1,457.90 | 2025-12-01 |
| `4` | Livello 4 (Par. 110) | € 1,409.19 | 2025-12-01 |
| `5` | Livello 5 (Par. 100) | € 1,325.69 | 2025-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

## Apprenticeship

**professionalizzante - dest livello 1** (type: `under_classification`)  
Destination levels: `1`  
under-level: `1`

**professionalizzante - dest livello 2** (type: `under_classification`)  
Destination levels: `2`  
under-level: `2`

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`  
under-level: `2`

**professionalizzante - dest livello 4** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "servizi-postali-appalto-fise/conditional_integrative_allowance · base_salary · impact unknown · open"
    SIMPLIFICATION: indennità integrativa Art. 34 modelled as unconditional fixed allowance. Art. 34 restricts it to companies without second-level bargaining that don't pay other economic treatments verified over 4 years. Kitech totals confirm its inclusion in the national contractual floor.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 34 condition on second-level bargaining with an employer input.

!!! warning "servizi-postali-appalto-fise/level_4s_seniority_amount · seniority · impact unknown · open"
    SIMPLIFICATION: L4S impiegati seniority amount (52.44) sourced from kitech.it proxy; the corresponding cell in the primary source PDF (p.85) is partially obscured by an adhesive note in the scan.

    **Applies when:** `seniority` applies; level in 4S.

    **Remediation:** Confirm the level 4S seniority amount against a legible copy of the primary source.

!!! warning "apprentice_seniority_simplified · seniority · impact unknown · open"
    Apprentices accrue only the CCNL apprentice-specific seniority increment (zero when the CCNL declares none); the increments of the level start after qualification. The run is affected when the apprentice has matured increments and the level amount differs from the apprentice amount.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, whether apprentices accrue the level increments or an amount of their own, model it, then resolve this limitation.

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
    SIMPLIFICATION: dest 5° apprenticeship not modelled — Allegato 10 places dest 5° apprentices at level 5 for the full 24-month duration (zero salary reduction; no structural levels_below > 0 is applicable).

!!! note ""
    SIMPLIFICATION: dest 3S° and dest 4S° apprenticeship not modelled — Allegato 10 names only ordinal destinations 1°-5°; S-level destinations are unaddressed in the accord text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-21 | [↗](https://slp-cisl.it/wp-content/uploads/2025/09/CCNL-SERVIZI-POSTALI-versione-stampa-250624.pdf) |
| — | — | 2023-12-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=K721) |

??? note "Coverage notes"
    CCNL Servizi Postali in Appalto signed 21/12/2023. Salary model: split — base_salary = paga tabellare + contingenza; fixed_allowances = indennità integrativa Art. 34 (frozen Dec 2013) + EDR 10.33. Verified: L1 Dec2025 (1875.95+75.62+10.33)/173=1961.90/173=11.34 EUR/h ✓.
    
    7 levels (1=highest, 5=lowest): 1(Par.166), 2(Par.139), 3S(Par.127), 3(Par.122), 4S(Par.116), 4(Par.110), 5(Par.100). 3 tranches: 01/01/2024, 01/01/2025, 01/12/2025. Allegato 1 (p.84), primary source.
    
    Hourly divisor 173 (Art. 33 explicit, p.50). Additional months: 14 — tredicesima (Art. 37) + quattordicesima (Art. 38).
    
    Seniority Art. 35: dual model. Operai (Art. 35A): single premio after 24mo company service (max=1), amounts frozen at 31/12/1994 tabellare (L2=56.66, L3S=51.71, L3=49.70, L4S=47.24, L4=44.94, L5=40.72). Impiegati (Art. 35B): biennale (cadence=24mo), first scatto after 48mo, max=10 (5.55% biennale capped at 60%), amounts frozen at 2001 reference (L1=71.79, L2=62.62, L3=56.86, L4S=52.44 (kitech proxy), L5=49.40). L1 operai: no seniority. L3S, L4 impiegati: no seniority. Level categories are open, so callers must set Employment.category to operaio or impiegato; with seniority_months and no category the calculation is rejected.
    
    Apprenticeship (Allegato 10, 15/01/2013 accord, p.132-133): under_classification. Dest 1°: first 18mo at 3° (lb=3), next 18mo at 2° (lb=1). Dest 2°: first 18mo at 4° (lb=4), next 18mo at 3° (lb=2). Dest 3°: first 18mo at 5° (lb=3), next 18mo at 4° (lb=2). Dest 4°: whole period at 5° (lb=1). Non-uniform lb due to S levels interspersed.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/servizi-postali-appalto-fise.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/servizi-postali-appalto-fise.py"
```
