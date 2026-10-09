# CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)

| | |
|---|---|
| **CNEL code** | `J121` |
| **Sector** | assicurazioni |
| **Tax sector** | `credito` |
| **Last renewal** | 2026-05-13 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIA
    - FIRST-CISL
    - FISAC-CGIL
    - FNA
    - SNFIA
    - UILCA

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
| **Limits of this contract** | base_salary, inps_employer, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-05-13 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

3 semplificazioni documentate. 1 feature mancanti.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L7` | 7° livello — Funzionario | € 3,112.27 | 2028-01-01 |
| `L6` | 6° livello — Quadro | € 2,629.37 | 2028-01-01 |
| `L5` | 5° livello — Impiegato | € 2,463.96 | 2028-01-01 |
| `L4` | 4° livello — Impiegato | € 2,324.66 | 2028-01-01 |
| `L3` | 3° livello — Impiegato | € 2,130.75 | 2028-01-01 |
| `L2` | 2° livello — Impiegato | € 1,946.58 | 2028-01-01 |
| `L1` | 1° livello — Impiegato | € 1,846.38 | 2028-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 11 increments

| Level | Increment (monthly) |
|---|---:|
| `L7` | € 102.08 |
| `L6` | € 81.77 |
| `L5` | € 76.63 |
| `L4` | € 72.30 |
| `L3` | € 66.27 |
| `L2` | € 60.54 |
| `L1` | € 57.42 |

## Apprenticeship

**area_c_l3** (type: `under_classification`)  
Destination levels: `L3`  
under-level: `1`

**area_b_l4** (type: `under_classification`)  
Destination levels: `L4`  
under-level: `1`

**area_b_l5** (type: `under_classification`)  
Destination levels: `L5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "assicurazioni-ania/seniority_modal_class_difference · seniority · impact yes · open"
    Seniority increment = modal per-class difference in the 1/14 monthly table (Allegato 2/B); classes above CL01 may differ from the official table by ±0.02. Source: Allegato 2/B, Rinnovo 13/05/2026.

    **Applies when:** `seniority` applies.

    **Remediation:** Replace the modal per-class difference with the official Allegato 2/B amounts per class.

!!! warning "assicurazioni-ania/inps_credit_rate_unverified · inps_employer · impact unknown · open"
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); reuses 2026-credito.json. Verify against the annual INPS circular.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the 26.76% employer rate against the annual INPS circular for the credit and insurance sector.

!!! warning "assicurazioni-ania/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-05-13 | [↗](https://www.first-cisl.it/) |
| — | — | — | [↗](https://www.contratticcnl.it/) |

??? note "Coverage notes"
    Covers personale amministrativo assunto dal 18/12/1999 (Allegato 2/B — tabella omnicomprensiva). Pre-1999 hires (Allegato 2/A) are out of scope.
    
    First tranche decorrenza 01/01/2026 is retroactive; CCNL signed 13/05/2026. Arretrati January–July 2026 paid in July 2026 (Allegato 7). Period start is 2026-01-01 in the engine.
    
    Additional months = 14 (tredicesima + quattordicesima). Monthly amounts are 1/14 of annual retribuzione. Source: Allegato 2/B header, FirstCISL PDF rinnovo 13/05/2026.
    
    Seniority: cl 1 = anni 1-4 (48 months, quadriennale); cl 2 onward = 3 years each (36 months, triennale). Source: Art. 113 CCNL + Allegato 2/B class table.
    
    L7 maximum seniority class is CL08 (anni 23-25); L1-L6 reach CL12 (oltre 34 anni). maximum_count_by_level overrides L7 to 7 advances.
    
    Hourly divisor 160 (37h/week). Source: ilccnl.it, confirmed from Art. orario di lavoro CCNL ANIA.
    
    Seniority increment amounts vary across tranches (e.g. L4: 67.51 → 70.17 → 72.30). Represented exactly via TimeSeries in amount_by_level.
    
    Indennità profilo J) 4° livello (Allegato 2/E) — modelled as fixed_allowance IND_PROFILO_J on L4 with role 'profilo_j'. Amounts: €57.26/mese dal 01/01/2026, €59.51 dal 01/01/2027, €61.32 dal 01/01/2028. Pass roles={'profilo_j'} in Scenario to include it.
    
    Indennità economica 6° livello quadro (Allegato 2/F) — modelled as fixed_allowance IND_QUADRO_6 on L6 with role 'quadro_6'. Amount: €74.09/mese dal 01/01/2026. Pass roles={'quadro_6'} in Scenario to include it.
    
    Salary tables: FirstCISL Gruppo Unipol, Allegato 2/B — Tabella omnicomprensiva post-1999, decorrenza 01/01/2026, 01/01/2027, 01/01/2028.
    
    Apprenticeship: Art. 5, Allegato 18 (Accordo apprendistato professionalizzante), CCNL testo 2017/2018, confirmed applicable post-rinnovo 2026.
    
    Class cadence: Art. 113 CCNL + column 'Anni serv.' Allegato 2/B.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/assicurazioni-ania.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/assicurazioni-ania.py"
```
