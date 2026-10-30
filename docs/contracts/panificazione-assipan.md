# CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)

| | |
|---|---|
| **CNEL code** | `E023` |
| **Sector** | alimentare |
| **Family** | `alimentare` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-26 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assipan — Associazione Sindacale Panificatori Industriali
    - Fiesa-Assopanificatori — Federazione Italiana Esercenti Specializzati Alimentazione
    - Federpanificatori
    - FLAI-CGIL — Federazione Lavoratori Agro-industrie
    - FAI-CISL — Federazione Agroalimentare e Industriale
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority |

1 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 48 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-26 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-09-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Titolo XIX - Art. 52 - Tredicesima e quattordicesima mensilità (p. 66): "Il diritto alle mensilità aggiuntive matura per dodicesimi, intendendosi per mese intero la frazione di mese superiore a 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `I` | Level I — managers, senior professionals, plant directors | € 2,458.99 | 2026-09-01 |
| `II` | Level II — supervisors, senior specialists, department coordinators | € 2,305.51 | 2026-09-01 |
| `IIIA` | Level IIIA — highly skilled workers, senior technicians, team leaders | € 2,162.35 | 2026-09-01 |
| `IIIB` | Level IIIB — specialist workers, master bakers, experienced technicians | € 2,046.31 | 2026-09-01 |
| `IV` | Level IV — skilled workers, qualified bakers and production workers | € 1,806.45 | 2026-09-01 |
| `V` | Level V — semi-skilled workers, basic production tasks under supervision | € 1,664.67 | 2026-09-01 |
| `VI` | Level VI — entry-level workers, no qualification required, unskilled tasks | € 1,481.15 | 2026-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 34.28 |
| `II` | € 31.67 |
| `IIIA` | € 29.25 |
| `IIIB` | € 27.24 |
| `IV` | € 22.91 |
| `V` | € 20.27 |
| `VI` | € 17.14 |

## Apprenticeship

**panif_track_a** (type: `percentage`)  
Destination levels: `I`, `II`, `IIIA`, `IIIB`, `IV`  
percentage: 0.90

**panif_track_b** (type: `percentage`)  
Destination levels: `V`  
percentage: 0.80

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "panificazione-assipan/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Testo Unico CCNL Panificazione e Settori Affini Industria, signed 26 Feb 2025. Economic provisions effective from Feb 1, 2024 (AFAC advance). Art. 50 bis (retribuzione), Art. 51 (scatti di anzianita), Art. 52 (mensilita aggiuntive), Art. 28 (apprendistato). | altro | 2025-02-26 | [↗](https://www.assipan.it/contratto-collettivo-nazionale-lavoro/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. Art. 50 bis states the minimo tabellare is the conglobated figure (paga base + contingenza frozen 1 Nov 1991 + EDR) and that the quota oraria is obtained by dividing it by 173. The premio di produzione nazionale is articled separately in Art. 50 ter as a distinct element outside the conglobated minimum, therefore modelled as fixed_allowance per level.
    
    SIGNATORIES: Assipan/Fiesa-Assopanificatori/Federpanificatori (employer) — FLAI-CGIL/FAI-CISL/UILA-UIL (worker). CNEL code E023. NOTE: Aidepi is NOT a signatory to E023; Aidepi firms use CCNL Alimentari Industria (E012).
    
    HOURLY DIVISOR: 173, verbatim from Art. 50 bis: 'I minimi di cui sopra sono riferiti ad una prestazione di lavoro di 173 ore mensili. La quota oraria si ricava dividendo le retribuzioni per 173.'
    
    ADDITIONAL MONTHS: 14 — tredicesima (Art. 52, para 1) + quattordicesima (Art. 52, para 2, paid June 30). Both confirmed from Testo Unico 2025.
    
    SENIORITY: biennale (24 months), maximum 5 scatti. Amounts frozen since Aug 1, 1997 (Art. 51). Per-level EUR: I=34.28, II=31.67, IIIA=29.25, IIIB=27.24, IV=22.91, V=20.27, VI=17.14.
    
    PREMIO DI PRODUZIONE NAZIONALE: fixed cifra per level, frozen since Aug 1, 1995 (Art. 50 ter). All seven levels receive it. Modelled as fixed_allowance with code PREMIO_PROD.
    
    PREMIO DI PRODUZIONE FREQUENCY: modelled as monthly (14x). Evidence: (1) the prize is listed as component c) of 'trattamento economico' in Art. 50 bis alongside paga base — all components in that list are monthly recurring pay; (2) the prize amounts are in 'cifra mensile' (no 'annuale' qualifier); (3) the TFR computation clause includes it in the monthly average calculation, consistent with monthly payment; (4) the quattordicesima (Art. 53) uses the 'ultima mensilità percepita' which would include the prize if monthly. No evidence of single-annual-sum treatment found in the primary 2025 Testo Unico.
    
    APPRENTICESHIP: Art. 28 percentage model. Two tracks: Track A (levels I/II/IIIA/IIIB/IV) periods 0-12m=70%, 12-24m=80%, 24m+=90%; Track B (level V) periods 0-12m=70%, 12m+=80%. Level VI is excluded from apprendistato per Art. 28. Maximum contractual durations: I-IIIB=36m, IV=30m, V=24m — not enforced by engine but documented here. The 95% bracket (Art. 28, months 49+) is unreachable given max durations; omitted from both tracks.
    
    PRE-AFAC TRANCHE: now modelled. Confirmed from Testo Unico 2025 (assipan.it PDF, 26/02/2025), column 'Retribuzione al 31/01/2024': I=2102.30, II=1977.36, IIIA=1860.95, IIIB=1766.31, IV=1569.25, V=1452.44, VI=1302.81. These amounts are added as the 2023-01-01 period (valid until 31/01/2024) for all seven levels.
    
    HOURLY RATE: Art. 50 bis defines the official quota oraria as minimo_tabellare/173 (base only). work_rules.time_supplements.hourly_base_method is minimo_tabellare, so a derived hourly base leaves PREMIO_PROD out; while the hourly base provenance is not verified the engine derives none and overtime and absences take the caller's hourly rate. Monthly and annual figures are unaffected. (review of 2026-10-30)
    

## Raw data

The contract file this page is generated from: [`agreement/panificazione-assipan.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/panificazione-assipan.json).

## Usage example

```python
--8<-- "docs/examples/agreement/panificazione-assipan/example.py"
```
