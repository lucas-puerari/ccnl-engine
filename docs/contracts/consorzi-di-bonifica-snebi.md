# CCNL Consorzi di Bonifica (SNEBI-FLAI-FAI-FILBI)

| | |
|---|---|
| **CNEL code** | `A131` |
| **Sector** | Agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-05-21 |
| **Workers (est.)** | ~4k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - SNEBI
    - FLAI-CGIL
    - FAI-CISL
    - FILBI-UIL

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
| **Last renewal** | 2025-05-21 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AQ187` | AQ187 — quadro | € 2,868.89 | 2026-01-01 |
| `AQ185` | AQ185 — quadro | € 2,838.21 | 2026-01-01 |
| `A184` | A184 | € 2,822.87 | 2026-01-01 |
| `A170` | A170 | € 2,608.08 | 2026-01-01 |
| `AQ164` | AQ164 — quadro | € 2,516.04 | 2026-01-01 |
| `AQ162` | AQ162 — quadro | € 2,485.35 | 2026-01-01 |
| `A160` | A160 | € 2,454.67 | 2026-01-01 |
| `A159` | A159 | € 2,439.32 | 2026-01-01 |
| `A157` | A157 | € 2,408.65 | 2026-01-01 |
| `A135` | A135 | € 2,071.13 | 2026-01-01 |
| `A134` | A134 | € 2,055.79 | 2026-01-01 |
| `B132_ex51` | B132 — ex cat. 5/1 (alternate scatto 47.73) | € 2,025.10 | 2026-01-01 |
| `B132` | B132 — ex cat. 4/1 (best-guess scatto 50.05) | € 2,025.10 | 2026-01-01 |
| `B128_ex52` | B128 — ex cat. 5/2 (alternate scatto 44.44) | € 1,963.73 | 2026-01-01 |
| `B128` | B128 — ex cat. 4/2 (best-guess scatto 47.92) | € 1,963.73 | 2026-01-01 |
| `C127` | C127 | € 1,948.38 | 2026-01-01 |
| `C122` | C122 | € 1,871.68 | 2026-01-01 |
| `C118` | C118 | € 1,810.32 | 2026-01-01 |
| `D117` | D117 | € 1,794.97 | 2026-01-01 |
| `D116` | D116 | € 1,779.62 | 2026-01-01 |
| `D115` | D115 | € 1,764.29 | 2026-01-01 |
| `D112` | D112 | € 1,718.28 | 2026-01-01 |
| `D107` | D107 | € 1,641.56 | 2026-01-01 |
| `D104` | D104 | € 1,595.53 | 2026-01-01 |
| `D100` | D100 | € 1,534.16 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "consorzi-di-bonifica-snebi/pre_2000_cohort_table_missing · base_salary · impact yes · open"
    Dual-cohort: workers hired by 15-07-2000 have a lower salary table (~1.4% below post-2000) not modeled here. Those workers are a declining cohort (tenure 25+ years); new hires always enter the post-2000 table.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the lower salary table for workers hired by 15-07-2000 behind a hire-date fact.

!!! warning "consorzi-di-bonifica-snebi/ex_sublevel_scatto_mapping · seniority · impact unknown · open"
    B128 and B132 each contain two ex-classification sub-levels (B128: ex-4/2 and ex-5/2; B132: ex-4/1 and ex-5/1) sharing the same base salary but with different scatto amounts. Modeled as B128/B128_ex52 and B132/B132_ex51. Plain codes carry the ex-4 (higher) scatto as best-guess; _ex52/_ex51 codes carry the ex-5 (lower) scatto. Mapping is unverifiable from public sources (B128: 47.92 vs 44.44; B132: 50.05 vs 47.73).

    **Applies when:** `seniority` applies; level in B128, B128_ex52, B132, B132_ex51.

    **Remediation:** Verify which ex-classification sub-level carries each scatto amount against the CCNL text.

!!! warning "consorzi-di-bonifica-snebi/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
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
| — | — | 2025-05-21 | [↗](https://www.redigo.info/2026/03/06/ccnl-consorzi-di-bonifica-le-tabelle-retributive-aggiornate/) |
| — | — | 2025-05-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=286) |
| — | — | 2025-05-21 | [↗](https://ilccnl.it/contratto/ccnl/consorzi-di-bonifica) |

??? note "Coverage notes"
    Salary model: split (paga base + contingenza) per ilccnl.it, contingenza frozen at EUR 0.00, terzo elemento 0.00 (confirmed via ilccnl.it for D100, D104, D107). base_salary is the full minimo tabellare. Note: ilccnl.it tabelle show the pre-2000 cohort (e.g. D100 Jan2026=1513.09); post-2000 values (D100 Jan2026=1534.16) are sourced from redigo.info and kitech=286.
    
    Cohort: two salary tables — 'in servizio al 15-07-2000' (pre-2000) and 'in servizio dal 15-07-2000' (post-2000). This file models the post-2000 table. kitech.it CodiceCateg=286 title confirms post-2000 identity; redigo.info column 2 matches (D100 Jan2026=1534.16). Pre-2000 table is ~1.4% lower.
    
    Hourly divisor 164.67 h/month from ilccnl.it (single source). Consistent with 38h/week: 52x38/12=164.67. Daily divisor: 26.
    
    Additional months: 14 — tredicesima (dicembre) + quattordicesima (giugno). Source: ilccnl.it ('quattordici mensilitA').
    
    Tranches: 2025-07-01 (+3%) and 2026-01-01 (+2.2%). Both sourced from redigo.info primary table. No pre-July-2025 salary is modeled; engine returns no result for as_of before 2025-07-01.
    
    Seniority: 10 scatti total — tier 1: 6 biennali (cadence 24 months), tier 2: 1 dodicennale (cadence 144 months after tier 1 exhausted), tier 3: 3 quadriennali (cadence 48 months). All tiers modeled. Per-scatto amounts for tiers 2-3 assumed equal to tier 1 amounts (no independent source found for higher-tier amounts; best-guess from standard CCNL practice).
    
    AQ-category levels (AQ162, AQ164, AQ185, AQ187) are quadri. An indennita di funzione may apply per standard quadri CCNL practice, but the amount could not be confirmed from available public sources; not modeled.
    
    layer_2 out_of_scope: no apprenticeship data found in available public sources. Full CCNL PDF required.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/consorzi-di-bonifica-snebi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/consorzi-di-bonifica-snebi.py"
```
