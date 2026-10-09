# CCNL Distribuzione Cooperativa (ANCC-Coop / Confcooperative Consumo)

| | |
|---|---|
| **CNEL code** | `H016` |
| **Sector** | distribuzione-cooperativa |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~63k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCC-Coop
    - Confcooperative Consumo e Utenza
    - AGCI Agrital
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
| **Limits of this contract** | seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2027-03-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — middle managers with coordination and responsibility (L. 190/1985) | € 2,322.33 | 2027-03-01 |
| `1` | Livello 1 — senior specialists and team coordinators | € 2,112.86 | 2027-03-01 |
| `2` | Livello 2 — highly qualified workers, responsible for complex processes | € 1,839.64 | 2027-03-01 |
| `3S` | Livello 3S — senior skilled workers, multi-competency roles | € 1,639.29 | 2027-03-01 |
| `3` | Livello 3 — skilled workers, complex tasks requiring specific competencies | € 1,520.91 | 2027-03-01 |
| `4S` | Livello 4S — intermediate between 4 and 3, specialised operations | € 1,411.61 | 2027-03-01 |
| `4` | Livello 4 — qualified workers with autonomous task execution | € 1,311.43 | 2027-03-01 |
| `5` | Livello 5 — semi-skilled workers, routine operations with basic training | € 1,183.91 | 2027-03-01 |
| `6` | Livello 6 — entry-level workers, basic operations | € 910.71 | 2027-03-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 27.82 |
| `1` | € 26.64 |
| `2` | € 24.52 |
| `3S` | € 21.79 |
| `3` | € 21.79 |
| `4S` | € 19.93 |
| `4` | € 19.93 |
| `5` | € 18.84 |
| `6` | € 16.51 |

## Apprenticeship

**livelli_1_a_4** (type: `under_classification`)  
Destination levels: `1`, `2`, `3S`, `3`, `4S`, `4`  
under-level: `1`

**livello_5** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "distribuzione-cooperativa-ancc/seniority_amounts_proxy_source · seniority · impact unknown · open"
    SENIORITY AMOUNTS: from kitech.it only (proxy source). No independent primary-source confirmation. Cadence (36 months) and maximum (10) confirmed from CCNL text via olympus.uniurb.it.

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the seniority amounts against a primary CCNL source.

!!! warning "distribuzione-cooperativa-ancc/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-03-29 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H016) |
| — | — | 2024-03-29 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=31717:coop29324&catid=262&Itemid=139) |
| — | — | 2024-03-29 | [↗](https://ilccnl.it/contratto/ccnl/cooperative-di-consumo) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimo tabellare only. fixed_allowances per level: (1) CONTINGENZA frozen since January 1993, level-specific constant; (2) TERZO_ELEMENTO 3.07 EUR all levels, constant; (3) INDENNITA_FUNZIONE 250.76 EUR, Q only, constant since 2008. Total monthly = base_salary + CONTINGENZA + TERZO_ELEMENTO (+ INDENNITA_FUNZIONE for Q). Verified against kitech.it Dec 2025 table: Q=2985.20 (expected 2985.23), L1=2533.93 (expected 2533.96), L4=1763.99 (expected 1764.02). 3-cent gap = TERZO_ELEMENTO rounding (3.07 filcams vs 3.10 kitech); filcams used.
    
    MODELLED TRANCHES: 2025-05-01 (third tranche, source-confirmed from filcams.cgil.it and kitech.it), 2025-12-01 (fourth tranche, confirmed), 2026-11-01 (fifth, derived), 2027-03-01 (sixth and final, derived). April 2023 and April 2024 tranches not modelled — pre-signing period. Derivation method: per-level ratios from confirmed Dec 2025 L4 increments (35 EUR/tranche); validated by independent check pre-2023 Q minimo = 1,897.32 EUR matching search snippet.
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: CCNL text (olympus.uniurb.it summary, kitech.it).
    
    SENIORITY: triennial (cadence_months=36), maximum 10 scatti. Per-level amounts from kitech.it Dec 2025 (proxy, label SIMPLIFICATION). Q=27.82, L1=26.64, L2=24.52, L3S=21.79, L3=21.79, L4S=19.93, L4=19.93, L5=18.84, L6=16.51 EUR/scatto. L3S=L3 and L4S=L4 duplication confirmed plausible in Terziario family.
    
    INPS: uses 2026-terziario.json (terziario sector). No bilateral fund substituting INPS contributions. CNEL code: H016.
    
    APPRENTICESHIP (2024 RENEWAL): Modelled from the 2020 CCNL text (CCNL-Utilia2020 PDF, 'Apprendistato accordo 13 giugno 2012'): levels 1-4 start 2 levels below for first 24 months then 1 level below; level 5 stays 1 level below throughout. The 2024 renewal (signed 2024-03-29) amended Arts. 75 and 80-82 but the updated text is not publicly accessible. Rules assumed unchanged from 2020 source.
    
    HOURLY DIVISOR: 165 h/month used, per ilccnl.it (38h/week standard, all levels). Art. 198 of the CCNL also references 168 for 40h/week and higher divisors for extended shifts. Conflict: ilccnl.it states 165 as the contract divisor; Art. 198 lists 168 for 40h/week. Dominant workforce (post-2011 hires in a high-turnover retail sector on the 38h standard) is served by 165. 42h/week (182) and 45h/week (195) schedules not modelled.
    
    MODELLED TRANCHES (Nov 2026 / Mar 2027): confirmed by studioagostini.org (secondary source, June 2024 commentary on the Mar 2024 renewal). L4 increments: +35.00 EUR (01/11/2026), +40.00 EUR (01/03/2027). L1 increments: +56.39 EUR (01/11/2026), +64.44 EUR (01/03/2027). All per-level values match the reparametrized ratio from confirmed prior tranches. Source: studioagostini.org/ccnl-distribuzione-cooperativa-aumenti-fino-a-240-euro/
    
    INDENNITA_FUNZIONE (Q): 250.76 EUR constant throughout 2023-2027 contract. Confirmed at Dec 2025 by kitech.it, unchanged since at least 2008. The 2024 renewal (IPSOA analysis, lavorofacile.it) modified Arts. 75 and 80-82 but did not alter the Q function allowance. Modelled with valid_from at the earliest salary period.
    
    UNA TANTUM: 350 EUR gross at L4 level (proportionally reparametrized per other levels), paid April 2024 and April 2025 to workers in service at 2024-03-29 signing date. One-off payment with no engine representation; deliberately excluded.
    
    PRE-SIGNING TRANCHES: April 2023 (retroactive) and April 2024 tranches not modelled. Coverage starts at 2025-05-01 (first source-confirmed post-signing tranche).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/distribuzione-cooperativa-ancc.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/distribuzione-cooperativa-ancc.py"
```
