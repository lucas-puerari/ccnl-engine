# CCNL Chimica e Affini PMI — Unionchimica Confapi

| | |
|---|---|
| **CNEL code** | `B018` |
| **Sector** | chimica |
| **Family** | `chimica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~56k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionchimica — Unione Italiana Industria Chimica PMI (Confapi)
    - FILCTEM-CGIL — Federazione Italiana Lavoratori Chimica Tessile Energia Manifatturiero
    - FEMCA-CISL — Federazione Energia Moda Chimica Affini
    - UILTEC-UIL — Unione Italiana Lavoratori Tecnologie Energie Chimica

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

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 21 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-02-23 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi of the 8 levels A-H of the chimica, concia e settori accorpati sector on 1 January 2026, derived from the minimi at 31/12/2025 and the 01/01/2026 increase printed in the signed ipotesi of 23 February 2026. | confirmed | Ipotesi 23 febbraio 2026 (22-page signed scan without text layer, published by Confapi Varese, territorial association of the Confapi system to which the signatory Unionchimica belongs; read on the page image of PDF p. 18; it bears the signatures of all parties and is linked from api.varese.it): the table 'Chimica - Concia e Settori accorpati' prints, for levels A (parametro 100,00) to H (178,79), the minimi al 31/12/2025 and the increases from 01/01/2026, 01/04/2027, 01/12/2027, 01/06/2028 and 01/12/2028. It does not print the resulting minimi, so the 2026-01-01 values are derived as minimo al 31/12/2025 + 01/01/2026 increase.<br>The file's levels A-H match the table (A lowest, H highest, same parameter order). All 8 file values equal the derivation to the cent: no correction. The same figures appear in the Confapi Varese illustrative circular of 24 February 2026 (p. 9).<br>The file's base_salary is the minimo tabellare, with the indennità di funzione (H) and the aggiunta personale (E, F, G) as fixed allowances; the table prints the minimi only, which matches.<br>The file's coverage note says 'Scala parametrale: H=100 reference, descending'; the signed table prints A = 100,00 rising to H = 178,79. The maintainer should fix the note.<br>The file models only the 2026-01-01 tranche: the four later tranches (1/4/2027, 1/12/2027, 1/6/2028, 1/12/2028) are printed in the same table and could be added by the maintainer.<br>The latest B018 text deposited at CNEL is the ipotesi of 5 December 2023 (deposito 194975); the 2026 renewal is not yet deposited. The ruleset now names the signed 2026 text: source_type contracting_party. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `H` | Level H — senior managers, top technical executives (quadri) | € 3,168.51 | 2026-01-01 |
| `G` | Level G — managers, senior professionals, department heads | € 2,973.58 | 2026-01-01 |
| `F` | Level F — senior technical staff, team leaders | € 2,703.06 | 2026-01-01 |
| `E` | Level E — specialist workers, junior technical staff | € 2,444.03 | 2026-01-01 |
| `D` | Level D — highly skilled operai, senior impiegati | € 2,267.00 | 2026-01-01 |
| `C` | Level C — skilled operai, standard impiegati | € 2,033.35 | 2026-01-01 |
| `B` | Level B — semi-skilled operai and lower-grade impiegati | € 1,830.43 | 2026-01-01 |
| `A` | Level A — entry workers, unskilled, first-time employees | € 1,690.69 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 10.33 |
| `B` | € 11.88 |
| `C` | € 12.91 |
| `D` | € 13.94 |
| `E` | € 15.49 |
| `F` | € 18.08 |
| `G` | € 20.66 |
| `H` | € 23.24 |

## Apprenticeship

**professionalizzante_C_H** (type: `under_classification`)  
Destination levels: `C`, `D`, `E`, `F`, `G`, `H`  
under-level: `1`

**professionalizzante_B** (type: `under_classification`)  
Destination levels: `B`  
under-level: `1`

**professionalizzante_A** (type: `under_classification`)  
Destination levels: `A`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "chimica-affini-pmi-unionchimica/tranches_2027_2028 · base_salary · impact yes · open"
    SINGLE TRANCHE ONLY. Only the 1 January 2026 tranche is modelled. The 4 subsequent tranches (Apr 2027, Dec 2027, Jun 2028, Dec 2028) are not accessible from primary source at time of extraction. Update with official amounts when the renewal text becomes available.

    **Applies when:** `base_salary` applies; from 2027-04-01.

    **Remediation:** Add the April 2027, December 2027, June 2028 and December 2028 tranches from the renewal text.

!!! warning "chimica-affini-pmi-unionchimica/apprentice_seniority · seniority · impact unknown · open"
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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Jan 2026 tabelle retributive for CNEL B018 Unionchimica Confapi | tabella_retributiva | 2026-02-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=181) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimum contractual (minimo tabellare). Levels H, G, F, E carry fixed_allowances: H has indennità di funzione (IND_FUN, EUR 160.00); G, F, E have aggiunta personale (AGG_PERSONALE, EUR 25.82 / 15.49 / 5.16). All allowances are TFR-relevant and contribution-relevant (default).
    
    RENEWAL: Unionchimica Confapi CCNL signed 23 February 2026, effective 1 January 2026 – 31 December 2028. Five tranches: 1 Jan 2026, 1 Apr 2027, 1 Dec 2027, 1 Jun 2028, 1 Dec 2028. Source: kitech.it B018.
    
    LEVELS: 8 professional levels A (lowest) to H (highest). Scala parametrale: H=100 reference, descending. All levels confirmed from kitech.it Jan 2026 table.
    
    CNEL CODE: B018 (Unionchimica Confapi). Distinct from B011 (Federchimica) which covers large-firm chemical-pharmaceutical. B018 covers PMI (piccole e medie imprese) chemical sector.
    
    TAX SECTOR: INDUSTRIA (existing). Standard INPS industria rates apply (2026-industria.json). No bilateral fund substitutes INPS in this contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: kitech.it B018 mensilità aggiuntive field.
    
    SENIORITY: biennale (24 months), maximum 5 scatti. Per-level EUR amounts from kitech.it Jan 2026 table: A=10.33, B=11.88, C=12.91, D=13.94, E=15.49, F=18.08, G=20.66, H=23.24.
    
    CHIMICA-CONCIA SUB-SECTOR SCOPE. Unionchimica Confapi covers three sub-sectors with different hourly divisors: Chimica-Concia (175), Plastica-Gomma (169), Abrasivi-Ceramica-Vetro (173). Only Chimica-Concia (divisor 175) is modelled — deliberate scope choice. The level codes and salary amounts are identical across all sub-sectors; only the hourly divisor differs.
    
    HOURLY DIVISOR 175: confirmed by cross-reference with CCNL Federchimica B011 (kitech.it), which independently uses 175 for chemical-pharmaceutical industry (same contractual week = 40h, 40×52/12=173.33 rounded to 175 via industry convention). No primary contractual clause directly retrieved but cross-verified via B011.
    
    APPRENTICESHIP. Apprendistato professionalizzante per sotto-inquadramento (D.Lgs. 81/2015). Durata massima 36 mesi, uniforme per tutti i livelli e sub-settori. Struttura: primo periodo (mesi 1-10) a 2 livelli sotto la destinazione; secondo periodo (mesi 11 a fine contratto) a 1 livello sotto la destinazione; al termine dell'apprendistato l'inquadramento finale è riconosciuto. Tre track modellati: professionalizzante_C_H (C-H, schema standard 2→1), professionalizzante_B (destinazione B: capped ad A per assenza di livelli inferiori, periodo unico), professionalizzante_A (destinazione A: resta ad A per tutta la durata). Fonte primaria: schede CNEL B018 direzionelavoro.it (ottobre 2023), voce (g) art. 1 Cap. I. Confermato invariato dal rinnovo 23/02/2026 (Confapi Padova circolare): apprendistato non oggetto di modifica.
    

## Raw data

The contract file this page is generated from: [`agreement/chimica-affini-pmi-unionchimica.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/chimica-affini-pmi-unionchimica.json).

## Usage example

```python
--8<-- "docs/examples/agreement/chimica-affini-pmi-unionchimica/example.py"
```
