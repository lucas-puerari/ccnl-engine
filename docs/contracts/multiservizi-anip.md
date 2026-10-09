# CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)

| | |
|---|---|
| **CNEL code** | `K511` |
| **Sector** | multiservizi |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIP-Confindustria
    - Legacoop Lavoro e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Servizi
    - Unionservizi Confapi
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltrasporti-UIL

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
| **Limits of this contract** | inps_employee, seniority |

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
| **Latest salary tranche** | 2029-03-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri with high-responsibility managerial duties | € 2,006.64 | 2029-03-01 |
| `7` | Employees with managerial functions | € 1,833.35 | 2029-03-01 |
| `6` | Workers with specialist duties / Senior white-collar employees | € 1,587.07 | 2029-03-01 |
| `5` | Expert workers / White-collar employees | € 1,276.96 | 2029-03-01 |
| `4` | Specialist workers / Junior clerical employees | € 1,167.51 | 2029-03-01 |
| `4par125` | Workers assigned to painting booths and lines employed as of 01/06/2001 (par. 125) | € 1,140.15 | 2029-03-01 |
| `3` | Skilled workers / Clerical employees | € 1,076.30 | 2029-03-01 |
| `2par115` | Workers assigned to auxiliary activities in school/healthcare settings (par. 115) | € 1,048.93 | 2029-03-01 |
| `2` | General workers / Clerical employees (first 18 months) | € 994.21 | 2029-03-01 |
| `1` | General labourers | € 912.12 | 2029-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 51.02 |
| `2` | € 54.39 |
| `2par115` | € 55.50 |
| `3` | € 58.18 |
| `4par125` | € 62.59 |
| `4` | € 63.15 |
| `5` | € 97.29 |
| `6` | € 116.67 |
| `7` | € 132.06 |
| `Q` | € 142.89 |

## Apprenticeship

**destinazione_5** (type: `under_classification`)  
Destination levels: `5`

**destinazione_4** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "multiservizi-anip/cigs_threshold_16_to_50 · inps_employee · impact yes · open"
    INPS RATES PROXY. Terziario sector confirmed for multiservizi/pulizie: kitech.it (p=4_129, "Commercio - terziario Imprese appaltatrici servizi pulizia") lists rates matching 2026-terziario.json. Simplification: the CIGS threshold for imprese di pulizia is >15 dipendenti (not >50 as in the general terziario tier); for 16-50 employee companies the modeled employee rate (9.19%) understates the actual 9.49%. FIS (Fondo Integrazione Salariale) may also apply for non-CIGS-eligible firms. Source: kitech.it/Contributi-previdenziali.aspx?p=4_129

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the CIGS threshold of more than 15 employees for cleaning firms.

!!! warning "multiservizi-anip/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2021-07-09 | [↗](https://www.oristanoservizi.it/wp-content/uploads/2021/11/CCNL-Multiservizi-scadenza-2024.pdf) |
| — | — | 2025-06-13 | [↗](https://www.redigo.info/2025/06/24/rinnovo-ccnl-imprese-di-pulizia-e-servizi-integrati-per-il-periodo-2025-2028/) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=99) |
| — | — | — | [↗](https://www.ccnlportatili.it/ccnl/terziario-servizi/multiservizi-servizi-di-pulizia/) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series; contingenza and EDR are frozen fixed_allowances. Source: oristanoservizi.it/CCNL-Multiservizi-scadenza-2024.pdf (2021-2024 contract, 5 tranches) and accordo integrativo 6 Aug 2025 (2025-2028 contract, 8 tranches) via redigo.info.
    
    hourly_divisor: 173 — confirmed per CCNL text: 'I divisori per ottenere la quota oraria e giornaliera sono, rispettivamente, 173 e 26'. Cross-checked: level Q July 2021 total 1953.62/11.29hr = 173 (hourly rate from table). Source: oristanoservizi.it PDF.
    
    additional_months: 14 (tredicesima + quattordicesima). Source: CCNL text — 'Tredicesima: entro il 20 dicembre; Quattordicesima: entro il 15 luglio'. Both in misura di una mensilità della retribuzione globale mensile.
    
    Seniority — impiegati (levels 5, 6, 7, Q): biennale scatti equal to 6.25% of (minimo tabellare + contingenza al 1 agosto 1983, EUR 279.60), maximum 8; amounts are recomputed at every salary tranche (verified against the July 2021 and July 2025 published values).
    
    Seniority — operai (levels 1, 2, 2par115, 3, 4par125, 4): 'anzianità forfettaria di settore', a single fixed monthly amount from the 5th year of sector seniority; modelled with first_cadence_months_by_level=48 and maximum_count_by_level=1. Amounts per CCNL text (June 2011 increase after E.d.a.r. cessation). Source: oristanoservizi.it PDF.
    
    Contingenza par levels: the CCNL text notes that contingenza values for 4par125 and 2par115 are not explicitly stated; by industry convention they match the values for levels 4 and 2 respectively. Source: note in oristanoservizi.it PDF.
    
    Apprenticeship: under-classification, 30 months for destination levels 4 and 5 (CCNL: '30 mesi per i livelli 4° e 5°'): first half two classification levels below the destination, second half one level below (the parametric sub-levels 2par115 and 4par125 are skipped, hence levels_below 3/1 for destination 5 and 4/2 for destination 4). Destination level 2 (apprentice stays at level 1 for the whole period) and other destinations are not modelled: durations not sourced. Source: ccnlportatili.it.
    
    July 2025 values: the 2021-2024 CCNL included a 5th salary tranche effective July 2025 (e.g. +10 EUR on level 2). This was superseded by the 2025-2028 renewal (signed 13 June 2025, definitive tables per accordo integrativo 6 August 2025, effective retroactively from 1 July 2025 per Art. 73). The JSON models post-renewal July 2025 values (819.21 for level 2) directly. Workers received the higher new-contract amount; the old 5th tranche value (779.21) was never separately operative.
    
    ANIP CONTRACT STATUS (2025): ANIP-Confindustria abandoned the final stages of the 2025 CCNL renewal negotiations without signing. The 2025 renewal was signed by Legacoop Produzione e Servizi, Unionservizi Confapi, AGCI + Filcams-CGIL/Fisascat-CISL/Uiltrasporti-UIL. ANIP companies continue to apply the previous CCNL (this file). A separate multiservizi-legacoop file would be needed to cover the new 2025-2028 renewal (levels 1-8: 1,296.39-2,256.14 EUR, 14 mensilità).
    
    Workers covered: ~403,000 per INPS-UNIEMENS 2025 data; largest uncovered CCNL at time of implementation.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/multiservizi-anip.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/multiservizi-anip.py"
```
