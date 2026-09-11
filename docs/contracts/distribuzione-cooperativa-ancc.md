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

[← Contracts index](index.md)

??? note "Signatories"
    - ANCC-Coop
    - Confcooperative Consumo e Utenza
    - AGCI Agrital
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — middle managers with coordination and responsibility (L. 190/1985) | € 2,322.33 | — |
| `1` | Livello 1 — senior specialists and team coordinators | € 2,112.86 | — |
| `2` | Livello 2 — highly qualified workers, responsible for complex processes | € 1,839.64 | — |
| `3S` | Livello 3S — senior skilled workers, multi-competency roles | € 1,639.29 | — |
| `3` | Livello 3 — skilled workers, complex tasks requiring specific competencies | € 1,520.91 | — |
| `4S` | Livello 4S — intermediate between 4 and 3, specialised operations | € 1,411.61 | — |
| `4` | Livello 4 — qualified workers with autonomous task execution | € 1,311.43 | — |
| `5` | Livello 5 — semi-skilled workers, routine operations with basic training | € 1,183.91 | — |
| `6` | Livello 6 — entry-level workers, basic operations | € 910.71 | — |

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

**livello_5** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SENIORITY AMOUNTS: from kitech.it only (proxy source). No independent primary-source confirmation. Cadence (36 months) and maximum (10) confirmed from CCNL text via olympus.uniurb.it.

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
