# CCNL Area Alimentazione e Panificazione — Artigianato (Confartigianato/CNA)

| | |
|---|---|
| **CNEL code** | `E015` |
| **Sector** | panificazione e alimentazione artigianato |
| **Family** | `alimentare` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-06-06 |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Alimentazione
    - CNA Alimentare
    - Casartigiani
    - CLAAI
    - FAI-CISL
    - FLAI-CGIL
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
| **Limits of this contract** | base_salary, inps_employer, territorial_supplement |

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 47 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-06-06 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2026-04-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-15 | claude-opus-5-5 (ai) | Second review of the artigianato group: retribuzione tabellare and indennità speciale of the ten panificazione levels in the four tranches, monthly payments and scatti, against the signed CCNL of 6 June 2024. | corrected | 39 of the 40 base_salary values equal the tabellare of Art. 32 (pp. 45-47, a scan read from the images) plus the indennità speciale of Art. 33 (p. 48) plus 0.44. A1s from 1 April 2026 was 2248.73: it added the indennità di funzione of 36.15, which Art. 65 (p. 79) grants from 1994 to the quadri of the settore alimentare, not to a panificazione level from 2026. Corrected to 2212.58.<br>The ERR of 0.44 is not in the signed text and no party source states it: the base_salary records stay derived.<br>13 monthly payments: verified (Art. 36, tredicesima; Art. 33, the ex 14a ceased from August 1995).<br>Scatti of Art. 34-bis (p. 49): the ten amounts and the 5 bienni match; the record stays derived because it also holds the apprentice amount, not checked here. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1S` | Level A1 Super — senior executive quadro / top-level manager | € 2,212.58 | 2026-04-01 |
| `B1` | Level B1 — senior operations manager | € 2,165.67 | 2026-04-01 |
| `A1` | Level A1 — production technical manager | € 2,056.93 | 2026-04-01 |
| `A2` | Level A2 — specialist technician / department head | € 1,926.61 | 2026-04-01 |
| `B2` | Level B2 — highly specialised operator | € 1,779.96 | 2026-04-01 |
| `A3` | Level A3 — qualified production technician | € 1,764.45 | 2026-04-01 |
| `B3S` | Level B3 Super — specialist operator with extended duties | € 1,732.79 | 2026-04-01 |
| `B3` | Level B3 — specialist production operator | € 1,676.43 | 2026-04-01 |
| `A4` | Level A4 — qualified support worker | € 1,671.86 | 2026-04-01 |
| `B4` | Level B4 — general worker and first-time hire | € 1,589.80 | 2026-04-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `B4` | € 14.46 |
| `A4` | € 14.46 |
| `B3` | € 16.01 |
| `B3S` | € 17.64 |
| `A3` | € 16.01 |
| `B2` | € 19.11 |
| `A2` | € 17.56 |
| `A1` | € 19.11 |
| `B1` | € 21.69 |
| `A1S` | € 21.69 |

## Apprenticeship

**gruppo_1_panificatori** (type: `percentage`)  
Destination levels: `A1`  
percentage: 1.00

**gruppo_a2_panificatori** (type: `percentage`)  
Destination levels: `A2`  
percentage: 1.00

**gruppo_a3_panificatori** (type: `percentage`)  
Destination levels: `A3`  
percentage: 1.00

**gruppo_b1_addetti** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_b2_addetti** (type: `percentage`)  
Destination levels: `B2`  
percentage: 1.00

**gruppo_b3s_addetti** (type: `percentage`)  
Destination levels: `B3S`  
percentage: 1.00

**gruppo_b4_addetti** (type: `percentage`)  
Destination levels: `B3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "panificazione-artigianato-confartigianato/special_allowance_in_base · base_salary · impact unknown · open"
    IND.SPECIALE: Indennita Speciale art.33 ter is fixed per level and does not change across tranches (confirmed: same amounts from 1995 to date, not subject to renewal increases). Folded into TOTALE base_salary for simplicity; the engine has no per-level fixed-allowance that is non-absorbable and constant — modeling as part of base_salary is the cleanest approach and does not affect any computation. The indennità speciale folded into base_salary takes the apprenticeship percentage and enters the tredicesima; whether Arts. 33, 36 and 58 do so is not confirmed (review of 2026-10-30).

    **Applies when:** `base_salary` applies.

    **Remediation:** Model the indennità speciale of Art. 33 as a fixed allowance per level with its own apprenticeship_pct_relevant flag and thirteenth inclusion as the text states.

!!! warning "panificazione-artigianato-confartigianato/err_unsourced · base_salary · impact unknown · open"
    ERR: an Elemento Retributivo Residuo of 0.44 EUR a month is folded into every base_salary. The signed text of 6 June 2024 (Art. 32-33, pp. 45-48) states the tabellare and the indennità speciale but no ERR, and no party source was found for it: the base_salary records stay derived until the 0.44 is sourced or dropped.

    **Applies when:** `base_salary` applies.

    **Remediation:** Source the 0.44 EUR ERR or drop it from every base_salary.

!!! warning "panificazione-artigianato-confartigianato/ert_veneto · territorial_supplement · impact yes · open"
    ERT (VENETO): Elemento Retributivo Territoriale Veneto (ERT, expired 31.12.2025) was a territorial supplement specific to Veneto. Not modeled at national level.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the Veneto ERT outside the engine for runs before 2026.

!!! warning "panificazione-artigianato-confartigianato/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "panificazione-artigianato-confartigianato/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (artigianato) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles whether the 0.91 NASpI reduction of the artisan employers also applies to apprentices, nor the wage-integration contribution they owe (the FSBA is paid outside INPS). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of artigianato (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/artigianato.json derived, then remove this note.

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

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

### Without monetary impact

!!! note ""
    IND.FUNZIONE: the indennità di funzione of 36.15 EUR a month is owed from 1 April 1994 to the quadri of the settore alimentare (Art. 65, p. 79 of the signed text of 6 June 2024), not to a panificazione level: it is not in the base_salary of A1S. It was added from April 2026 only, citing an Art. 33-quater the text does not have; removed on 15 October 2026.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.uila.eu/web/wp-content/uploads/2022/04/2024-06-06-CCNL-AREA-ALIMENTAZIONE-ARTIGIANATO-PANIFICAZIONE-2023-2026.pdf | altro | 2024-06-06 | [↗](https://www.uila.eu/web/wp-content/uploads/2022/04/2024-06-06-CCNL-AREA-ALIMENTAZIONE-ARTIGIANATO-PANIFICAZIONE-2023-2026.pdf) |
| https://www.artser.it/approfondimenti/accordo-di-rinnovo-del-ccnl-area-alimentazione-e-panificazione.html | tabella_retributiva | — | [↗](https://www.artser.it/approfondimenti/accordo-di-rinnovo-del-ccnl-area-alimentazione-e-panificazione.html) |

??? note "Coverage notes"
    SALARY MODEL: unified TOTALE as base_salary. Each level's TOTALE = Tabellare conglobato (contingenza+EDR absorbed, per Art. 32 + conglobamento clause) + Indennità Speciale per Panificazione (Art. 33, fixed per level since Aug 1995) + ERR (0.44 EUR/month, fixed). Ind.Speciale confirmed from Art. 33 table in UILA CCNL PDF: A1S=94.77, A1=88.06, A2=82.63, A3=75.92, A4=72.05, B1=92.19, B2=76.44, B3S=74.87, B3=72.56, B4=68.69. ERR=0.44. All folded into base_salary; fixed_allowances=[] for all levels. Cross-verified: artser.it tabellare A2 Apr 2024 = 1705.54; 1705.54 + 82.63 + 0.44 = 1788.61 exact match across all 4 tranches (diff constant 83.07 EUR). Art. 31 confirms hourly divisor 173.
    
    ADDITIONAL MONTHS: 13. Art. 33 (Ind.Speciale) replaced the quattordicesima from August 1995 ('viene a cessare, per tutti i lavoratori, la maturazione dei ratei relativi alla ex 14a mensilita'). Art. 36 (Gratifica natalizia) confirms only tredicesima remains. Source: UILA CCNL PDF Art. 33 and Art. 36.
    
    TRANCHE DATES: four tranches — 2024-04-01 (April 2024, first 2024 renewal tranche), 2025-01-01 (January 2025), 2025-11-01 (November 2025), 2026-04-01 (April 2026). Source: ilccnl.it panificazione tables + lavoro-economia.it renewal PDF (CCNL 6 June 2024).
    
    HOURLY DIVISOR: 173, derived from 40-hour work week. Formula: 40 h/week x 52/12 = 173.33, rounded to 173 per contract practice. Verified: A2 Apr 2024 = 1788.61 / 173 = 10.34 EUR/h; A1 Apr 2024 = 1909.58 / 173 = 11.04 EUR/h; B1 Apr 2024 = 2010.49 / 173 = 11.62 EUR/h — consistent divisor 173 across 3 levels, confirming TOTALE model.
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Governed by Art. 34-bis (Aumenti periodici di anzianita per il settore della Panificazione). In force since 1 January 1996 per Art. 34-bis text ('A decorrere dal 1 gennaio 1996, i lavoratori, esclusi gli apprendisti, hanno diritto a maturare aumenti periodici di anzianita per ogni biennio [...] fino ad un massimo di 5 bienni'). The June 2024 renewal (Art. 58 amendment) separately added seniority for APPRENTICES (10 EUR flat from 2025-01-01) — that is a distinct provision. Per-level amounts confirmed from Art. 34-bis table in UILA CCNL PDF: A1S=21.69, A1=19.11, A2=17.56, A3=16.01, A4=14.46, B1=21.69, B2=19.11, B3S=17.64, B3=16.01, B4=14.46 EUR/scatto. valid_from set to 1996-01-01. The apprentice scatto (10 EUR flat from 2025-01-01, Art. 58 as amended by the June 2024 renewal) is modelled as seniority_increments.apprentice_amount.
    
    APPRENTICESHIP: 1° Gruppo (Panificazione Gruppo A livelli A1s, A1 → destination A1, duration 5 anni/10 semestri). Percentages confirmed from Art. 58 table in UILA CCNL PDF (p. 69, Settore Panificazione Gruppo A 1° Gruppo): sem 1-2=70%, sem 3-4=75%, sem 5-6=84%, sem 7-8=90%, sem 9-10=100%. Converted to 12-month periods: 0-12mo=70%, 12-24mo=75%, 24-36mo=84%, 36-48mo=90%, 48-60mo=100%. Source: Art. 58, UILA CCNL PDF. The other gruppi (A2, A3, B1, B2, B3S, B4) are separate tracks, see the APPRENTICESHIP gruppi note. (review of 2026-10-30)
    
    PRE-APRIL-2024: periods before 2024-04-01 are outside the modelled window (2018-2022 CCNL values not included).
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector, existing file).
    
    APPRENTICESHIP gruppi A2, A3, B1, B2, B3S, B4 added from formazione-apprendistato.com panificazione table (medium-high confidence: secondary aggregator + IPSOA 2024 news confirm 2024 rinnovo structure). Semiannual progressions as per Art. 58 + Allegato apprendistato. Gruppo 1° (dest=A1, primary source UILA PDF) unchanged.
    

## Raw data

The contract file this page is generated from: [`agreement/panificazione-artigianato-confartigianato.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/panificazione-artigianato-confartigianato.json).

## Usage example

```python
--8<-- "docs/examples/agreement/panificazione-artigianato-confartigianato/example.py"
```
