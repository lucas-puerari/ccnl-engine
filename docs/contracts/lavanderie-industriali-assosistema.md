# CCNL Lavanderie Industriali (Assosistema Confindustria)

| | |
|---|---|
| **CNEL code** | `D0L1` |
| **Sector** | lavanderie-industriali |
| **Family** | `pulizia-multiservizi` |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-05-19 |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assosistema Confindustria
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

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
| **Rule provenance** | 0 verified / 37 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-05-19 |
| **Last review** | — |
| **Latest salary tranche** | 2026-12-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `D2` | Livello D2 — quadri, executive management (L. 190/1985) | € 3,015.43 | 2026-12-01 |
| `C3` | Livello C3 — senior managers, strategic operational responsibility | € 3,015.43 | 2026-12-01 |
| `C2` | Livello C2 — area managers, planning and operational leadership | € 2,566.77 | 2026-12-01 |
| `C1` | Livello C1 — senior specialists, supervisory and quality-control functions | € 2,275.64 | 2026-12-01 |
| `B3` | Livello B3 — highly qualified workers, team coordination and process oversight | € 2,202.14 | 2026-12-01 |
| `B2` | Livello B2 — specialist workers, multi-task roles with technical responsibility | € 2,012.94 | 2026-12-01 |
| `B1` | Livello B1 — skilled workers, complex laundry and sterilisation operations | € 1,917.54 | 2026-12-01 |
| `A3` | Livello A3 — qualified workers, autonomous standard operations | € 1,882.49 | 2026-12-01 |
| `A2` | Livello A2 — semi-skilled workers, assisted operations | € 1,786.94 | 2026-12-01 |
| `A1` | Livello A1 — entry-level workers, basic laundry operations | € 1,579.32 | 2026-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 6.71 |
| `A2` | € 6.97 |
| `A3` | € 7.23 |
| `B1` | € 7.23 |
| `B2` | € 8.00 |
| `B3` | € 8.26 |
| `C1` | € 8.26 |
| `C2` | € 9.81 |
| `C3` | € 11.88 |
| `D2` | € 11.88 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `A3`, `B1`, `B2`, `B3`, `C1`, `C2`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `A2`, `C3`, `D2`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "lavanderie-industriali-assosistema/tranches_from_october_2027 · base_salary · impact yes · open"
    MODELLED TRANCHES: 2026-05-01 (source-confirmed from ilccnl.it, iqnotizie.it, previdenza-professionisti.it, all concordant); 2026-12-01 (derived: +20 EUR on B1, other levels proportional using coefficient vector verified across 4 historical tranches 2023-2025). Oct 2027 (+50 EUR B1) and Oct 2028 (+60 EUR B1) announced but table not published — not modelled.

    **Applies when:** `base_salary` applies; from 2027-10-01.

    **Remediation:** Model the October 2027 (+50 at B1) and October 2028 (+60 at B1) tranches once the tables are published, or derive them with the level coefficients of note 8.

!!! warning "lavanderie-industriali-assosistema/apprentice_seniority · seniority · impact unknown · open"
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
| https://www.assosistema.it/11527-2/ | altro | 2026-05-19 | [↗](https://www.assosistema.it/11527-2/) |
| https://ilccnl.it/contratto/ccnl/lavanderie---industria | tabella_retributiva | 2026-05-19 | [↗](https://ilccnl.it/contratto/ccnl/lavanderie---industria) |
| https://www.iqnotizie.it/notizia/IQ47433/ | tabella_retributiva | 2026-05-19 | [↗](https://www.iqnotizie.it/notizia/IQ47433/) |
| https://previdenza-professionisti.it/ | tabella_retributiva | 2026-05-19 | [↗](https://previdenza-professionisti.it/) |

??? note "Coverage notes"
    SECTOR SCOPE: both turismo and sanitario comparti. Pre-2026 the two sectors had distinct tranche dates (sanitario ~9 months behind turismo), but converged to identical minimi by Apr 2025 (sanitario) / Oct 2025 (turismo). The 2026-2028 rinnovo (19 May 2026) applies a single undifferentiated table labelled SANITARIO_TURISMO by Assosistema — confirmed by Assosistema circular title 'Costo medio orario CCNL Lavanderie industriali SANITARIO_TURISMO Aree ABCD tranche 2026'. This contract covers workers in both comparti from 2026-05-01.
    
    SALARY MODEL: split. base_salary = minimo tabellare (contingenza conglobata since 2008, confirmed in CCNL text). fixed_allowances per level = INCENTIVO_DI_MODULO (frozen, level-specific constant). D2 also receives INDENNITA_FUNZIONE 130.00 EUR/month. A1 has no incentivo di modulo (0 EUR). Verified: B1 May 2026 = 1897.54; B1/173 = 10.97 (non-integer, consistent with split). C2 May 2026 = 2535.98; (2535.98+93.44)/173 = 15.20 (matches ilccnl.it hourly for C2).
    
    AGREEMENT DATE: 2026-05-19 is ipotesi di accordo date. Ratification (scioglimento della riserva) was due by 2026-06-19 per Assosistema circular. Definitive signing date not independently confirmed; 2026-05-19 used in sources.
    
    SENIORITY: biennale (cadence_months=24), maximum 5 scatti. Per-level amounts from previdenza-professionisti.it (Assosistema D0L1 table): A1=6.71, A2=6.97, A3=7.23, B1=7.23, B2=8.00, B3=8.26, C1=8.26, C2=9.81, C3=11.88, D2=11.88. Cross-confirmed by lavoro-economia.it (identical amounts). Amounts from previgente CCNL assumed unchanged in 2026 renewal.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it and lavoro-economia.it. No quattordicesima.
    
    INPS: uses 2026-industria.json (industria sector, Assosistema Confindustria). Bilateral funds FASIIL (health) and PREVIMODA (pension) are supplementary to INPS, not substituting. Employer INPS rate unaffected.
    
    APPRENTICESHIP: under_classification professionalizzante only. Two tracks per previdenza-professionisti.it (Assosistema D0L1, 2023 rules assumed unchanged in 2026 renewal): 36-month track (destinations A3..C2, periods: 0-12 at 2 levels below, 12-24 at 1 level below, 24+ at destination); 24-month track (destinations A2, C3, D2, periods: 0-12 at 1 level below, 12+ at destination). A1 excluded (no destination below it). Alta formazione and qualifica/diploma apprenticeship not modelled.
    
    DERIVED TRANCHE: Dec 2026 amounts derived from B1+20 using level coefficients (A1=0.7936, A2=0.9126, A3=0.9762, B1=1.0000, B2=1.0794, B3=1.2540, C1=1.2778, C2=1.5396, C3=D2=1.9762). Coefficients verified as identical across all 4 historical tranches of the 2023-2025 agreement, confirming a stable parametric scale. Not independently confirmed from a published Dec 2026 official table (that table has not been released as of 2026-09-09).
    
    INCENTIVO DI MODULO: per-level amounts cross-confirmed from lavoro-economia.it and previdenza-professionisti.it for the previgente CCNL. Assumed unchanged in 2026 renewal: no published 2026 contract text or renewal summary indicates a change to these allowances.
    
    SENIORITY AMOUNTS: previgente CCNL values retained for 2026 renewal. 2026 renewal public summary does not mention changes to scatti amounts — consistent with the standard Italian CCNL practice of not modifying frozen seniority increments in renewals.
    
    APPRENTICESHIP ALLOWANCES: engine draws INCENTIVO_DI_MODULO from the effective pay level, not the destination level. An apprentice at A3 destination (month 6, pay level A1) receives 0.00 allowances because A1 has no incentivo. An apprentice at B1 destination (month 18, pay level A3) receives 57.00 EUR (A3 incentivo). Verified by compute sweep across all five boundary cases (A3/m6, A2/m6, B1/m18, C2/m30, D2/m18).
    
    SOURCE CAVEAT: previdenza-professionisti.it entry uses a domain-level URL; the exact deep-link page was not captured. Data cross-confirmed by lavoro-economia.it for seniority amounts.
    

## Raw data

The contract file this page is generated from: [`agreement/lavanderie-industriali-assosistema.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/lavanderie-industriali-assosistema.json).

## Usage example

```python
--8<-- "docs/examples/agreement/lavanderie-industriali-assosistema/example.py"
```
