# CCNL Edilizia PMI CONFAPI ANIEM

| | |
|---|---|
| **CNEL code** | `F018` |
| **Sector** | Edilizia |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-04-15 |
| **Workers (est.)** | ~70000 |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFAPI ANIEM
    - FENEAL UIL
    - FILCA CISL
    - FILLEA CGIL

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
| **Last renewal** | 2025-04-15 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-03-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7` | Livello VII — impiegato di 1a categoria Super / Quadro | € 2,325.96 | 2027-03-01 |
| `6` | Livello VI — impiegato di 1a categoria | € 2,093.36 | 2027-03-01 |
| `5` | Livello V — impiegato di 2a categoria | € 1,744.48 | 2027-03-01 |
| `4` | Livello IV — operaio di 4o livello / assistente tecnico | € 1,628.17 | 2027-03-01 |
| `3` | Livello III — operaio specializzato / impiegato di 3a categoria | € 1,551.88 | 2027-03-01 |
| `2` | Livello II — operaio qualificato / impiegato d'ordine | € 1,360.69 | 2027-03-01 |
| `1` | Livello I — manodopera generica | € 1,162.99 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.22 |
| `2` | € 8.22 |
| `3` | € 8.99 |
| `4` | € 9.61 |
| `5` | € 10.46 |
| `6` | € 12.84 |
| `7` | € 13.94 |

## Apprenticeship

**gruppo_4** (type: `percentage`)  
Destination levels: `2`  
percentage: 1.00

**gruppo_3_impiegati_3** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_2_impiegati_4_5** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 1.00

**gruppo_1_impiegati_6_7** (type: `percentage`)  
Destination levels: `6`, `7`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-pmi-confapi-aniem/operai_gruppo_3_track_merged · base_salary · impact unknown · open"
    SIMPLIFICATION: Apprenticeship destination conflicts. Art. G defines 4 operai groups and 3 impiegati bands. Engine tracks use disjoint destination_levels: level '2' -> gruppo_4 (36m); level '3' -> gruppo_3 (48m, ref=L2); levels '4'/'5' -> gruppo_2 (51m, ref=L3); levels '6'/'7' -> gruppo_1 (60m, ref=L3). Level '1' has no apprenticeship track (manual labor). Operai gruppo_3 (also exits at level '2', 48m) not modelled separately.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 2.

    **Remediation:** Model the operai gruppo 3 track (48 months, exit at level 2) separately and select it by track name.

!!! warning "edilizia-pmi-confapi-aniem/apprentice_its_evr_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Apprentice base per Art. G includes ITS and EVR alongside paga_base + contingenza. Engine covers only paga_base + contingenza; apprentice gross is understated where ITS applies.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Add ITS and EVR to the apprentice base of Art. G.

!!! warning "edilizia-pmi-confapi-aniem/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-04-15 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL%20_Aniem_Confapi%20Armonizzato_15042025.pdf) |

??? note "Coverage notes"
    SPLIT MODEL: paga_base (changes each tranche) + contingenza (frozen) + EDR (frozen at 10.33). Tranche 1: 01/04/2025; Tranche 2: 01/03/2027. Source: FILLEA CGIL testo armonizzato 15/04/2025 (Art. 25 and tabelle allegate).
    
    CONGLOBATED CHECK: L1 01/04/2025 total 1611.78 / 173 = 9.317 (non-integer). L4 = 2055.65 / 173 = 11.88 (matches official hourly table). Split model confirmed.
    
    HOURLY DIVISOR: 173, from Art. 25 CCNL: 'dividendo per 173 i valori minimi mensili'. Confirmed by official hourly rate column in FILLEA CGIL salary table.
    
    ITS (Indennita' Territoriale di Settore) not modelled: varies by province/region. National table footnote: 'A questa Tabella occorre aggiungere l'ITS che varia da territorio a territorio'. The national tabular minimum does not include ITS.
    
    CASSA EDILE: for blue-collar workers (levels 1-4), holidays (8.5%) and Christmas bonus (10%) accrue through the Edilcassa system rather than direct employer payment. The engine models the Christmas bonus as a direct 13th month. Consequences: (1) employer_cost_annual underestimates by ~18.5% of gross for blue-collar workers; (2) net_monthly is correct.
    
    ADDITIONAL_MONTHS: 13 monthly payments (gratifica natalizia). Impiegati (Art. 64) additionally receive a premio annuo equal to one monthly salary (14th month). Engine models 13 for all levels as an approximation; the 14th month for impiegati is not modelled.
    
    SENIORITY: Art. 49 lists impiegati scatti biennali by category. Level 1 has no explicit Art. 49 amount; engine uses 8.22 (Impiegati 4a category, same as level 2) as an approximation. For operai (levels 1-4), seniority is governed by the Cassa Edile anzianita' professionale edile (APE) system; engine uses the Art. 49 impiegati amounts as an approximation.
    
    EVR (Elemento Variabile della Retribuzione): conditional, company/territory-specific bonus. Not modelled.
    
    INPS: reuses 2026-edilizia.json (proxy rates, employer_tiers=[], employee_rate=null inherited from F012). Cassa Edile ~18.5% contribution is separate and not included in INPS rates.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/edilizia-pmi-confapi-aniem.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/edilizia-pmi-confapi-aniem.py"
```
