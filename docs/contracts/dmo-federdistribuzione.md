# Distribuzione Moderna Organizzata — Federdistribuzione

| | |
|---|---|
| **CNEL code** | `H008` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~460k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federdistribuzione
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| **Limits of this contract** | seniority, territorial_supplement |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2027-02-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Managers (Quadri) | € 2,313.29 | 2027-02-01 |
| `I` | First level | € 2,083.84 | 2027-02-01 |
| `II` | Second level | € 1,802.50 | 2027-02-01 |
| `III` | Third level | € 1,540.66 | 2027-02-01 |
| `IV` | Fourth level | € 1,332.46 | 2027-02-01 |
| `V` | Fifth level | € 1,203.83 | 2027-02-01 |
| `VI` | Sixth level | € 1,080.77 | 2027-02-01 |
| `VII` | Seventh level | € 925.31 | 2027-02-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `I` | € 24.84 |
| `II` | € 22.83 |
| `III` | € 21.95 |
| `IV` | € 20.66 |
| `V` | € 20.30 |
| `VI` | € 19.73 |
| `VII` | € 19.47 |

## Apprenticeship

**standard_II_V** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`, `V`  
under-level: `1`

**standard_VI** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dmo-federdistribuzione/provincial_elements_missing · territorial_supplement · impact yes · open"
    Terzo elemento nazionale (Art. 199): EUR 2.07/month (lire 4,000) for workers in provinces without provincial terzi elementi (Art. 198, frozen since 1973). Modelled as 'edr' fixed allowance for all workers. # SIMPLIFICATION: some provinces have higher provincial elements (second-level bargaining, out of scope).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the provincial terzi elementi of Art. 198 as a territorial supplement.

!!! warning "dmo-federdistribuzione/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-04-23 | [↗](https://www.federdistribuzione.it/wp-content/uploads/2025/01/CCNL-DMO-Testo-Unico-29.09.2025.pdf) |

??? note "Coverage notes"
    Salary tables: 6 tranches from 01/04/2023 through 01/02/2027 per Allegato 11, Testo Unico CCNL DMO 29/09/2025 (Federdistribuzione). 47/48 cells verified arithmetic; L4 01/04/2023 PDF OCR reads '1112.46' but total (1646.68) and contingenza (524.22) prove 1122.46 — consistent with pre-acconto 1092.46 + 30 EUR acconto (Dec 2022 Protocol).
    
    Split model confirmed: total / 168 at L1 = 14.905, L4 = 10.605, L7 = 8.309 — all non-integer. Source: Art. 194 (divisore 168 for 40h/week), Allegato 11.
    
    Contingenza: frozen values from Allegato 11 column. EDR (lire 20,000 = 10.33 EUR) conglobated into contingenza on 01/01/1995 per Art. 190 — no separate EDR allowance modelled.
    
    Indennità di funzione Quadri (Art. 113): EUR 260.76/month for 14 months (cumulative increments: 51.65+77.47+51.65+70.00+10.00=260.77; 0.01 rounding from lire). Allegato 11 shows 260.76.
    
    Indennità di funzione 7° livello: EUR 5.16/month (lire 10,000) in 'altri elementi' column of Allegato 11 for Level VII. Same element and amount as Commercio Confcommercio 'ind_funzione' for livello 7.
    
    Seniority: 10 scatti triennali (Art. 188), amounts from Testo Unico Art. 188 table. valid_from set to 2024-04-23 (renewal date).
    
    Additional months: 14 (tredicesima Art. 204 + quattordicesima Art. 205).
    
    APPRENTICESHIP: sotto-inquadramento per Art. 46 + Art. 57 Testo Unico DMO 29/09/2025. Art. 55: destinazioni ammesse livelli II–VI (I e Q esclusi). Livelli II–V: 36 mesi, 0–18m = 2 livelli sotto dest, 18m+ = 1 livello sotto. Livello VI: 24 mesi, 0–12m = 1 livello sotto (VII), 12m+ = livello VI (dest). Source: Testo Unico Federdistribuzione 29/09/2025 (Allegato apprendistato).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dmo-federdistribuzione.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dmo-federdistribuzione.py"
```
