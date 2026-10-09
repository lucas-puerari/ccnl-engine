# CCNL Acconciatura ed Estetica — Confartigianato/CNA

| | |
|---|---|
| **CNEL code** | `H515` |
| **Sector** | acconciatura ed estetica |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~95k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Benessere-Acconciatori
    - CNA Unione Benessere e Sanità
    - Casartigiani
    - CLAAI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| **Limits of this contract** | base_salary |

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
| **Latest salary tranche** | 2026-10-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Level 1 — technical director / senior supervisor | € 1,722.76 | 2026-10-01 |
| `2` | Level 2 — specialist worker / technical supervisor | € 1,573.78 | 2026-10-01 |
| `3` | Level 3 — qualified worker (hairdresser/beautician) | € 1,492.00 | 2026-10-01 |
| `4` | Level 4 — auxiliary worker / entry-level apprentice | € 1,406.73 | 2026-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `4` | € 7.23 |
| `3` | € 7.75 |
| `2` | € 8.26 |
| `1` | € 9.30 |

## Apprenticeship

**gruppo_1** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_2** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3** (type: `percentage`)  
Destination levels: `2`  
percentage: 0.85

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "acconciatura-estetica-confartigianato/gruppo_2_semester_mapping · base_salary · impact unknown · open"
    APPRENTICESHIP Gruppo 2 (manicure/pedicure → level 3, max 18 months, 70%/80%/100%), track 'gruppo_2': the three percentages are mapped to 6-month periods (0-6, 6-12, 12-18). Select with Apprentice(track='gruppo_2'); without a track name level 3 is ambiguous.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 3.

    **Remediation:** Confirm from the accordo tables that the 70/80/100% steps of Gruppo 2 run on 6-month periods.

!!! warning "acconciatura-estetica-confartigianato/gruppo_1_reduced_duration · base_salary · impact yes · open"
    APPRENTICESHIP DURATION (TAB.3): the 6-month reduction for post-secondary qualification holders (Gruppo 1: 54 months instead of 60) is not modelled; the standard 60-month table applies.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 54-month Gruppo 1 table for post-secondary qualification holders and a request field to select it.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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
| — | — | 2024-05-20 | [↗](https://www.confartigianatomarcatrevigiana.it/wp-content/uploads/2024/09/ccnl-benessere-app.prof-fino-30.9.24.pdf) |
| — | — | 2024-05-20 | [↗](https://www.studiomion.it/tabelle-retributive/tabelle-retributive-acconciatura-estetica/) |
| — | — | — | [↗](https://www.ilccnl.it/contratto/acconciatura-estetica/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati — contingenza and EDR fully absorbed). Back-calculation: May 2024 L3=1379.00/173=7.97 EUR/h; L2=1454.58/173=8.41 EUR/h; L1=1592.29/173=9.20 EUR/h — consistent divisor confirms conglobated model (lexplain.it + ilccnl.it).
    
    TRANCHE DATES: four tranches — 2024-05-01 (retroactive, renewal signed 20 May 2024), 2025-01-01, 2026-01-01, 2026-10-01. Source: studiomion.it salary tables; cross-checked ilccnl.it for Jan 2026 values.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 12 CCNL). Formula: 40 h/week × 52/12 = 173.33, rounded to 173 per contract usage. Confirmed: 1379.00/7.97=173.0 (L3 May 2024).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it Art. 40; informaimpresa.it ('tredici mensilità' explicitly stated as basis for Responsabile Tecnico allowance calculation).
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level amounts: L1=9.30, L2=8.26, L3=7.75, L4=7.23 EUR/scatto. Source: ilccnl.it (current database), cross-checked CISL 2013 PDF (amounts unchanged by 2024 renewal, which only introduced a 6 EUR apprentice-specific scatto).
    
    APPRENTICESHIP Gruppo 1 (acconciatori, estetisti, tricologi, tatuatori → destination level 3, max 5 years), track 'gruppo_1'. Primary source: Confartigianato Marca Trevigiana PDF (ccnl-benessere-app.prof-fino-30.9.24.pdf) for the pre-Oct-2024 table; post-Oct-2024 update (filcams.cgil.it + fisascat.it) raised months 1-12 from 65% to 70%, making months 1-18 uniformly 70%. Modelled table: 0-18=70%, 18-24=78%, 24-36=85%, 36-48=90%, 48-54=95%, 54+=100%.
    
    APPRENTICE SENIORITY: apprentice-specific scatto of 6 EUR (Art. 25 of the 2024 renewal, from 2024-10-01) modelled as seniority_increments.apprentice_amount.
    
    RESPONSABILE TECNICO: 100 EUR x 13 mensilità for workers designated Responsabile Tecnico at level 1 or 2, modelled as a role-scoped allowance (role 'responsabile_tecnico').
    
    PRE-MAY-2024 SALARY: the final tranche of the 2022 renewal (from 2023-02-01: L1=1511.46, L2=1380.74, L3=1309.00, L4=1234.19) is modelled; earlier periods are not.
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    
    APPRENTICESHIP Gruppo 3 (impiegati amministrativi, destination level 2, 3 anni / 6 semestri): 70/70/70/78/85/85 per semester. Source: consulenza.it circolare acconciatura 2024; lexplain.it tabella apprendistato acconciatori (medium-high confidence: two concordant secondary sources; primary accordo tables not online).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/acconciatura-estetica-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/acconciatura-estetica-confartigianato.py"
```
