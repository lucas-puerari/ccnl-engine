# CCNL Laterizi e Manufatti Cementizi - Industria

| | |
|---|---|
| **CNEL code** | `F021` |
| **Sector** | industria |
| **Family** | `materiali-estrattive` |
| **Tax sector** | `industria` |
| **Last renewal** | 2022-05-31 |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Ceramica Raggruppamento Laterizi
    - Assobeton
    - FENEAL-UIL
    - FILCA-CISL
    - FILLEA-CGIL

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
| **Rule provenance** | 1 verified / 98 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2022-05-31 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | confirmed | Art. 26 - Tredicesima mensilità (p. 42): "Nel caso di inizio o di cessazione del rapporto di lavoro nel corso dell'anno, saranno corrisposti tanti dodicesimi della 13ª mensilità per quanti sono i mesi di servizio prestato presso l'azienda. La frazione di mese superiore ai 15 giorni sarà considerata agli effetti della 13ª mensilità come un mese intero.". Match: more_than 15. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ASQ` | Quadri AS — Impiegati inquadrati al livello AS con responsabilita di coordinamento e gestione di settori fondamentali | € 2,588.66 | 2028-07-01 |
| `AS` | AS — Impiegati con funzioni direttive e discrezionalita di poteri | € 2,588.66 | 2028-07-01 |
| `A` | A — Impiegati con funzioni autonome di guida e coordinamento | € 2,176.82 | 2028-07-01 |
| `B` | B — Impiegati e Operai con mansioni di concetto o manutenzione impianti con coordinamento | € 1,776.77 | 2028-07-01 |
| `CS` | CS — Operai specializzati con interventi elettrici/elettronici o coordinamento squadra | € 1,681.04 | 2028-07-01 |
| `C` | C — Impiegati e Operai con autonomia esecutiva e conoscenze professionali specifiche | € 1,599.23 | 2028-07-01 |
| `D` | D — Impiegati con mansioni d'ordine e Operai con capacita tecnico-pratiche | € 1,485.67 | 2028-07-01 |
| `E` | E — Impiegati con mansioni esecutive generiche e Operai con capacita pratica di mestiere | € 1,377.67 | 2028-07-01 |
| `F` | F — Operai con semplici conoscenze conseguibili con breve pratica (incl. superminimo 4.13 EUR) | € 1,178.55 | 2028-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `ASQ` | € 14.72 |
| `AS` | € 14.72 |
| `A` | € 11.71 |
| `B` | € 9.60 |
| `CS` | € 8.70 |
| `C` | € 8.32 |
| `D` | € 7.87 |
| `E` | € 7.23 |
| `F` | € 6.79 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `ASQ`, `AS`, `A`, `B`

**professionalizzante_30** (type: `under_classification`)  
Destination levels: `CS`, `C`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `D`

**professionalizzante_12** (type: `under_classification`)  
Destination levels: `E`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "laterizi-industria-f021/level_e_first_period_one_below · base_salary · impact yes · open"
    APPRENTICESHIP — level E period 1: the CCNL Art. 9 prescribes 2 levels below destination for period 1 in all tracks. For destination E (order=2), 2 below would reach order=0 which does not exist. Engine level_by_order raises ValueError for missing orders. SIMPLIFICATION: E track period 1 uses levels_below=1 (pay at level F, order=1), the lowest available level below E. Duration: 6+6 months.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in E.

    **Remediation:** Confirm the level E first period against Art. 9 and model it once a level two below exists.

!!! warning "laterizi-industria-f021/asq_seniority_from_as · seniority · impact unknown · open"
    ASQ SENIORITY: thaler.it seniority table lists AS, A, B, CS, C, D, E, F amounts but not ASQ separately. SIMPLIFICATION: ASQ uses the same scatto amount as AS (14.72 EUR/biennio).

    **Applies when:** `seniority` applies; level in ASQ.

    **Remediation:** Source the ASQ scatto amount from the official seniority table.

!!! warning "laterizi-industria-f021/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.filcacisl.it/sindacato/wp-content/uploads/2022/06/Ccnl-laterizi-manufatti-industria-31-5-2022.pdf | altro | 2022-05-31 | [↗](https://www.filcacisl.it/sindacato/wp-content/uploads/2022/06/Ccnl-laterizi-manufatti-industria-31-5-2022.pdf) |
| https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/LATERIZI/Ipotesi_di_Accordo_Rinnovo_CCNL_Laterizi_e_manufatti_31.10.2025.pdf | altro | 2025-10-31 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/LATERIZI/Ipotesi_di_Accordo_Rinnovo_CCNL_Laterizi_e_manufatti_31.10.2025.pdf) |
| https://www.filcacisl.it/sindacato/wp-content/uploads/2025/02/Tabella-retributiva-CCNL-Laterizi-INDUSTRIA-DA-FEBBRAIO-2025.pdf | tabella_retributiva | 2022-05-31 | [↗](https://www.filcacisl.it/sindacato/wp-content/uploads/2025/02/Tabella-retributiva-CCNL-Laterizi-INDUSTRIA-DA-FEBBRAIO-2025.pdf) |
| https://lawinsider.com/it/contracts/euRWxUzbye9 | altro | 2020-02-12 | [↗](https://lawinsider.com/it/contracts/euRWxUzbye9) |
| https://www.thaler.it/assets/files/Transparenzdekret/Laterizi_-_Aziende_industriali.pdf | tabella_retributiva | — | [↗](https://www.thaler.it/assets/files/Transparenzdekret/Laterizi_-_Aziende_industriali.pdf) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = paga tabellare (TEM), varying by level and tranche. fixed_allowances per level: CONTINGENZA (frozen since 1993 Protocol) + EDR (10.33 EUR, all levels). Level AS also carries Indennita di funzione quadri (51.65 EUR) — applied to ASQ level only. Source: FILCA-CISL tabella retributiva (2022 and 2025 renewals); thaler.it parametri contrattuali.
    
    SALARY TABLE: 2022 contract (decorrenza 01/04/2022, signed 31/05/2022): 3 tranches at 01/07/2022, 01/10/2023, 01/02/2025. 2025 contract (decorrenza 01/10/2025, signed 31/10/2025): 4 tranches at 01/10/2025, 01/07/2026, 01/07/2027, 01/07/2028. Sources: FILCA-CISL salary tables (primary).
    
    HOURLY DIVISOR: 174. Source: thaler.it parametri contrattuali ('Divisori Giornaliero: 174'). Consistent with 40h/week standard (40 x 52 / 12 = 173.33 rounded to 174) and confirmed by filleacgil.it lapidei CCNL text referencing the same divisor.
    
    APPRENTICESHIP: under_classification, Art. 9 Apprendistato professionalizzante from 12/02/2020 CCNL organic text (lawinsider.com/it/contracts/euRWxUzbye9). Checked 2022 renewal (modified articles: 13, 14, 21, 31, 33, 35bis, 35ter, 52 — Art. 9 absent) and 2025 renewal (modified articles: 3, 4, 9bis, 13, 21, 32, 33, 35bis, 35ter, 53, 55, 66 — Art. 9 absent). Art. 9 unchanged in both renewals; 2020 text governs.
    
    LEVEL F SUPERMINIMO: FILCA-CISL table note: 'Nel livello F e compreso l'importo di euro 4,13 a titolo di superminimo.' The 4.13 EUR is already embedded in the base_salary values for level F across all tranches. No separate fixed_allowance added.
    
    ASQ LEVEL: distinct classification from AS. Quadri (ASQ) hold the same paga tabellare as AS but additionally receive the Indennita di funzione quadri (51.65 EUR/month). Source: thaler.it 'Livelli e Qualifiche' table and 'Indennita funzione quadri: 51.65 euro mensili lordi'. FILCA-CISL salary table groups AS+quadri in a single row labelled 'A S' with Supermin.individ.=51.65; lavoro-economia.it c=131 shows separate ASQ and AS totals.
    
    ARCO FUND: employer complementary pension contribution from 01/07/2026 = 1.90%, from 01/01/2028 = 2.00% (2025 renewal Art. 55). The ARCO base is: paga tabellare + contingenza + EDR + indennita funzione quadri (where applicable). Not modelled: parameters.employer_funds holds no ARCO fund, so a PensionFundEnrolment in ARCO is rejected; the schema holds CCNL pension funds on enrolment (employer_funds), as other CCNLs do (review of 2026-10-30)
    
    TAX SECTOR: industria. Brick and tile makers are classified in the industria, class 11 'Lavorazione dei minerali non metalliferi' (category 08 'Produzione di materiali da costruzione in laterizio'; ATECO 23.32.00 'Fabbricazione di mattoni, tegole ed altri prodotti per l'edilizia in terracotta' takes CSC 11108), and concrete products in category 11, not in the class 13 of the edilizia: INPS, Manuale di classificazione dei datori di lavoro ai fini previdenziali e assistenziali, maggio 2021 (https://www.inps.it/content/dam/inps-site/pdf/allegati/3212KEY-manuale_di_classificazione_dei_datori_di_lavoro_maggio_2021.pdf, sha256 ad8704fbb47ccf22b7f3728a2537351294a12b2aa031a7bb2cce88121d884678), pp. 29 and 96. Their CIGO is the 1.70% / 2.00% of the industrial firms (D.Lgs. 148/2015 art. 13 c. 1 (Normattiva, text in force on 2026-10-14, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-09-14;148~art13!vig=2026-10-14, snapshot sha256 3f7019a244e01d36ac8e7c9e25bcf058c777c8ed758418ba261d83867672c46a), lett. a-b), not the 4.70% of the 'operai delle imprese dell'industria e artigianato edile' (lett. c) the edilizia table carries.
    

## Raw data

The contract file this page is generated from: [`agreement/laterizi-industria-f021.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/laterizi-industria-f021.json).

## Usage example

```python
--8<-- "docs/examples/agreement/laterizi-industria-f021/example.py"
```
