# CCNL Comparto Funzioni Centrali — Triennio 2022-2024

| | |
|---|---|
| **CNEL code** | `S005` |
| **Sector** | Pubblica Amministrazione — Comparto Funzioni Centrali |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-01-27 |
| **Workers (est.)** | ~250k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - CISL
    - CONFSAL UNSA
    - CONFSAL
    - FLP
    - CGS
    - CONFINTESA FP
    - CONFINTESA
    - UIL PA
    - UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 26 verified / 5 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-01-27 |
| **Last review** | 2026-10-14 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables, additional months, hourly and daily divisors, overtime, leave, sickness and seniority, against the CCNLs of 12 February 2018, 9 May 2022, 27 January 2025 and 6 August 2026. | corrected | Salary amounts confirmed (annual table over 12; elevate professionalità 2022: 35,000 / 13).<br>The first period started on 2022-05-09, the signing date; the new classification applies from 1 November 2022 (art. 18 c. 1).<br>The 2025-2027 values cited a union page; they are now cited to the ARAN text of 6 August 2026 (Tabella 3).<br>Daily quota: art. 29 c. 4 divides by 30, not 26.<br>Overtime is in art. 25 c. 5 of the CCNL 12.2.2018, kept in force by the CCNL 2025-2027.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 24), not 270 days at 100%.<br>Leave: 26 days for the first three years of a first public employment until 31 December 2026 (art. 21 CCNL 2022-2024). |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella 3 of the CCNL of 6 August 2026 for the four areas and the three years; the remaining derived records; the next review date. | confirmed | The twelve monthly amounts (four areas from 1 January 2025, 2026 and 2027) are the annual tabellare of Tabella 3 over 12, to the cent.<br>Perseo Sirio stays derived: the 1% of the employer and of the worker are read in the fund's information sheet, which states the rates in force, not since when; the CCNL does not print them.<br>review_due set to 2027-12-31, the expiry of the 2025-2027 agreement. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATE_PROFESSIONALITA` | Area Elevate Professionalità | € 3,107.21 | 2027-01-01 |
| `FUNZIONARI` | Area Funzionari ed Elevata Qualificazione — Funzionari | € 2,275.39 | 2027-01-01 |
| `ASSISTENTI` | Area Assistenti | € 1,873.56 | 2027-01-01 |
| `OPERATORI` | Area Operatori | € 1,780.57 | 2027-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "funzioni-centrali-aran/ctps_rates_proxy · inps_employer · impact unknown · open"
    aliquote INPS CTPS (ex-INPDAP) — dipendente 8,80%, datore 24,20% — da proxy kitech.it 2026; verificare circolare INPS annuale per valori esatti.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the CTPS rates against the annual INPS circular.

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
| — | — | 2026-08-06 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/08/2026_08_06_CCNL_CFC_2025-2027-1.pdf) |
| — | — | 2025-01-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL_L_C_FC_2022_2024.pdf) |
| — | — | 2022-05-09 | [↗](https://www.aranagenzia.it/wp-content/uploads/2023/05/Frontespizio-e-CCNL-Comparto-Funzioni-Centrali-2019-2021-1.pdf) |
| — | — | 2018-02-12 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL-definitivo-Funzioni-centrali-triennio-2016-2018_firmato_12-2-2018.pdf) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    apprendistato assente dal CCNL vigente (fonte primaria: indice ARAN CCNL 2022-2024, Art. 1-38 senza capitolo apprendistato) e dal CCNL Ministeri 12/6/2003 richiamato dall'Art. 38 Conferme, che esclude espressamente gli apprendisti dall'ambito di applicazione (fonte secondaria: olympus.uniurb.it); quadro normativo PA D.Lgs. 165/2001 non prevede apprendistato ex D.Lgs. 81/2015.
    
    CCNL Funzioni Centrali 2025-2027 (S005) firmato definitivamente il 2026-08-06; in vigore dal 2026-08-07. Incrementi retroattivi al 1/1/2025 e 1/1/2026 liquidati con gli stipendi di agosto/settembre 2026. Tre periodi aggiornati: 2025-01-01, 2026-01-01, 2027-01-01. Fonte: CISL FP (cislfp.it), testo ARAN definitivo non ancora pubblicato su aranagenzia.it al 2026-09-09.
    
    codice CNEL S005 confermato da tre fonti secondarie convergenti: lavoro-economia.it (intestazione pagina "CCNL Comparto Funzioni Centrali [Cnel: S005]"), blia.it (ID S005-209278), contratticcnl.it (/ccnl/s005/). Verificato 2026-09-09.
    
    progressione economica non automatica — differenziali stipendiali assegnati per graduatoria (Art. 16 CCNL 2022-2024); seniority_increments.maximum_count=0.
    
    sub-settori ENAC, ANSFISA, ANSV e AGID hanno tabelle retributive proprie (Tabelle 3-6 CCNL) non modellate — out_of_scope per implementazione standard.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    SALARY TABLES: 1.11.2022-31.12.2023 CCNL 9.5.2022 Tabella H (new classification from 1.11.2022; elevate professionalità art. 53: 35,000 a year with the tredicesima); 2024 CCNL 27.1.2025 Tabella 2; 2025, 2026, 2027 CCNL 6.8.2026 Tabella 3. Monthly = annual / 12, the tredicesima paid apart. Hourly divisor 156 (art. 29 c. 3), daily 30 (art. 29 c. 4).
    

## Raw data

The contract file this page is generated from: [`agreement/funzioni-centrali-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/funzioni-centrali-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/funzioni-centrali-aran/example.py"
```
