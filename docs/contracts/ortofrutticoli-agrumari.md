# CCNL Ortofrutticoli ed Agrumari (Import-Export)

| | |
|---|---|
| **CNEL code** | `H341` |
| **Sector** | ortofrutticoli ed agrumari import-export |
| **Family** | `commercio` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60000 |
| **Ruleset version** | `2024.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Fruitimprese
    - FLAI-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, leave, seniority, sickness |

5 documented simplification(s) and 1 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 46 verified / 0 derived / 8 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-19 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-08-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-17 | claude-opus-5-5 (ai) | The paga nazionale conglobata of the nine levels against Allegato 1 of the CCNL of 19 July 2024 published by FLAI-CGIL. | corrected | Allegato 1 (PDF pp. 58-59, printed pp. 113-114, text layer): the 45 paghe conglobate from 31/08/2024 to 01/08/2027 move from assumed to verified; the file had them from aggregators (lavoro-economia.it, ilccnl.it, kitech.it).<br>The ruleset names this source, published by FLAI-CGIL, a signatory: source_type contracting_party instead of estimated.<br>Corrected to the printed table: 4 2025-06-01: 1728.12 -> 1728.13; Q 2026-06-01: 2396.59 -> 2396.58; 1 2026-06-01: 2286.83 -> 2286.84; 4 2026-06-01: 1750.00 -> 1750.01; 7 2026-06-01: 1538.26 -> 1538.27; Q 2027-08-01: 2486.49 -> 2486.48; 1 2027-08-01: 2372.61 -> 2372.62; 4 2027-08-01: 1815.64 -> 1815.65; 7 2027-08-01: 1595.96 -> 1595.97. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 79 - Anzianità di servizio (general clause), applied to Art. 77 - 13ª mensilità (p. 43) (p. 44): "le frazioni di anno saranno computate, a tutti gli effetti contrattuali, per dodicesimi computandosi come mese intero le frazioni di mese superiori o uguali a 15 giorni.". Added: at_least 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,486.48 | 2027-08-01 |
| `1` | Primo livello | € 2,372.62 | 2027-08-01 |
| `2` | Secondo livello | € 2,096.50 | 2027-08-01 |
| `3` | Terzo livello | € 2,004.71 | 2027-08-01 |
| `4` | Quarto livello | € 1,815.65 | 2027-08-01 |
| `5` | Quinto livello | € 1,737.47 | 2027-08-01 |
| `6S` | Sesto livello superiore | € 1,700.37 | 2027-08-01 |
| `6` | Sesto livello | € 1,659.53 | 2027-08-01 |
| `7` | Settimo livello | € 1,595.97 | 2027-08-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 13 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.45 |
| `1` | € 29.40 |
| `2` | € 27.30 |
| `3` | € 27.30 |
| `4` | € 26.25 |
| `5` | € 26.25 |
| `6S` | € 25.20 |
| `6` | € 25.20 |
| `7` | € 25.20 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ortofrutticoli-agrumari/seniority_assumed_constant · seniority · impact unknown · open"
    SIMPLIFICATION: Importi scatti anzianità assunti costanti per tutto il periodo 2024-2027. La fonte primaria (kitech.it giugno 2026) non indica data decorrenza; il rinnovo 2024 non menziona modifiche agli scatti.

    **Applies when:** `seniority` applies.

    **Remediation:** Source the effective dates of the seniority amounts.

!!! warning "ortofrutticoli-agrumari/ind_fun_assumed_constant · base_salary · impact unknown · open"
    SIMPLIFICATION: IND_FUN 154.94 EUR assunta costante dal 2024-01-01 senza adeguamenti. Allowance pre-euro congelata (300.000 lire). Nessuna fonte indica variazioni nel rinnovo 2024.

    **Applies when:** `base_salary` applies; level in Q.

    **Remediation:** Confirm the IND_FUN amount against the 2024 renewal text.

!!! warning "ortofrutticoli-agrumari/ind_fun_fourteen_months · base_salary · impact unknown · open"
    SIMPLIFICATION: IND_FUN assunta corrisposta su 14 mensilità (ereditato da additional_months contratto); months_per_year non specificato. Nessuna fonte accessibile indica il numero di mensilità dell'indennità. Impatto: ±154.94 EUR/anno livello Q se la vera risposta è 12 mensilità.

    **Applies when:** `base_salary` applies; level in Q; run kind in fourteenth.

    **Remediation:** Source the number of monthly payments of IND_FUN.

!!! warning "ortofrutticoli-agrumari/assumed_sickness_integration_rates · sickness · impact unknown · open"
    SIMPLIFICATION: Tassi integrazione malattia assunti 100% (carenza_integration_rate e full_pay_integration_rate). Fonti accessibili non riportano percentuali per H341. Comporto 180 giorni da snippet ricerca H341. Il motore può sovrastimare il supplemento datoriale durante la malattia.

    **Applies when:** `sickness` applies.

    **Remediation:** Source the carenza and integration rates of the CCNL and replace the assumed 100%.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded. A CCNL whose comporto the engine counts over the calendar year (Commercio Art. 186 and the others with comporto_calendar_year) is not affected.

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
    SIMPLIFICATION: Apprendistato non modellato (apprenticeship=[]). Il rinnovo 2024 ha modificato la disciplina dell'apprendistato ma il testo consolidato è dietro paywall. Le fonti accessibili (aggregatori) non sono attribuibili con certezza al CCNL Fruitimprese H341 rispetto al CCNL Confsal/Fesica. Rischio: retribuzione apprendistato restituisce zero anziché un importo errato.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Ortofrutta e Agrumi (Import-Export) — tabella retributiva CNEL H341 (lavoro-economia.it) | tabella_retributiva | 2024-07-19 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=72) |
| CCNL Ortofrutta ed Agrumi — tabella settembre 2024 con Contingenza=0 e EDR=0 (ilccnl.it) | tabella_retributiva | 2024-09-01 | [↗](https://ilccnl.it/contratto/ccnl/ortofrutticoli-ed-agrumari) |
| Kitech tabella retributiva CCNL Ortofrutta ed Agrumari — giugno 2026 | tabella_retributiva | 2026-06-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=72) |
| CCNL Ortofrutticolo — accordo di rinnovo 2024-2027 (Fisascat-CISL comunicato) | associazione | 2024-07-19 | [↗](https://www.fisascat.it/news/ccnl-ortofrutticolo) |
| Aziende ortofrutticole e agrumarie — siglato il rinnovo del CCNL (edotto.com) | associazione | 2024-07-19 | [↗](https://www.edotto.com/articolo/ortofrutticoli-agrumari-rinnovo-ccnl) |

??? note "Coverage notes"
    IND_FUN livello Q: 154.94 EUR/mese. Lavoro-economia.it c=72 mostra livello Q totale = 2551.53 = 2396.59 (base giugno 2026) + 154.94. Equivale a 300.000 lire (300.000/1936.27 = 154.94): allowance pre-euro congelata.
    
    BASE SALARY: every base_salary period of the nine levels is verified against Allegato 1 of the FLAI text (p. 58, review 2026-10-17-ai-tables); no value is derived by the proportional rule any more (review of 2026-10-30).
    
    Salary model: conglobato. ilccnl.it Sept 2024 table shows Contingenza=0.00 e EDR=0.00 per tutti i livelli. Divisore orario 173 confermato da lavoro-economia.it c=72 (CNEL H341) quota diretta: 'L'importo della retribuzione oraria si ottiene dividendo l'importo della retribuzione mensile per il divisore convenzionale 173'. Verifica aritmetica su 4 livelli: 1 (2286.83/13.22=173), 2 (2020.70/11.68=173), 3 (1932.23/11.17=173), 6 (1599.53/9.25=173).
    
    Identità c=72 = CNEL H341 = Fruitimprese: tabella giugno 2026 su lavoro-economia.it c=72 forward-verified su 9 livelli con tranches Fruitimprese (65+20+20 EUR a livello 6, da edotto.com e fisascat.it) con match al centesimo. Un tavolo Confsal/Fesica non riprodurrebbe questa struttura. Stipendianti: Fruitimprese + FLAI-CGIL, FISASCAT-CISL, UILTUCS-UIL (da ilccnl.it e consulentidellavoro.fi.it).
    
    14 mensilità (tredicesima + quattordicesima): lavoro-economia.it c=72 quote 'I lavoratori hanno diritto alla corresponsione di 14 mensilità'. Quattordicesima corrisposta entro luglio (fisascat.it comunicato 2024).
    
    Scatti anzianità: 13 aumenti triennali, lavoro-economia.it c=72 quote 'i lavoratori hanno diritto a maturare 13 aumenti triennali'. Importi mensili da kitech.it CodiceCateg=72 (tabella giugno 2026): Q=30.45, 1=29.40, 2=27.30, 3=27.30, 4=26.25, 5=26.25, 6S=25.20, 6=25.20, 7=25.20.
    

## Raw data

The contract file this page is generated from: [`agreement/ortofrutticoli-agrumari.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/ortofrutticoli-agrumari.json).

## Usage example

```python
--8<-- "docs/examples/agreement/ortofrutticoli-agrumari/example.py"
```
