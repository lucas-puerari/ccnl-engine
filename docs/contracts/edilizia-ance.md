# CCNL Edilizia — Industria (ANCE), operai

| | |
|---|---|
| **CNEL code** | `F012` |
| **Sector** | edilizia |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-02-21 |
| **Workers (est.)** | ~550k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🏭 Production |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCE
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Produzione e Lavoro
    - Fillea-CGIL
    - Filca-Cisl
    - Feneal-Uil

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, overtime, sickness, territorial_supplement |

5 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 31 verified / 8 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 🏭 Production | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-10-15 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule of the operai read again in the ANCE minimi table of the CCNL of 21 February 2025, the CCNL of 19 April 2010 (FILLEA text), the Art. 92 apprenticeship text of 2019 and the ANCE provincial tables, for the production tier. | corrected | 26 records verified, 12 derived (contingenza, EDR, contractual fund, absence quota, sickness mapping).<br>Split by category (Art. 77): the operai of levels 1-4 in edilizia-ance, the impiegati and quadri of levels 1-7 in edilizia-ance-impiegati.<br>base_salary is now the national minimo of the ANCE table; the ex contingenza and the EDR 10.33 are fixed allowances (derived, ANCE provincial tables), the EDR outside the TFR base. The previous consolidated values (minimo + contingenza + EDR) matched.<br>Aggregator sources (idealista, leggeinchiaro, businessonline, kitech) removed.<br>Absence quota: by_hourly 8 hours (1/173 of Art. 44 and Allegato A), not by_26, which no clause supports.<br>contractual_fund_uncovered closed: every operaio level has an hourly Prevedi amount and every impiegato or quadro level a monthly one.<br>No renewal changing the national minimi after the verbale of 21 February 2025 through October 2026.<br>Twelve monthly payments, not 13: the gratifica natalizia and the ferie are the 18.5% of Art. 18 through the Cassa Edile (declared).<br>No scatti for the operai (Art. 49 is for the impiegati; APE through the Cassa Edile, Art. 29): seniority removed, the apprentice seniority note closed.<br>Sickness: the coefficients of Art. 26, not 100% for 180 days; comporto 270 days (derived mapping, declared).<br>Night overtime 40% (Art. 19) confirmed; sources now the CCNL text.<br>Notes corrected: the TFR is paid by the employer (Art. 33), not the Cassa Edile; the INPS rates are the verified 2026 edilizia table. |
| 2026-10-13 | claude-opus-5-5 (ai) | Scope of the declared limitations and readiness. | demoted | The 18.5% Cassa Edile accrual and the 4.95% riposi annui are missing from every operaio payslip: declared as cassa_edile_riposi_missing on every run, so the file goes back to reviewed.<br>edilizia_operai_sickness is recorded on every run with a sickness event. |
| 2026-10-13 | claude-opus-5-5 (ai) | The hourly pay of the operai (Allegato A), the riposi annui of Art. 5 B, the Cassa Edile percentage of Art. 18 with the conventional net of Allegato D and the TFR base of Art. 33, read in the CCNL of 19 April 2010 (FILLEA text), for the production tier. | corrected | hourly_pay added: the operai are paid the monthly elements over 173 times the ordinary hours worked (Allegato A, p. 164); without the hours the run has a missing_fact ordinary_hours_worked blocker.<br>RIPOSI_ANNUI 4.95% (Art. 5 B, p. 27) paid with the pay and CASSA_EDILE 18.5% (Art. 18, pp. 37-38) accrued net of the withholdings: 14.2% withheld from the net pay (Allegato D, p. 172); both on the paga base and the ex contingenza (Art. 24 point 3-4, p. 49), in the INPS, IRPEF and TFR bases (Art. 33, p. 56).<br>No renewal changes the rates: the OCR of the verbali of 1 July 2014, 18 July 2018, 3 March 2022 and 21 February 2025 has no hit for 4,95, 18,5 or 14,2; the ANCE Ragusa table of 1 March 2026 prints 4,95%, 18,50% and 14,20%.<br>The ANCE Sassari table of 1 February 2025 computes the 18.5% and the 4.95% on a sub-total with the hourly EDR (0,06); the CCNL base of Art. 24 does not list the EDR and the data follow the CCNL.<br>cassa_edile_riposi_missing closed; the festività of Art. 17, the capisquadra maggiorazione, the Allegato D sickness and injury percentages and its point 4 exception declared.<br>Promoted to production. |
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: the minimi of the operai for the tranches of 1 February 2025, 1 March 2026 and 1 March 2027 against the ANCE national table; the remaining derived records. | confirmed | The 12 monthly minimi of the four operai levels match the impiegati column of the national table, and each over 173 is the hourly minimo the table prints for the operai.<br>Contingenza and EDR stay derived: Art. 11 of the CCNL of 19 April 2010 refers to the interconfederal agreements and no national signed table prints the amounts; the ANCE provincial tables do.<br>Prevedi stays derived (fund information sheet); the accrual rule is a placeholder the operai do not read (no extra month paid by the employer). |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | corrected | CNEL F012 matches. Signatory names corrected to the report: Legacoop Produzione e Servizi (was Legacoop Costruzioni) and AGCI Produzione e Lavoro.<br>Term: expiry 30/06/2028 from the report; valid_from is the first tranche of the renewal of 21 February 2025, the start of its term was not read. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'scatti di anzianità, indennità e altri elementi fissi': the scatti and fixed allowances of the file against the text read in the P1 review. | confirmed | Ex contingenza 512,87 / 516,43 / 519,16 / 521,25 and EDR 10,33 of levels I-IV match the ANCE table of 1 February 2025 (ANCE is a signatory). The same table prints the operai hourly amounts 2,96 / 2,99 / 3,00 / 3,01 and 0,06, which are the monthly amounts divided by the hourly divisor 173: the monthly records are consistent with the hourly pay. Verified.<br>No scatti for the operai: the anzianità professionale edile is paid by the Cassa Edile (Art. 29), as the file states. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | flagged | Part-time supplementary hours at 20% and the 10% of the flexible clauses (pp. 105-106): declared. The apprenticeship track was verified in P1. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'confrontare lordo, netto e costo azienda con esempi indipendenti': a run of the engine against the cost table of the Ministry of Labour for the CCNL (D.Lgs. 36/2023 art. 41 c. 13). | flagged | Operaio di 1° livello, January 2026 (the tranche of the table of May 2025), 30 employees, 173 hours: minimo 6,17, ex contingenza 2,96 and EDR 0,06 an hour equal the monthly amounts over 173; riposi annui 4,95% and the Cassa Edile accrual 18,50% are the table's rates on minimo and contingenza; the employer INPS rate 34.28% (15-50 employees) matches. Match.<br>Deviations, with cause and decision: the EVR, the indennità territoriale di settore and the transport and meal indemnities are provincial and declared (NOT MODELLED AMOUNTS); the Cassa Edile contribution (5,47% in the table) was not declared: declared; INAIL 11% is not computed by the engine (documented). No independent net pay example: not compared. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `4` | Livello 4: operai di quarto livello (art. 77) | € 1,634.31 | 2027-03-01 |
| `3` | Livello 3: operai specializzati (art. 77) | € 1,517.56 | 2027-03-01 |
| `2` | Livello 2: operai qualificati (art. 77) | € 1,365.81 | 2027-03-01 |
| `1` | Livello 1: operai comuni (art. 77) | € 1,167.36 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-ance/edilizia_operai_sickness · sickness · impact yes · open"
    SICKNESS (Art. 26): the employer pays a coefficient of the hourly minimo, ex contingenza and indennità territoriale times a sixth of the weekly hours, six days a week: 0.5495 for days 1-3 when the sickness lasts more than 6 days, 1.0495 when it lasts more than 12, 0.3795 for days 4-20 and 0.1565 for days 21-180 on top of the INPS indemnity, 0.5495 for days 181-365. The engine stores the coefficient plus the INPS rate of the day as the target (0.8795 and 0.8231), so its employer share is the coefficient on the engine's daily quota, which counts the EDR and not the indennità territoriale. Not modelled: the 1.0495 of a sickness over 12 days (paid 0.5495), the comporto of 365 days past 3.5 years of seniority and the cumulated comporto of 9 months in 20 (12 in 24), the 4.95% paid for the carenza days of a sickness of up to 6 days and for the day of an injury (60% on days 1-3); the percentages accrued with the Cassa Edile during sickness and injury (Allegato D: 18.5% gross and 14.2% net for the carenza days and from day 4 of sickness, 7.4% and 5.7% for days 4-90 of injury or occupational disease, 4.6% and 3.6% from day 91); and the exception of Allegato D point 4: in a pay period without direct pay the conventional net does not apply and the actual withholdings are taken from the accruals. The sick hours of an operaio are not in the hours paid by the hour, so the sick days deduct nothing from the pay.

    **Applies when:** `sickness` applies.

    **Remediation:** Model the coefficients of Art. 26 on their own base and the comporto by seniority.

!!! warning "edilizia-ance/edilizia_operai_unmodelled · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the EVR set by the provincial agreements (Art. 46); the special maggiorazione of the capisquadra in the base of Art. 17 and 18 (Art. 24 point 4); the festività of Art. 17 point 3 (8 hours of the point 4 elements, with the 4.95% and the 18.5% on them), which PeriodFacts.ordinary_hours_worked leaves out; the una tantum premio di ingresso of EUR 100 to operai under 29 of the verbale of 3 March 2022 (Allegato 5); the APE paid by the Cassa Edile (Art. 29); the premiums on ordinary hours of Art. 19 (lavoro festivo 45%, notturno 28%, turni 9% and 12%, guardiano 8%, notturno continuativo 16%, festivo notturno 50%, domenicale con riposo compensativo 8%) and the 8% of a Saturday in a six-day week (Art. 5); the indennità for lavori speciali disagiati, alta montagna and cantiere ferroviario (Art. 20-21); mensa, trasporto and trasferta (provincial; verbale 2025); the riduzione contributiva edile on the employer INPS contributions of full-time operai (art. 29 L. 341/1995).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the provincial elements and the festività hours as inputs.

!!! warning "edilizia-ance/territorial_sector_allowance · territorial_supplement · impact yes · open"
    INDENNITÀ TERRITORIALE DI SETTORE: set by the provincial agreements (Art. 12) and owed to every operaio, also in the base of the 4.95% and 18.5% and in the TFR base of Art. 33. Not modelled: the net pay and the employer cost are short of it.

    **Applies when:** `territorial_supplement` applies.

    **Remediation:** Model the indennità territoriale di settore with a fact naming the province, then remove this note.

!!! warning "edilizia-ance/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: supplementary hours of the operai are paid with 20% of the hourly quota, and a flexible clause adds 10% (CCNL 19 April 2010, Art. 78, pp. 105-106). The request has no kind for supplementary hours: an overtime event of a part-time worker takes the overtime bands unless the caller passes the multiplier.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a supplementary-hours kind to the overtime event and a supplementare band with the CCNL rate.

!!! warning "edilizia-ance/cassa_edile_contribution · bilateral_funds · impact yes · open"
    CASSA EDILE CONTRIBUTION: the contribution to the Cassa Edile, set by the provincial agreements and shared by employer and worker (5,47% on the hourly elements in the Agrigento table of the Ministry of Labour of May 2025), is not modelled; only the 18.5% accrual for ferie and gratifica is. The worker's share lowers the net pay.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the provincial Cassa Edile contribution as a bilateral fund event, or model the provincial rates.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-02-21 | [↗](https://ance.it/wp-content/uploads/allegati/Tabella_nuovi_minimi_orari-_CCNL_2025.pdf) |
| — | — | 2025-02-21 | [↗](https://ance.it/wp-content/uploads/allegati/20250221_Verbale_accordo_rinnovo_CCNL_firmato.pdf) |
| — | — | 2010-04-19 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL_EDILIZIA_INDUSTRIA_2010_TESTO_COMPLETO.pdf) |
| — | — | 2019-04-04 | [↗](https://ance.it/wp-content/uploads/archive/37937-Art%20%2092%20Apprendistato-Nota%20a%20verbale.pdf) |

??? note "Coverage notes"
    RENEWAL: verbale di accordo of 21 February 2025 (ANCE, Legacoop Produzione e Servizi, Confcooperative Lavoro e Servizi, AGCI Produzione e Lavoro, Feneal-Uil, Filca-Cisl, Fillea-Cgil) renewing the CCNL of 3 March 2022 to 30 June 2028; three tranches of the minimi from 1 February 2025, 1 March 2026 and 1 March 2027 (ANCE table of the new minimi, the same as Allegato 10 of the verbale). Normative text: CCNL of 19 April 2010 (FILLEA text), as amended by the verbali of 2014, 2018, 2022 and 2025. The testo coordinato signed on 24 March 2026 is in the ANCE members' area and was not read.
    
    STRUCTURE: the CCNL treats operai and impiegati differently (extra months, seniority, sickness, night overtime), so the bundle splits it: edilizia-ance holds the operai of levels 1-4, edilizia-ance-impiegati the impiegati of levels 1-7 and the quadri of level 7 (Art. 77).
    
    PAY ELEMENTS: base_salary is the national minimo of the ANCE table; the ex indennità di contingenza and the EDR of EUR 10.33 (frozen national elements of the Protocollo of 31 July 1992) are fixed allowances read from the ANCE provincial tables. The EDR is outside the TFR base (Art. 33 and 72). hourly_divisor 173: Allegato A and Art. 44 last comma.
    
    INPS: the rates of contribution/2026/edilizia.json, by category of the worker.
    
    OPERAI: twelve monthly payments; paid by the hour worked (Allegato A, parameters.hourly_pay; state PeriodFacts.ordinary_hours_worked); ferie and gratifica natalizia are the 18.5% of the paga base and ex contingenza accrued with the Cassa Edile net of the withholdings (Art. 16 and 18, Allegato D: 14.2% withheld from the net pay), not extra months; the riposi annui are the 4.95% paid with the pay (Art. 5 B). No scatti di anzianità: the operai receive the APE through the Cassa Edile (Art. 29). The TFR is paid by the employer under L. 297/1982 (Art. 33). Prevedi: the contractual contribution of an operaio is an amount per ordinary hour worked (state PeriodFacts.ordinary_hours_worked).
    
    APPRENTICESHIP: Art. 92 (ANCE text of 4 April 2019): 72/72/78/78/85/90% by semester for 36 months towards levels 2-4 of the operai; the lavorazioni artistiche (48 months, semesters 7-8 at 90%), the apprendistato duale and the alta formazione are not modelled.
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-ance.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-ance.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-ance/example.py"
```
