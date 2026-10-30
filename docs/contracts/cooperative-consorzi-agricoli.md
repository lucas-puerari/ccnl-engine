# CCNL Cooperative e Consorzi Agricoli

| | |
|---|---|
| **CNEL code** | `A016` |
| **Sector** | cooperative e consorzi agricoli — impiegati e operai agricoli |
| **Family** | `agricoltura` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGCI-Agrital
    - Confcooperative-Fedagripesca
    - Legacoop-Agroalimentare
    - FLAI-CGIL
    - FAI-CISL
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

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 33 verified / 9 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-19 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-02-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | Second review of the agricoltura group: minimi conglobati of the eight levels in the four tranches, monthly payments, fixed-term operai and scatti, against the signed verbale of 19 July 2024. | corrected | The 32 minimi match the signed All. n. 1 (p. 19, a scanned page read from the image; each tranche equals the one before plus the printed aumento): verified.<br>14 monthly payments: the verbale names the 13ma and 14ma for the operai a tempo indeterminato (p. 14) but restates no clause for the impiegati: derived, no longer assumed.<br>Fixed-term operai are owed a terzo elemento of 30.44% instead of the monthly payments (p. 14): not modelled and not declared; now a limitation.<br>Scatti are not in the verbale: derived. The file applies the impiegati maximum of 12 to the operai, whose maximum is 5; the note said so but did not block: now a limitation from the 6th biennale. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 34 - 13ma e 14ma mensilita' (p. 52): "La frazione di mese superiore a 15 giorni viene considerata come mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1° | € 2,303.40 | 2027-02-01 |
| `2` | Livello 2° | € 2,070.77 | 2027-02-01 |
| `3` | Livello 3° | € 1,906.06 | 2027-02-01 |
| `4` | Livello 4° | € 1,772.31 | 2027-02-01 |
| `5` | Livello 5° | € 1,685.38 | 2027-02-01 |
| `6` | Livello 6° | € 1,636.55 | 2027-02-01 |
| `7` | Livello 7° | € 1,518.40 | 2027-02-01 |
| `np` | Area non professionalizzati | € 1,280.82 | 2027-02-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `np` | € 0.00 |
| `7` | € 9.44 |
| `6` | € 10.85 |
| `5` | € 11.39 |
| `4` | € 11.93 |
| `3` | € 12.20 |
| `2` | € 29.44 |
| `1` | € 33.05 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `np`, `7`, `6`, `5`, `4`, `3`, `2`, `1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cooperative-consorzi-agricoli/operai_seniority_over_five · seniority · impact yes · open"
    SENIORITY: operai Art. 61 (max 5 biennali) e impiegati Art. 49 (max 12 biennali) hanno importi differenti per livelli 3-7. Operai amounts confirmed from rinnovo 2024 (lavoro-economia.it, businessonline.it): L7=9.44, L6=10.85, L5=11.39, L4=11.93, L3=12.20, L2=29.44, L1=33.05 EUR/biennio. Modelled with operai amounts (dominant workforce in cooperatives) and maximum_count=12 (impiegati cap). Queries for operai with seniority_count>5 will overstate by at most 1-5 scatti. The engine supports per-category amounts and maxima (amount_by_level_by_category, maximum_count_by_category): the gap is in the data only (review of 2026-10-30).

    **Applies when:** `seniority` applies; category in operaio; seniority of at least 144 months.

    **Remediation:** Fill amount_by_level_by_category with the operai (Art. 61) and impiegati (Art. 49) amounts and maximum_count_by_category with 5 and 12.

!!! warning "cooperative-consorzi-agricoli/apprenticeship_passthrough · base_salary · impact unknown · open"
    Apprendistato: regola non reperita nel PDF 2024. Modellato come 100% passthrough.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Source the apprenticeship rule of the 2024 CCNL and model its track.

!!! warning "cooperative-consorzi-agricoli/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "cooperative-consorzi-agricoli/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/agricoltura.json derived, then remove this note.

!!! warning "cooperative-consorzi-agricoli/otd_terzo_elemento_missing · base_salary · impact yes · open"
    OTD: a fixed-term operaio is paid the minimo conglobato giornaliero or orario plus a terzo elemento of 30.44% (festività 5.45%, ferie 8.33%, 13ma 8.33%, 14ma 8.33%) on 312 working days instead of the monthly payments (Art. 60, verbale 19 July 2024, p. 14); the engine pays the monthly structure.

    **Applies when:** `base_salary` applies; contract type in fixed_term; category in operaio.

    **Remediation:** Model the daily pay and the terzo elemento of the fixed-term operai, as the operai agricoli CCNL requires.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on calendar days: the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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
| Verbale di accordo 19/07/2024 All. n.1: tabelle retributive conglobate per 8 livelli (1-7+np), 4 tranches 2024-2027. Seniority: Art. 61 (operai) e Art. 49 (impiegati). Indennità funzione quadri Art. 45 rivisitata dal 01/08/2024. | tabella_retributiva | 2024-07-19 | [↗](https://www.flai.it/wp-content/uploads/2018/11/CCNL-Cooperative-e-consorzi-agricoli-2024-2027.pdf) |

??? note "Coverage notes"
    CCNL A016 — Cooperative e Consorzi Agricoli. Conglobated model. 8 livelli: np-7-6-5-4-3-2-1. Divisore 169, 14 mesi. 4 tranches: apr-2024, mag-2025, mag-2026, feb-2027.
    
    Quadri: i livelli 1Q e 2Q del precedente impianto corrispondono a livello 1° e 2° con aggiunta dell'indennità di funzione quadri (Art. 45): 1Q +EUR 180→230/mese, 2Q +EUR 125→160/mese dal 01/08/2024. Modellata come fixed_allowance a 14 mensilità su ciascun livello.
    

## Raw data

The contract file this page is generated from: [`agreement/cooperative-consorzi-agricoli.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/cooperative-consorzi-agricoli.json).

## Usage example

```python
--8<-- "docs/examples/agreement/cooperative-consorzi-agricoli/example.py"
```
