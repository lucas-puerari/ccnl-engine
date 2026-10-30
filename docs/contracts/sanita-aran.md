# CCNL Comparto Sanità 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S205` |
| **Sector** | Pubblica Amministrazione |
| **Family** | `pubblico-impiego` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-10-27 |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - FIALS
    - NURSIND
    - NURSING UP
    - CISL
    - CONFSAL
    - CGS
    - CSE

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

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 16 verified / 5 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-27 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2024-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables, additional months, hourly and daily divisors, overtime, leave, sickness and seniority, against the CCNL of 2 November 2022 and the definitive CCNL of 27 October 2025. | corrected | Salary amounts confirmed (annual table over 12; elevata qualificazione 2023: 35,000 / 13).<br>The first period started on 2022-11-02, the signing date; the new classification applies from 1 January 2023 (art. 99 c. 3).<br>Overtime is art. 47 c. 8 of the CCNL 2.11.2022, in force from 2022, not from 2024.<br>Citations moved from the ipotesi of January 2025 (other article numbers) to the definitive text of 27 October 2025.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 40), not 270 days at 100%.<br>Leave: 26 days for the first three years of a first public employment (art. 35 c. 4).<br>Signatories: FP CGIL and UIL FPL did not sign; CONFSAL, CGS, CSE and CISL signed.<br>The 2025-2027 renewal is an ipotesi of 29 July 2026, not in force. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-31: the tabellare of 2024 against Tabella 2a of the CCNL of 27 October 2025, and the status of the 2025-2027 renewal. | confirmed | Tabella 2a (p. 107): the five annual amounts from 1 January 2024 over 12 give the monthly amounts of the file (21.545,34 / 12 = 1.795,445, 1.795,45 half up). Match.<br>The 2025-2027 renewal is still the ipotesi of 29 July 2026 on 2026-10-17; renewal_2025_2027_not_modelled stays open with the status recorded. The next review is moved to 2027-01-31.<br>No independent example (an ARAN worked example or a real payslip of the comparto) was found in this review. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATA_QUALIFICAZIONE` | Elevata qualificazione (ex area DS dirigenza) | € 2,886.21 | 2024-01-01 |
| `PROFESSIONISTI` | Professionisti della salute e funzionari (ex area D/DS) | € 2,076.58 | 2024-01-01 |
| `ASSISTENTI` | Assistenti (ex area C/C1) | € 1,913.48 | 2024-01-01 |
| `OPERATORI` | Operatori (ex area B/B1) | € 1,795.45 | 2024-01-01 |
| `SUPPORTO` | Personale di supporto (ex area A/A1) | € 1,701.59 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sanita-aran/nursing_specificity_allowance · base_salary · impact yes · open"
    Indennità di specificità infermieristica (Art. 62, Tabella 3) not modelled as fixed_allowance — applies only to specific nursing profiles (infermieri, ostetriche), not universally to all area members.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model l'indennità di specificità infermieristica (Art. 62, Tabella 3) as an allowance gated by a role (infermieri, ostetriche) or record a limitation.

!!! warning "sanita-aran/renewal_2025_2027_not_modelled · base_salary · impact unknown · open"
    2025-2027 RENEWAL NOT YET MODELLED. An ipotesi di CCNL 2025-2027 was signed by ARAN on 29 July 2026 with retroactive effect from 1 January 2025. Increases (monthly, 13 mensilità) from Jan 2024 base: support +41.40 (Jan 2025)/+82.80 (Jan 2026)/+106.70 (Jan 2027); operatori +43.70/+87.40/+112.60; assistenti +46.60/+93.20/+120.00; funzionari +50.50/+101.10/+130.20; elevata qualificazione +70.20/+140.50/+181.00. Not yet modelled — ipotesi pending comitato di settore, Governo, and Corte dei conti certification. STATUS CHECKED 2026-10-17: still an ipotesi (signed text of 29 July 2026, lentepubblica.it copy); no definitive signature found on 2026-10-17.

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Model the 2025-2027 increases once the ipotesi is certified and signed.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| CCNL Comparto Sanità 2022-2024 signed definitively on 27 October 2025 (FP CGIL and UIL FPL did not sign). Tabella 2a (p. 107), art. 59 (divisors), art. 60 (tredicesima), art. 35 (ferie), art. 40 (malattia). | altro | 2025-10-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/10/2025_10_27_COMP-SANITA_2022-2024.pdf) |
| CCNL 2019-2021. Tabella D (p. 167), art. 99 (classification from 1.1.2023), art. 100 (elevata qualificazione), art. 47 (straordinario). | altro | 2022-11-02 | [↗](https://www.aranagenzia.it/wp-content/uploads/2022/11/2022_11_02_COMP-SANITA_2019-2021.pdf) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Seniority via DEP (Differenziali Economici di Professionalità) per Art. 60 Fondo incarichi: selective procedure, not automatic — maximum_count=0.
    
    CNEL code S205 confirmed via multiple secondary sources: lavoro-economia.it lists 'CCNL Comparto Sanità [Cnel: S205]', kitech.it and ilccnl.it concur. Not stated in the official ipotesi PDF text; CNEL archive not separately verified.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    SALARY TABLES: 1.1.2023-31.12.2023 CCNL 2.11.2022 Tabella D (new classification from 1.1.2023; elevata qualificazione art. 100: 35,000 a year with the tredicesima); from 1.1.2024 CCNL 27.10.2025 Tabella 2a. Monthly = annual / 12, the tredicesima paid apart. The old categories of November and December 2022 and the anticipation increments are not modelled. Overtime hourly base: art. 47 c. 7 counts the retribuzione base with the rateo of tredicesima over 156; the run takes the hourly rate the caller states.
    

## Raw data

The contract file this page is generated from: [`agreement/sanita-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/sanita-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/sanita-aran/example.py"
```
