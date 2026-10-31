# CCNL Edilizia PMI CONFAPI ANIEM

| | |
|---|---|
| **CNEL code** | `F018` |
| **Sector** | Edilizia |
| **Family** | `edilizia` |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-04-15 |
| **Workers (est.)** | ~70000 |
| **Ruleset version** | `2025.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFAPI ANIEM
    - FENEAL UIL
    - FILCA CISL
    - FILLEA CGIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, pension_fund_contribution, seniority, territorial_supplement |

9 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 15 verified / 30 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-04-15 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | Second review of the edilizia group: minimi of the seven levels in the two tranches and the monthly payments, against the testo armonizzato of the renewal of 15 April 2025. | corrected | The 14 minimi match Allegato A (operai, p. 187) and Allegato B (impiegati, p. 188) from 1 April 2025 and 1 March 2027: verified.<br>Monthly payments: the single file pays 13 to all levels, but the impiegati are owed 14 (Art. 63-64) and the operai a 18.5% to the Edilcassa instead of a tredicesima (Art. 16, 18). Both gaps were info notes; they are now limitations that block the runs they concern. The 13 stays assumed. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Articolo 63 - Tredicesima mensilita' (Parte II, impiegati) (p. 95): "La frazione di mese non superiore ai quindici giorni non va considerata mentre deve essere considerata come mese intero la frazione di mese superiore ai quindici giorni.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `7` | Livello VII — impiegato di 1a categoria Super / Quadro | € 2,325.96 | 2027-03-01 |
| `6` | Livello VI — impiegato di 1a categoria | € 2,093.36 | 2027-03-01 |
| `5` | Livello V — impiegato di 2a categoria | € 1,744.48 | 2027-03-01 |
| `4` | Livello IV — operaio di 4o livello / assistente tecnico | € 1,628.17 | 2027-03-01 |
| `3` | Livello III — operaio specializzato / impiegato di 3a categoria | € 1,511.88 | 2027-03-01 |
| `2` | Livello II — operaio qualificato / impiegato d'ordine | € 1,360.69 | 2027-03-01 |
| `1` | Livello I — manodopera generica | € 1,162.99 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.22 |
| `2` | € 8.22 |
| `3` | € 8.99 |
| `4` | € 9.61 |
| `5` | € 10.46 |
| `6` | € 12.84 |
| `7` | € 13.94 |

## Apprenticeship

**gruppo_4** (type: `percentage`)  
Destination levels: `2`  
percentage: 1.00

**gruppo_3_impiegati_3** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_2_impiegati_4_5** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 1.00

**gruppo_1_impiegati_6_7** (type: `percentage`)  
Destination levels: `6`, `7`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-pmi-confapi-aniem/territorial_sector_allowance · territorial_supplement · impact yes · open"
    ITS (Indennita' Territoriale di Settore) not modelled: varies by province/region. National table footnote: 'A questa Tabella occorre aggiungere l'ITS che varia da territorio a territorio'. The national tabular minimum does not include ITS.

    **Applies when:** `territorial_supplement` applies.

    **Remediation:** Model the ITS with a fact naming the province, or take it as a second-level element, then remove this limitation.

!!! warning "edilizia-pmi-confapi-aniem/cassa_edile_accruals_missing · bilateral_funds · impact yes · open"
    CASSA EDILE: the operai are owed the gratifica natalizia and the ferie as a 18.5% of the pay paid to the Edilcassa (Art. 16 and 18), not a tredicesima from the employer; the file pays them a direct 13th month, so the net, the employer cost and the Edilcassa contribution are all off.

    **Applies when:** `bilateral_funds` applies; category in operaio.

    **Remediation:** Model the operai in a file of their own with 12 monthly payments and the 18.5% Edilcassa accrual, as edilizia-ance does.

!!! warning "edilizia-pmi-confapi-aniem/impiegati_premio_annuo_missing · base_salary · impact yes · open"
    ADDITIONAL_MONTHS: the file pays 13 monthly payments to every level. The impiegati are owed a tredicesima (Art. 63) and a premio annuo of one monthly payment on 30 June (Art. 64), 14 in all, and after twenty years with the employer a premio di fedeltà (Art. 65); the premio annuo is not paid and the TFR and accruals read 13.

    **Applies when:** `base_salary` applies; category in impiegato, quadro.

    **Remediation:** Model the impiegati in a file of their own with 14 monthly payments (Art. 63-64), as edilizia-ance-impiegati does.

!!! warning "edilizia-pmi-confapi-aniem/operai_seniority_ape · seniority · impact yes · open"
    SENIORITY: Art. 49 lists impiegati scatti biennali by category. Level 1 has no explicit Art. 49 amount; engine uses 8.22 (Impiegati 4a category, same as level 2) as an approximation. For operai (levels 1-4), seniority is governed by the Cassa Edile anzianita' professionale edile (APE) system; engine uses the Art. 49 impiegati amounts as an approximation.

    **Applies when:** `seniority` applies; level in 1, 2, 3, 4.

    **Remediation:** Give the operai levels no scatti (APE paid by the Cassa Edile) and source the level 1 amount of Art. 49.

!!! warning "edilizia-pmi-confapi-aniem/provincial_evr · territorial_supplement · impact unknown · open"
    EVR (Elemento Variabile della Retribuzione): conditional, company/territory-specific bonus. Not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the provincial EVR as an input.

!!! warning "edilizia-pmi-confapi-aniem/operai_gruppo_3_track_merged · base_salary · impact unknown · open"
    SIMPLIFICATION: Apprenticeship destination conflicts. Art. G defines 4 operai groups and 3 impiegati bands. Engine tracks use disjoint destination_levels: level '2' -> gruppo_4 (36m); level '3' -> gruppo_3 (48m, ref=L2); levels '4'/'5' -> gruppo_2 (51m, ref=L3); levels '6'/'7' -> gruppo_1 (60m, ref=L3). Level '1' has no apprenticeship track (manual labor). Operai gruppo_3 (also exits at level '2', 48m) not modelled separately.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in 2.

    **Remediation:** Model the operai gruppo 3 track (48 months, exit at level 2) separately and select it by track name.

!!! warning "edilizia-pmi-confapi-aniem/apprentice_its_evr_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Apprentice base per Art. G includes ITS and EVR alongside paga_base + contingenza. Engine covers only paga_base + contingenza; apprentice gross is understated where ITS applies.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Add ITS and EVR to the apprentice base of Art. G.

!!! warning "edilizia-pmi-confapi-aniem/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "edilizia-pmi-confapi-aniem/contractual_fund_partial · pension_fund_contribution · impact unknown · open"
    The Fondapi contractual contribution (10 EUR riparametrati a month) is owed on every run that pays the month, in full; the Scheda states no rule for a partly employed month, a part-time worker or the extra months: a partial month or part time pays the full amount, an extra-month run none.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source the rule of the CCNL Confapi Aniem for a partial month and part time and model it, then remove this note.

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

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL%20_Aniem_Confapi%20Armonizzato_15042025.pdf | altro | 2025-04-15 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/EDILIZIA/CCNL%20_Aniem_Confapi%20Armonizzato_15042025.pdf) |

??? note "Coverage notes"
    SPLIT MODEL: paga_base (changes each tranche) + contingenza (frozen) + EDR (frozen at 10.33). Tranche 1: 01/04/2025; Tranche 2: 01/03/2027. Source: FILLEA CGIL testo armonizzato 15/04/2025 (Art. 25 and tabelle allegate).
    
    CONGLOBATED CHECK: L1 01/04/2025 total 1611.78 / 173 = 9.317 (non-integer). L4 = 2055.65 / 173 = 11.88 (matches official hourly table). Split model confirmed.
    
    HOURLY DIVISOR: 173, from Art. 25 CCNL: 'dividendo per 173 i valori minimi mensili'. Confirmed by official hourly rate column in FILLEA CGIL salary table.
    
    INPS: reuses 2026-edilizia.json (the edilizia rates by employer size and worker category). Cassa Edile ~18.5% contribution is separate and not included in INPS rates (review of 2026-10-30)
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-pmi-confapi-aniem.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-pmi-confapi-aniem.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-pmi-confapi-aniem/example.py"
```
