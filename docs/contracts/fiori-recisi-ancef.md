# CCNL Fiori Freschi Recisi, Verde e Piante Ornamentali (ANCEF)

| | |
|---|---|
| **CNEL code** | `H201` |
| **Sector** | Fiori recisi, verde e piante ornamentali (import-export) |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-03-30 |
| **Workers (est.)** | ~1.3k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCEF
    - FLAI-CGIL
    - FISASCAT-CISL
    - UIL Tucs

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 38 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-03-30 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Articolo 46 - 13° Mensilità (p. 29): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell’anno, e sempre che sia superato il periodo di prova, il lavoratore avrà diritto a tanti dodicesimi dell’ammontare della tredicesima mensilità per quanti sono i mesi di servizio prestati nell’azienda, intendendo per mese intero, le frazioni pari o superiori a 15 giorni.". Added: at_least 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,700.25 | 2026-01-01 |
| `1S` | 1° Super | € 2,460.21 | 2026-01-01 |
| `1` | 1° livello | € 2,185.36 | 2026-01-01 |
| `2` | 2° livello | € 1,920.48 | 2026-01-01 |
| `3` | 3° livello | € 1,792.57 | 2026-01-01 |
| `4` | 4° livello | € 1,655.26 | 2026-01-01 |
| `5` | 5° livello | € 1,576.97 | 2026-01-01 |
| `6` | 6° livello | € 1,478.65 | 2026-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 34.70 |
| `1S` | € 30.30 |
| `1` | € 29.50 |
| `2` | € 26.90 |
| `3` | € 25.00 |
| `4` | € 23.70 |
| `5` | € 23.10 |
| `6` | € 22.40 |

## Apprenticeship

**professionalizzante - dest livelli 1-2** (type: `under_classification`)  
Destination levels: `1`, `2`  
under-level: `1`

**professionalizzante - dest livelli 3-4** (type: `under_classification`)  
Destination levels: `3`, `4`  
under-level: `1`

**professionalizzante - dest livello 5** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "fiori-recisi-ancef/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.ccnlportatili.it/ccnl/fiori-recisi/ | altro | 2023-03-30 | [↗](https://www.ccnlportatili.it/ccnl/fiori-recisi/) |
| https://www.redigo.info/tabelle-retributive/fiori-recisi-ancef | tabella_retributiva | 2023-03-30 | [↗](https://www.redigo.info/tabelle-retributive/fiori-recisi-ancef) |
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=29864 | altro | 2023-03-30 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=29864) |

??? note "Coverage notes"
    CCNL signed 30/03/2023 by ANCEF, FLAI-CGIL, FISASCAT-CISL, UIL Tucs. Valid 01/01/2023-31/12/2026.
    
    Salary model: conglobated. ilccnl.it shows contingenza=0 and EDR=0 for all levels at 2026-01-01. No split components.
    
    8 levels (highest to lowest): Q, 1S, 1, 2, 3, 4, 5, 6. 4 tranches: 01/01/2023, 01/01/2024, 01/01/2025, 01/01/2026.
    
    Salary values at all 4 tranches confirmed from redigo.info tabelle retributive (structured table, all 8 levels).
    
    Additional months: 14. Art. 38 (tredicesima) + Art. 39 (quattordicesima). Confirmed from FISASCAT announcement.
    
    Hourly divisor: 170. Art. 45 of the CCNL. Confirmed from ccnlportatili.it and ilccnl.it.
    
    Seniority (Art. 48): triennale cadence (36 months), maximum 10 scatti. Per-level amounts confirmed from ccnlportatili.it; Q and 1S and levels 1-2 amounts cross-checked against ilccnl.it (Q=34.70, 1S=30.30, 1=29.50, 2=26.90).
    
    Apprenticeship (Art. 15): under_classification. Durations by destination group confirmed from olympus.uniurb.it (2023 renewal): L1-L2=36mo, L3-L4=30mo, L5=27mo. L5 structure (12mo at lb=1, then lb=0) confirmed from esterinocafasso.it 2023 renewal coverage.
    
    Headcount: 1,341 workers (ADAPT 18 Rapporto CNEL, 2022 UniEmens data). FISASCAT quotes ~15,000 addetti del settore — this is sector-wide (including florists and growers under other CCNLs); ADAPT figure is INPS code H201 only.
    
    L1-L2 and L3-L4 apprenticeship pay progression (2 levels below for first half, 1 level below for second half) confirmed from 2023 renewal news (UILTuCS / farecontrattazione.adapt.it): "due livelli inferiori alla mansione per la prima metà, un livello inferiore per la seconda metà." For L5: 12mo at level 6, then level 5 (from olympus.uniurb.it). Modelled as under_classification tracks (levels_below 2 then 1; L5 1 then 0). Durations are confirmed from olympus.uniurb.it; the internal half-split structure is not independently confirmed from the 2023 CCNL primary text for L1-L4 (review of 2026-10-30)
    
    tax_sector=terziario: ANCEF represents importers and wholesalers of cut flowers (commercio all'ingrosso). The INPS sector code is terziario (commercial trade, ATECO G). Terziario rates (FISASCAT/Confcommercio). This is consistent and confirmed — no dedicated floricoltura INPS sector code exists for the importing/wholesale sub-sector.
    

## Raw data

The contract file this page is generated from: [`agreement/fiori-recisi-ancef.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/fiori-recisi-ancef.json).

## Usage example

```python
--8<-- "docs/examples/agreement/fiori-recisi-ancef/example.py"
```
