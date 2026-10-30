# CCNL Poste Italiane S.p.A. (personale non dirigente)

| | |
|---|---|
| **CNEL code** | `K700` |
| **Sector** | Servizi postali |
| **Family** | `servizi-postali` |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-23 |
| **Workers (est.)** | ~117k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - POSTE ITALIANE S.p.A.
    - SLP-CISL
    - SLC-CGIL
    - UIL Poste

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority, una_tantum |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 53 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-23 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 67 - Tredicesima mensilità (p. 141): "quanti sono i mesi di servizio prestati presso la Società, computando come mese intero la frazione di mese pari o superiore a 15 giorni.". Match: at_least 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A — posizione retributiva A1 | € 2,169.37 | 2027-12-01 |
| `A2` | Livello A — posizione retributiva A2 | € 1,926.89 | 2027-12-01 |
| `B` | Livello B | € 1,652.98 | 2027-12-01 |
| `C` | Livello C | € 1,522.56 | 2027-12-01 |
| `D` | Livello D | € 1,452.20 | 2027-12-01 |
| `E` | Livello E | € 1,287.61 | 2027-12-01 |
| `F` | Livello F | € 1,154.49 | 2027-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B`, `C`, `D`, `E`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "poste-italiane-k700/edr_pre_privatization · base_salary · impact yes · open"
    SIMPLIFICATION: EDR (elemento distintivo della retribuzione) omitted. Art. 65 I qualifies it as 'ove spettante'; amount not stated in Allegato 9 or CCNL body. Legacy entitlement for pre-privatization workers only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the EDR for pre-privatization workers once its amount is sourced.

!!! warning "poste-italiane-k700/fondo_quiescenza_poste_rates · inps_employer · impact unknown · open"
    SIMPLIFICATION: INPS industria rates applied. Poste Italiane employees are enrolled in the Fondo Quiescenza Poste (INPS special fund, Art. 7 L. 335/1995; merged from IPOST 2012). Correct rates differ from standard industria rates. Verify against INPS Fondo Quiescenza Poste documentation. Verified 2026-09-09: INPS website confirms Fondo Quiescenza Poste exists for Poste Italiane SpA but specific aliquote not publicly listed on INPS portal in machine-readable form.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the Fondo Quiescenza Poste rates and apply them in place of the industria rates.

!!! warning "poste-italiane-k700/legacy_individual_seniority · seniority · impact yes · open"
    SIMPLIFICATION: Legacy retribuzione individuale di anzianità (D.P.R. 335/1990) and posizioni economiche differenziate (CCNL 1997) not modeled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Let the caller state the retribuzione individuale di anzianità and the posizioni economiche differenziate (e.g. EarnedIncrements or an individual allowance) and record the limitation.

!!! warning "poste-italiane-k700/anticipo_lump_sum_2024 · una_tantum · impact yes · open"
    SIMPLIFICATION: Salary tranche 01/07/2024–31/08/2025 covered by one-time 'anticipo sui futuri miglioramenti economici' (lump sum, September 2024). Engine carries paga base at 2024-07-23 level (same as pre-renewal) for that window.

    **Applies when:** `una_tantum` applies; from 2024-09-01.

    **Remediation:** Model the September 2024 anticipo sui futuri miglioramenti economici as an una tantum (or a caller event) and its absorption, or record a limitation for runs of September 2024.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf | altro | 2024-07-23 | [↗](https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = minimo tabellare (Allegato 9, changes each tranche); fixed_allowances = contingenza (per-level, frozen) + indennità di funzione for A1/A2 (months_per_year=12).
    
    Hourly divisor 156 from Art. 65 III: retribuzione base oraria = mensile / 156. Cross-check: 36h/week × 52/12 = 156 h/month (Art. 26 normal workweek = 36h).
    
    Additional months: 14. Art. 67 tredicesima: base = posizione retributiva + contingenza + EDR — funzione excluded. Art. 68 quattordicesima: same explicit enumeration. Both articles confirm funzione not in mensilità aggiuntive.
    
    Seniority: no traditional scatti di anzianità for new hires. Retribuzione individuale di anzianità (D.P.R. 335/1990) is a legacy element for pre-privatization workers only (Art. 25 CCNL). Model: cadence_months=24, maximum_count=0.
    
    A1/A2 levels: paga base and contingenza are identical for staff and produzione; funzione differs (Art. 21 CCNL). Modeled as two-tier allowances: base rate (staff, unconditional) + produzione delta via role="produzione". Pass Employee(roles=frozenset(["produzione"])) to add the differential.
    
    Apprenticeship: Art. 24 CCNL — under_classification, inquadrato al livello immediatamente inferiore per l'intera durata (max 36 mesi). Destinations B, C, D, E. Level A excluded (Quadri e coordinamento/controllo). Level F excluded (lowest, no level below).
    
    Headcount: ~116,801 workers (CNEL/INPS archive, K700).
    
    INDENNITA DI FUNZIONE — PRODUZIONE DIFFERENTIAL: Staff rate (A1: 333.33/mo, A2: 187.50/mo) is unconditional. Produzione workers receive an additional delta (A1: +58.34, A2: +45.83) via IND_FUNZIONE_A*_PROD_DELTA with role="produzione". Total produzione: A1=391.67, A2=233.33 (Art. 21 CCNL K700). Callers: pass Employee(roles=frozenset(['produzione'])) for the higher rate.
    
    SIMPLIFICATION: industria CIGO (1.70-2.00%) included in employer INPS rate. Poste Italiane is not a manufacturing firm and is not CIGO-subject; actual employer cost is lower. Verify against INPS circ. for the correct Poste INPS classification.
    

## Raw data

The contract file this page is generated from: [`agreement/poste-italiane-k700.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/poste-italiane-k700.json).

## Usage example

```python
--8<-- "docs/examples/agreement/poste-italiane-k700/example.py"
```
