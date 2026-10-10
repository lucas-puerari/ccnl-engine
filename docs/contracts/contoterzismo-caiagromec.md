# CCNL Attivita Agromeccaniche (Contoterzismo) CAI Agromec-FAI-FLAI-UILA

| | |
|---|---|
| **CNEL code** | `A051` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-06-18 |
| **Workers (est.)** | ~4k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CAI Agromec
    - FAI-CISL
    - FLAI-CGIL
    - UILA-UIL

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
| **Limits of this contract** | inps_employer |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-06-18 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-06-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | 1° livello | € 2,392.94 | 2027-06-01 |
| `2` | 2° livello | € 2,241.78 | 2027-06-01 |
| `3` | 3° livello | € 2,054.03 | 2027-06-01 |
| `4` | 4° livello | € 1,862.10 | 2027-06-01 |
| `5` | 5° livello | € 1,750.99 | 2027-06-01 |
| `6` | 6° livello | € 1,489.41 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "contoterzismo-caiagromec/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of social_security/contribution/2026/agricoltura.json derived, then remove this note.

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-18 | [↗](https://www.redigo.info/2024/07/02/ccnl-contoterzismo-in-agricoltura-rinnovato-il-quadriennio-2024-2027/) |
| — | — | 2024-06-18 | [↗](https://ilccnl.it/contratto/ccnl/agricoltura---contoterzisti) |
| — | — | 2024-06-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=1) |

??? note "Coverage notes"
    Salary model: paga base nazionale conglobata (contingenza absorbed since 2009 in agriculture sector). Single TimeSeries per level, no separate contingenza or EDR. Back-check: L3 Jun2026 2014.03/169=11.92, L4 1827.82/169=10.82, L5 1720.14/169=10.18 — all match redigo.info hourly rates.
    
    Divisore convenzionale 169 h/month (confirmed: lavoro-economia.it c=1 shows hourly column; cross-checked 3 levels). Daily divisor: 26.
    
    Mensilita supplementari: tredicesima (dicembre) e quattordicesima (giugno). additional_months=14. Source: ilccnl.it fetched page.
    
    4 salary tranches effective: 2024-06-01, 2025-06-01, 2026-06-01, 2027-06-01. Source: redigo.info (primary, all 4 tranches verified); ilccnl.it (Jun2026 cross-check).
    
    Salary floors reflect CCNL national minimums only. kitech.it (CodiceCateg=1) shows values ca. EUR 20/month higher — those are in-assenza-di-contratto-integrativo-territoriale top-ups, not CCNL minimums. redigo.info and ilccnl.it agree on the lower CCNL floor used here.
    
    Seniority: 'premi di continuita professionale' modeled as fixed_allowances with service_months_threshold (60/120/180 months) and months_per_year=1 (annual lump sums: EUR 50/150/180/year). Amounts assumed cumulative (stacking thresholds) per standard CCNL practice; cumulation unverified from public sources. seniority_increments is a schema placeholder (maximum_count=0).
    
    layer_2 out_of_scope: no apprenticeship tracks modeled. The 2024 CCNL text (Art. 13 and Allegati E/F per CAI Agromec contract structure) references apprendistato professionalizzante but no percentage or under-classification table was found in any primary source (ilccnl.it, redigo.info, lavoro-economia.it). If apprenticeship provisions exist, they require the full CCNL PDF to model correctly.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/contoterzismo-caiagromec.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/contoterzismo-caiagromec.py"
```
