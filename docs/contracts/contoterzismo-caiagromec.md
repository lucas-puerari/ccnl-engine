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
| **Last renewal** | 2024-06-18 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-06-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

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
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/contoterzismo-caiagromec.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/contoterzismo-caiagromec.py"
```
