# CCNL Energia e Petrolio (Confindustria Energia)

| | |
|---|---|
| **CNEL code** | `B254` |
| **Sector** | energia |
| **Family** | `energia-utilities` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-04-16 |
| **Workers (est.)** | ~38k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Energia
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
| **Core payroll path** | ✅ |
| **Limits of this contract** | — |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 171 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-16 |
| **Last review** | — |
| **Latest salary tranche** | 2027-07-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1-5` | Quadro Gruppo 1/5 — manager, fifth CREA tier (highest) | € 3,748.10 | 2027-07-01 |
| `1-4` | Quadro Gruppo 1/4 — manager, fourth CREA tier | € 3,748.10 | 2027-07-01 |
| `1-3` | Quadro Gruppo 1/3 — manager, third CREA tier | € 3,748.10 | 2027-07-01 |
| `1-2` | Quadro Gruppo 1/2 — manager, second CREA tier | € 3,748.10 | 2027-07-01 |
| `1-1` | Quadro Gruppo 1/1 — manager, first CREA tier | € 3,748.10 | 2027-07-01 |
| `2-4` | Gruppo 2/4 — specialist workers, fourth function allowance tier | € 3,394.47 | 2027-07-01 |
| `2-3` | Gruppo 2/3 — specialist workers, third function allowance tier | € 3,394.47 | 2027-07-01 |
| `2-2` | Gruppo 2/2 — specialist workers, second function allowance tier | € 3,394.47 | 2027-07-01 |
| `2-1` | Gruppo 2/1 — specialist workers, first function allowance tier | € 3,394.47 | 2027-07-01 |
| `3-4` | Gruppo 3/4 — senior workers, fourth function allowance tier | € 3,074.11 | 2027-07-01 |
| `3-3` | Gruppo 3/3 — senior workers, third function allowance tier | € 3,074.11 | 2027-07-01 |
| `3-2` | Gruppo 3/2 — senior workers, second function allowance tier | € 3,074.11 | 2027-07-01 |
| `3-1` | Gruppo 3/1 — senior workers, first function allowance tier | € 3,074.11 | 2027-07-01 |
| `4-4` | Gruppo 4/4 — skilled workers, fourth function allowance tier | € 2,716.61 | 2027-07-01 |
| `4-3` | Gruppo 4/3 — skilled workers, third function allowance tier | € 2,716.61 | 2027-07-01 |
| `4-2` | Gruppo 4/2 — skilled workers, second function allowance tier | € 2,716.61 | 2027-07-01 |
| `4-1` | Gruppo 4/1 — skilled workers, first function allowance tier | € 2,716.61 | 2027-07-01 |
| `5-4` | Gruppo 5/4 — standard workers, fourth function allowance tier | € 2,382.32 | 2027-07-01 |
| `5-3` | Gruppo 5/3 — standard workers, third function allowance tier | € 2,382.32 | 2027-07-01 |
| `5-2` | Gruppo 5/2 — standard workers, second function allowance tier | € 2,382.32 | 2027-07-01 |
| `5-1` | Gruppo 5/1 — standard workers, first function allowance tier | € 2,382.32 | 2027-07-01 |
| `5-0` | Gruppo 5/0 — standard workers, base position (no function allowance) | € 2,382.32 | 2027-07-01 |
| `6-0` | Gruppo 6/0 — entry-level workers, basic routine operations | € 2,072.49 | 2027-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**livelli_2_3** (type: `percentage`)  
Destination levels: `2-1`, `2-2`, `2-3`, `2-4`, `3-1`, `3-2`, `3-3`, `3-4`  
percentage: 0.95

**livello_4** (type: `percentage`)  
Destination levels: `4-1`, `4-2`, `4-3`, `4-4`  
percentage: 0.95

**livello_5** (type: `percentage`)  
Destination levels: `5-0`, `5-1`, `5-2`, `5-3`, `5-4`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

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
    APPRENTICESHIP LEVEL 6: percentages not found in any consulted source (previdenza-professionisti.it lists only tracks for levels 2-3, 4, 5). Level 6-0 omitted from apprenticeship tracks.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.redigo.info/2025/08/06/tabelle-retributive-ccnl-energia-e-petrolio/ | tabella_retributiva | 2025-04-16 | [↗](https://www.redigo.info/2025/08/06/tabelle-retributive-ccnl-energia-e-petrolio/) |
| https://www.previdenza-professionisti.it/diritto-del-lavoro/ccnl-energia-e-petrolio---scheda.html | altro | 2025-04-16 | [↗](https://www.previdenza-professionisti.it/diritto-del-lavoro/ccnl-energia-e-petrolio---scheda.html) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=B254 | tabella_retributiva | 2026-07-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=B254) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = paga_base (minimi tabellari) only. fixed_allowances per level include: (1) EDR_IPCA — Elemento Distinto della Retribuzione, group-specific TimeSeries from Jul 2025; (2) INDENNITA_FUNZIONE — level-specific function allowance (constant for groups 2-6, TimeSeries Jul 2025=190/Jan 2027=200 for group 1 quadri); (3) CREA — level-specific, constant, group 1 only. Total paga tabellare = base_salary + INDENNITA_FUNZIONE + CREA; verified against kitech at Jul 2026 (exact match 23/23 levels).
    
    MODELLED TRANCHES: 2025-07-01 (first tranche, new CCNL 2025-2027), 2025-12-01 (second), 2026-01-01 (third), 2026-07-01 (fourth), 2027-07-01 (fifth and final). Jan-Jun 2025 retroactive tranche (ipotesi signed 2025-04-16) not modelled — belongs to the transition period of the previous CCNL.
    
    EDR IPCA: introduced 2025-03-01 (pre-modelled). First modelled period from 2025-07-01 at increased amounts: G1=60.71, G2=54.98, G3=49.79, G4=44.00, G5=38.59, G6=33.57. Second period from 2026-01-01: G1=70.37, G2=63.73, G3=57.71, G4=51.00, G5=44.73, G6=38.91. Open-ended (no further increase published). Source: redigo.info.
    
    FUNCTION ALLOWANCE GROUP 1 (indennità di funzione quadri): 190 EUR/month for all 14 mensilità, valid 2025-07-01 to 2026-12-31; increases to 200 EUR from 2027-01-01. Source: contratticcnl.it (CCNL 2025-2027). Constant for groups 2-5; absent for group 6.
    
    CREA (Compenso per Risultato ed Eccellenza Aziendale): only for group 1 (quadri). Amounts from kitech Jul 2026 back-calculation: 1-1=90.65, 1-2=181.31, 1-3=271.96, 1-4=362.61, 1-5=453.26. Constant throughout the contract (no source indicates time variation).
    
    CATEGORY: group 1 levels (1-1 through 1-5) are Quadri under L. 190/1985. Groups 2-6 are impiegati/operai; category omitted as the CCNL does not publish a clean impiegato/operaio split by level.
    
    SENIORITY INCREMENTS: abolished from 2016-01-01 by the 2016 CCNL renewal. Amounts accrued up to 2015 are crystallised as a personal supplement. Modelled as maximum_count=0, amount_by_level={}, cadence_months=24 (historical biennial cadence).
    
    HOURLY DIVISOR: 174.5 h/month (confirmed from previdenza-professionisti.it and lavoro-economia.it for CCNL B254). The CCNL states EDR is 'omnicomprensivo' with no impact on other contractual institutes. The engine derives no hourly rate for this CCNL (no verified work_rules.time_supplements.hourly_base_provenance: overtime takes the caller's rate); when derived, hourly_base_method=minimo_tabellare leaves the EDR out. All monthly and annual figures are unaffected (review of 2026-10-30)
    
    ADDITIONAL MONTHS: 14 (tredicesima December + quattordicesima June). Source: previdenza-professionisti.it.
    
    INPS: uses 2026-industria.json (standard industry sector). CNEL code: B254.
    
    APPRENTICESHIP: percentage type, 3 tracks (livelli_2_3, livello_4, livello_5). Source: previdenza-professionisti.it (2025-04-16 CCNL). Livelli 2-3 max 24 months (90% for first 12m, 95% thereafter). Livello 4 max 36 months (90% for first 12m, 95% thereafter). Livello 5 max 36 months (80% for first 12m, 90% thereafter). Reference retribution per CCNL Art.: 'il minimo del livello di inquadramento e del relativo CREA'.
    
    APPRENTICESHIP REFERENCE BASE: per CCNL, reference is 'minimo tabellare e relativo CREA'. Modelled correctly: INDENNITA_FUNZIONE and INDENNITA_FUNZIONE_QUADRI set apprenticeship_pct_relevant=false (paid at full value, not reduced); EDR set apprenticeship_pct_relevant=false (omnicomprensivo, no impact on other institutes); CREA set apprenticeship_pct_relevant=true (explicitly in CCNL base for group 1).
    
    FUNCTION ALLOWANCE GROUPS 2-5: amounts assumed constant throughout 2025-2027 CCNL. No published text or renewal announcement indicates a change to these allowances. Values from kitech Jul 2026. In the energia-petrolio sector, INDENNITA_FUNZIONE is a fixed contractual element rarely changed mid-contract; constancy is consistent with historical pattern.
    
    CREA CONSTANCY: CREA amounts assumed constant throughout 2025-2027 (no source indicates time variation). Values from kitech Jul 2026. CREA is a fixed contractual element (Compenso per Risultato Aziendale Aggiuntivo) set at contract-level; constancy is standard for this type of element.
    

## Raw data

The contract file this page is generated from: [`agreement/energia-petrolio-confindustria.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/energia-petrolio-confindustria.json).

## Usage example

```python
--8<-- "docs/examples/agreement/energia-petrolio-confindustria/example.py"
```
