# CCNL per il personale dipendente non dirigente delle imprese di assicurazione (ANIA)

| | |
|---|---|
| **CNEL code** | `J121` |
| **Sector** | assicurazioni |
| **Family** | `assicurazioni` |
| **Tax sector** | `credito` |
| **Last renewal** | 2026-05-13 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIA
    - FIRST-CISL
    - FISAC-CGIL
    - FNA
    - SNFIA
    - UILCA

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

6 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 30 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-05-13 |
| **Last review** | — |
| **Latest salary tranche** | 2028-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `L7` | 7° livello — Funzionario | € 3,112.27 | 2028-01-01 |
| `L6` | 6° livello — Quadro | € 2,629.37 | 2028-01-01 |
| `L5` | 5° livello — Impiegato | € 2,463.96 | 2028-01-01 |
| `L4` | 4° livello — Impiegato | € 2,324.66 | 2028-01-01 |
| `L3` | 3° livello — Impiegato | € 2,130.75 | 2028-01-01 |
| `L2` | 2° livello — Impiegato | € 1,946.58 | 2028-01-01 |
| `L1` | 1° livello — Impiegato | € 1,846.38 | 2028-01-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 11 increments

| Level | Increment (monthly) |
|---|---:|
| `L7` | € 102.08 |
| `L6` | € 81.77 |
| `L5` | € 76.63 |
| `L4` | € 72.30 |
| `L3` | € 66.27 |
| `L2` | € 60.54 |
| `L1` | € 57.42 |

## Apprenticeship

**area_c_l3** (type: `under_classification`)  
Destination levels: `L3`  
under-level: `1`

**area_b_l4** (type: `under_classification`)  
Destination levels: `L4`  
under-level: `1`

**area_b_l5** (type: `under_classification`)  
Destination levels: `L5`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "assicurazioni-ania/pre_1999_hire_table · base_salary · impact yes · open"
    Covers personale amministrativo assunto dal 18/12/1999 (Allegato 2/B — tabella omnicomprensiva). Pre-1999 hires (Allegato 2/A) are out of scope.

    **Applies when:** `base_salary` applies.

    **Remediation:** Model Allegato 2/A for the staff hired before 18/12/1999, gated on the hire date, or open a limitation.

!!! warning "assicurazioni-ania/funzionari_economic_allowance · base_salary · impact yes · open"
    Indennità economica funzionari (Allegato 2/D) — L7 only, six sub-grade variants (Ex 3°/2°/1° Grado, Funz. Senior, Funz. Business, Ass. ex F2) with distinct amounts. Monthly amounts not found in publicly accessible sources (Allegato 2/D not published). Not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model Allegato 2/D: the indennità economica of the six L7 funzionari sub-grades as role-keyed fixed_allowances on L7 (like IND_PROFILO_J), once the amounts are sourced.

!!! warning "assicurazioni-ania/seniority_modal_class_difference · seniority · impact yes · open"
    Seniority increment = modal per-class difference in the 1/14 monthly table (Allegato 2/B); classes above CL01 may differ from the official table by ±0.02. Source: Allegato 2/B, Rinnovo 13/05/2026.

    **Applies when:** `seniority` applies.

    **Remediation:** Replace the modal per-class difference with the official Allegato 2/B amounts per class.

!!! note "assicurazioni-ania/inps_credit_rate_unverified · inps_employer · impact unknown · resolved"
    INPS employer_rate 26.76% flat from kitech.it (Credito e Assicurazioni 2026); reuses 2026-credito.json. Verify against the annual INPS circular.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Resolved as a duplicate of assicurazioni-ania/inps_sector_rates_unsourced, which stays open (review of 2026-10-30): both say the credito employer rate is not confirmed by a 2026 INPS source. contribution/2026/credito.json now takes 26.76 from the INPS 2012 table and keeps the Fondo di solidarietà out of the totals, in parameters.solidarity_fund.

!!! warning "assicurazioni-ania/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "assicurazioni-ania/inps_sector_rates_unsourced · inps_employer · impact unknown · open"
    INPS RATES: the employer and worker INPS rates of the sector (credito) are totals no 2026 INPS or association table confirms: the only component split found is the INPS guide of 2012 and the 2026 totals come from a software house page that does not prove its year. The contributions of every run rest on them.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the credito rates of 2026 on an INPS or association table, mark the inps block of contribution/2026/credito.json derived, then remove this note.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.first-cisl.it/ | tabella_retributiva | 2026-05-13 | [↗](https://www.first-cisl.it/) |
| https://www.contratticcnl.it/ | altro | — | [↗](https://www.contratticcnl.it/) |

??? note "Coverage notes"
    First tranche decorrenza 01/01/2026 is retroactive; CCNL signed 13/05/2026. Arretrati January–July 2026 paid in July 2026 (Allegato 7). Period start is 2026-01-01 in the engine.
    
    Additional months = 14 (tredicesima + quattordicesima). Monthly amounts are 1/14 of annual retribuzione. Source: Allegato 2/B header, FirstCISL PDF rinnovo 13/05/2026.
    
    Seniority: cl 1 = anni 1-4 (48 months, quadriennale); cl 2 onward = 3 years each (36 months, triennale). Source: Art. 113 CCNL + Allegato 2/B class table.
    
    L7 maximum seniority class is CL08 (anni 23-25); L1-L6 reach CL12 (oltre 34 anni). maximum_count_by_level overrides L7 to 7 advances.
    
    Hourly divisor 160 (37h/week). Source: ilccnl.it, confirmed from Art. orario di lavoro CCNL ANIA.
    
    Seniority increment amounts vary across tranches (e.g. L4: 67.51 → 70.17 → 72.30). Represented exactly via TimeSeries in amount_by_level.
    
    Indennità profilo J) 4° livello (Allegato 2/E) — modelled as fixed_allowance IND_PROFILO_J on L4 with role 'profilo_j'. Amounts: €57.26/mese dal 01/01/2026, €59.51 dal 01/01/2027, €61.32 dal 01/01/2028. Set Employment.roles=profilo_j to include it (review of 2026-10-30).
    
    Indennità economica 6° livello quadro (Allegato 2/F) — modelled as fixed_allowance IND_QUADRO_6 on L6 with role 'quadro_6'. Amount: €74.09/mese dal 01/01/2026. Set Employment.roles=quadro_6 to include it (review of 2026-10-30).
    
    SOLIDARITY FUND: Fondo di solidarietà del settore assicurativo (accord ANIA of 20 May 2013, D.I. 78459 of 17 January 2014): ordinary contribution 0.30% of the INPS taxable pay of permanent workers, 0.20% employer and 0.10% worker, dirigenti excluded (INPS circ. 56/2015 p. 11); collected by INPS in the overall rate.
    
    Salary tables: FirstCISL Gruppo Unipol, Allegato 2/B — Tabella omnicomprensiva post-1999, decorrenza 01/01/2026, 01/01/2027, 01/01/2028.
    
    Apprenticeship: Art. 5, Allegato 18 (Accordo apprendistato professionalizzante), CCNL testo 2017/2018, confirmed applicable post-rinnovo 2026.
    
    Class cadence: Art. 113 CCNL + column 'Anni serv.' Allegato 2/B.
    

## Raw data

The contract file this page is generated from: [`agreement/assicurazioni-ania.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/assicurazioni-ania.json).

## Usage example

```python
--8<-- "docs/examples/agreement/assicurazioni-ania/example.py"
```
