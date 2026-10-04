# CCNL per i lavoratori dell'industria del legno, del sughero, del mobile, dell'arredamento e delle industrie affini (Federlegno-Arredo)

| | |
|---|---|
| **CNEL code** | `F051` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federlegno-Arredo
    - Feneal-Uil
    - Filca-Cisl
    - Fillea-Cgil

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
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2025-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AD3` | Management Area — Level 3 (top management) | € 2,536.28 | 2025-01-01 |
| `AD2` | Management Area — Level 2 | € 2,478.22 | 2025-01-01 |
| `AD1` | Management Area — Level 1 | € 2,358.74 | 2025-01-01 |
| `AC5` | Competency Area — Level 5 (quadri) | € 2,239.93 | 2025-01-01 |
| `AC4` | Competency Area — Level 4 | € 2,061.83 | 2025-01-01 |
| `AS4` | Specialist Area — Level 4 | € 1,883.66 | 2025-01-01 |
| `AC3` | Competency Area — Level 3 | € 1,883.66 | 2025-01-01 |
| `AC2` | Competency Area — Level 2 | € 1,883.66 | 2025-01-01 |
| `AS3` | Specialist Area — Level 3 | € 1,795.17 | 2025-01-01 |
| `AS2` | Specialist Area — Level 2 | € 1,705.36 | 2025-01-01 |
| `AC1` | Competency Area — Level 1 | € 1,705.36 | 2025-01-01 |
| `AS1` | Specialist Area — Level 1 | € 1,633.95 | 2025-01-01 |
| `AE4` | Executive Area — Level 4 (highly skilled workers) | € 1,633.95 | 2025-01-01 |
| `AE3` | Executive Area — Level 3 (skilled workers) | € 1,544.94 | 2025-01-01 |
| `AE2` | Executive Area — Level 2 (qualified workers) | € 1,455.87 | 2025-01-01 |
| `AE1` | Executive Area — Level 1 (general workers) | € 1,230.69 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AE1` | € 7.95 |
| `AE2` | € 8.53 |
| `AE3` | € 8.80 |
| `AE4` | € 9.09 |
| `AS1` | € 9.09 |
| `AC1` | € 10.76 |
| `AS2` | € 9.66 |
| `AS3` | € 10.22 |
| `AC2` | € 10.79 |
| `AC3` | € 10.79 |
| `AS4` | € 10.79 |
| `AC4` | € 11.92 |
| `AC5` | € 13.07 |
| `AD1` | € 13.92 |
| `AD2` | € 14.77 |
| `AD3` | € 14.77 |

## Apprenticeship

**professionalizzante_1** (type: `under_classification`)  
Destination levels: `AE3`, `AE4`

**professionalizzante_2** (type: `under_classification`)  
Destination levels: `AS1`, `AC1`

**professionalizzante_3** (type: `under_classification`)  
Destination levels: `AS2`, `AC4`

**professionalizzante_4** (type: `under_classification`)  
Destination levels: `AS3`, `AC3`

**professionalizzante_5** (type: `under_classification`)  
Destination levels: `AC2`

**professionalizzante_6** (type: `under_classification`)  
Destination levels: `AS4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "apprenticeship_midpoint_allowances · base_salary · impact yes · open"
    In an under-classification apprenticeship period flagged midpoint_to_destination the engine pays the mean of the pay-level and destination base salaries, but the fixed allowances stay those of the pay level. The contract midpoint may cover the whole pay; the run is affected only when the allowances of the two levels differ.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Apply the midpoint to every component the CCNL averages, with the source of the rule, then resolve this limitation.

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
    APPRENTICESHIP under_classification (CCNL Legno, renewal 20/06/2023, CNEL F051 PDF): 1st period (0-12 months) two salary bands below destination; 2nd period (12-24) one band below; 3rd period (24-36) one band below with intermediate pay between current and destination level (midpoint_to_destination on the minimum pay table); then destination. The bands are AE1 | AE2 | AE3 | AE4-AS1 | AC1-AS2 | AS3 | AC2-AC3-AS4 | AC4 | AC5 | AD1 | AD2 | AD3; tracks group destinations sharing the same order offset. Modelled destinations: from AE3 to AC4; AE1/AE2 (no band two steps below), AC5 (quadri) and management area excluded.

!!! note ""
    LEVEL DESCRIPTIONS: the level description texts (e.g. 'Area Esecutiva — 1° livello') are placeholders generated by the engine based on area codes (AE/AS/AC/AD) and do not correspond to the official classification article texts of the CCNL. The text extracted from the CNEL F051 PDF did not include the official category names for each level code.

!!! note ""
    INTRA-BAND ORDERING: for levels sharing the same base pay (AE4/AS1, AC1/AS2, AC2/AC3/AS4), the relative order is assigned arbitrarily (ascending within the group) to satisfy the engine's order-uniqueness constraint. The CCNL does not define an internal hierarchy among levels within the same salary band. Functionally irrelevant — the validator only requires salary to be non-decreasing for ascending order.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-06-20 | [↗](https://www.direzionelavoro.it/wp-content/uploads/2023/07/Legno-industria-CNEL-F051.pdf) |
| — | — | — | [↗](https://www.lexplain.it/ccnl-legno-arredamento-industria/) |
| — | — | — | [↗](https://www.previdenza-professionisti.it/ccnl-legno-industria-scatti-anzianita/) |

??? note "Coverage notes"
    SALARY MODEL: split (paga base + contingenza + EDR). Base pay varies by tranche (Jul 2023, Jan 2024, Jan 2025). Contingenza frozen from 31/07/1992 (values from CNEL F051 PDF). EDR fixed at EUR 10.33 for all levels (Agreement 31/07/1992). Table sources: CNEL F051 PDF (renewal 20/06/2023); Jan 2024 tranche confirmed by lexplain.it; Jan 2025 tranche derived from the difference between the total from dottrinalavoro.it and contingenza+EDR.
    
    ADDITIONAL MONTHS: 13 mensilità (tredicesima). Source: CNEL F051 PDF, field 'Numero mensilità: 13'.
    
    CONTINGENZA: 12 salary bands for 16 level codes. Levels AE4 and AS1 share the same base pay and contingenza (band 4). Levels AC1 and AS2 share the same base pay and contingenza (band 5); AS2 has a different seniority increment from AC1. Levels AC2, AC3 and AS4 share the same base pay and contingenza (band 7). All contingenza values from CNEL F051 PDF.
    
    MANAGEMENT FUNCTION ALLOWANCE AD3: EUR 25.82/month, not included in the minimum pay table, modelled as a fixed_allowance for level AD3.
    
    INPS: industry sector rates from 2026-industria.json (existing file reused). Employee 9.19%; employer: ≤15 employees 30.13%, 16-50 employees 30.20%, >50 employees 30.50%. No substitute bilateral fund for CCNL Legno Industria (Fondimpresa for training only, does not affect INPS contribution rates).
    
    HOURLY DIVISOR 174 (40h x 52 / 12 = 173.33, rounded up as used by the sector): no published hourly table in accessible primary sources; independent secondary sources converge on 174 (previdenza-professionisti.it). Daily coefficient 26 confirmed by the CNEL F051 PDF.
    
    SENIORITY: biennial cadence (24 months), maximum 5 increments; amounts from previdenza-professionisti.it (2025, unchanged since 2009). AS2 (9.66) and AC1 (10.76) have different increment amounts despite sharing the same base pay. valid_from 2023-07-01 assumed equal to the first tranche; the 2023 renewal did not modify seniority increments.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/legno-arredamento-federlegno.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/legno-arredamento-federlegno.py"
```
