# CCNL Area Legno-Lapidei — Artigianato

| | |
|---|---|
| **CNEL code** | `F060` |
| **Sector** | legno arredamento lapidei artigianato |
| **Family** | `legno-arredamento` |
| **Tax sector** | `artigianato` |
| **Last renewal** | 2024-03-05 |
| **Workers (est.)** | ~95k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNA Produzione
    - CNA Costruzioni
    - Confartigianato Legno e Arredo
    - Confartigianato Marmisti
    - Casartigiani
    - CLAAI
    - Feneal-UIL
    - Filca-CISL
    - Fillea-CGIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer |

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 33 verified / 6 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-05 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 47 - Gratifica natalizia per il Settore Legno, Arredamento, Mobili; Art. 47 bis - Gratifica natalizia per il Settore Escavazione e Lavorazione di materiali Lapidei (p. 45): "il lavoratore non in prova ha diritto a tanti dodicesimi dell'ammontare della 13° mensilità quanti sono i mesi di servizio prestati presso l'azienda. La frazione di mese superiore ai 15 giorni sarà considerata come mese intero. [...] La frazione di mese superiore a 15 giorni sarà considerata come mese intero.". Match: more_than 15. |
| 2026-10-18 | claude-opus-5-5 (ai) | The conglobated retribuzione tabellare of the eight levels of the Imprese Artigiane, Settore Legno, Arredamento, Mobili table against the signed verbale integrativo of 15 March 2024, which prints the table after each of the four tranches (01/03/2024, 01/01/2025, 01/01/2026, 01/10/2026) of the renewal of 5 March 2024. | confirmed | The signed verbale integrativo of 15 March 2024 (signatures of CNA, Confartigianato Legno e Arredo, Confartigianato Marmisti, Casartigiani, CLAAI, Feneal, Filca, Fillea) prints, for the Imprese Artigiane Settore Legno, Arredamento, Mobili, the retribuzione tabellare before and after each tranche (PDF pp. 2-4). Image-only scan, read on the page images. The file models this table (not the PMI or Lapidei tables): all 32 values match.<br>The copy used is published by Confartigianato Imprese Vicenza, a territorial association of the signatory Confartigianato. Cross-checks: the signed ipotesi of 5 March 2024 (FILLEA-CGIL copy, PDF p. 7) prints the level D tranches 55/50/40/35; the FILLEA-CGIL leaflet prints the same 01/09/2022 base, per-level tranches and 01/10/2026 regime values for every level.<br>The printed item is the retribuzione tabellare (conglobated minimo, contingenza conglobata), matching the file's base_salary meaning.<br>Level C 01/03/2024 is printed '1639,4' (trailing zero dropped); recorded as 1639,40, equal to the file value.<br>The ruleset names a document of a signatory association: source_type contracting_party. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `AS` | Level AS — quadro / senior technical manager (top level) | € 2,278.43 | 2026-10-01 |
| `A` | Level A — managerial employee / highly specialised technician | € 2,123.69 | 2026-10-01 |
| `B` | Level B — white-collar employees / expert skilled workers | € 1,941.22 | 2026-10-01 |
| `CS` | Level CS — expert skilled worker / senior white-collar employee | € 1,856.85 | 2026-10-01 |
| `C` | Level C — skilled worker / white-collar employee | € 1,771.64 | 2026-10-01 |
| `D` | Level D — qualified worker / employee | € 1,674.71 | 2026-10-01 |
| `E` | Level E — general worker / clerical staff | € 1,585.97 | 2026-10-01 |
| `F` | Level F — entry grade (transitional, max 12 months) | € 1,490.13 | 2026-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `AS` | € 20.49 |
| `A` | € 18.94 |
| `B` | € 16.88 |
| `CS` | € 16.18 |
| `C` | € 15.33 |
| `D` | € 14.30 |
| `E` | € 13.52 |
| `F` | € 0.00 |

## Apprenticeship

**gruppo_1_legno** (type: `percentage`)  
Destination levels: `AS`, `A`, `B`  
percentage: 1.00

**gruppo_2_legno** (type: `percentage`)  
Destination levels: `CS`, `C`, `D`  
percentage: 1.00

**gruppo_3_legno** (type: `percentage`)  
Destination levels: `E`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "legno-lapidei-artigianato-confartigianato/lapidei_tables_not_modelled · base_salary · impact yes · open"
    Only Legno/Arredamento/Mobili sub-sector salary tables modelled. Lapidei (stone/marble) sub-sector uses different salary tables and is not modelled. CNEL code F060 covers both sub-sectors. Workers in Lapidei should verify against the specific Lapidei tables.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Lapidei sub-sector salary tables as a separate file.

!!! warning "legno-lapidei-artigianato-confartigianato/impiegati_apprenticeship_duration · base_salary · impact yes · open"
    Apprenticeship tables use operai duration tracks (5 years for gruppi 1-2, 2.5 years for gruppo 3). Impiegati and impiegati amministrativi have shorter 3-year apprenticeship durations with the same percentages — not separately modelled. For impiegato apprenticeships the operai duration overstates the period.

    **Applies when:** `base_salary` applies; contract type in apprentice; category in impiegato.

    **Remediation:** Model the 3-year impiegati apprenticeship tracks.

!!! note "legno-lapidei-artigianato-confartigianato/null_category_operaio_rate · inps_employer · impact unknown · resolved"
    LEVEL CATEGORY: all levels left null. Primary source text shows multiple levels map to both operai and impiegati (e.g. level B = 'Impiegati di concetto - Operai specializzati provetti') — this is a genuine one-to-many mapping that the schema cannot represent as a single category value, not a data gap. 2026-artigianato.json applies rate 0.2693 (default/operaio) for null category; impiegato rate 0.2471 not applied to impiegato-eligible levels.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved (review of 2026-10-30): a level without category takes the category the employment declares (employment/category/rules.py resolve_worker_category), and contribution/rate/rules.py inps_employer_rate applies employer_rate_by_category to it; a run that declares none gets the provisional issue employer_rate_category_assumed. Tests: tests/integration/ccnl_engine/contribution/rate/test_rules.py::test_declared_category_needs_no_issue, ::test_level_without_category_gets_a_provisional_issue.

!!! warning "legno-lapidei-artigianato-confartigianato/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (artigianato) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the artigianato rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "legno-lapidei-artigianato-confartigianato/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (artigianato) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles whether the 0.91 NASpI reduction of the artisan employers also applies to apprentices, nor the wage-integration contribution they owe (the FSBA is paid outside INPS). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of artigianato (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/artigianato.json derived, then remove this note.

!!! warning "legno-lapidei-artigianato-confartigianato/cigo_rate_by_activity · inps_employer · impact yes · open"
    CIGO: an artisan firm of the lapidei is within the CIGO (D.Lgs. 148/2015 art. 13 c. 1 (Normattiva, text in force on 2026-10-14, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-09-14;148~art13!vig=2026-10-14, snapshot sha256 3f7019a244e01d36ac8e7c9e25bcf058c777c8ed758418ba261d83867672c46a)): 3.30% for its operai (lett. d) and 1.70% / 2.00% for its impiegati and quadri (lett. e-f); a firm of the legno is not. The artigianato table charges no CIGO and the request does not say which kind of firm it is, so the employer contributions of a lapidei firm are understated.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Model the CIGO of D.Lgs. 148/2015 art. 13 c. 1 by activity (edile, lapidei) apart from the tax sector, then remove this note.

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

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "notice_indemnity_partial · termination_notice · impact unknown · open"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source how the CCNL or case law measures the indemnity of a notice partly worked and apply it, then resolve this limitation.

!!! warning "notice_indemnity_extra_months · termination_notice · impact yes · open"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source whether the indemnity carries the rateo of the extra months (CCNL clause or case law) and add it, then resolve this limitation.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year, over 365 days (366 in a leap year), as INPS circ. 64/2001 par. 4 sets for a month worked full time. For a vertical part time the circular divides the pay of the month by its paid days, rest days included, which the request does not state: the engine applies the full-time measure, so the indemnity of a vertical or mixed part time may be misstated.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Take the paid days of the month before the leave of a vertical or mixed part time as a fact of the leave and divide its pay by them, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

!!! warning "arrears_unused_deductions · contract_renewal_arrears · impact yes · open"
    The engine computes the rate of the separate taxation of arrears from PriorYearTaxFacts.net_income_biennio (art. 21 cc. 1, 3 TUIR) but does not reduce the tax by the deductions of artt. 12 and 13 cc. 1-2 the worker did not use in the years the arrears refer to (art. 21 c. 4): the request does not state them, so the tax may be overstated.

    **Applies when:** `contract_renewal_arrears` applies; the run takes the engine code path.

    **Remediation:** Add the deductions the worker declares as unused for each year of the arrears and reduce the tax by them, then resolve this limitation.

!!! warning "una_tantum_readings · base_salary · impact unknown · open"
    The una tantum of a renewal is paid from the CCNL data with readings no text read settles in full: a month of service in the covered period counts with the days of the una tantum (15 when the text is silent), over the months of the period; the absences of a month do not reduce it, though a text may pay the months 'di effettiva prestazione'; a part time is paid in proportion to its hours; a run without the employment period is paid none; the share of the covered months of earlier years is taxed apart as arrears.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source the counting of the months, the part time and the taxation of each una tantum from its agreement, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| SOURCE: Direzionelavoro.it — Base CCNL 2022. Tables: salary base values by level (Sep 2022), hourly divisor 174, seniority amounts pre-Jan-2025, apprenticeship percentages (3 gruppi), mensilita=13, conglobated model confirmed ('Contingenza: conglobata nei minimi retributivi'). | altro | 2022-09-01 | [↗](https://www.direzionelavoro.it/files/ccnl_legno_lapidei_artigianato_2022.pdf) |
| SOURCE: StudioDalmaschio.it — 2024 rinnovo summary (signed 5 marzo 2024). Agreement date, salary increases per tranche (Mar 2024, Jan 2025, Jan 2026, Oct 2026), new seniority amounts from Jan 2025 per level, new apprentice seniority EUR 8.00 from Jan 2025, signatories confirmed. | altro | 2024-03-05 | [↗](https://www.studiodalmaschio.it/rinnovo-ccnl-legno-lapidei-artigianato-2024) |
| SOURCE: Kitech.it — CNEL code F060 confirmed. Jan 2026 salary table cross-validated: AS=2230.81, A=2079.31, B=1900.65, CS=1818.04, C=1734.61, D=1639.71, E=1552.82, F=1458.99. All 8 levels match computed values exactly. | tabella_retributiva | 2024-03-05 | [↗](https://www.kitech.it/ccnl/legno-arredo-artigianato) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati). Confirmed by primary source ('Contingenza: conglobata nei minimi retributivi'). Back-calculation at Jan 2025: AS=2176.39/174=12.508 EUR/h, D=1599.71/174=9.194 EUR/h, F=1423.40/174=8.180 EUR/h — all consistent with hourly divisor 174, confirming conglobated model.
    
    CNEL CODE: F060 confirmed from kitech.it page text ('Area Legno Lapidei (CNEL: F060)') and from direzionelavoro.it PDF URL slug.
    
    TRANCHE DATES: four tranches — 2024-03-01 (retroactive from renewal 5 Mar 2024), 2025-01-01, 2026-01-01, 2026-10-01. Source: studiodalmaschio.it rinnovo summary, cross-validated Jan 2026 values against kitech.it.
    
    HOURLY DIVISOR: 174. Source: primary CCNL text ('Coefficiente orario = 174'). Derived: 40h/week x 52/12 = 173.33, rounded to 174 per contract clause.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). No quattordicesima in this CCNL. Source: direzionelavoro.it base CCNL PDF (mensilita aggiuntive clause).
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level amounts pre-Jan-2025 from 2022 base CCNL: AS=15.494, A=13.944, B=11.879, CS=11.181, C=10.329, D=9.296, E=8.522, F=none. From Jan 2025 (2024 rinnovo): AS=20.49, A=18.94, B=16.88, CS=16.18, C=15.33, D=14.30, E=13.52, F=none. Level F: transitional level (max 12 months), no seniority applies.
    
    APPRENTICE SENIORITY: EUR 8.00 from Jan 2025. New clause introduced by 2024 rinnovo. Source: studiodalmaschio.it rinnovo summary.
    
    LEVEL F: transitional insertion level, maximum duration 12 months. No seniority and no apprenticeship track apply. Workers in F are re-levelled to E or higher after the transitional period.
    
    APPRENTICESHIP: 3 gruppi from base CCNL 2022 (unchanged in 2024 rinnovo). Gruppo 1 (dest AS, A, B — operai 5 years = 60m), Gruppo 2 (dest CS, C, D — operai 5 years = 60m), Gruppo 3 (dest E — operai 2.5 years = 30m). Level F has no apprenticeship track.
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    

## Raw data

The contract file this page is generated from: [`agreement/legno-lapidei-artigianato-confartigianato.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/legno-lapidei-artigianato-confartigianato.json).

## Usage example

```python
--8<-- "docs/examples/agreement/legno-lapidei-artigianato-confartigianato/example.py"
```
