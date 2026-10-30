# CCNL Dipendenti Aziende Enti Pubblici Economici Federcasa

| | |
|---|---|
| **CNEL code** | `T611` |
| **Sector** | Case popolari |
| **Family** | `servizi-immobiliari` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-11-06 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federcasa
    - FP CGIL
    - FPS CISL
    - UIL FPL
    - Fesica Confsal

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

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 23 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-11-06 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2024-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 76 - Tredicesima e quattordicesima mensilità (p. 68): "In tali casi il lavoratore non in prova ha diritto a tanti dodicesimi dell'ammontare delle predette mensilità quanti sono i mesi interi di servizio prestato. Le frazioni di mese superiore a quindici giorni vanno computate come un mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Quadro 1 (parametro 220) | € 3,483.40 | 2024-12-01 |
| `Q2` | Quadro 2 (parametro 190) | € 3,001.82 | 2024-12-01 |
| `As` | Area A Super (parametro 176) | € 2,773.72 | 2024-12-01 |
| `A1` | Area A 1 (parametro 162) | € 2,542.96 | 2024-12-01 |
| `A2` | Area A 2 (parametro 150) | € 2,358.35 | 2024-12-01 |
| `A3` | Area A 3 (parametro 138) | € 2,169.12 | 2024-12-01 |
| `Bs` | Area B Super (parametro 137) | € 2,143.87 | 2024-12-01 |
| `B1` | Area B 1 (parametro 135) | € 2,084.39 | 2024-12-01 |
| `B2` | Area B 2 (parametro 128) | € 1,979.16 | 2024-12-01 |
| `B3` | Area B 3 (parametro 121) | € 1,874.51 | 2024-12-01 |
| `C1` | Area C 1 (parametro 118) | € 1,829.95 | 2024-12-01 |
| `C2` | Area C 2 (parametro 114) | € 1,762.49 | 2024-12-01 |
| `C3` | Area C 3 (parametro 110) | € 1,706.87 | 2024-12-01 |
| `Ds` | Area D Super (parametro 108) | € 1,699.39 | 2024-12-01 |
| `D1` | Area D 1 (parametro 103) | € 1,601.65 | 2024-12-01 |
| `D2` | Area D 2 (parametro 100) | € 1,548.03 | 2024-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 14 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 38.25 |
| `Q2` | € 31.50 |
| `As` | € 28.35 |
| `A1` | € 25.20 |
| `A2` | € 22.05 |
| `A3` | € 19.35 |
| `Bs` | € 18.90 |
| `B1` | € 18.45 |
| `B2` | € 16.74 |
| `B3` | € 15.39 |
| `C1` | € 14.85 |
| `C2` | € 13.95 |
| `C3` | € 13.05 |
| `Ds` | € 12.60 |
| `D1` | € 12.06 |
| `D2` | € 11.61 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "federcasa/terziario_rates_proxy · inps_employer · impact unknown · open"
    tax_sector=terziario: Federcasa entities (ex-IACP/ATER/ATC) left the public-sector comparto (Art. 1.2 CCNL Federcasa). Actual INPS classification not publicly documented; terziario is the best available proxy (commercial/housing entities without industria-style CIG). Same approach as other para-public entities in the engine.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the INPS classification of the Federcasa entities and its rates.

!!! warning "federcasa/pre_2018_seniority_cohort · seniority · impact yes · open"
    Seniority amounts use the 10%-reduced values (post-01/01/2018 cohort per Art. 73.4). Workers hired before ~1990 may still have pre-2018 grandfathered scatti at full amounts (engine cannot model the two cohorts separately). New-hire case is exact; long-tenure pre-2018 cohort is understated by ~10%. Structural engine limitation.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the scatti matured before 01/01/2018 at the full amount (Art. 73.4), from the seniority start date or a worker fact.

!!! warning "federcasa/ivc_renewal_gap · base_salary · impact yes · open"
    CCNL expired 31/12/2024. Art. 4 B.5-8 mandates IVC (Indennità Vacanza Contrattuale) at 30% of IPCA (~Mar 2025) and 50% (~Sep 2025) during the renewal gap. Engine models tabellare only; IVC during the gap is not included. This is a structural out-of-scope element (ultrattività compensation, not a tabellare change).

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Source the IVC dates and amounts of Art. 4 B.5-8 (30% then 50% of IPCA) and add them as a time-bound allowance, or close the gap when the renewal is modelled.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://cislfp.it/wp-content/uploads/2024/11/CCNL-Federcasa-2022-2024.pdf | altro | 2024-11-06 | [↗](https://cislfp.it/wp-content/uploads/2024/11/CCNL-Federcasa-2022-2024.pdf) |
| https://cislfp.it/wp-content/uploads/2024/11/Tabelle-economiche-CCNL-Federcasa-2022-2024.pdf | altro | 2024-11-06 | [↗](https://cislfp.it/wp-content/uploads/2024/11/Tabelle-economiche-CCNL-Federcasa-2022-2024.pdf) |
| https://ilccnl.it/ccnl/federcasa/federcasa/tabelleretributive | altro | 2024-11-06 | [↗](https://ilccnl.it/ccnl/federcasa/federcasa/tabelleretributive) |

??? note "Coverage notes"
    Salary model: conglobated. Art. 71 (p.63): retribuzione base = minimi tabellari. Art. 72 (p.64): single importo column, no contingenza or EDR columns. Confirmed by ilccnl.it (A1, A2, A3, As, B1 at 01/12/2024).
    
    16 levels (highest to lowest): Q1, Q2, As, A1, A2, A3, Bs, B1, B2, B3, C1, C2, C3, Ds, D1, D2.
    
    Single salary period from 01/12/2024 (Art. 72). Increases for 2022, 2023, and pre-Dec 2024 paid as una tantum (IVC and arretrati), not as tabellare changes.
    
    Dec 2024 increase formula: NUOVO = round(OLD x 1.075, 2). Confirmed: A1 2365.54 x 1.075 = 2542.96, A2 2193.81 x 1.075 = 2358.35, A3 2017.79 x 1.075 = 2169.12, As 2580.20 x 1.075 = 2773.72, B1 1938.97 x 1.075 = 2084.39 (all matching ilccnl.it to the cent).
    
    Hourly divisor 156 from Art. 71.5: 'un importo pari ad 1/156 della retribuzione individuale mensile'. Also derived from 36h/week x 52/12 = 156.
    
    Art. 71.5 defines 'retribuzione oraria' as 1/156 of monthly including tredicesima and quattordicesima quotas. The engine derives no hourly rate for this CCNL (no verified hourly_base_provenance): overtime and hourly events take the caller's rate, which should include those quotas (review of 2026-10-30)
    
    Additional months: 14. Art. 76 (p.68): tredicesima in December + quattordicesima in June.
    
    Seniority: biennale cadence (Art. 73.1: 'al compimento di ogni biennio'), maximum 14 (Art. 73.2: 'un massimo di 14 aumenti periodici'). Art. 73.4: scatti maturated from 01/01/2018 reduced by 10%.
    
    Apprenticeship: Art. 19 defers terms to accordo interconfederale 18/05/2016 and a CCNL-specific agreement within 6 months of signing. No public text of that agreement found.
    
    Headcount: not verified. No CNEL/ADAPT figure located for T611 Federcasa.
    

## Raw data

The contract file this page is generated from: [`agreement/federcasa.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/federcasa.json).

## Usage example

```python
--8<-- "docs/examples/agreement/federcasa/example.py"
```
