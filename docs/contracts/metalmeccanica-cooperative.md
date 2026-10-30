# CCNL Metalmeccanica - Cooperative

| | |
|---|---|
| **CNEL code** | `C016` |
| **Sector** | metalmeccanico cooperativo |
| **Family** | `metalmeccanica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-07-22 |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGI Produzione e Lavoro
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 45 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-07-22 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Titolo IV - Retribuzione ed altri istituti economici, Art. 7 - Tredicesima mensilità (p. 123): "il lavoratore ha diritto a tanti dodicesimi dell'ammontare della 13° mensilità quanti sono i mesi di anzianità di servizio presso l'azienda. La frazione di mese superiore a 15 giorni va considerata a questi effetti come mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A1 — quadro superiore, massima responsabilita gestionale | € 3,177.92 | 2028-06-01 |
| `B3` | Livello B3 — quadro intermedio, caposquadra o coordinatore di gruppo | € 2,883.46 | 2028-06-01 |
| `B2` | Livello B2 — specialista senior o responsabile di funzione | € 2,651.95 | 2028-06-01 |
| `B1` | Livello B1 — specialista o tecnico con responsabilita di progetto | € 2,471.90 | 2028-06-01 |
| `C3` | Livello C3 — tecnico o impiegato di concetto con autonomia operativa | € 2,306.18 | 2028-06-01 |
| `C2` | Livello C2 — operatore polivalente, mansioni di concetto | € 2,153.36 | 2028-06-01 |
| `C1` | Livello C1 — operatore specializzato, mansioni tecnico-pratiche | € 2,108.77 | 2028-06-01 |
| `D2` | Livello D2 — operatore qualificato, mansioni esecutive | € 2,064.18 | 2028-06-01 |
| `D1` | Livello D1 — operatore comune, mansioni semplici e ripetitive | € 1,861.42 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.90 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 45.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanica-cooperative/apprenticeship_from_federmeccanica · base_salary · impact unknown · open"
    APPRENTICESHIP: percentages (85/90/95% over 36 months) modelled as C011 Federmeccanica (accordo 20/04/2021). No independent C016-specific source found in 2025 renewal documentation. Checked: ecnews.it (renewal article), dottrinalavoro.it, ilccnl.it (two URL paths), kitech.it CodiceCateg=48. Destination levels D2-B3 mirror C011; D1 and A1 excluded as in C011.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Confirm the apprenticeship percentages against a C016-specific source.

!!! warning "metalmeccanica-cooperative/cooperative_inps_rates_unverified · inps_employer · impact unknown · open"
    INPS: employer rates from 2026-industria.json (same tax sector as C011). Cooperative employers may have different INPS addizionale rates; this is a SIMPLIFICATION — verify against INPS circular for cooperative sector if precise employer cost is critical.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Check the INPS rates of the cooperative employers (circular of the sector, CSC of the cooperatives) against contribution/2026/industria.json and record any difference.

!!! warning "metalmeccanica-cooperative/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

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
| https://geps.it/rinnovo-ccnl-metalmeccanica-cooperative-2025-2028-10377/ | tabella_retributiva | 2025-07-22 | [↗](https://geps.it/rinnovo-ccnl-metalmeccanica-cooperative-2025-2028-10377/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=48 | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=48) |
| https://www.fiom-cgil.it/net/cooperative/trattativa-coop/11211-ccnl-cooperative-incrementi-salariali-e-nuovi-minimi-retributivi | tabella_retributiva | 2025-07-22 | [↗](https://www.fiom-cgil.it/net/cooperative/trattativa-coop/11211-ccnl-cooperative-incrementi-salariali-e-nuovi-minimi-retributivi) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2025-07-22 by Legacoop Produzione e Servizi, Confcooperative Lavoro e Servizi, AGI Produzione e Lavoro with FIM-CISL, FIOM-CGIL and UILM-UIL. Validity 17/06/2025-30/06/2028. First tranche retroactive to 2025-06-01.
    
    CONGLOBATED MINIMUMS: base_salary values are the consolidated 'minimi contrattuali', incorporating all salary components (paga base, contingenza, EDR) into a single figure, consistent with the metalmeccanici industry practice adopted since 1993. No separate contingenza or EDR column appears in any source table.
    
    FIXED ALLOWANCES: A1 (+180 EUR indennita di funzione) and B3 (+120 EUR indennita di funzione) are paid in addition to base_salary, per kitech.it (CodiceCateg=48), which lists them as separate columns. C011 (Federmeccanica) omits these from its JSON; C016 models them explicitly for accuracy.
    
    SENIORITY: biennali scatti (cadence 24 months), maximum 5 per level. Amounts per level confirmed on kitech.it CodiceCateg=48.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). No quattordicesima in any source. Consistent with C011 federmeccanica structure.
    
    HOURLY DIVISOR: 173 h/month (40 h/week standard, same as C011). Confirmed on kitech.it.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanica-cooperative.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanica-cooperative.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanica-cooperative/example.py"
```
