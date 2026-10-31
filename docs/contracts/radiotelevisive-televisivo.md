# CCNL Radiotelevisivo — Settore Televisivo Multimediale

| | |
|---|---|
| **CNEL code** | `G091` |
| **Sector** | radiotelevisione — settore televisivo multimediale |
| **Family** | `spettacolo-media` |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-01-08 |
| **Workers (est.)** |  |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Radio Televisioni
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UIL-COM

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
| **Rule provenance** | 28 verified / 0 derived / 11 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-01-08 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-01-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-17 | claude-opus-5-5 (ai) | The minimi tabellari of the Settore Televisivo Multimediale against the tables of the renewal published by Confindustria Radio Televisioni. | confirmed | The minimi of the 9 levels from 2026-01-01 to 2028-01-01 (PDF p. 1, text layer; the same tables are in the consolidated CCNL 2026, PDF pp. 74-75) match the file and move from assumed to verified.<br>The ruleset names this source, published by Confindustria Radio Televisioni, the employer signatory: source_type contracting_party instead of estimated. |
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 45 - Tredicesima mensilità (p. 76): "Nel caso di inizio del rapporto durante il corso dell’anno, il lavoratore avrà diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità per quanti sono i mesi di servizio prestati nell’Azienda. Le frazioni di mese superiori a 15 giorni saranno da considerare mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | 9° livello | € 2,282.56 | 2028-01-01 |
| `8` | 8° livello | € 2,092.44 | 2028-01-01 |
| `7` | 7° livello | € 1,929.62 | 2028-01-01 |
| `6` | 6° livello | € 1,840.62 | 2028-01-01 |
| `5` | 5° livello | € 1,696.00 | 2028-01-01 |
| `4` | 4° livello | € 1,425.96 | 2028-01-01 |
| `3` | 3° livello | € 1,190.33 | 2028-01-01 |
| `2` | 2° livello | € 1,046.74 | 2028-01-01 |
| `1` | 1° livello | € 902.11 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.39 |
| `2` | € 12.91 |
| `3` | € 15.49 |
| `4` | € 18.08 |
| `5` | € 19.63 |
| `6` | € 21.17 |
| `7` | € 21.69 |
| `8` | € 22.72 |
| `9` | € 24.79 |

## Apprenticeship

**professionalizzante_breve** (type: `percentage`)  
Destination levels: `3`  
percentage: 0.90

**professionalizzante_esteso** (type: `percentage`)  
Destination levels: `4`, `5`, `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "radiotelevisive-televisivo/inps_rates_reused_unverified · inps_employer · impact unknown · open"
    INPS rates reuse existing 2026-industria.json (tax_sector=industria). No bilateral fund substitution for broadcasting sector identified; standard Confindustria INPS rates apply.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Confirm the 2026 INPS rates of the broadcasters (industria, CIGO vs FIS by size) against the INPS circular, and route the roles insured in the ex-ENPALS FPLS to that regime.

!!! warning "radiotelevisive-televisivo/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
| https://www.confindustriaradiotv.it/ | associazione | 2026-01-08 | [↗](https://www.confindustriaradiotv.it/) |

??? note "Coverage notes"
    CCNL Radiotelevisivo 2026 signed 08/01/2026 in Roma. Employer: Confindustria Radio Televisioni (pres. Antonio Marano) and ANICA (pres. Alessandro Usai). Unions: SLC-CGIL (Sindacato Lavoratori della Comunicazione), FISTEL-CISL (Federazione Informazioni Spettacolo e Telecomunicazioni), UIL-COM (UIL Comunicazione). Signatories sourced from Art. 1, page 7 of CCNL PDF.
    
    Source anchor: https://www.confindustriaradiotv.it/ is the employer association homepage; a direct PDF permalink was not published. PDF read locally as ccnl_radiotv_2026.pdf (81 MB, read 2026-09-12).
    
    SPLIT model: paga base (minimo tabellare, Art. 43) + contingenza congelata al 1° novembre 1991 (Allegato A). EDR not present in 2026 CCNL.
    
    DUAL-SECTOR contract: Settore Televisivo Multimediale (9 livelli) and Settore Radiofonico (6 livelli) modelled in two separate files because the engine's monotonicity validator (higher order >= higher salary at every tranche date) rejects a merged 15-level file: at 01/01/2026 Radio L2 (868.41) > TV L1 (835.62) and Radio L6 (1632.31) > TV L5 (1571.00), inverting the relative ordering set at the CCNL base date.
    
    TV sector has three new tranches: 01/01/2026, 01/06/2027, 01/01/2028. Radio sector has only two: 01/01/2026, 01/06/2027 (no 01/01/2028 tranche). The pre-2026 CCNL column values (from the 2022 contract) are not modelled.
    
    Hourly divisor 173 sourced from Art. 43. Verified on levels 3, 5, 7: none of the three back-calculations from the published hourly rate yield a conglobated total — values are paga base only, confirming the split model.
    
    Apprenticeship (Art. 27): professionalizzante, percentage type. TV L3 max 24 months; TV L4-L6 max 48-60 months (same % schedule). Levels L7-L9 not accessible via apprenticeship per Art. 27.
    
    Apprenticeship open tail: Art. 27 sets 24-month max for L3 (breve track). The final period {18, null, 0.90} cannot be closed to {18, 24, 0.90} because the engine schema requires the last apprenticeship period to be open-ended (validate_open_sequence). A query past month 24 is outside the contract duration and should not arise in normal use.
    

## Raw data

The contract file this page is generated from: [`agreement/radiotelevisive-televisivo.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/radiotelevisive-televisivo.json).

## Usage example

```python
--8<-- "docs/examples/agreement/radiotelevisive-televisivo/example.py"
```
