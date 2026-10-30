# CCNL per i lavoratori delle imprese produttrici, distributrici di energia elettrica (Elettricita Futura)

| | |
|---|---|
| **CNEL code** | `K051` |
| **Sector** | industria |
| **Family** | `energia-utilities` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-11 |
| **Workers (est.)** | ~60k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Elettricita Futura
    - Utilitalia
    - Enel SpA
    - GSE
    - Sogin SpA
    - Terna SpA
    - FILCTEM-CGIL
    - FLAEI-CISL
    - UILTEC-UIL

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
| **Rule provenance** | 57 verified / 21 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-11 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 40 - Tredicesima e Quattordicesima mensilità (p. 96): "Nel caso di inizio o di cessazione del rapporto di lavoro durante l’anno o nel caso di assenza non retribuita, il lavoratore, non in prova, ha diritto a tanti dodicesimi dell’ammontare di tali mensilità quanti sono i mesi interi di servizio prestato, computando come mese intero la frazione di mese superiore a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi contrattuali integrati of the 14 levels on the four tranches of the ipotesi di accordo of 11 February 2025 (1/4/2025, 1/4/2026, 1/4/2027, 1/10/2027), against the table printed in the signed text deposited at CNEL. | corrected | The signed ipotesi of 11 February 2025 (CNEL K051, deposito 216334, 44-page scan without text layer, read on the page image of PDF p. 37) prints the table 'Minimi contrattuali integrati' with the parameter, the increment and the minimo of the 14 levels QS-C1 on 1/4/2025, 1/4/2026, 1/4/2027 and 1/10/2027 ('Aumento medio a regime €290 su parametro medio 179,76 valore punto 29,80'). The table level labels are the file codes.<br>41 of the 56 file values match; 15 (all on 1/4/2027 or 1/10/2027) differ by one cent and are corrected to the printed table.<br>Art. 38 c. 1 (PDF p. 34) defines the monthly pay as the minimo contrattuale integrato (minimi tabellari conglobated with the ex indennità di contingenza from 1 April 2013) and c. 3 adds the EDR of EUR 10,33 separately: the file's base_salary (minimo) with the EDR as a fixed allowance matches.<br>The appendix table on PDF p. 42 (5 categories, 'Aumento medio a regime € 220 su parametro medio 134,19') belongs to the separate area contrattuale in the appendix and is not used.<br>The ruleset now names the CNEL deposit of the text signed by the contracting parties (Elettricità Futura, Utilitalia, Energia Libera, Enel, GSE, Terna, Sogin, Filctem-CGIL, Flaei-CISL, Uiltec-UIL): source_type contracting_party.<br>Corrected to the printed table: Q 2027-04-01: 3858.47 -> 3858.48; Q 2027-10-01: 3947.60 -> 3947.61; ASS 2027-04-01: 3405.74 -> 3405.73; ASS 2027-10-01: 3484.42 -> 3484.41; AS 2027-04-01: 3187.64 -> 3187.65; AS 2027-10-01: 3261.27 -> 3261.28; A1 2027-04-01: 2913.65 -> 2913.66; A1 2027-10-01: 2980.96 -> 2980.97; BSS 2027-04-01: 2774.62 -> 2774.63; BS 2027-04-01: 2656.36 -> 2656.35; BS 2027-10-01: 2717.73 -> 2717.72; B1 2027-04-01: 2417.48 -> 2417.49; B2S 2027-04-01: 2257.70 -> 2257.71; CS 2027-04-01: 1862.65 -> 1862.64; CS 2027-10-01: 1905.68 -> 1905.67. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QS` | Senior Quadro | € 4,399.12 | 2027-10-01 |
| `Q` | Quadro | € 3,947.61 | 2027-10-01 |
| `ASS` | Senior Senior Specialist Area | € 3,484.41 | 2027-10-01 |
| `AS` | Senior Specialist Area | € 3,261.28 | 2027-10-01 |
| `A1S` | Area 1 Senior | € 3,124.14 | 2027-10-01 |
| `A1` | Area 1 | € 2,980.97 | 2027-10-01 |
| `BSS` | Area B Senior Senior | € 2,838.72 | 2027-10-01 |
| `BS` | Area B Senior | € 2,717.72 | 2027-10-01 |
| `B1S` | Area B1 Senior | € 2,589.64 | 2027-10-01 |
| `B1` | Area B1 | € 2,473.33 | 2027-10-01 |
| `B2S` | Area B2 Senior | € 2,309.87 | 2027-10-01 |
| `B2` | Area B2 | € 2,149.26 | 2027-10-01 |
| `CS` | Area C Senior | € 1,905.67 | 2027-10-01 |
| `C1` | Area C1 | € 1,724.71 | 2027-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `QS` | € 49.01 |
| `Q` | € 46.33 |
| `ASS` | € 43.07 |
| `AS` | € 39.82 |
| `A1S` | € 37.86 |
| `A1` | € 35.74 |
| `BSS` | € 33.72 |
| `BS` | € 31.97 |
| `B1S` | € 30.16 |
| `B1` | € 28.46 |
| `B2S` | € 26.13 |
| `B2` | € 23.81 |
| `CS` | € 20.30 |
| `C1` | € 17.66 |

## Apprenticeship

**gruppo_c** (type: `percentage`)  
Destination levels: `CS`  
percentage: 1.00

**gruppo_b** (type: `percentage`)  
Destination levels: `B1`  
percentage: 1.00

**gruppo_a_bss** (type: `percentage`)  
Destination levels: `BSS`, `A1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "elettrico-elettricita-futura/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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
| https://www.contratticcnl.it/elettrico/tabelle-retributive/ | tabella_retributiva | 2025-02-11 | [↗](https://www.contratticcnl.it/elettrico/tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92 | tabella_retributiva | 2025-02-11 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=92) |

??? note "Coverage notes"
    Salary model is split. base_salary = paga base (time-series, 4 tranches from the 2025-02-11 renewal); fixed_allowances = EDR (Elemento Distinto della Retribuzione) frozen at EUR 10.33/month since 1988, same for all levels.
    
    hourly_divisor 173.33 as stated by the contract (40h/week statutory base: 40 x 52 / 12). Actual weekly hours are 38 (non-shift) or 40 (shift); the divisor is contractually fixed on the 40h base.
    
    Seniority cadence 24 months (biennale), maximum 5 scatti (10 years of service per contract text). Amounts vary by level (kitech.it, April 2026).
    
    APPRENTICESHIP (Art. 15 CCNL 2025-02-11, apprendistato professionalizzante). Three tracks by qualification group. Gruppo C (dest CS, 36m): yr1=86%, yr2=90%, yr3=96%, then 100%. Gruppo B excl. BSS (dest B1, 36m): same progression. BSS + Gruppo A (dest BSS and A1, 24m): yr1=86%, yr2=96%, then 100%. Source: Art. 15 para.5 table (CCNL full text PDF filctemcgil.it, 2025-02-11). Note: only the four qualification levels explicitly cited in Art.15 (CS, B1, BSS, A1) are modelled; S-suffix variants (B1S, A1S, etc.) are senior-grade levels not addressed in the apprenticeship article.
    
    APR 2027 VALUES: confirmed via parametric derivation. The CCNL elettrici system applies a fixed valore-punto increase each tranche (same absolute amount per parametro per tranche). Apr 2026 and Apr 2027 increments are equal across all 14 levels (ratio=1.000 verified); A1S reference level gets +65.50 EUR matching the search-confirmed '+65 EUR average TEM' for Apr 2027 (fiscoetasse.com, pmi.it). October 2027 values verified against contratticcnl.it (all 14 levels match).
    
    Workers covered: approximately 63,000 in 687 companies (Enel SpA, Terna SpA, GSE, Sogin, Energia Libera and affiliated). Agreement signed 2025-02-11; valid until 2027-12-31.
    
    INPS rates from 2026-industria.json (industria sector, 50 employees tier). IRPEF 2026 brackets applied (L. 199/2025).
    
    contratticcnl.it shows data alignment errors for BSS, BS, B1 in the April 2026 and April 2027 columns; kitech.it April 2026 values used as authoritative for all 14 levels.
    

## Raw data

The contract file this page is generated from: [`agreement/elettrico-elettricita-futura.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/elettrico-elettricita-futura.json).

## Usage example

```python
--8<-- "docs/examples/agreement/elettrico-elettricita-futura/example.py"
```
