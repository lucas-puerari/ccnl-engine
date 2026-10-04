# CCNL Area Comunicazione — Artigianato

| | |
|---|---|
| **CNEL code** | `G016` |
| **Sector** | comunicazione grafica editoria stampa artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-11-18 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Comunicazione e Terziario Avanzato
    - Confartigianato Comunicazione
    - Casartigiani
    - CLAAI
    - SLC-CGIL
    - FISTEL-CISL
    - UILCOM-UIL

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
| **Limits of this contract** | base_salary, worker_category |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-11-18 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-11-01 |

### Semplificazioni note

5 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1A` | Level 1A — senior manager / department head (+ function allowance EUR 51.65) | € 2,546.29 | 2026-11-01 |
| `1B` | Level 1B — intermediate manager / executive employee | € 2,264.27 | 2026-11-01 |
| `2` | Level 2 — technician / senior white-collar employee | € 2,124.16 | 2026-11-01 |
| `3` | Level 3 — highly specialised worker / white-collar employee | € 1,992.23 | 2026-11-01 |
| `4` | Level 4 — higher-grade specialised worker | € 1,848.56 | 2026-11-01 |
| `5bis` | Level 5 BIS — specialised worker (intermediate between 5 and 4) | € 1,690.94 | 2026-11-01 |
| `5` | Level 5 — qualified worker | € 1,616.72 | 2026-11-01 |
| `6` | Level 6 — common worker, assigned to routine duties | € 1,522.42 | 2026-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1A` | € 16.01 |
| `1B` | € 16.01 |
| `2` | € 14.20 |
| `3` | € 13.43 |
| `4` | € 12.65 |
| `5bis` | € 11.88 |
| `5` | € 11.36 |
| `6` | € 10.33 |

## Apprenticeship

**operai_tecnici** (type: `percentage`)  
Destination levels: `1A`, `1B`, `2`, `3`, `4`, `5bis`, `5`, `6`  
percentage: 1.00

**amministrativi** (type: `percentage`)  
Destination levels: `1A`, `1B`, `2`, `3`, `4`, `5bis`, `5`, `6`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "comunicazione-artigianato-confartigianato/pmi_non_artigiane_tables · base_salary · impact yes · open"
    Only aziende artigiane salary tables modelled. PMI non-artigiane tables (Art. 4, with EUR 207 total increase vs EUR 200 for artigiane, difference of EUR 7 in the Nov 2026 tranche) are not modelled. Applies to a small minority of firms covered by this CCNL.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Art. 4 PMI non-artigiane salary tables and a request field to select them.

!!! warning "comunicazione-artigianato-confartigianato/switchboard_apprenticeship_duration · base_salary · impact yes · open"
    Centraliniste (switchboard operators) have a 2-year apprenticeship track per the 2024 rinnovo. Modelled as the general 3-year amministrativi track (overstates duration by 1 year for that role).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 2-year apprenticeship track for centraliniste.

!!! warning "comunicazione-artigianato-confartigianato/level_category_not_declared · worker_category · impact unknown · open"
    LEVEL CATEGORY: all levels left null. Multiple levels map to both operai and impiegati roles — a genuine one-to-many mapping the schema cannot represent as a single category value.

    **Applies when:** `worker_category` applies.

    **Remediation:** Declare the worker category in the request; the levels map to both operai and impiegati.

!!! warning "comunicazione-artigianato-confartigianato/function_allowance_constant · base_salary · impact unknown · open"
    Level 1A indennita di funzione EUR 51.65 assumed constant across all four tranches (Dec 2024 through Nov 2026+). Kitech.it only shows the Mar 2026 value; no primary source confirms the amount in Dec 2024 or Jul 2025. Difference is likely zero (function allowances are rarely changed in salary renewals) but not verified.

    **Applies when:** `base_salary` applies; level in 1A; before 2026-03-01.

    **Remediation:** Confirm the level 1A function allowance amount for the December 2024 and July 2025 tranches.

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
    Both apprenticeship tracks (operai_tecnici and amministrativi) are assigned to all 8 destination levels. In practice, the CCNL differentiates by job role, not only by destination level. Firms must select the correct track by role type.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-11-18 | [↗](https://www.redigo.info/ccnl/comunicazione-artigianato) |
| — | — | 2024-11-18 | [↗](https://www.kitech.it/ccnl/comunicazione-artigianato) |
| — | — | 2024-11-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=155) |
| — | — | 2024-11-18 | [↗](https://farecontrattazione.adapt.it/per-una-storia-della-contrattazione-collettiva-in-italia-247-il-nuovo-ccnl-artigianato-area-comunicazione-un-rinnovo-contrattuale-al-passo-con-i-tempi/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Confirmed: ilccnl.it shows contingenza=0.00 for all levels. Back-calculation at Jul 2025: livello 4=1763.56/173=10.194 EUR/h, livello 1B=2160.15/173=12.487 EUR/h, livello 6=1452.42/173=8.394 EUR/h — all values divide to proportional hourly rates consistent with divisor 173, confirming conglobated model.
    
    CNEL CODE: G016 confirmed from kitech.it and ADAPT farecontrattazione.it.
    
    TRANCHE DATES: four tranches — 2024-12-01 (from Nov 2024 verbale integrativo), 2025-07-01, 2026-03-01, 2026-11-01. Source: redigo.info. Cross-validated Mar 2026 values against kitech.it.
    
    HOURLY DIVISOR: 173. Source: ilccnl.it explicit '173.00 ore'. Cross-validated via back-calculation across 3 levels (see conglobated check above).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it ('una mensilita globale di fatto'). No quattordicesima.
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level EUR amounts from two independent aggregators (kitech.it, lavoro-economia.it): 1A=16.01, 1B=16.01, 2=14.20, 3=13.43, 4=12.65, 5bis=11.88, 5=11.36, 6=10.33. Cadence confirmed '5 aumenti biennali' from lavoro-economia.it. SIMPLIFICATION: primary source (CCNL PDF or official signatory site) not fetched; amounts not disputed by the 2024 rinnovo analysis (informaimpresa.it mentions only the NEW EUR 10 apprentice scatto, not a change to permanent scatti).
    
    APPRENTICE SENIORITY: EUR 10.00 from 2025-01-01. New clause introduced by Nov 2024 rinnovo ('Migliorata la norma relativa agli apprendisti che andranno a maturare gli scatti di anzianita'). Amount EUR 10.00 from CNA Ancona official communication. Zero before Jan 2025.
    
    LEVEL 1A FUNCTION ALLOWANCE: indennita di funzione EUR 51.65, confirmed kitech.it Mar 2026 (base 2490.07 + allowance 51.65 = total 2541.72). Assumed constant from Dec 2024; no primary source shows a change in this amount through the 2024 rinnovo.
    
    LEVEL ORDERING: 6 (lowest) < 5 < 5bis < 4 < 3 < 2 < 1B < 1A (highest). Level 5bis has higher salary than level 5 — this is correct per the CCNL (5bis = specializzato BIS, above the basic specializzato).
    
    APPRENTICESHIP: new rules from 2024-11-18 rinnovo for post-Nov-18-2024 contracts. Track durations confirmed from adapt.it (G016-specific): operai/tecnici max 5 years, amministrativi max 3 years, centraliniste 2 years. Percentage progressions (70/78/85/92/100% for operai/tecnici; 70/80/90% for amministrativi) follow the Confartigianato/CNA artigianato national framework agreement (CCNA); G016-specific source (adapt.it) confirms durations but not the individual percentages. SIMPLIFICATION: percentages assumed from artigianato CCNA framework; not found in a G016-specific primary source (CCNL PDF not fetched).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    
    APPRENTICESHIP SCOPE: only post-Nov-18-2024 rules modelled. Pre-renewal CCNL used a semestrali hybrid model (old percentage tables). Firms with apprenticeship contracts signed before Nov 18, 2024 may follow previgente rules. This is a deliberate scope decision (modelling current rules only); historical contract tracking is out of engine scope.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/comunicazione-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/comunicazione-artigianato-confartigianato.py"
```
