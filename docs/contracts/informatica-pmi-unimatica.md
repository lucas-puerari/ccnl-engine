# CCNL Comunicazione, Informatica e Servizi Innovativi PMI — Settore Informatico

| | |
|---|---|
| **CNEL code** | `G029` |
| **Sector** | informatica-servizi-innovativi |
| **Family** | `ict-telecomunicazioni` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-04-14 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Unigec Confapi
    - Unimatica Confapi
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL

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

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 40 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-14 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 80 - Tredicesima mensilità (impiegati) (p. 123): "Nel caso di inizio o di cessazione del rapporto durante il corso dell'anno, l'impiegato non in prova avrà diritto a tanti dodicesimi dell'ammontare della 13ª mensilità per quanti sono i mesi di servizio prestato. La frazione di mese non superiore ai 15 giorni non sarà considerata, mentre sarà considerata come mese intero la frazione di mese superiore a 15 giorni.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro — manager, exceptional leadership and innovative thinking (PAR 248 + indennità funzione 51.65) | € 2,889.92 | 2027-01-01 |
| `1` | Livello 1 — top professional, full strategic responsibility (PAR 247) | € 2,827.50 | 2027-01-01 |
| `2` | Livello 2 — expert professional, strategic solutions, wide autonomy (PAR 209) | € 2,468.03 | 2027-01-01 |
| `3` | Livello 3 — senior professional, leads in complex environments (PAR 195) | € 2,336.94 | 2027-01-01 |
| `4` | Livello 4 — senior specialist, responsible for team performance (PAR 182) | € 2,218.03 | 2027-01-01 |
| `5` | Livello 5 — reference level (PAR 169); experienced specialist with consultancy role | € 2,095.18 | 2027-01-01 |
| `6` | Livello 6 — senior technician, coordinates others in limited contexts (PAR 150) | € 1,967.68 | 2027-01-01 |
| `7` | Livello 7 — technical specialist, independent in structured contexts (PAR 133) | € 1,776.03 | 2027-01-01 |
| `8` | Livello 8 — qualified technical worker, applies skills to defined problems (PAR 125) | € 1,678.58 | 2027-01-01 |
| `9` | Livello 9 — basic technical tasks, limited autonomy (PAR 114) | € 1,575.27 | 2027-01-01 |
| `10` | Livello 10 — entry-level worker, simple tasks under close supervision (PAR 100) | € 1,444.33 | 2027-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 16.01 |
| `1` | € 16.01 |
| `2` | € 16.01 |
| `3` | € 14.46 |
| `4` | € 13.94 |
| `5` | € 13.43 |
| `6` | € 13.17 |
| `7` | € 12.91 |
| `8` | € 12.39 |
| `9` | € 11.88 |
| `10` | € 11.62 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6`, `7`

**automatico_it** (type: `under_classification`)  
Destination levels: `8`, `9`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "informatica-pmi-unimatica/apprenticeship_duration_by_agreement · base_salary · impact unknown · open"
    APPRENTICESHIP GENERAL TRACK DURATION: the CCNL offers three duration options (36/30/24 months) by agreement between the parties; no per-destination-level assignment was found in the available text. The 36-month track (12+12+12) is used as representative for destination levels 1, 2, 3, 4, 5, 6, 7. Real durations may be shorter by agreement.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the 30 and 24-month durations as separate tracks selectable by name.

!!! warning "informatica-pmi-unimatica/apprentice_seniority · seniority · impact unknown · open"
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

### Without monetary impact

!!! note ""
    APPRENTICESHIP — QUADRO (Q) NOT MODELLED AS DESTINATION: Art. 52 and Art. 64 contain no affirmative listing of Q as an apprendistato professionalizzante destination. Following repo precedent (telecomunicazioni-asstel, gomma-plastica) where Quadri are excluded from apprenticeship destinations when no explicit contractual text lists them, Q is omitted from destination_levels of the general track.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.cdltorino.it/ccnl-informatica-piccola-industria-rettifica-tabelle-retributive/ | tabella_retributiva | 2025-04-14 | [↗](https://www.cdltorino.it/ccnl-informatica-piccola-industria-rettifica-tabelle-retributive/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=302 | tabella_retributiva | 2025-04-14 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=302) |
| https://slc.cgil.it/ccnl/20210309-CCNL_CONFAPI_UNIGEC_UNIMATICA.pdf | altro | 2021-03-09 | [↗](https://slc.cgil.it/ccnl/20210309-CCNL_CONFAPI_UNIGEC_UNIMATICA.pdf) |

??? note "Coverage notes"
    SCOPE: models the SETTORE INFORMATICO E SERVIZI INNOVATIVI sub-sector of G029 only (levels Q, 1–10). The SETTORE GRAFICO-EDITORIALE and SETTORE CARTARIO-CARTOTECNICO sub-sectors of G029 are NOT modelled here. Applicable to ICT companies covered by Art. 1 of the CCNL.
    
    SALARY MODEL — CONGLOBATED: base_salary values are the total contractual retribuzione mensile (paga base + contingenza + EDR + indennità di funzione for Q) at each tranche date. Contingenza per level is frozen since 1994 and sourced from Allegato 24 of the G029 CCNL 09/03/2021 PDF. EDR = EUR 10.33 (all levels). Q level includes indennità di funzione = EUR 51.65 introduced from 01/01/2025 (sourced from kitech.it April 2025 tables, component-level breakdown). fixed_allowances is empty for all levels.
    
    CONGLOBATED CHECK (non-circular): paga_base values from the April 14 2025 corrected tables (cdltorino.it) plus frozen contingenza (Allegato 24 PDF) plus EDR 10.33 independently sum to the kitech Jan 2026 totals to within EUR 0.01 on all 11 levels. Example at Jan 2026: level 5 paga_base 1529.38 + contingenza 525.47 + EDR 10.33 = 2065.18 (kitech ✓); level 10: 903.38 + 512.87 + 10.33 = 1426.58 (kitech ✓); Q: 2242.26 + 541.65 + 10.33 + 51.65 = 2845.89 (kitech ✓). The kitech values ARE the conglobated total, not paga_base only.
    
    HOURLY DIVISOR = 169. Source: Art. 113 G029 CCNL 2021 PDF ('dal 1° gennaio 2019 si dividerà per 169'). Independent cross-check: contractual weekly hours = 39 h from 01/01/2019 (same Art. text); 39 × 52 / 12 = 169.00 exactly.
    
    PAR COEFFICIENTS from Art. 116 G029 CCNL 2021 PDF (Settori Grafico-Editoriale, Informatico-Servizi Innovativi): Q=248, 1=247, 2=209, 3=195, 4=182, 5=169, 7=133, 8=125, 9=114, 10=100. CORRECTION: level 6 PAR was changed from 156 (2021 CCNL) to 150 in the April 14 2025 verbale integrativo corrected tables. This is confirmed by cdltorino.it rettifica article (PAR=150 shown explicitly) and is consistent with the kitech Jan 2026 total for level 6 (1407.71 + 523.01 + 10.33 = 1941.05). All base_salary values are computed from official paga_base (cdltorino April 2025) + frozen contingenza (Allegato 24 CCNL PDF) + EDR 10.33.
    
    TRANCHE DATES: 01/01/2025 (first, effective retroactively from April 2025 per verbale); 01/01/2026 (second); 01/01/2027 (third). Reference level 5 increases: +60, +60, +30 EUR paga base. Confirmed by search results (bollettinoadapt.it, fiscoetasse.com).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: Art. 97 G029 CCNL 2021 PDF (tredicesima mensilità). No quattordicesima article exists in G029.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Source: Art. 45 G029 CCNL 2021 PDF ('per ogni biennio, e fino ad un massimo di 5 bienni'). Per-level amounts from same article (effective from 01/01/2002 update). kitech April 2025 table confirms same amounts unchanged in the 2025 renewal.
    
    INPS: reuses 2026-industria.json (Confapi/industria sector). Unimatica-Confapi belongs to industria. CIGO applies (D.Lgs. 148/2015). No Cassa Edile or bilateral fund substituting INPS contributions.
    
    APPRENTICESHIP GENERAL TRACK (Art. 52 CCNL, para. C Apprendistato professionalizzante): first period 2 levels below destination; second period 1 level below; third period classification stays 1 below but retribuzione is at destination level (levels_below=0 in engine, which models pay, not classification). Duration options: 36, 30 or 24 months by agreement. The 36-month (12+12+12) track is modelled as representative.
    
    APPRENTICESHIP AUTOMATICO TRACK (Art. 52 CCNL, settore informatico-servizi innovativi Area Tecnica): destination level 8 → entry at level 9 (1 below), 18 months; destination level 9 → entry at level 10 (1 below), 18 months. After permanent hire, destination-level 8 apprentices spend 6 months at level 9 before final assignment (this post-apprenticeship transition is not modelled; it occurs outside the apprendistato period).
    
    EDR ROLL-UP: rolling EDR (EUR 10.33) into base_salary is safe for G029 because G029 uses under_classification apprenticeship, meaning the apprentice pay is determined by the classified level's base_salary directly. The EDR percentage-of-base exemption (Art. 3 L. 537/1993) does not apply to under_classification.
    

## Raw data

The contract file this page is generated from: [`agreement/informatica-pmi-unimatica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/informatica-pmi-unimatica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/informatica-pmi-unimatica/example.py"
```
