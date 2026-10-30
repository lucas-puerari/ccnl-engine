# CCNL Servizi di Pulizia e Servizi Integrati/Multiservizi (ANIP-Confindustria)

| | |
|---|---|
| **CNEL code** | `K511` |
| **Sector** | multiservizi |
| **Family** | `pulizia-multiservizi` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2021-06-08 |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANIP-Confindustria
    - Legacoop Lavoro e Servizi
    - Confcooperative Lavoro e Servizi
    - AGCI Servizi
    - Unionservizi Confapi
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltrasporti-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 57 verified / 93 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2021-06-08 |
| **Last review** | 2026-10-13 |
| **Latest salary tranche** | 2029-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Signatories of the renewals behind the salary periods from July 2025. | flagged | The renewal of 13 June 2025 (CNEL K511, deposits 234754 and 234752) is not signed by ANIP; the file pays its minima from July 2025. Declared as the limitation anip_unsigned_renewal; values left unchanged pending an ANIP amount. |
| 2026-10-13 | claude-opus-5-5 (ai) | Limited scope, tier unchanged: the rules that do not depend on the missing ANIP amounts, read in the CNEL K511 deposits 105782 (2011 text) and 139292 (2021 renewal); the salary periods from July 2025 stay as they are. | corrected | 66 records verified: the 2021-2024 tabellare, contingenza and EDR of levels 1-7 and Q, the quadri allowance, the levels 1, 2par115, 4par125, 7 and Q, the divisor 173, the 14 monthly payments and their accrual rule, the overtime rates and 22 days of leave.<br>Added the payment days of the tredicesima (20 December) and quattordicesima (15 July, window July to June), arts. 20-21.<br>The 2par115 and 4par125 tabellare is computed (April 2013 amount plus the parametric increments): derived, descriptions corrected to the notes a verbale of art. 10.<br>Closed cigs_threshold_16_to_50: terziario.json already charges the CIGS above 15 employees (D.Lgs. 148/2015 arts. 20 and 23).<br>Closed apprentice_seniority: apprentices are paid tabellare, contingenza and EDR only (art. 12), apprentice_amount 0 (derived).<br>Corrected the notes on the July 2025 values (the 2021 fifth tranche is the operative ANIP amount), on scatti recomputed at every tranche, on the apprenticeship durations, on the 2025 signatories and on the worker estimate.<br>Declared multiservizi_unmodelled_rules: seniority and sickness by worker type, the 181-270 sickness band, the /22 divisor, the overtime base and premiums, the art. 24 allowances, the funds and the apprenticeship durations.<br>hourly_base_method gross_incl_allowances: the art. 38 premiums are on tabellare plus contingenza.<br>Left derived: the periods from July 2025 (renewal not signed by ANIP, re-cited to CNEL 234752), the seniority block, the contingenza of the parametric positions, levels 2 to 6 (mixed categories), absence and sickness rules.<br>The aggregator sources (oristano summary, redigo, kitech, ccnlportatili) are replaced by the CNEL deposits. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri with high-responsibility managerial duties | € 2,006.64 | 2029-03-01 |
| `7` | Employees with managerial functions | € 1,833.35 | 2029-03-01 |
| `6` | Workers with specialist duties / Senior white-collar employees | € 1,587.07 | 2029-03-01 |
| `5` | Expert workers / White-collar employees | € 1,276.96 | 2029-03-01 |
| `4` | Specialist workers / Junior clerical employees | € 1,167.51 | 2029-03-01 |
| `4par125` | Skilled workers on painting booths and lines in service on 1 June 2001: level IV at parameter 125, closed group (nota a verbale) | € 1,140.15 | 2029-03-01 |
| `3` | Skilled workers / Clerical employees | € 1,076.30 | 2029-03-01 |
| `2par115` | Common workers on auxiliary support activities in school and healthcare settings: level 2 at parameter 115 (nota a verbale, profile 1.9) | € 1,048.93 | 2029-03-01 |
| `2` | General workers / Clerical employees (first 18 months) | € 994.21 | 2029-03-01 |
| `1` | General labourers | € 912.12 | 2029-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 8 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 51.02 |
| `2` | € 54.39 |
| `2par115` | € 55.50 |
| `3` | € 58.18 |
| `4par125` | € 62.59 |
| `4` | € 63.15 |
| `5` | € 97.29 |
| `6` | € 116.67 |
| `7` | € 132.06 |
| `Q` | € 142.89 |

## Apprenticeship

**destinazione_5** (type: `under_classification`)  
Destination levels: `5`

**destinazione_4** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "multiservizi-anip/anip_unsigned_renewal · base_salary · impact yes · open"
    UNSIGNED RENEWAL: the salary periods from 1 July 2025 come from the renewal of 13 June 2025 and its tables of 6 August 2025 (CNEL K511, deposits 234754 and 234752), signed by AGCI, Confcooperative, Legacoop and Confapi but not by ANIP. For an ANIP member the last signed amount is the fifth tranche of July 2025 of the 2021 renewal (deposit 139292, p. 34, level 2 779.21 against 819.21 here); no ANIP amount after it was found. Runs from July 2025 may overpay an ANIP employer's workers.

    **Applies when:** `base_salary` applies; from 2025-07-01.

    **Remediation:** Use the 2021 renewal values for ANIP members, or the 2025 renewal once ANIP signs or joins it.

!!! warning "multiservizi-anip/multiservizi_unmodelled_rules · base_salary · impact yes · open"
    NOT MODELLED (CNEL 105782 and 139292): (1) worker type: levels 2 to 6 hold both impiegati and operai (art. 10), but the file keys seniority and category by level, so impiegati of levels 2-4 get the operai forfettaria instead of the biennial scatti of art. 22 and operai of levels 5-6 get scatti instead of the forfettaria (66.77, 82.99, p. 90); each scatto is priced on the tabellare in force at its maturation and capped at 50% of tabellare + 279.60, while the engine prices it at the run date. (2) Sickness (art. 51 as replaced in 2021, CNEL 139292 pp. 22-24): operai are topped up to 100% of the net retribuzione globale for days 1-180 and paid 50% of the gross one for days 181-270 (the file stops at day 180); impiegati get 100% for 5 months and 50% for 7; comporto 12 months in 36. (3) Absence: the daily quota is the monthly pay /22 on a 5-day week (art. 19, the norm of art. 30); the file divides by 26. (4) Overtime is paid on quote of the retribuzione globale and its premiums on the retribuzione base, tabellare plus contingenza (art. 38); the premiums for holiday work (50%) and night work (20% in rotating shifts, 30% otherwise), the part-time supplementary hours (+28%, elastic clauses +10%, art. 33 as amended in 2021) and the 40 ROL hours (art. 42). (5) The allowances of art. 24 (disagio 15% of tabellare a day, maneggio denaro 3%, riscossione 5%, hourly allowances) and the EDAR ad personam. (6) Funds: Previambiente 1% + 1% of tabellare and contingenza for members (art. 54); ASIM and ONBSI are the limitation health_and_bilateral_funds. (7) Apprenticeship durations of the accord of 19 July 2012 (destination 5 lasts 36 months, destinations 2, 3, 6 and 7 are missing).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Key seniority and sickness by worker category, model the second sickness band, the /22 divisor, the art. 38 and art. 24 premiums, the funds and the apprenticeship durations of the 2012 accord.

!!! warning "multiservizi-anip/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    HEALTH AND BILATERAL FUNDS: ASIM 4.00 or 6.00 EUR a month (art. 69) and ONBSI 0.50 + 0.50 EUR a month (art. 66 as amended in 2021) are owed for every worker. Not modelled: the net pay and the employer cost are short of them.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Model the ASIM and ONBSI contributions per worker, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/139292 | cnel | 2021-06-08 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/139292) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/105782 | cnel | 2011-05-31 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/105782) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234754 | cnel | 2025-06-13 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234754) |
| https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234752 | cnel | 2025-08-06 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/234752) |

??? note "Coverage notes"
    Salary model: SPLIT. The tabellare is a time series; contingenza and EDR are frozen fixed_allowances. Tranches of July 2021 to July 2024: art. 73 tables of the renewal of 8 June 2021 (CNEL 139292, pp. 32-34, signed by ANIP). Tranches from July 2025: tables of 6 August 2025 (CNEL 234752), not signed by ANIP (see anip_unsigned_renewal). No table prints the tabellare of 2par115 and 4par125 after April 2013: it is the April 2013 amount (CNEL 105782 pp. 30-31) plus the parametric increments.
    
    hourly_divisor 173: 'Ai fini della determinazione della retribuzione oraria, il divisore mensile è 173' (art. 19, CNEL 105782 p. 40).
    
    additional_months 14: tredicesima by 20 December (art. 20) and quattordicesima by 15 July (art. 21), each one retribuzione globale mensile (CNEL 105782 p. 41). The quattordicesima accrues from 1 July to 30 June.
    
    Seniority, impiegati: biennial scatti of 6.25% of the tabellare in force when each scatto matures plus the contingenza at 1/8/1983 (EUR 279.60), at most 8 and up to 50% of tabellare + 279.60 (art. 22, CNEL 105782 p. 41). A matured scatto keeps its amount: it is not recomputed at later tranches. The file holds one series per level (2021-2024 computed on the CNEL 139292 tables) and the engine prices every matured scatto at the run date; it pays scatti to levels 5, 6, 7 and Q, while the CCNL pays them to the impiegati of levels 2-7 and Q. Declared in multiservizi_unmodelled_rules.
    
    Seniority, operai: anzianità forfettaria di settore, one fixed monthly amount not paid for the first four years of sector seniority (art. 22, CNEL 105782 pp. 41-42; amounts in the table of p. 90). Modelled with first_cadence_months_by_level 48 and maximum_count_by_level 1 for levels 1 to 4; the CCNL also pays it to the operai of levels 5 and 6 (66.77, 82.99). Declared in multiservizi_unmodelled_rules.
    
    Contingenza of 2par115 and 4par125: no text prints one. The notes a verbale of art. 10 (CNEL 105782 p. 30) classify these workers at level 2 with parameter 115 and at level IV with parameter 125, so the file applies the contingenza of levels 2 and 4.
    
    Apprenticeship: two levels below the destination for the first half and one below for the second, destination II at level I throughout (art. 12, CNEL 105782 p. 37; the parametric positions are skipped). Durations come from the accord of 19 July 2012, read only in a third-party copy of the 2021 text: II 24, III 30, IV 30, V 36, VI 36, VII 36 months. The file models destinations 4 and 5 with 30 months each: destination 5 should last 36 and the other destinations are missing. Declared in multiservizi_unmodelled_rules.
    
    July 2025 values: the renewal of 8 June 2021 (CNEL 139292, signed by ANIP) sets a fifth tranche from 1 July 2025 (level 2 +10.00, tabellare 779.21, p. 34), provisional under the art. 73 consuntivo. The renewal of 13 June 2025 (CNEL 234754) and its tables of 6 August 2025 (CNEL 234752) raise level 2 to 819.21 from the same date, but ANIP signed neither. The file carries the 2025 renewal from July 2025, so for an ANIP member the operative amount is the 2021 tranche, not the file's (see anip_unsigned_renewal). No ANIP amount for the art. 73 consuntivo or the IPCA increments of art. 73-bis and 73-ter was found.
    
    ANIP CONTRACT STATUS (2025): the renewal of 13 June 2025 (CNEL 234754) and its tables of 6 August 2025 (CNEL 234752) are signed by AGCI Servizi, Confcooperative Lavoro e Servizi, Legacoop Produzione e Servizi and Unionservizi Confapi with Filcams-CGIL, Fisascat-CISL and Uiltrasporti-UIL; ANIP-Confindustria signed neither. ANIP companies keep the renewal of 8 June 2021 (this file). A separate file would cover the 2025-2028 renewal (levels 1-7 and Q, retribuzione base 1,296.39 to 2,256.14 EUR from May 2026, 14 mensilità).
    
    INPS: terziario regime. Cleaning contractors are CIGS employers above 15 employees: D.Lgs. 148/2015 art. 20 c. 1 d) ('imprese appaltatrici di servizi di pulizia, anche se costituite in forma di cooperativa, che subiscano una riduzione di attività') and, from 1 January 2022, art. 20 c. 3-bis and art. 23 c. 1-bis ('a carico dei datori di lavoro che, nel semestre precedente la data di presentazione della domanda, abbiano occupato mediamente più di quindici dipendenti [...] è stabilito un contributo ordinario nella misura dello 0,90 per cento'). contribution/2026/terziario.json already charges the CIGS 0.90% (0.30% on the worker, INPS circ. 117/2022 all. 1) above 15 employees and the FIS of art. 29 below.
    
    Workers covered: no sourced figure. The earlier note (~403,000, INPS-UNIEMENS 2025) and meta.workers_estimate (~580k) disagree and neither cites a document.
    

## Raw data

The contract file this page is generated from: [`agreement/multiservizi-anip.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/multiservizi-anip.json).

## Usage example

```python
--8<-- "docs/examples/agreement/multiservizi-anip/example.py"
```
