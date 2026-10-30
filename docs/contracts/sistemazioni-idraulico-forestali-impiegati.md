# CCNL Sistemazioni Idraulico-Forestali e Idraulico-Agraria (Impiegati)

| | |
|---|---|
| **CNEL code** | `A181` |
| **Sector** | sistemazioni idraulico-forestali e idraulico-agrarie — impiegati |
| **Family** | `bonifica-forestazione` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2025-12-04 |
| **Workers (est.)** | ~430 (impiegati subset) |
| **Ruleset version** | `2026.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Confcooperative-Lavoro-e-Servizi
    - Federforeste
    - Legacoop-Agroalimentare
    - FAI-CISL
    - FLAI-CGIL
    - UILA-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 27 derived / 2 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-12-04 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 14 - Mensilità aggiuntive (13ª e 14ª) (p. 43): "dette mensilità aggiuntive sono frazionabili in dodicesimi nell’ipotesi di inizio o di cessazione del rapporto nel corso dell’anno. [...] La frazione di mese superiore a 15 giorni viene considerata come un mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `I6Q` | Impiegato 6° livello — Quadro (Art. 36 CCNL) | € 2,095.91 | 2028-01-01 |
| `I6` | Impiegato 6° livello | € 2,095.91 | 2028-01-01 |
| `I5` | Impiegato 5° livello | € 1,827.07 | 2028-01-01 |
| `I4` | Impiegato 4° livello | € 1,679.91 | 2028-01-01 |
| `I3` | Impiegato 3° livello | € 1,579.56 | 2028-01-01 |
| `I2` | Impiegato 2° livello | € 1,488.46 | 2028-01-01 |
| `I1` | Impiegato 1° livello | € 1,376.66 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `I1` | € 22.21 |
| `I2` | € 23.76 |
| `I3` | € 24.79 |
| `I4` | € 26.86 |
| `I5` | € 29.44 |
| `I6` | € 33.05 |
| `I6Q` | € 33.05 |

## Apprenticeship

**apprendistato_I3_22mesi** (type: `under_classification`)  
Destination levels: `I3`

**apprendistato_I4_32mesi** (type: `under_classification`)  
Destination levels: `I4`

**apprendistato_I5I6_36mesi** (type: `under_classification`)  
Destination levels: `I5`, `I6`, `I6Q`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sistemazioni-idraulico-forestali-impiegati/derived_tranche_rounding · base_salary · impact yes · open"
    Tranches 01/01/2027 and 01/01/2028 for impiegati derived from confirmed Art. 35 parametri (L1=100, L2=108, L3=115, L4=122, L5=133, L6=152) applied to 01/01/2026 base. Rounding wobble up to 0.15 EUR on L4-L6 compared to rounded CCNL tables.

    **Applies when:** `base_salary` applies; level in I4, I5, I6; from 2027-01-01.

    **Remediation:** Replace the parameter-derived 2027 and 2028 tranches with the rounded CCNL tables.

!!! warning "sistemazioni-idraulico-forestali-impiegati/ind_funzione_transition_date · base_salary · impact unknown · open"
    IND_FUNZIONE quadri: modelled at 120.00 EUR/month from 2026-01-01 (current published value per lavoro-economia.it). The 2021 CCNL shows 103.00 from 01/08/2002; transition date to 120.00 not confirmed from 2025 rinnovo (PDF image-only).

    **Applies when:** `base_salary` applies; level in I6Q.

    **Remediation:** Confirm the date IND_FUNZIONE moved from 103.00 to 120.00 EUR.

!!! warning "sistemazioni-idraulico-forestali-impiegati/structural_rules_from_2021_text · base_salary · impact unknown · open"
    Structural rules (Art. 7, 35, 41, 52) taken from 2021 previgente CCNL text. The 2025 rinnovo PDF is image-only and full text is unavailable for independent verification.

    **Applies when:** `base_salary` applies.

    **Remediation:** Verify the structural rules against the 2025 renewal text.

!!! warning "sistemazioni-idraulico-forestali-impiegati/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "sistemazioni-idraulico-forestali-impiegati/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/agricoltura.json derived, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato of a month not worked in full without the pay of a whole month, an unknown worker category, or a lavoratore dello spettacolo without the pay of the last daily contributions (SpettacoloSicknessBase). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Derive the base from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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

### Without monetary impact

!!! note ""
    Serie retributiva starts 01/01/2026 (first tranche with primary-source data). Retroactive 2025 tabella not available in machine-readable form; pre-2026 amounts omitted.

!!! note ""
    Apprendistato: livelli I1 e I2 esclusi da destination_levels (engine requires at least 2 levels below minimum; I2 at order=2 cannot go 2 below). Only I3, I4, I5, I6, I6Q supported.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabella retributiva impiegati CCNL A181 rinnovo 04/12/2025. Tranches 01/01/2026, 01/01/2027, 01/01/2028. Conglobato. Parametri Art. 35 CCNL 2021: L1=100, L2=108, L3=115, L4=122, L5=133, L6=152. Pre-2026 amounts not modelled: table not available in machine-readable form. | tabella_retributiva | 2025-12-04 | [↗](https://www.lavoro-economia.it/?c=9) |
| CCNL previgente 2021: Art. 35 parametri impiegati, Art. 41 scatti anzianita, Art. 7 apprendistato sotto-inquadramento, Art. 36 IND_FUNZIONE quadri, Art. 52 modello conglobato div=169. Structural rules carried forward to 2025 rinnovo (2025 PDF image-only; full text unavailable). | altro | 2021-01-01 | not available |

??? note "Coverage notes"
    CCNL A181 — Sistemazioni Idraulico-Forestali (Impiegati). Split from operai contract: salary bands overlap, requiring separate files for correct engine ordering and under-classification apprenticeship. 7 livelli impiegati (I1-I6, I6Q). Conglobated model. Divisore 169, 14 mensilita.
    
    Seniority: Art. 41 CCNL 2021 — 12 scatti biennali. Amounts per level confirmed from 2021 previgente text; carried forward to 2025 rinnovo (structural rules unchanged per summary).
    
    OVERTIME/LEAVE/ABSENCE (L3): Art. 37 CCNL 2023 — straordinario 30%, notturno 50%, festivo 50%. Ferie 22 giorni (orario su 5 giorni, Art. 12). Malattia: integrazione datoriale al 100% per max 6 mesi (Art. 44). Assenza: divisore 26. Rates from 2023 CCNL PDF; 2025 rinnovo structural rules assumed unchanged (text image-only).
    

## Raw data

The contract file this page is generated from: [`agreement/sistemazioni-idraulico-forestali-impiegati.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/sistemazioni-idraulico-forestali-impiegati.json).

## Usage example

```python
--8<-- "docs/examples/agreement/sistemazioni-idraulico-forestali-impiegati/example.py"
```
