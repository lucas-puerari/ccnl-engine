# CCNL Lavoratori Dipendenti Organizzazioni Sindacali (UNSIC/CONFSAL)

| | |
|---|---|
| **CNEL code** | `V925` |
| **Sector** | Organizzazioni sindacali nazionali e territoriali |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-01-19 |
| **Workers (est.)** | ~7k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - UNSIC
    - CONFSAL
    - ASNALI
    - SNALV CONFSAL
    - FNA CONFSAL
    - CONFIAL
    - FISMIC CONFSAL
    - FAST CONFSAL
    - SNALA CONFSAL
    - FEDER.AGRI.
    - FENALCA INTERNATIONAL

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
| **Last renewal** | 2023-01-19 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello I - Direttore Generale | € 2,788.00 | 2026-01-01 |
| `2` | Livello II - Direttori Nazionali / Coordinatori | € 2,331.75 | 2026-01-01 |
| `3` | Livello III - Responsabili Regionali / Impiegati di concetto | € 2,096.38 | 2026-01-01 |
| `4` | Livello IV - Responsabili Zonali / Operatori servizi | € 1,863.44 | 2026-01-01 |
| `5` | Livello V - Impiegati d'ordine / Addetti | € 1,735.04 | 2026-01-01 |
| `6` | Livello VI - Usciere / Fattorino / Autista / Addetto pulizie | € 1,588.78 | 2026-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 27.88 |
| `2` | € 23.32 |
| `3` | € 20.96 |
| `4` | € 18.63 |
| `5` | € 17.35 |
| `6` | € 15.89 |

## Apprenticeship

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`  
under-level: `1`

**professionalizzante - dest livello 4** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

**professionalizzante - dest livello 5** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ooss-unsic-confsal/salary_2026_from_proxy · base_salary · impact unknown · open"
    SIMPLIFICATION: 2026 salary values (L1=2788.00, L2=2331.75, L3=2096.38, L4=1863.44, L5=1735.04, L6=1588.78) sourced from proxy (kitech.it) for the 2026-2028 renewal. Primary source PDF covers 2023-2025 only.

    **Applies when:** `base_salary` applies; from 2026-01-01.

    **Remediation:** Verify the 2026-2028 salary values against the primary renewal text.

!!! warning "ooss-unsic-confsal/level_5_apprentice_one_level_below · base_salary · impact unknown · open"
    SIMPLIFICATION: dest level 5 apprenticeship: lb=2 is structurally impossible (only 1 level below exists). Modelled as lb=1 for full 36mo duration per Art. 15 cap ('non piu di due livelli').

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 5.

    **Remediation:** Confirm the level 5 apprenticeship classification against Art. 15.

!!! warning "ooss-unsic-confsal/apprentice_seniority · seniority · impact unknown · open"
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
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-01-19 | [↗](https://unsic.it/wp-content/uploads/2023/02/CCNL-OOSS.pdf) |
| — | — | 2026-03-26 | [↗](https://www.kitech.it/) |

??? note "Coverage notes"
    CCNL OO.SS. signed 19/01/2023 by UNSIC/CONFSAL. Valid 01/01/2023-31/12/2025; renewed 26/03/2026 for 01/01/2026-31/12/2028.
    
    Salary model: conglobated. Art. 49 states 'paga base nazionale conglobata'. No split components.
    
    6 levels (1=highest: Direttore Generale, 6=lowest: Usciere/Fattorino). Art. 49 table.
    
    Hourly divisor 170: Art. 49 explicit ('divisore convenzionale 170'). Verified: 2746.80/170=16.16, 2065.40/170=12.15, 1565.30/170=9.21.
    
    Additional months: 14. Art. 52: gratifica natalizia (13ma) + quattordicesima mensilita.
    
    Seniority (Art. 51): triennale (36mo), max 5 scatti, 1% of current tabellare. Amounts stored per tranche.
    
    Apprenticeship (Art. 15): under_classification, max 2 levels below destination. 3 tracks (dest 3,4,5). Duration 36mo each with 18/18 split confirmed from CCNL text.
    
    No dedicated INPS code per contratticcnl.it. Tax sector=terziario applied.
    
    Headcount: 6,968 workers, 830 employers (ADAPT 18 Rapporto CNEL).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/ooss-unsic-confsal.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ooss-unsic-confsal.py"
```
