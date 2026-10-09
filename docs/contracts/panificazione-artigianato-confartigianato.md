# CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)

| | |
|---|---|
| **CNEL code** | `E015` |
| **Sector** | panificazione e alimentazione artigianato |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Alimentazione
    - CNA Alimentare
    - Casartigiani
    - CLAAI
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
| **Limits of this contract** | territorial_supplement |

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
| **Latest salary tranche** | 2026-04-01 |

### Semplificazioni note

4 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1S` | Level A1 Super — senior executive quadro / top-level manager | € 2,248.73 | 2026-04-01 |
| `B1` | Level B1 — senior operations manager | € 2,165.67 | 2026-04-01 |
| `A1` | Level A1 — production technical manager | € 2,056.93 | 2026-04-01 |
| `A2` | Level A2 — specialist technician / department head | € 1,926.61 | 2026-04-01 |
| `B2` | Level B2 — highly specialised operator | € 1,779.96 | 2026-04-01 |
| `A3` | Level A3 — qualified production technician | € 1,764.45 | 2026-04-01 |
| `B3S` | Level B3 Super — specialist operator with extended duties | € 1,732.79 | 2026-04-01 |
| `B3` | Level B3 — specialist production operator | € 1,676.43 | 2026-04-01 |
| `A4` | Level A4 — qualified support worker | € 1,671.86 | 2026-04-01 |
| `B4` | Level B4 — general worker and first-time hire | € 1,589.80 | 2026-04-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `B4` | € 14.46 |
| `A4` | € 14.46 |
| `B3` | € 16.01 |
| `B3S` | € 17.64 |
| `A3` | € 16.01 |
| `B2` | € 19.11 |
| `A2` | € 17.56 |
| `A1` | € 19.11 |
| `B1` | € 21.69 |
| `A1S` | € 21.69 |

## Apprenticeship

**gruppo_1_panificatori** (type: `percentage`)  
Destination levels: `A1`  
percentage: 1.00

**gruppo_a2_panificatori** (type: `percentage`)  
Destination levels: `A2`  
percentage: 1.00

**gruppo_a3_panificatori** (type: `percentage`)  
Destination levels: `A3`  
percentage: 1.00

**gruppo_b1_addetti** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_b2_addetti** (type: `percentage`)  
Destination levels: `B2`  
percentage: 1.00

**gruppo_b3s_addetti** (type: `percentage`)  
Destination levels: `B3S`  
percentage: 1.00

**gruppo_b4_addetti** (type: `percentage`)  
Destination levels: `B3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "panificazione-artigianato-confartigianato/ert_veneto · territorial_supplement · impact yes · open"
    ERT (VENETO): Elemento Retributivo Territoriale Veneto (ERT, expired 31.12.2025) was a territorial supplement specific to Veneto. Not modeled at national level.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Veneto ERT outside the engine for runs before 2026.

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
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    IND.SPECIALE: Indennita Speciale art.33 ter is fixed per level and does not change across tranches (confirmed: same amounts from 1995 to date, not subject to renewal increases). Folded into TOTALE base_salary for simplicity; the engine has no per-level fixed-allowance that is non-absorbable and constant — modeling as part of base_salary is the cleanest approach and does not affect any computation.

!!! note ""
    ERR: Elemento Retributivo Residuo (0.44 EUR/month) is a national fixed element, identical for all levels. Folded into TOTALE; the rounding impact on any level is less than 0.01 EUR/month.

!!! note ""
    IND.FUNZIONE A1S: Indennita di Funzione 36.15 EUR/month for level A1S introduced from April 2026 (Art. 33 quater, CCNL 2024). Included in the Apr 2026 TOTALE value (2248.73) as confirmed by lavoro-economia.it. Not modeled as a separate fixed_allowance.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-06 | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/2024-06-06-CCNL-AREA-ALIMENTAZIONE-ARTIGIANATO-PANIFICAZIONE-2023-2026.pdf) |
| — | — | — | [↗](https://www.artser.it/approfondimenti/accordo-di-rinnovo-del-ccnl-area-alimentazione-e-panificazione.html) |

??? note "Coverage notes"
    SALARY MODEL: unified TOTALE as base_salary. Each level's TOTALE = Tabellare conglobato (contingenza+EDR absorbed, per Art. 32 + conglobamento clause) + Indennità Speciale per Panificazione (Art. 33, fixed per level since Aug 1995) + ERR (0.44 EUR/month, fixed). Ind.Speciale confirmed from Art. 33 table in UILA CCNL PDF: A1S=94.77, A1=88.06, A2=82.63, A3=75.92, A4=72.05, B1=92.19, B2=76.44, B3S=74.87, B3=72.56, B4=68.69. ERR=0.44. All folded into base_salary; fixed_allowances=[] for all levels. Cross-verified: artser.it tabellare A2 Apr 2024 = 1705.54; 1705.54 + 82.63 + 0.44 = 1788.61 exact match across all 4 tranches (diff constant 83.07 EUR). Art. 31 confirms hourly divisor 173.
    
    ADDITIONAL MONTHS: 13. Art. 33 (Ind.Speciale) replaced the quattordicesima from August 1995 ('viene a cessare, per tutti i lavoratori, la maturazione dei ratei relativi alla ex 14a mensilita'). Art. 36 (Gratifica natalizia) confirms only tredicesima remains. Source: UILA CCNL PDF Art. 33 and Art. 36.
    
    TRANCHE DATES: four tranches — 2024-04-01 (April 2024, first 2024 renewal tranche), 2025-01-01 (January 2025), 2025-11-01 (November 2025), 2026-04-01 (April 2026). Source: ilccnl.it panificazione tables + lavoro-economia.it renewal PDF (CCNL 6 June 2024).
    
    HOURLY DIVISOR: 173, derived from 40-hour work week. Formula: 40 h/week x 52/12 = 173.33, rounded to 173 per contract practice. Verified: A2 Apr 2024 = 1788.61 / 173 = 10.34 EUR/h; A1 Apr 2024 = 1909.58 / 173 = 11.04 EUR/h; B1 Apr 2024 = 2010.49 / 173 = 11.62 EUR/h — consistent divisor 173 across 3 levels, confirming TOTALE model.
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Governed by Art. 34-bis (Aumenti periodici di anzianita per il settore della Panificazione). In force since 1 January 1996 per Art. 34-bis text ('A decorrere dal 1 gennaio 1996, i lavoratori, esclusi gli apprendisti, hanno diritto a maturare aumenti periodici di anzianita per ogni biennio [...] fino ad un massimo di 5 bienni'). The June 2024 renewal (Art. 58 amendment) separately added seniority for APPRENTICES (10 EUR flat from 2025-01-01) — that is a distinct provision. Per-level amounts confirmed from Art. 34-bis table in UILA CCNL PDF: A1S=21.69, A1=19.11, A2=17.56, A3=16.01, A4=14.46, B1=21.69, B2=19.11, B3S=17.64, B3=16.01, B4=14.46 EUR/scatto. valid_from set to 1996-01-01. The apprentice scatto (10 EUR flat from 2025-01-01, Art. 58 as amended by the June 2024 renewal) is modelled as seniority_increments.apprentice_amount.
    
    APPRENTICESHIP: 1° Gruppo only (Panificazione Gruppo A livelli A1s, A1 → destination A1, duration 5 anni/10 semestri). Percentages confirmed from Art. 58 table in UILA CCNL PDF (p. 69, Settore Panificazione Gruppo A 1° Gruppo): sem 1-2=70%, sem 3-4=75%, sem 5-6=84%, sem 7-8=90%, sem 9-10=100%. Converted to 12-month periods: 0-12mo=70%, 12-24mo=75%, 24-36mo=84%, 36-48mo=90%, 48-60mo=100%. Source: Art. 58, UILA CCNL PDF.
    
    PRE-APRIL-2024: periods before 2024-04-01 are outside the modelled window (2018-2022 CCNL values not included).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector, existing file).
    
    APPRENTICESHIP gruppi A2, A3, B1, B2, B3S, B4 added from formazione-apprendistato.com panificazione table (medium-high confidence: secondary aggregator + IPSOA 2024 news confirm 2024 rinnovo structure). Semiannual progressions as per Art. 58 + Allegato apprendistato. Gruppo 1° (dest=A1, primary source UILA PDF) unchanged.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/panificazione-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/panificazione-artigianato-confartigianato.py"
```
