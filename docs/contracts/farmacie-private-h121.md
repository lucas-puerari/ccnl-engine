# CCNL Dipendenti delle Farmacie Private

| | |
|---|---|
| **CNEL code** | `H121` |
| **Sector** | Farmacie private |
| **Family** | `farmacie` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-09-07 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERFARMA
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 37 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2021-09-07 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2021-11-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Titolo XVIII - Anzianità di servizio, Art. 51 (p. 23): "Le frazioni di anno sono computate a tutti gli effetti contrattuali per dodicesimi, computando come mese intero le frazioni di mese superiori a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Area Q1 - Direttore responsabile di farmacia | € 1,668.97 | 2021-11-01 |
| `Q2` | Area Q2 - Farmacista collaboratore specializzato | € 1,499.19 | 2021-11-01 |
| `Q3` | Area Q3 - Farmacista collaboratore con 24+ mesi in qualifica | € 1,429.19 | 2021-11-01 |
| `1` | 1o livello - Farmacista collaboratore | € 1,429.19 | 2021-11-01 |
| `2` | 2o livello - Lavoratori di concetto con funzioni di coordinamento | € 1,215.92 | 2021-11-01 |
| `3` | 3o livello - Lavoratori di concetto con conoscenze tecniche | € 1,130.17 | 2021-11-01 |
| `4` | 4o livello - Lavoratori con compiti operativi e conoscenze tecnico-pratiche | € 1,017.02 | 2021-11-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze | € 898.97 | 2021-11-01 |
| `6` | 6o livello - Lavoratori di pulizia e operazioni semplici | € 807.81 | 2021-11-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 25.82 |
| `Q2` | € 25.30 |
| `Q3` | € 25.30 |
| `1` | € 25.30 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.65 |
| `5` | € 20.14 |
| `6` | € 19.62 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "farmacie-private-h121/rural_pharmacy_table · base_salary · impact yes · open"
    SIMPLIFICATION: Farmacie Rurali Sussidiate (Tabella B) excluded. Rural pharmacies have lower base salaries; Tabella A (urban) is modelled only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Tabella B pay of the Farmacie Rurali Sussidiate with a fact selecting it, or refuse such employers.

!!! warning "farmacie-private-h121/isq_twelve_year_tier · base_salary · impact yes · open"
    SIMPLIFICATION: ISQ for Q2 and Q3 modelled at flat 100 EUR (the 2+ anni tier per Tabella C). Workers with 12+ anni receive 130 EUR (delta 30 EUR/month, max ~360 EUR/yr). The 12-year tier is not modelled, although an allowance can be gated on service months (service_months_threshold) (review of 2026-10-30)

    **Applies when:** `base_salary` applies; level in Q2, Q3.

    **Remediation:** Check whether the 12 anni of Tabella C count service or time in the quadro qualification; if service, split the ISQ of Q2/Q3 into a 100 EUR allowance with service_months_until=144 and a 130 EUR one with service_months_threshold=144 (Employment.seniority), otherwise add a worker fact for the qualification time.

!!! warning "farmacie-private-h121/edr_thirteen_months · base_salary · impact yes · open"
    SIMPLIFICATION: EDR (10.33 EUR, Art. 54e) is contractually due for 13 mensilita but the file leaves its months_per_year unset, so the engine also pays it in the quattordicesima. Annual overcount ~10 EUR per worker (review of 2026-10-30)

    **Applies when:** `base_salary` applies.

    **Remediation:** Set months_per_year=13 on the edr allowance of every level, then remove this limitation.

!!! warning "farmacie-private-h121/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf | altro | 2021-09-07 | [↗](https://www.mnlf.it/documenti/ContrattoCollettivoNazionalediLavorodeidipendentidafarmaciaprivata2021.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = retribuzione base nazionale conglobata (Tabella A, Art. 58). fixed_allowances = contingenza (per-level, frozen since 1977 per settore commercio) + EDR 10.33 (all levels, accordo 31/07/1992) + ISQ (Q levels, Tabella C).
    
    Divisore convenzionale 173 confirmed from Art. 57 of primary CCNL text.
    
    Additional months: 14. Art. 62 (13a mensilita) and Art. 63 (14a mensilita) confirmed from primary source.
    
    Seniority: 15 scatti biennali (Art. 53). Amounts from Tabella D (1.2.1996 column) of primary CCNL PDF.
    
    Contract expired 31/08/2024 (Art. 102). No successor signed as of 2026-09-09 (INPS-CNEL spreadsheet updated 25/07/2026 shows Periodo finale=null for H121). Tables valid open-ended under ultrattività.
    
    SIMPLIFICATION resolved: The CCNL rinnovo 07/09/2021 (Tabella A confirmed from UILTUCS primary PDF) established ONE salary tranche from 01/11/2021 — not three separate tranches. Increases vs. Dec 2012 base: Q1=+89.97, Q2=+150.00 (incl. 70 Area Q2), Q3=+80.00, L1=+80.00, L2=+70.98, L3=+67.39, L4=+62.65, L5=+57.72, L6=+53.90. These are fully modelled in this file. The '3 tranches / +113 EUR' figure cited in some secondary sources refers to the separate CCNL farmacie speciali/municipalizzate (Assofarm H122), not this contract.
    
    Apprenticeship from Accordo 14 giugno 2012 (Allegato II). Farmacista collaboratore (dest 1o) stays at level 1o for all 36 months. Commesso/Magazziniere/Contabile (dest 4o): months 0-12 at level 6o, months 13-36 at level 5o.
    
    Headcount: 77,146 workers in 16,324 companies (INPS-CNEL archive, H121).
    
    SIMPLIFICATION: Tabella D groups Q2, Q3, and 1o into a single scatto amount of 25.30 EUR. Q1 uses 25.82 EUR.
    

## Raw data

The contract file this page is generated from: [`agreement/farmacie-private-h121.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/farmacie-private-h121.json).

## Usage example

```python
--8<-- "docs/examples/agreement/farmacie-private-h121/example.py"
```
