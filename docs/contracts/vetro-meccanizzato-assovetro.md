# CCNL Vetro (Industrie) — Settori Meccanizzati (Prime Lavorazioni)

| | |
|---|---|
| **CNEL code** | `B132` |
| **Sector** | vetro industria — settori meccanizzati |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-04-09 |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assovetro
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

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
| **Extraction method** | 🧑 Manual | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 0 derived / 35 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟡 Needs review | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-04-09 |
| **Last review** | 2026-10-12 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-17 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | File-level confidence against the provenance of its payable rules; no value re-read. | flagged | confidence was 'verified' while no payable rule is verified, 35 are assumed and the accrual rule is missing; the review of 2026-09-17 recorded neither the documents it read nor the values it checked. Confidence set to needs_review until the values are read in the signed text. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A` | Livello A — base | € 2,874.69 | 2026-01-01 |
| `B` | Livello B — base | € 2,616.86 | 2026-01-01 |
| `C` | Livello C — base | € 2,354.05 | 2026-01-01 |
| `D` | Livello D — base | € 2,080.92 | 2026-01-01 |
| `E` | Livello E — base | € 1,822.13 | 2026-01-01 |
| `F` | Livello F — base | € 1,683.88 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 17.56 |
| `B` | € 16.53 |
| `C` | € 14.98 |
| `D` | € 12.91 |
| `E` | € 10.33 |
| `F` | € 8.26 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "vetro-meccanizzato-assovetro/other_subsectors_tables · base_salary · impact yes · open"
    SCOPE: Settori meccanizzati (prime lavorazioni) only — 6 base sub-levels (A, B, C, D, E, F). Other sub-sectors (trasformazione, soffio, lampade e display) and sub-levels (A2, B2, C2, D2, D3, E2, E3) not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the trasformazione, soffio and lampade e display tables with a sub-sector input, or record the limitation.

!!! warning "vetro-meccanizzato-assovetro/seniority_assumed_constant · seniority · impact unknown · open"
    SENIORITY: 5 biennial scatti (cadence 24 months, max 5). Per-level amounts sourced from kitech.it Jan 2026: A=17.56, B=16.53, C=14.98, D=12.91, E=10.33, F=8.26 EUR. Historical amounts assumed stable (not verified for 2023-2025 periods).

    **Applies when:** `seniority` applies.

    **Remediation:** Source the scatto amounts of the 2023-2025 periods (or confirm unchanged) and record the limitation for runs before 2026-01-01.

!!! warning "vetro-meccanizzato-assovetro/tranches_from_october_2026 · base_salary · impact yes · open"
    TRANCHE 2026-2028: Only the Jan 2026 tranche is modelled (retroactive from renewal 2026-04-09). Remaining tranches at D1: +15 EUR Oct 2026, +30 EUR Jan 2027, +25 EUR Jun 2027, +75 EUR Jul 2028. Per-level amounts confirmed proportional (A:D=1.5, F:D=0.7462) but official per-level tables not publicly available at extraction date 2026-09-17.

    **Applies when:** `base_salary` applies; from 2026-10-01.

    **Remediation:** Add the October 2026 to July 2028 tranches once the per-level tables are published.

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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

### Without monetary impact

!!! note ""
    APPRENTICESHIP: not modelled. Under-classification type confirmed (first half: 2 levels below; second half: 1 level below). Total duration not verified from post-2026 source.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Settori meccanizzati Vetro Industrie — KITech | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=215) |
| Industrie del Vetro, Lampade e Display — Tabelle retributive 2023-2025 | tabella_retributiva | — | [↗](https://esterinocafasso.it/rubrica-mensile/industrie-del-vetro-lampade-e-display-nuovo-ccnl-diffuse-le-tabelle-dei-minimi-retributivi/) |
| CCNL Vetro Meccanizzato Industria — ilCCNL.it tabelle retributive | tabella_retributiva | — | [↗](https://ilccnl.it/ccnl/vetro---industria/vetro-meccanizzato---industria/tabelleretributive) |
| Accordo di rinnovo CCNL Vetro Industrie 2026-2028 — Assovetro | altro | — | [↗](https://confindustriatoscanacentroecosta.it/ccnl-vetro-industria-ipotesi-di-accordo-e-nuovi-minimi-tabellari/) |

??? note "Coverage notes"
    SALARY MODEL: split — base_salary = minimo tabellare (paga base); fixed_allowance TER = Terzo Elemento della Retribuzione (EDR, 10.33 EUR, frozen). Sources: esterinocafasso.it for 2023-03-01 / 2024-01-01 / 2025-04-01 periods; kitech.it + ilccnl.it for 2026-01-01.
    
    HOURLY_DIVISOR: 173 — confirmed by ilccnl.it tabelle retributive (divisore orario column, 2026-01-01). Back-check D1: (2080.92+10.33)/173 = 12.09 EUR/h.
    
    FONCHIM: employer contribution 1.5%, raised by 0.5% to 2.0% from 1 January 2027 by the renewal of 9 April 2026 (source: Confindustria Toscana Centro e Costa summary of the ipotesi di accordo). No employee minimum is bundled.
    

## Raw data

The contract file this page is generated from: [`agreement/vetro-meccanizzato-assovetro.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/vetro-meccanizzato-assovetro.json).

## Usage example

```python
--8<-- "docs/examples/agreement/vetro-meccanizzato-assovetro/example.py"
```
