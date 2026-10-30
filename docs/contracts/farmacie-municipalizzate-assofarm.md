# CCNL Dipendenti delle Farmacie Municipalizzate (ASSOFARM)

| | |
|---|---|
| **CNEL code** | `H124` |
| **Sector** | Farmacie municipalizzate e partecipate da enti locali |
| **Family** | `farmacie` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2022-07-07 |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSOFARM
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, seniority |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 45 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2022-07-07 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2024-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Articolo 20 - Tredicesima e quattordicesima mensilita' (p. 20): "Le frazioni di mese pari o superiori a 15 giorni vengono computate come mese intero e si trascurano quelle inferiori.". Match: at_least 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | 1o livello Q - Direttore responsabile e area manager | € 2,456.91 | 2024-07-01 |
| `1S` | 1o livello super - Direttore responsabile con funzioni direttive | € 2,372.46 | 2024-07-01 |
| `1C` | 1o livello C - Farmacista collaboratore con funzioni speciali | € 2,266.37 | 2024-07-01 |
| `1_12` | 1o livello + 12 anni - Farmacista collaboratore con 12+ anni di servizio | € 2,109.97 | 2024-07-01 |
| `1_2` | 1o livello + 2 anni - Farmacista collaboratore con 24+ mesi di servizio | € 2,109.97 | 2024-07-01 |
| `1` | 1o livello - Farmacista collaboratore | € 2,109.97 | 2024-07-01 |
| `2` | 2o livello - Lavoratori con funzioni di coordinamento o tecnico-specialistiche | € 1,872.16 | 2024-07-01 |
| `3` | 3o livello - Lavoratori con conoscenze tecnico-pratiche qualificate | € 1,777.29 | 2024-07-01 |
| `4` | 4o livello - Lavoratori con compiti esecutivi e conoscenze tecnico-pratiche | € 1,652.61 | 2024-07-01 |
| `5` | 5o livello - Lavoratori qualificati con normali conoscenze operative | € 1,522.17 | 2024-07-01 |
| `6` | 6o livello - Lavoratori con mansioni di pulizia e operazioni semplici | € 1,421.48 | 2024-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 15 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 26.50 |
| `1S` | € 25.82 |
| `1C` | € 25.31 |
| `1_12` | € 25.31 |
| `1_2` | € 25.31 |
| `1` | € 25.31 |
| `2` | € 23.24 |
| `3` | € 22.72 |
| `4` | € 20.66 |
| `5` | € 20.14 |
| `6` | € 19.63 |

## Apprenticeship

**farmacista_collaboratore** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante** (type: `under_classification`)  
Destination levels: `4`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "farmacie-municipalizzate-assofarm/terziario_rates_proxy · inps_employer · impact unknown · open"
    INPS RATES. Terziario proxy used. ASSOFARM entities operate as aziende speciali or società di gestione farmacia (private-law entities under municipal control); the contract is registered CNEL H124 and negotiated by UGL Terziario — standard private-sector INPS regime (terziario) is the expected classification. Note: CCNL text references "INPS Gestione ex INPDAP" in benefit provisions, suggesting legacy workers transferred from public-sector management may retain the ex-INPDAP pension regime — contribution rates for those workers differ. No sector-specific INPS circular identified; kitech.it does not list a dedicated contribution table for farmacie municipalizzate. Simplification retained.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification against a sector circular, including ex-INPDAP legacy workers.

!!! warning "farmacie-municipalizzate-assofarm/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf | altro | 2022-07-07 | [↗](https://www.assofarm.it/wp-content/uploads/2024/12/CCNL2022.2024.signedcorrect.pdf) |

??? note "Coverage notes"
    Salary model: conglobated. Allegato B shows unified retribuzione di base with no separate contingenza or EDR columns. Back-calculation: L1=2109.97/173=12.20 EUR/h, L3=1777.29/173=10.27 EUR/h, L6=1421.48/173=8.22 EUR/h (all consistent with divisor 173).
    
    Hourly divisor 173: Art. 18 explicit: 'La quota oraria di retribuzione si ottiene dividendo la retribuzione mensile per 173'.
    
    Additional months: 14. Art. 20 explicit: quattordicesima (luglio) + tredicesima (dicembre).
    
    IQ (Indennita Quadri): Allegato C, effective 01/07/2022. Levels 1Q=160, 1S=150, 1C=145 EUR/month.
    
    IS (Indennita Speciale): Art. 19bis + Allegato A. Level 1+12anni=130, Level 1+2anni=100 EUR/month. Unchanged in 2022 renewal (Allegato C covers only IQ increments; Art. 19bis refers to Tabella A 2015 values).
    
    Seniority: 15 scatti biennali per Allegato E, decorrenza 1 gennaio 2014.
    
    Apprenticeship: Allegato F, under-classification. Farmacista collaboratore stays at Primo livello for all 36 months (levels_below=0). Non-pharmacist roles (Coadiutore, Capo settore, Addetto amministrativo): months 1-12 at Sesto, months 13-36 at Quinto, exit Quarto.
    
    Contract valid 07/07/2022-31/12/2024, ultrattivo since 01/01/2025 (no successor deposited at CNEL as of 2026-09-05). Third tranche (01/07/2024) modelled open-ended.
    
    Headcount: 6,389 workers, 335 employers (ASSOFARM primary source).
    
    Levels 1_12 and 1_2 (Farmacista Collaboratore with 12+ or 2+ years continuous service) are automatic time-in-grade progressions under Art. 19bis. Engine cannot model auto-advancement; implemented as static level codes distinguishable by IS allowance amount (1_12=130, 1_2=100 EUR/month). Structural engine limitation — correct payroll calculation requires knowing the worker's actual time-in-grade.
    
    Function and Tech-Prof allowances shown in kitech for L2/L3/quadri sub-levels are EXCLUDED. They appear in no allegato of the signed CCNL; Art. 17 defines retribuzione di base as Tabelle A+B only. Verification: 1Q base+IQ=2456.91+160=2616.91 vs kitech 2758.68; delta 141.77 = sum of the two extra kitech lines — confirming they are historical/personal elements outside the contractual minimum. Exclusion is correct.
    

## Raw data

The contract file this page is generated from: [`agreement/farmacie-municipalizzate-assofarm.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/farmacie-municipalizzate-assofarm.json).

## Usage example

```python
--8<-- "docs/examples/agreement/farmacie-municipalizzate-assofarm/example.py"
```
