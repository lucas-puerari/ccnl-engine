# CCNL Comparto Istruzione e Ricerca 2022-2024 e 2025-2027 (trattamento economico) - ARAN

| | |
|---|---|
| **CNEL code** | `S305` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-07-01 |
| **Workers (est.)** | ~1,2M |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FSUR
    - FLC CGIL
    - UIL SCUOLA RUA
    - SNALS CONFSAL
    - GILDA UNAMS
    - ANIEF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employee, overtime |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 48 verified / 41 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-07-01 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2027-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-12 | claude-opus-5-5 (ai) | Salary tables of the seven scuola profiles, leave, sickness, seniority, overtime and the daily quota, against the signed ARAN texts of 2007, 2024, 2025 and 2026. | corrected | Every monthly tabellare was the annual amount over 13; the tables are per 12 mensilità plus the tredicesima: the values were about 7.7% low (e.g. Docente infanzia 2024: 1,724.65 -> 1,868.37).<br>The pre-2024 periods were back-calculated with the increments times 13 and started on 2022-01-01; they are now the tables of the CCNL 2019-2021, in force from 1 February 2023.<br>The CCNL 2025-2027 on the economic treatment, signed definitively on 1 July 2026, was missing: periods from 1.1.2025, 1.1.2026 and 1.1.2027 added.<br>Signatories: FLC CGIL did not sign the CCNL 2022-2024 (it signed the 2025-2027); ANIEF signed both and was missing.<br>Ferie: 32 days, 30 for the first 3 years (CCNL 2007 art. 13), not 28.<br>Sickness: comporto of 18 months with 9 months at 100%, 3 at 90% and 6 at 50% (art. 17), not 270 days at 100%.<br>Overtime: the scuola pays fixed hourly amounts, not percentages: the 15/30/30/50% bands had no basis and are removed.<br>Daily quota: no scuola text fixes it; by_26 is now assumed. |
| 2026-10-12 | claude-opus-5-5 (ai) | Overtime of the scuola ATA staff: Tabella E1.7 of the CCNL 2019-2021 and the overtime articles of the CCNL 2022-2024 and 2025-2027. | corrected | The ATA 'prestazioni aggiuntive' are paid at fixed hourly amounts by area from 1 January 2024 (Tabella E1.7): nine bands in EUR per hour by area and time of day, now paid by the engine.<br>The CCNL 2022-2024 (art. 23) and 2025-2027 (art. 11) update only the università overtime (Tabella B4): the scuola amounts stay those of 2024.<br>The docenti ore aggiuntive (Tabella E1.6) are by activity, not by time of day: left to the caller (limitation fixed_hourly_overtime, docenti levels). |
| 2026-10-12 | claude-opus-5-5 (ai) | Fasce stipendiali of the scuola staff, 2023-2027. | corrected | Every worker was paid the first fascia (0-8 years): the five higher fasce are now seniority steps, read on the tables of the three CCNL.<br>DOCENTE_SECONDARIA joined the scuola media and the laureato di II grado, equal in the first fascia only: split into DOCENTE_SECONDARIA (scuola media) and DOCENTE_LAUREATO_SECONDARIA_II. |
| 2026-10-12 | claude-opus-5-5 (ai) | Months from 1.1.2022 to 31.1.2023 (CCNL 2019-2021 Tabella C1). | corrected | The file started on 1.2.2023 (limitation before_february_2023): the tabellare dal 1.1.2021 and the elemento perequativo by fascia of Tabella C1 now cover 2022 and January 2023. |
| 2026-10-17 | claude-opus-5-5 (ai) | The number of instalments of the elemento perequativo of the CCNL 19/04/2018 the file pays until its conglobamento. | corrected | The 35 elemento perequativo records of the Scuola levels move from assumed to derived: INPS msg. 3224/2018 reads the element as paid 'con cadenza mensile', Tabella D2 of the CCNL 19/04/2018 gives 10 monthly instalments in 2018, and Tabella C1 of the CCNL 6/12/2022 (p. 244) prints the yearly amount as twelve monthly ones (308,04 = 12 x 25,67). No text puts it in the tredicesima. Art. 37 of the Scuola section was not read, so the records stay derived.<br>The absence rule stays assumed: no text of the comparto fixes the daily quota of an unpaid absence of the scuola staff. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `FUNZIONARIO_ED_ESPERTO` | ATA: Funzionario ed esperto (ex dsga, direttori servizi generali) | € 2,249.26 | 2027-01-01 |
| `DOCENTE_LAUREATO_SECONDARIA_II` | Docente laureato degli istituti secondari di II grado | € 2,141.60 | 2027-01-01 |
| `DOCENTE_SECONDARIA` | Docente scuola secondaria di I grado (scuola media, educazione fisica) | € 2,141.60 | 2027-01-01 |
| `DOCENTE_DIPLOMATO_SECONDARIA` | Docente diplomato degli istituti secondari di II grado | € 1,978.53 | 2027-01-01 |
| `DOCENTE_INFANZIA_PRIMARIA` | Docente scuola dell'infanzia e primaria | € 1,978.53 | 2027-01-01 |
| `ASSISTENTE` | ATA: Assistente amministrativo, assistente tecnico, cuoco, infermiere | € 1,717.20 | 2027-01-01 |
| `OPERATORE` | ATA: Operatore scolastico (nuovo profilo dal 1/5/2024 CCNL 18/1/2024) | € 1,615.41 | 2027-01-01 |
| `COLLABORATORE_SCOLASTICO` | ATA: Collaboratore scolastico (ex bidello, ex commesso) | € 1,540.49 | 2027-01-01 |

## Seniority increments

**Cadence:** every 108 months  
**Maximum:** 5 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "istruzione-ricerca-aran/enam_base · inps_employee · impact yes · open"
    The ENAM of a permanent teacher of the scuola dell'infanzia and primaria (L. 93/1957 art. 3: 1% of 80% of the stipendio) is computed on the whole minimum of the level; the stipendio it counts leaves out the IIS conglobata the retribuzione tabellare holds, which the bundle does not give apart: the contribution is overstated.

    **Applies when:** `inps_employee` applies; the run takes the engine code path.

    **Remediation:** Source the IIS conglobata of the profile, leave it out of the ENAM base, then remove this note.

!!! warning "istruzione-ricerca-aran/fixed_hourly_overtime · overtime · impact yes · open"
    The ore aggiuntive of the docenti are paid at fixed hourly amounts by activity (CCNL 2019-2021 Tabella E1.6: corsi di recupero 55,00, insegnamento 38,50, non di insegnamento 19,25), not by time of day: no overtime band is modelled for the docenti levels, so their overtime event needs the amount as hourly_rate with multiplier 1. The ATA areas are paid by the bands of Tabella E1.7.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the amount of Tabella E1.6 of the activity as hourly_rate with multiplier 1.

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

### Without monetary impact

!!! note ""
    CNEL S305 confermato per comparto, include tutte le sezioni (scuola, università, ricerca, AFAM).

!!! note ""
    Hourly divisor 156 = 36h/settimana × 52/12. I docenti hanno orario cattedra (18h/settimana insegnamento), non direttamente comparabile. Il divisore si applica per l'hourly_rate indicativo.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL 2025-2027 sui principali aspetti del trattamento economico, signed definitively on 1 July 2026 by ARAN and every union of the comparto. Tabella A2 (pp. 18-19): tabellare from 1.1.2025, 1.1.2026, 1.1.2027. | altro | 2026-07-01 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/07/2026_07_01_CCNL_C_IR_2025-2027.pdf) |
| CCNL 2022-2024 (FLC CGIL did not sign). Tabella A2 (pp. 50-51): tabellare from 1.1.2024. | altro | 2025-12-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/12/2025_12_23_COMP-IR_2022-2024.pdf) |
| CCNL 2019-2021. Tabelle C1 and E1.5 (pp. 246, 256): tabellare from 1.2.2023. | altro | 2024-01-18 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/01/2024_01_18_COMP-IR_2019-2021.pdf) |
| CCNL Scuola 2006-2009, still in force for ferie (art. 13), malattia (art. 17) and tredicesima (art. 80). | altro | 2007-11-29 | [↗](https://www.aranagenzia.it/wp-content/uploads/2024/07/CCNL-SCUOLA-2006-2009.pdf) |

??? note "Coverage notes"
    Platea ~1,2M: ~800k docenti (infanzia, primaria, secondaria I e II), ~230k ATA scuola, ~130k personale università e ricerca, ~80k AFAM (quifinanza.it).
    
    Indennità di funzione (IF) docenti: da ~200€ a ~313€/mese a seconda dell'ordine (da CCNL 23/12/2025). Non modellata come fixed_allowance per eterogeneità tra ordini (SIMPLIFICATION).
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Personale università, ricerca e AFAM: non modellato separatamente (trattamento retributivo distinto con sezioni specifiche nel CCNL). SIMPLIFICATION: unico JSON copre principalmente la scuola.
    
    PENSION FUND. Fondo Scuola Espero (1% + 1%); enrolment is a fact, the silenzio-assenso of the hires from 2019 is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    ASSICURAZIONE SOCIALE VITA. The employers of this CCNL are Amministrazioni dello Stato (the State schools; the forze di polizia), which INPS circ. 104/2014 leaves out of the Assicurazione Sociale Vita (ex ENPDEP): meta.public_life_insurance is false.
    
    LEVELS. The Tabelle A1 and A2 of the CCNL 2022-2024 (from 1.1.2024) list 'Docente scuola dell'infanzia ed elementare' and 'Docente diplomato istituti sec. II grado' as two rows with the same amounts (22,420.48 a year in the first band): two levels with the same minimum, DOCENTE_INFANZIA_PRIMARIA and DOCENTE_DIPLOMATO_SECONDARIA, since only the first owes the ENAM.
    
    FASCE STIPENDIALI: the six fasce of anzianità di servizio (0-8, 9-14, 15-20, 21-27, 28-34, da 35) are paid as five seniority steps after 9, 15, 21, 28 and 35 years, each the difference between the monthly tabellari of two fasce (CCNL 2019-2021 Tabelle C1 and E1.5, 2022-2024 and 2025-2027 Tabella A2). The seniority is the anzianità di servizio recognised for the fasce (ricostruzione di carriera), which the caller states; the engine does not reconstruct it. The scuola media and the laureato di II grado have the same first fascia and differ above it: two levels, DOCENTE_SECONDARIA and DOCENTE_LAUREATO_SECONDARIA_II.
    
    FROM 1.1.2022 TO 31.1.2023: the tabellare dal 1.1.2021 of Tabella C1 of the CCNL 2019-2021 (column 1) and, apart, the elemento perequativo by fascia (column 2, 12 instalments assumed), conglobated in the tabellare from 1.2.2023.
    
    SALARY TABLES: monthly tabellare = annual tabellare of the fascia 0-8 over 12 (the tables are 'per 12 mensilità cui aggiungere la 13^ mensilità'). 1.2.2023-31.12.2023: CCNL 2019-2021 Tabelle C1 and E1.5; 2024: CCNL 2022-2024 Tabella A2; 2025, 2026, 2027: CCNL 2025-2027 Tabella A2.
    
    CNEL S305 da kitech.it per comparto Istruzione e Ricerca personale docente. Confermato coerente con S325 (area dirigenza IR).
    

## Raw data

The contract file this page is generated from: [`agreement/istruzione-ricerca-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/istruzione-ricerca-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/istruzione-ricerca-aran/example.py"
```
