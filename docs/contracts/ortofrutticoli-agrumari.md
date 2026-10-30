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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

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
