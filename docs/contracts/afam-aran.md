# CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, AFAM (Alta formazione artistica, musicale e coreutica)

| | |
|---|---|
| **CNEL code** | `S305` |
| **Sector** | Pubblica Amministrazione |
| **Family** | `pubblico-impiego` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-07-01 |
| **Workers (est.)** | ~1,2M |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FSUR
    - FLC CGIL
    - UIL SCUOLA RUA
    - SNALS CONFSAL
    - GILDA UNAMS
    - ANIEF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | pension_fund_contribution, sickness |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 24 verified / 13 derived / 2 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-07-01 |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-12 | claude-opus-5-5 (ai) | Tabellare and seniority bands of the AFAM staff, 2024-2027. | corrected | New file for the AFAM staff of the comparto Istruzione e Ricerca: Tabella D2 of the CCNL 2022-2024 and 2025-2027, read on the ARAN texts. |
| 2026-10-12 | claude-opus-5-5 (ai) | AFAM allowances, Tabelle D3-D6 of the CCNL 2022-2024 and 2025-2027. | corrected | The AFAM allowances were a limitation (afam_allowances_missing): RPD, RPR, CIA and the retribuzione di posizione are now paid, the 2024 amounts derived from the increments of the CCNL 2022-2024. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DOCENTE_PRIMA_FASCIA` | Docente di prima fascia | € 2,569.53 | 2027-01-01 |
| `ELEVATA_QUALIFICAZIONE` | Area delle Elevate Qualificazioni | € 2,261.86 | 2027-01-01 |
| `RICERCATORE` | Ricercatore | € 2,055.65 | 2027-01-01 |
| `FUNZIONARIO` | Area dei Funzionari | € 1,995.39 | 2027-01-01 |
| `ASSISTENTE` | Area degli Assistenti | € 1,729.56 | 2027-01-01 |
| `OPERATORE` | Area degli Operatori | € 1,551.68 | 2027-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "afam-aran/shared_rules_unchecked · sickness · impact unknown · open"
    SHARED RULES: the hourly divisor, the tredicesima, the leave, absence, sickness and accrual rules are those of the scuola file of the same comparto (istruzione-ricerca-aran), not read again for the AFAM staff. No overtime table is modelled.

    **Applies when:** `sickness` applies.

    **Remediation:** Read the AFAM sections of the CCNL 2019-2021 (18/1/2024) for leave, absence, sickness and overtime.

!!! warning "afam-aran/pension_fund_not_modelled · pension_fund_contribution · impact yes · open"
    PENSION FUND: the AFAM staff join the Fondo Espero, not modelled in this file.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Fondo Espero rates of the AFAM staff.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL 2025-2027 sui principali aspetti del trattamento economico, signed definitively on 1 July 2026 by ARAN and every union of the comparto. Tabella A2 (pp. 18-19): tabellare from 1.1.2025, 1.1.2026, 1.1.2027. | altro | 2026-07-01 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/07/2026_07_01_CCNL_C_IR_2025-2027.pdf) |
| CCNL 2022-2024 (FLC CGIL did not sign). Tabella A2 (pp. 50-51): tabellare from 1.1.2024. | altro | 2025-12-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/12/2025_12_23_COMP-IR_2022-2024.pdf) |
| CCNL 2019-2021. Tabelle C1 and E1.5 (pp. 246, 256): tabellare from 1.2.2023. | altro | 2024-01-18 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/01/2024_01_18_COMP-IR_2019-2021.pdf) |
| CCNL Scuola 2006-2009, still in force for ferie (art. 13), malattia (art. 17) and tredicesima (art. 80). | altro | 2007-11-29 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/07/CCNL-SCUOLA-2006-2009.pdf) |

??? note "Coverage notes"
    SCOPE: staff of the AFAM institutions (accademie, conservatori, ISIA): Aree Operatori, Assistenti, Funzionari, Elevate Qualificazioni (new classification of art. 165 CCNL 18/1/2024 from 1.5.2024, allegato J), docenti di prima fascia and ricercatori, with seven bands of anzianità di servizio (Tabella D2 of the CCNL 2022-2024 and 2025-2027) as seniority steps, from 1.1.2024.
    
    ALLOWANCES: RPD of the docenti (Tabella D3) and RPR of the ricercatori (D4) by band of anzianità di servizio (0-14, 15-27, 28 years and more), the CIA of operatori, assistenti and funzionari (D6), 12 instalments; the retribuzione di posizione parte fissa of the Elevate Qualificazioni (D5), annual over 12 (assumed). The banded allowances need the seniority of the worker.
    

## Raw data

The contract file this page is generated from: [`agreement/afam-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/afam-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/afam-aran/example.py"
```
