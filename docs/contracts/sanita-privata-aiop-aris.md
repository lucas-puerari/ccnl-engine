# CCNL Case di Cura Private - Personale Non Medico (AIOP/ARIS)

| | |
|---|---|
| **CNEL code** | `T011` |
| **Sector** | Sanità privata |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2020-10-08 |
| **Workers (est.)** | ~150k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AIOP
    - ARIS
    - FP-CGIL
    - CISL-FPS
    - UIL-FPL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | overtime |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 36 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2020-10-08 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2020-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-14 | claude-opus-5-5 (ai) | P1 audit: Tabella 1 of the CCNL of 8 October 2020 for the 28 positions, the number of monthly payments and the term. | corrected | The 28 monthly tabellari match column D of Tabella 1 (p. 104) to the cent: verified.<br>13 monthly payments: verified ('x 13 mensilità', column C).<br>No renewal after the CCNL of 8 October 2020 was found; the table stays in force (ultrattività). Seniority, overtime, absence and sickness rules are not re-read in this pass. |
| 2026-10-15 | claude-opus-5-5 (ai) | Registry check: CNEL code, name, signatories and term against the 21st CNEL report of CCNLs in force (30 June 2025) and the term clause of the text read in the P1 review. | corrected | CNEL T011 matches. Signatories corrected: the text of 8 October 2020 is signed by AIOP and ARIS with FP-CGIL, CISL-FPS and UIL-FPL only (the report adds UGL Sanità); FILCAMS, FISASCAT, UILTuCS, FIALS and CISAL Sanità were listed by mistake.<br>Term: 'Decorrenza: 1° gennaio 2016 - Scadenza: 31 dicembre 2018' (Art. 4), the same in the report; the CCNL applies in ultrattività. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'straordinario, notturno, festivo, turni e maggiorazioni cumulabili': the overtime bands and the night, holiday and shift premiums of the file against the text read in the P1 review. | corrected | Art. 59 (p. 89): daytime overtime is paid at 20%, not 15%: corrected. Night or holiday overtime 30% and night-holiday overtime 50% match. All four bands verified; the hourly quota is the monthly pay over 26 and 6 (Art. 58), the divisor 156 of the file.<br>Art. 60-61: the night and holiday shift indemnities, the on-call indemnity and the radiation risk indemnity were neither modelled nor declared: declared as an outside-input limitation. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'ferie, permessi, festività, assenze, malattia e comporto': the leave, accrual, absence and sickness rules of the file against the text read in the P1 review. | corrected | Sickness (Art. 43, pp. 58-60): the employer tops up to 100% of the retribuzione globale from the first day up to the 365th day of absence in four years, within a comporto of 540 days in a rolling four years, net of what the worker would have received working. The file paid 50% in the waiting days and 75% after, up to 180 days: corrected and verified.<br>Ferie (Art. 32, p. 42): 30 working days plus 4 days for the festività soppresse, 34 in all (was 30): corrected and verified.<br>Absence divisor 26 (Art. 58, p. 88) and the tredicesima accrual of more than 15 days (Art. 66, p. 96, was assumed): verified. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'part-time, tempo determinato, apprendistato e periodo di prova': the apprenticeship tracks and the part-time supplementary hours of the file against the text read in the P1 review. | corrected | Apprenticeship (p. 31): only the 36-month track (85% then 90%) was modelled; the 18-month and 24-month tracks are added. An apprentice now names the track.<br>Part-time supplementary hours are paid at 15% (Art. 22, p. 25): declared, the request cannot state them.<br>Probation and fixed-term rules carry no amount the engine computes. |
| 2026-10-15 | claude-opus-5-5 (ai) | Checklist item 'fondi sanitari, previdenza complementare, bilateralità e quote a carico di lavoratore e datore': the pension, health and bilateral contributions of the file against the text read in the P1 review. | confirmed | The CCNL of 8 October 2020 sets no contractual pension, health or bilateral contribution: Art. 74 only confirms the will to institute a supplementary pension. None is modelled. |
| 2026-10-17 | claude-opus-5-5 (ai) | Periodic review due 2026-12-31: the minimi of every level against the CCNL of 8 October 2020, the status of the renewal, and the readiness of the file. | confirmed | The 28 minimi of the file are printed in the CCNL of 8 October 2020. Match.<br>No renewal of the CCNL 2016-2018 was signed by 2026-10-17: the unions report a contract in ultrattività and a dispute open in January 2026 (FP CGIL, letter to the Ministry of Health and the Conferenza delle Regioni); the 2020 tables stay in force.<br>Not promoted to reviewed: verification.confidence is unverified, the level records are derived from a CCNL text of 2020 with an aggregator as second source, and shift_on_call_allowances and part_time_supplementary_rate are open. The derived rule stays derived. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `E2` | Categoria E — progressione orizzontale 2 | € 3,554.39 | 2020-07-01 |
| `E1` | Categoria E — progressione orizzontale 1 | € 2,936.33 | 2020-07-01 |
| `DS4` | Categoria DS — progressione orizzontale 4 | € 2,418.05 | 2020-07-01 |
| `E` | Categoria E — quadro / specialista | € 2,410.22 | 2020-07-01 |
| `DS3` | Categoria DS — progressione orizzontale 3 | € 2,345.38 | 2020-07-01 |
| `DS2` | Categoria DS — progressione orizzontale 2 | € 2,261.56 | 2020-07-01 |
| `D4` | Categoria D — progressione orizzontale 4 | € 2,209.98 | 2020-07-01 |
| `DS1` | Categoria DS — progressione orizzontale 1 | € 2,180.26 | 2020-07-01 |
| `D3` | Categoria D — progressione orizzontale 3 | € 2,147.12 | 2020-07-01 |
| `DS` | Categoria DS — coordinatore | € 2,101.08 | 2020-07-01 |
| `D2` | Categoria D — progressione orizzontale 2 | € 2,084.77 | 2020-07-01 |
| `C4` | Categoria C — progressione orizzontale 4 | € 2,076.38 | 2020-07-01 |
| `D1` | Categoria D — progressione orizzontale 1 | € 2,022.94 | 2020-07-01 |
| `C3` | Categoria C — progressione orizzontale 3 | € 1,984.10 | 2020-07-01 |
| `D` | Categoria D — professionista sanitario | € 1,953.87 | 2020-07-01 |
| `C2` | Categoria C — progressione orizzontale 2 | € 1,921.25 | 2020-07-01 |
| `C1` | Categoria C — progressione orizzontale 1 | € 1,857.14 | 2020-07-01 |
| `C` | Categoria C — operatore qualificato | € 1,803.61 | 2020-07-01 |
| `B4` | Categoria B — progressione orizzontale 4 | € 1,733.54 | 2020-07-01 |
| `B3` | Categoria B — progressione orizzontale 3 | € 1,697.76 | 2020-07-01 |
| `B2` | Categoria B — progressione orizzontale 2 | € 1,669.36 | 2020-07-01 |
| `B1` | Categoria B — progressione orizzontale 1 | € 1,624.54 | 2020-07-01 |
| `A4` | Categoria A — progressione orizzontale 4 | € 1,592.19 | 2020-07-01 |
| `B` | Categoria B — operatore tecnico-pratico | € 1,579.86 | 2020-07-01 |
| `A3` | Categoria A — progressione orizzontale 3 | € 1,566.67 | 2020-07-01 |
| `A2` | Categoria A — progressione orizzontale 2 | € 1,544.35 | 2020-07-01 |
| `A1` | Categoria A — progressione orizzontale 1 | € 1,506.44 | 2020-07-01 |
| `A` | Categoria A — ausiliario generico | € 1,467.45 | 2020-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**Apprendistato professionalizzante 18 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

**Apprendistato professionalizzante 24 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

**Apprendistato professionalizzante 36 mesi** (type: `percentage`)  
Destination levels: `A`, `B`, `C`, `D`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sanita-privata-aiop-aris/shift_on_call_allowances · overtime · impact yes · open"
    SHIFT, ON-CALL AND RISK ALLOWANCES (Art. 60-61, pp. 89-90): the indennità notturna of 2,74 euro an hour of shift between 22 and 6, the holiday shift indemnity of 17,82 euro (8,91 for half a shift or less), the pronta disponibilità of 21,69 euro per 12 hours and the radiation risk indemnity of 1.239,50 euro a year are not modelled: no field of the request states the shifts or the on-call duty of the worker.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 60-61 indemnities with facts naming the night and holiday shift hours and the on-call turns of the worker.

!!! warning "sanita-privata-aiop-aris/part_time_supplementary_rate · overtime · impact yes · open"
    PART-TIME SUPPLEMENTARY HOURS: the ore supplementari of a part-time worker are paid with 15% of the retribuzione oraria globale (Art. 22, CCNL 8 October 2020, p. 25). The request has no kind for supplementary hours: an overtime event of a part-time worker takes the overtime bands unless the caller passes the multiplier.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a supplementary-hours kind to the overtime event and a supplementare band with the CCNL rate.

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
| Official CCNL text signed 2020-10-08; salary tables in Tabella 1 effective 2020-07-01 per Art. 51; values conglobated (EADR included per Art. 55) | altro | 2020-10-08 | [↗](https://www.fondazionerimed.eu/wp-content/uploads/2023/12/CCNL-CASE-DI-CURA-PRIVATE-08.10.2020.pdf) |
| CNEL registry entry confirming code T011, 146585 employees, ARIS/AIOP signatories | cnel | — | [↗](https://www.contratticcnl.it/ccnl/t011/) |

??? note "Coverage notes"
    CCNL signed 2020-10-08; nominally covers 2016-2018 (Art. 4). Applied in ultrattività from 2019 onwards. Salary tables (Tabella 1) effective 2020-07-01 per Art. 51. No renewal signed as of 2026-09-09. Confirmed 2026-09-09: preintesa June 2020 is the last event; all 2023-2025 bridge agreements found refer to the separate AIOP RSA contract (different CNEL code). The AIOP-ARIS ospedaliero (T011) T011 remains in pure ultrattività.
    
    Salary values are conglobated: EADR incorporated into tabellare from 2020-07-01 per Art. 55. Back-calculation: A 1467.45×13=19076.85 ✓; C4 2076.38×13=26992.94 ✓; DS4 2418.05×13=31434.65 ✓.
    
    28 levels (A, A1–A4, B, B1–B4, C, C1–C4, D, D1–D4, DS, DS1–DS4, E, E1, E2). Order assigned by 2020-07-01 salary because professional families A/B/C/D/DS/E have overlapping salary ranges — categories are not a single hierarchy. A4 (order 6) is paid above B (order 5) per Tabella 1. Horizontal progressions within each category are modelled as static levels per Art. 48; the engine does not auto-advance a worker's level after the contractual service threshold.
    
    Retribuzione individuale di anzianità frozen at 1993-12-31 per Art. 56 (no new seniority accruals). Modelled as seniority_increments.maximum_count=0.
    
    CCNL covers ospedalieri, IRCCS, riabilitazione (AIOP/ARIS members). Does not apply to RSA governed by separate AIOP RSA or Uneba agreements.
    
    hourly_divisor=156 (Art. 58: paga giornaliera=monthly/26, oraria=giornaliera/6 for 36h/week). Levels D4, DS4, E, E1, E2 work 38h/week per Art. 18 (oraria=giornaliera/6.33, exact divisor≈164.6), modelled as 156 uniformly.
    
    Apprenticeship (Art. 23 §14, Art. 23 §2): destination levels are the four category entry positions A, B, C, D only. Horizontal-progression steps (A1-A4, B1-B4, C1-C4, D1-D4) are not apprenticeship destinations. DS and E categories excluded per Art. 23 §2. OSS and Albo-registered health professions excluded per Art. 23 §2 but per-qualification restriction not modellable at level granularity.
    
    INPS: terziario sector confirmed. Kitech.it (table "TERZIARIO attività VARIE", kitech.it/Contributi-previdenziali.aspx?p=4_143) lists operai/impiegati at 9.19% employee contribution and 28.98% employer (≤50 dipendenti) / 29.58% (>50) — matching 2026-terziario.json exactly. Private healthcare (AIOP/ARIS) is classified under terziario standard rates; no healthcare-specific INPS regime applies. INPS Circolare n. 6/2026 confirms 9.19% employee rate for private sector workers.
    
    CCNL applied in ultrattività; Decreto Lavoro 2026 introduced a statutory 30% IPCA auto-adjustment if no renewal within 12 months of expiry. If triggered, legally applicable 2026 minimums may exceed the 2020 Tabella 1 values modelled here. Engine models contractual tables only.
    
    TERM: the CCNL of 8 October 2020 renews the economic part 2016-2018 and its table applies from 1 July 2020; no later renewal signed by AIOP and ARIS was found on 14 October 2026 (the unions were still asking to open the table), so the 2020 tabellari stay in force under ultrattività.
    
    APPRENTICESHIP (CCNL 8 October 2020, apprendistato professionalizzante, point 14, p. 31): 85% of the pay of the qualifica da conseguire, then 90%, by the length of the contract: months 1-9 and 10-12 for up to 18 months (the text does not state months 13-18, which keep 90%), 1-12 and 13-24 for up to 24 months, 1-18 and 19-36 for up to 36 months. Three tracks: set Apprentice.track. Apprentices accrue no seniority 'a nessun fine'.
    
    CNEL code T011 verified at https://www.contratticcnl.it/ccnl/t011/ (146585 employees, ARIS/AIOP, ATECO 86).
    

## Raw data

The contract file this page is generated from: [`agreement/sanita-privata-aiop-aris.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/sanita-privata-aiop-aris.json).

## Usage example

```python
--8<-- "docs/examples/agreement/sanita-privata-aiop-aris/example.py"
```
