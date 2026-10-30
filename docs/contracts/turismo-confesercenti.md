# CCNL Turismo (Assoturismo-Confesercenti)

| | |
|---|---|
| **CNEL code** | `H058` |
| **Sector** | turismo — alberghi, campeggi, pubblici esercizi, agenzie di viaggi |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-22 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assoturismo-Confesercenti
    - Assohotel
    - Assocamping
    - Assoviaggi
    - FIEPET
    - FIBA
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
| **Limits of this contract** | base_salary, seniority, trattamento_integrativo |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 57 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-22 |
| **Last review** | — |
| **Latest salary tranche** | 2027-11-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A | € 2,495.22 | 2027-11-01 |
| `QB` | Quadro B | € 2,310.11 | 2027-11-01 |
| `1` | Livello 1 | € 2,152.32 | 2027-11-01 |
| `2` | Livello 2 | € 1,967.20 | 2027-11-01 |
| `3` | Livello 3 | € 1,855.32 | 2027-11-01 |
| `4` | Livello 4 | € 1,750.69 | 2027-11-01 |
| `5` | Livello 5 | € 1,641.85 | 2027-11-01 |
| `6S` | Livello 6S | € 1,578.72 | 2027-11-01 |
| `6` | Livello 6 | € 1,556.35 | 2027-11-01 |
| `7` | Livello 7 | € 1,458.42 | 2027-11-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `7` | € 30.47 |
| `6` | € 30.99 |
| `6S` | € 31.25 |
| `5` | € 32.54 |
| `4` | € 33.05 |
| `3` | € 34.86 |
| `2` | € 36.15 |
| `1` | € 37.70 |
| `QB` | € 39.25 |
| `QA` | € 40.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `7`, `6`, `6S`, `5`, `4`, `3`, `2`, `1`, `QB`, `QA`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "turismo-confesercenti/other_subsectors_tables · base_salary · impact yes · open"
    Models the alberghi/campeggi sub-sector only (CCNL H058, conglobated model). Pubblici esercizi and stabilimenti balneari use a split (paga base + contingenza) model with different values — out_of_scope deliberate: these sub-sectors have meaningfully different pay structures requiring separate files.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the pubblici esercizi and stabilimenti balneari tables (split paga base + contingenza) with a sub-sector input, or record the limitation.

!!! warning "turismo-confesercenti/apprenticeship_under_classification · base_salary · impact yes · open"
    Apprenticeship model confirmed: CCNL Turismo Confesercenti provides sotto-inquadramento 2 levels below destination (consistent with Testo Unico apprendistato Art. 11, secondary sources). Modeled as 100% passthrough pending contract text; the engine supports under_classification tracks with levels_below. (review of 2026-10-30)

    **Applies when:** `base_salary` applies.

    **Remediation:** Source the contract text and model under_classification tracks (2 levels below destination) instead of the 100% passthrough.

!!! warning "turismo-confesercenti/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "turismo-confesercenti/tourism_special_supplement · trattamento_integrativo · impact yes · open"
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-20, Gazzetta Ufficiale text, https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=1&art.versione=1, page sha256 e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d): from 1 January to 30 September 2026 the workers of the esercizi di somministrazione di alimenti e bevande (L. 287/1991 art. 5) and of the 'comparto del turismo, ivi inclusi gli stabilimenti termali', with employment income of 2025 not above 40,000 EUR, receive 'un trattamento integrativo speciale, che non concorre alla formazione del reddito, pari al 15 per cento delle retribuzioni lorde corrisposte in relazione al lavoro notturno e alle prestazioni di lavoro straordinario [...] effettuate nei giorni festivi'. The employer pays it 'su richiesta del lavoratore' (c. 20), a fact the request has no field for: the engine does not pay it, so the net pay of a worker who asked for it is understated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the worker's request of c. 20 to the request, pay 15% of the night and holiday overtime pay of the run as a credit, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Full alberghi sector table, all 5 tranches. Jul 2024 - Nov 2027. | tabella_retributiva | 2024-07-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=257) |
| Confirms alberghi table at 01/05/2026. | tabella_retributiva | 2024-07-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=82) |
| Tranche schedule and seniority cadence confirmed. | altro | 2024-07-22 | [↗](https://www.redigo.info/2024/07/24/ccnl-turismo-confesercenti-il-rinnovo-consolida-il-contratto-unico/) |

??? note "Coverage notes"
    CCNL H058 — Assoturismo-Confesercenti. Conglobated. 10 levels: 7-6-6S-5-4-3-2-1-QB-QA. Divisor 172, 14 months. Seniority 36-month cadence, max 6. 5 tranches: Jul-2024 to Nov-2027.
    
    Indennita di funzione for QA (EUR 75/month) and QB (EUR 70/month) conglobated into base_salary. Consistent with turismo-federalberghi.json modeling for the same allowances. The CCNL H058 does not publish them as separate line items in the tabella retributiva; absorption into base_salary matches the conglobated model.
    

## Raw data

The contract file this page is generated from: [`agreement/turismo-confesercenti.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/turismo-confesercenti.json).

## Usage example

```python
--8<-- "docs/examples/agreement/turismo-confesercenti/example.py"
```
