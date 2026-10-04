# CCNL Area Tessile-Moda e Chimica-Ceramica — Artigianato

| | |
|---|---|
| **CNEL code** | `V751` |
| **Sector** | tessile moda chimica ceramica artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-07-16 |
| **Workers (est.)** | ~120k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Federmoda
    - CNA Produzione
    - CNA Artistico e Tradizionale
    - CNA Servizi alla Comunità
    - Confartigianato Moda
    - Confartigianato Chimica
    - Confartigianato Ceramica
    - Casartigiani
    - CLAAI
    - Filctem CGIL
    - Femca CISL
    - Uiltec UIL

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
| **Last renewal** | 2024-07-16 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-10-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `6S` | Level 6S — senior manager / technical director (incl. function allowance EUR 20.66) | € 2,133.07 | 2026-10-01 |
| `6` | Level 6 — skilled technician / senior clerical employee | € 1,978.15 | 2026-10-01 |
| `5` | Level 5 — specialist operator / clerical employee | € 1,813.50 | 2026-10-01 |
| `4` | Level 4 — highly qualified operator | € 1,675.42 | 2026-10-01 |
| `3` | Level 3 — specialist operator | € 1,606.03 | 2026-10-01 |
| `2` | Level 2 — qualified operator | € 1,538.39 | 2026-10-01 |
| `1` | Level 1 — basic operator | € 1,454.41 | 2026-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 4 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 7.23 |
| `2` | € 7.75 |
| `3` | € 8.26 |
| `4` | € 9.30 |
| `5` | € 10.85 |
| `6` | € 12.91 |
| `6S` | € 15.49 |

## Apprenticeship

**gruppo_1_abb** (type: `percentage`)  
Destination levels: `4`, `5`, `6`, `6S`  
percentage: 1.00

**gruppo_2_abb** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3_abb** (type: `percentage`)  
Destination levels: `2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "tessile-moda-artigianato-confartigianato/chimica_ceramica_subsectors · base_salary · impact yes · open"
    Only tessile-abbigliamento sub-sector modelled. Chimica-ceramica sub-sectors (different salary tables) are not modelled. CNEL code V751 covers all three sub-sectors.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the chimica-ceramica salary tables with a sub-sector input.

!!! warning "tessile-moda-artigianato-confartigianato/apprentice_seniority_hire_date · seniority · impact yes · open"
    APPRENTICE SENIORITY treated as uniform 6.00 EUR from 2025-01-01 regardless of hire date. Strictly, only workers hired after 17 Jul 2024 get 6.00 from Jan 2025; workers hired before that date remain at 5.16. For new hires this model is correct.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 5.16 EUR apprentice increment for workers hired before 17 July 2024 with a hire-date input.

!!! warning "tessile-moda-artigianato-confartigianato/level_category_unconfirmed · inps_employer · impact unknown · open"
    LEVEL CATEGORY: all levels left null (no primary-source text confirming operaio/impiegato split). The 2026-artigianato.json tier applies the impiegato rate (0.2471) for category='impiegato'/'quadro' vs. default 0.2693. Employer cost for higher levels (5, 6, 6S) may be slightly overestimated until categories are confirmed from primary CCNL text.

    **Applies when:** `inps_employer` applies; level in 5, 6, 6S.

    **Remediation:** Confirm the operaio/impiegato category of each level from the CCNL text.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-16 | [↗](https://www.kitech.it/ccnl/tessile-abbigliamento-artigianato) |
| — | — | — | [↗](https://www.eber.org) |
| — | — | 2024-07-16 | [↗](https://olympus.uniurb.it) |
| — | — | 2017-12-14 | [↗](https://www.cna.it) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Back-calculation: L3 Jan 2025 = 1502.03/173 = 8.68 EUR/h; L4 Jan 2025 = 1566.69/173 = 9.05 EUR/h; L6 Jan 2025 = 1849.57/173 = 10.69 EUR/h — consistent divisor 173 across levels confirms conglobated model.
    
    CNEL CODE: V751 confirmed from EBER (Ente Bilaterale Emilia-Romagna) 'Allegato 2 — Sintesi codifica contratti INPS e CNEL', INPS code 003. D025 found on lavoro-economia.it refers to the older separate 'Area Tessile-Moda' pre-unification entry; V751 covers the current unified area contract (tessile+chimica+ceramica).
    
    TRANCHE DATES: four tranches — 2024-07-01 (retroactive from renewal 16 Jul 2024), 2025-01-01, 2025-10-01, 2026-10-01. Source: FEMCA CISL Bergamo salary sheet, cross-checked kitech.it.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 9 CCNL tessile-moda artigianato). Formula: 40 h/week × 52/12 = 173.33 rounded to 173 per contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it / CNA PDF art. mensilità aggiuntive.
    
    SENIORITY: biennale (every 24 months), maximum 4 scatti. Per-level amounts from Art. 67 CNA PDF 2017 (primary source): 6S=15.49, 6=12.91, 5=10.85, 4=9.30, 3=8.26, 2=7.75, 1=7.23 EUR. Unchanged in 2024 rinnovo.
    
    APPRENTICE SENIORITY: raised from 5.16 to 6.00 EUR by 2024 rinnovo (Art. 25), effective 2025-01-01 for new hires after 17 Jul 2024. Modelled as uniform 6.00 from 2025-01-01 (pre-Jul-2024 hires staying at 5.16 not separately tracked — minor simplification for new engagements).
    
    APPRENTICESHIP: 3 gruppi (Art. 68 CNA PDF 2017, Section 7 retribution marked 'Omissis' in 2024 rinnovo = unchanged). Gruppo 1 (destination levels 4-6S, max 54 months), Gruppo 2 (destination level 3, max 42 months), Gruppo 3 (destination level 2, max 24 months). Level 1 has no apprenticeship track.
    
    Level 6S indennità di funzione (EUR 20.66) confirmed fixed across all four tranches. Verification 2026-09-09: web sources show L6S minimi (without indennità) as 1922.59/1975.32/2039.91/2112.41 (Jul 2024/Jan 2025/Oct 2025/Oct 2026); file stores 1943.25/1995.98/2060.57/2133.07 — difference exactly 20.66 EUR at every tranche (kitech.it Oct 2025 confirmation plus back-check against all 4 tranches). Indennità conglobata in base_salary (no separate fixed_allowances entry).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/tessile-moda-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/tessile-moda-artigianato-confartigianato.py"
```
