# CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN, Enti pubblici di ricerca (ASI compresa)

| | |
|---|---|
| **CNEL code** | `S305` |
| **Sector** | Pubblica Amministrazione |
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
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, pension_fund_contribution, sickness |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 32 verified / 4 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
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
| 2026-10-12 | claude-opus-5-5 (ai) | Tabellare and seniority bands of the research bodies, 2024-2027. | corrected | New file for the research bodies of the comparto Istruzione e Ricerca: Tabelle C3 and C4 of the CCNL 2022-2024 and 2025-2027, read on the ARAN texts. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `I` | Livello I - Dirigente di ricerca e Dirigente tecnologo | € 4,803.99 | 2027-01-01 |
| `II` | Livello II - Primo ricercatore e Primo tecnologo | € 3,724.23 | 2027-01-01 |
| `III` | Livello III - Ricercatore e Tecnologo | € 2,940.70 | 2027-01-01 |
| `IV` | Livello IV (personale tecnico e amministrativo) | € 2,637.25 | 2027-01-01 |
| `V` | Livello V (personale tecnico e amministrativo) | € 2,396.19 | 2027-01-01 |
| `VI` | Livello VI (personale tecnico e amministrativo) | € 2,204.83 | 2027-01-01 |
| `VII` | Livello VII (personale tecnico e amministrativo) | € 2,019.58 | 2027-01-01 |
| `VIII` | Livello VIII (personale tecnico e amministrativo) | € 1,910.33 | 2027-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "enti-ricerca-aran/research_allowances_missing · base_salary · impact yes · open"
    ALLOWANCES: the indennità di Ente of levels IV-VIII (Tabella C5) and the indennità di valorizzazione professionale of levels I-III (Tabella C6) are stated by the CCNL only as increments from 1.1.2027, their earlier amounts set by older contracts not read: not modelled, the caller pays them.

    **Applies when:** `base_salary` applies.

    **Remediation:** Read the indennità di Ente and di valorizzazione professionale of the earlier CCNL and add them with the 2027 increments.

!!! warning "enti-ricerca-aran/shared_rules_unchecked · sickness · impact unknown · open"
    SHARED RULES: the hourly divisor, the tredicesima, the leave, absence, sickness and accrual rules are those of the scuola file of the same comparto (istruzione-ricerca-aran), not read again for the research bodies. No overtime table is modelled.

    **Applies when:** `sickness` applies.

    **Remediation:** Read the research sections of the CCNL 2019-2021 (18/1/2024) for leave, absence, sickness and overtime.

!!! warning "enti-ricerca-aran/perseo_sirio_not_modelled · pension_fund_contribution · impact yes · open"
    PENSION FUND: the staff of the research bodies join the Fondo Perseo Sirio, not modelled here.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the employer and employee rates of Fondo Perseo Sirio.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL 2025-2027 sui principali aspetti del trattamento economico, signed definitively on 1 July 2026 by ARAN and every union of the comparto. Tabella A2 (pp. 18-19): tabellare from 1.1.2025, 1.1.2026, 1.1.2027. | altro | 2026-07-01 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/07/2026_07_01_CCNL_C_IR_2025-2027.pdf) |
| CCNL 2022-2024 (FLC CGIL did not sign). Tabella A2 (pp. 50-51): tabellare from 1.1.2024. | altro | 2025-12-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/12/2025_12_23_COMP-IR_2022-2024.pdf) |
| CCNL 2019-2021. Tabelle C1 and E1.5 (pp. 246, 256): tabellare from 1.2.2023. | altro | 2024-01-18 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/01/2024_01_18_COMP-IR_2019-2021.pdf) |
| CCNL Scuola 2006-2009, still in force for ferie (art. 13), malattia (art. 17) and tredicesima (art. 80). | altro | 2007-11-29 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/07/CCNL-SCUOLA-2006-2009.pdf) |

??? note "Coverage notes"
    SCOPE: staff of the enti pubblici di ricerca (ASI included): levels IV-VIII (Tabella C3, one tabellare) and the ricercatori and tecnologi of levels I-III (Tabella C4, seven bands of anzianità di servizio as seniority steps), from 1.1.2024 (CCNL 2022-2024) and 2025-2027 (CCNL 2025-2027).
    

## Raw data

The contract file this page is generated from: [`agreement/enti-ricerca-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/enti-ricerca-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/enti-ricerca-aran/example.py"
```
