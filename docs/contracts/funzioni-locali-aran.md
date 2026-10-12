# CCNL Comparto Funzioni Locali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S105` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~400k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - UIL FPL
    - CSA RAL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 18 verified / 9 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-02-23 |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables, additional months, hourly and daily divisors, overtime, leave, sickness and seniority, against the CCNL of 16 November 2022 and of 23 February 2026. | corrected | Salary amounts confirmed (annual table over 12).<br>The first period started on 2022-11-16, the signing date; the new classification of Tabella G applies from 1 April 2023 (art. 13 c. 1).<br>Overtime is in art. 32 c. 5 of the CCNL 16.11.2022, not in the CCNL 2022-2024.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 36), not 270 days at 100%.<br>Leave: 26 days for the first three years of a first public employment (art. 28 cc. 4-5).<br>The 2025-2027 renewal is an ipotesi of 21 July 2026, not in force. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `FUNZIONARI_EQ` | Funzionari ed Elevata Qualificazione (ex Area D) | € 2,092.84 | 2026-01-01 |
| `ISTRUTTORI` | Istruttori (ex Area C) | € 1,928.23 | 2026-01-01 |
| `OPERATORI_ESPERTI` | Operatori Esperti (ex Area B) | € 1,715.27 | 2026-01-01 |
| `OPERATORI` | Operatori (ex Area A) | € 1,646.09 | 2026-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "funzioni-locali-aran/renewal_2025_2027_missing · base_salary · impact unknown · open"
    2025-2027 RENEWAL NOT YET MODELLED. ARAN signed an ipotesi di CCNL Funzioni Locali 2025-2027 on 21 July 2026. Retroactive increases from Jan 1, 2025. Pending comitato di settore, Governo, and Corte dei conti certification. Average monthly increase will be around €136.76 from base; exact per-level amounts not yet verified for this file.

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Add the 2025-2027 per-level amounts once the CCNL is certified and signed.

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
| — | — | 2026-02-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/CCNL-Comparto-2022-2024-23-02-26.pdf) |
| — | — | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=396) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Seniority via differenziali stipendiali (Art. 14 and Art. 78 CCNL 16.11.2022): selective procedure, not automatic — maximum_count=0.
    
    CNEL code S105 confirmed via multiple secondary sources: kitech.it lists 'CCNL Comparto Funzioni Locali [Cnel: S105]', lavoro-economia.it concurs. Not stated in official ARAN PDF; CNEL archive not separately queried.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    PENSION FUND. The contractual adherence to Perseo Sirio of art. 98 CCNL 16/11/2022 (polizia locale) is funded by the fines of art. 208 D.Lgs. 285/1992, not by the payroll: it is not modelled.
    
    INDENNITÀ DI COMPARTO: fixed monthly amount per area, paid for 12 months (Tabella C CCNL 23.2.2026): column 1 until 31.12.2025, column 4 from 1.1.2026, after the partial conglobamento of columns 2 and 3 in the tabellare (art. 60).
    
    SALARY TABLES: 1.4.2023-31.12.2023 CCNL 16.11.2022 Tabella G (new classification in force from 1.4.2023); from 1.1.2024 and 1.1.2026 CCNL 23.2.2026 Tabella B. Monthly = annual / 12. The anticipation increments of 2022-2023 and the old categories before 1.4.2023 are not modelled.
    
    Salary tables from CCNL Comparto Funzioni Locali 2022-2024 (ARAN, 23.02.2026). Art. 56 Tabella A (monthly increments per 13 months) and Tabella B (annual amounts per 12 months + 13th). Monthly values = Tabella B / 12.
    
    Tranche 3 (2026-01-01) from parziale conglobamento indennità di comparto (Art. 60): Tabella B col.2 / 12. ARAN announcement explicitly states 'decorrenza retroattiva al 1/1/2026'. DATE CORRECTED 2026-09-09: was incorrectly set to 2027-01-01 in initial extraction; confirmed as 2026-01-01 via ilccnl.it (values match exactly) and ARAN press release.
    
    Hourly divisor 156 from Art. 74 CCNL 16.11.2022 (36h/week standard working time for comparto Funzioni Locali).
    
    13 mensilità confirmed by Art. 56 comma 1 terzo alinea ('per tredici mensilità') and Tabella A header.
    

## Raw data

The contract file this page is generated from: [`agreement/funzioni-locali-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/funzioni-locali-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/funzioni-locali-aran/example.py"
```
