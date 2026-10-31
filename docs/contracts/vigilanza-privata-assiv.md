# CCNL Istituti e Imprese di Vigilanza Privata e Servizi Fiduciari — ASSIV/ANIVP/UNIV (GPG)

| | |
|---|---|
| **CNEL code** | `HV40` |
| **Sector** | vigilanza-privata |
| **Family** | `vigilanza` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-05-30 |
| **Workers (est.)** | ~85k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSIV
    - ANIVP
    - UNIV
    - Legacoop Produzione e Servizi
    - AGCI Servizi
    - Confcooperative Lavoro e Servizi
    - FILCAMS-CGIL
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
| **Limits of this contract** | inps_employer, seniority |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 49 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2023-05-30 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-12-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The paga base tabellare conglobata of the GPG section (levels Q and 1-6), six tranches from 1/6/2023 to 1/12/2026, against the ipotesi di accordo of 16 February 2024 and the cost-of-labour tables of Ministry of Labour D.D. n. 50 of 8 August 2024. | confirmed | Ipotesi di accordo 16/02/2024 (p. 2, page image checked): the table printing the 4th and 6th level paga base tabellare conglobata from 1/6/2024 to 1/12/2026 matches the file; these 10 minimi move to verified. The other levels follow, per the same page, by applying the conventional parameters of the CCNL to the 4th level increments; the 6th level is set conventionally.<br>Ministry of Labour D.D. n. 50 of 8/8/2024 (tables for the Servizio tecnico-operativo, PDF pp. 18-23; same values on the amministrativo pages 12-17) prints the annual paga base tabellare conglobata per level at 6/2023, 6/2024, 6/2025, 12/2025, 4/2026 and 12/2026; the decree states the signatory parties formally shared the final tables on 7/8/2024. Divided by 12, all 42 values equal the file: the 32 periods not printed monthly in the ipotesi are recorded as derived.<br>FILCAMS CGIL publishes the same monthly table online (page 'Vigilanza privata e Servizi di sicurezza - 16 febbraio 2024'); it matches the file for every tranche from 1/6/2024 and for levels 1, 3, 4, 6 at 1/6/2023, but prints Q 2049,04, level 2 1660,39 and level 5 1261,86 at 1/6/2023 (file and decree: 2049.03, 1660.38, 1261.87). Its own 1/6/2024 values (2097,24, 1696,09, 1285,44) build on the file's figures, so the difference is a 0.01 rounding in that column; the decree values are kept.<br>The base_salary of the file is the paga base tabellare conglobata (salario unico nazionale, art. 106 CCNL 2013), the item both sources print; scatti, the una tantum and the 13th/14th are separate.<br>The ruleset now names the ipotesi of 16/02/2024 published via the FILCAMS CGIL contract page: source_type contracting_party instead of the aggregator page.<br>Maintainer decision: all 42 periods are derived from the Ministry of Labour D.D. n. 50 of 08/08/2024 (cost tables, annual paga base / 12); the unsigned ipotesi of 16/02/2024 is only a cross-check for levels 4 and 6. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | GPG Senior Manager (Quadro) — maximum operational and managerial responsibility | € 2,434.74 | 2026-12-01 |
| `1` | GPG Grade 1 — security guard with operational responsibilities | € 2,086.89 | 2026-12-01 |
| `2` | GPG Grade 2 — highly specialist security guard | € 1,946.09 | 2026-12-01 |
| `3` | GPG Grade 3 — specialist security guard | € 1,723.31 | 2026-12-01 |
| `4` | GPG Grade 4 — qualified security guard (contractual reference level) | € 1,528.88 | 2026-12-01 |
| `5` | GPG Grade 5 — security guard with specific qualification | € 1,450.44 | 2026-12-01 |
| `6` | GPG Grade 6 — security guard, basic duties | € 1,350.44 | 2026-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 31.30 |
| `1` | € 26.12 |
| `2` | € 23.83 |
| `3` | € 22.46 |
| `4` | € 21.13 |
| `5` | € 20.52 |
| `6` | € 19.66 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `6`, `5`, `4`, `3`, `2`, `1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "vigilanza-privata-assiv/terziario_tax_sector_unverified · inps_employer · impact unknown · open"
    INPS: reuses the terziario contribution table. SIMPLIFICATION: tax_sector='terziario' is a modelling choice. Supporting facts: ASSIV/ANIVP/UNIV are not Confindustria members; private security companies do not access CIGO; the sector uses Ebivip (Ente Bilaterale Vigilanza Privata) for bilateral welfare, not INPS integration schemes. TERZIARIO is the standard classification for non-Confindustria services sector employers in INPS circular IVS rates. Counterargument: some aspects of the sector (24/7 operations, shift work) could suggest INDUSTRIA classification, whose employer rate is about 1.2 points higher in each headcount band of the bundle (review of 2026-10-30).

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS classification of private security employers against the INPS circular.

!!! warning "vigilanza-privata-assiv/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "notice_indemnity_partial · termination_notice · impact unknown · open"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source how the CCNL or case law measures the indemnity of a notice partly worked and apply it, then resolve this limitation.

!!! warning "notice_indemnity_extra_months · termination_notice · impact yes · open"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source whether the indemnity carries the rateo of the extra months (CCNL clause or case law) and add it, then resolve this limitation.

!!! warning "notice_indemnity_tfr · termination_notice · impact unknown · open"
    The notice indemnity enters the TFR base as payroll practice holds; art. 2120 c. 2 c.c. counts the sums paid 'a titolo non occasionale' and no primary source read settles whether this indemnity is among them, so the TFR quota of the termination run may be overstated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the notice indemnity (case law of the Cassazione or a Ministry ruling) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30121:vigilanza452023&catid=257&Itemid=139 | altro | 2023-05-30 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30121:vigilanza452023&catid=257&Itemid=139) |
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=33337:servizi-vigilanza-privata-e-servizi-fiduciari-ccnl,-21-novembre-2024&catid=262&Itemid=139 | altro | 2024-11-21 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=33337:servizi-vigilanza-privata-e-servizi-fiduciari-ccnl,-21-novembre-2024&catid=262&Itemid=139) |
| https://www.univigilanza.it/263/CODICE-ALFANUMERICO-UNICO-DEI-CCNL-.html | altro | 2024-11-21 | [↗](https://www.univigilanza.it/263/CODICE-ALFANUMERICO-UNICO-DEI-CCNL-.html) |
| https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30385:vigilanza-privata19723&catid=257&Itemid=139 | altro | 2023-07-19 | [↗](https://olympus.uniurb.it/index.php?option=com_content&view=article&id=30385:vigilanza-privata19723&catid=257&Itemid=139) |

??? note "Coverage notes"
    SCOPE: GPG section only (Guardie Particolari Giurate, livelli Q e 1-6). The Servizi Fiduciari/Sicurezza section (livelli A-E, 9 tranches from 01/08/2022) is a distinct salary table and would be a separate data file.
    
    CNEL CODE: HV40 confirmed from primary source: univigilanza.it (UNIV is a signatory employer association), article titled 'Codice Alfanumerico Unico dei CCNL' — 'L'attuale codice di riferimento per il settore vigilanza privata è il HV40.'
    
    SALARY MODEL: conglobated (paga base tabellare conglobata). Sources: (1) 2024 integrative accord salary table header reads 'Paga Conglobata' explicitly; (2) Art. 112 base CCNL 2013: 'stipendio o salario unico nazionale (paga base tabellare conglobata).' Back-calculation: 4° livello 01/06/2023 = 1328.88 / 173 = 7.68 EUR/h; 1° livello = 1772.60 / 173 = 10.25 EUR/h; Q = 2049.03 / 173 = 11.84 EUR/h. Non-integer results confirm conglobated total (not an integer-multiple hourly rate), consistent with historical accumulation of contingenza increments. fixed_allowances=[] for all levels.
    
    SALARY TRANCHES: 6 tranches modelled (01/06/2023 → 01/12/2026) from the 2024 integrative accord 'Tabelle Retributive' (PDF, 2 pages). A prior 01/03/2016 historical column is also present but predates current renewal scope and is not modelled. Source: 2024 integrative accord signed by all 9 signatories.
    
    LEVEL ORDERING: CCNL numbering is counter-intuitive — level '6' is the entry level (lowest salary) and 'Q' (Quadro) is the highest. order=1 corresponds to level 6 (lowest), order=7 to level Q (highest). Salary strictly monotone across all 6 tranches: verified.
    
    HOURLY DIVISOR: 173. Source: Art. 115 base CCNL 2013 — 'dividendo convenzionalmente la retribuzione stessa per 173.' Consistent with 40h/week standard (Art. 71, base CCNL 2013).
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Source: Art. 117 base CCNL 2013. Confirmed applicable to part-time workers too (Art. 64, base CCNL 2013).
    
    APPRENTICESHIP professionalizzante, 100% of the destination level for the whole period (CCNL 21/11/2024 Art. 86, olympus.uniurb.it: 'L'Apprendista ha diritto per tutta la durata del periodo di apprendistato all'inquadramento e alla corrispondente retribuzione del livello finale di collocazione'), max 36 months (Art. 82). The track covers GPG levels 6 to 1; Quadri are not a destination.
    
    SENIORITY triennale (36 months), max 6 scatti; per-level amounts from Art. 111 base CCNL 2013 (Q=31.30, 1°=26.12, 2°=23.83, 3°=22.46, 4°=21.13, 5°=20.52, 6°=19.66), effective 01/02/2013 and assumed current: the 2023 accord (30/05/2023) covers salary tranches and una tantum only, the 2024 integrative accord salary tables only. The 2023 clause on 'permanenza nei Livelli VI e V ... da 24 a 18 mesi' concerns classificatory progression, not seniority.
    

## Raw data

The contract file this page is generated from: [`agreement/vigilanza-privata-assiv.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/vigilanza-privata-assiv.json).

## Usage example

```python
--8<-- "docs/examples/agreement/vigilanza-privata-assiv/example.py"
```
