# CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso

| | |
|---|---|
| **CNEL code** | `H0B1` |
| **Sector** | agenzie immobiliari |
| **Family** | `servizi-immobiliari` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-19 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FIAIP — Federazione Italiana Agenti Immobiliari Professionali
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, pension_fund_contribution, seniority, una_tantum |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 29 verified / 1 derived / 2 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-19 |
| **Last review** | 2026-11-01 |
| **Latest salary tranche** | 2027-05-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-17 | claude-opus-5-5 (ai) | The paga base nazionale conglobata of the seven levels against the signed ipotesi of 19 May 2025 and the final text of the CCNL 2025 (Ebnaip). | confirmed | Tabelle retributive of the signed ipotesi (p. 7, scan checked on the page image): the 28 minimi from 1/5/2025 to 1/5/2027 match the file and move from assumed to verified. The final text of the CCNL (Ebnaip copy, art. 162-163, PDF pp. 96-97) prints the same base at April 2025, increments and final amounts.<br>The ruleset names the signed ipotesi published by FIAIP, the employer signatory: source_type contracting_party instead of estimated. |
| 2026-11-01 | claude-opus-5-5 (ai) | The indennità di funzione of the quadri, Art. 162 note (*) (p. 97). | corrected | Art. 162 note (*) (p. 97): 250.00 a month for 12 months to the quadri responsible for operational or local units: levels[Q].fixed_allowances[IND_FUNZIONE], role responsabile_unita, months_per_year 12. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri — lavoratori con funzioni direttive e responsabilità di unità operative o locali (legge 190/85) | € 2,799.14 | 2027-05-01 |
| `I` | 1° livello — lavoratori con elevata professionalità e autonomia tecnica e gestionale | € 2,583.51 | 2027-05-01 |
| `II` | 2° livello — lavoratori con funzioni di coordinamento e autonomia operativa di rilievo | € 2,317.37 | 2027-05-01 |
| `III` | 3° livello — lavoratori con mansioni qualificate che richiedono specifica preparazione professionale | € 2,069.63 | 2027-05-01 |
| `IV` | 4° livello — lavoratori con mansioni esecutive richiedenti preparazione specifica o pratica acquisita | € 1,872.68 | 2027-05-01 |
| `V` | 5° livello — lavoratori con mansioni esecutive semplici o di supporto operativo | € 1,750.97 | 2027-05-01 |
| `VI` | 6° livello — lavoratori con mansioni elementari o di ausilio generale | € 1,623.19 | 2027-05-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 33.05 |
| `I` | € 30.99 |
| `II` | € 28.41 |
| `III` | € 25.31 |
| `IV` | € 23.24 |
| `V` | € 22.21 |
| `VI` | € 21.17 |

## Apprenticeship

**II-agenti-immobiliari-36m** (type: `under_classification`)  
Destination levels: `II`

**III-agenti-immobiliari-36m** (type: `under_classification`)  
Destination levels: `III`

**IV-agenti-immobiliari-36m** (type: `under_classification`)  
Destination levels: `IV`

**V-agenti-immobiliari-36m** (type: `under_classification`)  
Destination levels: `V`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! note "agenti-immobiliari-fiaip/quadri_function_allowance · base_salary · impact yes · resolved"
    SIMPLIFICATION: Q indennità di funzione (Art. 162 footnote) not modelled. Amount: 250 EUR/month × 12 mensilità, for quadri with responsibility over operational or local units ('nei casi di responsabilità di unità operative o di unità locali'). The schema can express it (Allowance.role, Allowance.months_per_year); the conglobated file keeps fixed_allowances empty. employer_cost_annual may be understated by up to 3000 EUR/year for qualifying Q employees (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Resolved: level Q carries IND_FUNZIONE, 250.00 for 12 months, for the role responsabile_unita of Employment.roles.

!!! warning "agenti-immobiliari-fiaip/ebnaip_qsc_and_flat_quota · bilateral_funds · impact yes · open"
    SIMPLIFICATION: QSC and Quota Forfettaria (Art. 11) not modelled. QSC: 1.90% of monthly retribuzione × 14 mensilità (0.30% employee + 1.60% employer), paid to EBNAIP. Quota Forfettaria: 12 EUR/month × 12 mensilità, employer only. Both go to the bilateral entity; the QSC constitutes retribuzione ordinaria for TFR purposes (Art. 11). Modelling would require percentage-based bilateral fund logic not yet implemented. employer_cost_annual understated by (QSC employer portion + 144 EUR/year).

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the QSC and the quota forfettaria as a bilateral fund event, or model percentage-based bilateral contributions.

!!! warning "agenti-immobiliari-fiaip/specialist_apprenticeship_track · base_salary · impact yes · open"
    SIMPLIFICATION: Apprendistato specialistico (Art. 55) not modelled. Two-year fast-track for workers holding the mediazione immobiliare exam: 24 months starting at 5° and ending at 3°. Intermediate classification not specified in the article. Modelled only under the four standard Art. 40/48 tracks.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 55 two-year specialist track once its intermediate classification is sourced.

!!! warning "agenti-immobiliari-fiaip/una_tantum_2025_2026 · una_tantum · impact yes · open"
    SIMPLIFICATION: Una tantum payments (01/09/2025 and 01/05/2026) for employees hired before 01/01/2024 not modelled. One-time payments only; not part of ongoing monthly retribuzione.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pay the 01/09/2025 and 01/05/2026 una tantum outside the engine for workers hired before 01/01/2024.

!!! warning "agenti-immobiliari-fiaip/fonte_pension_fund · pension_fund_contribution · impact yes · open"
    SIMPLIFICATION: Fondo Fon.Te. supplementary pension (Art. 15) not modelled. Voluntary adhesion. Employee: 0.55% of TFR-eligible retribuzione; employer: 1.55% + 0.05% quota associativa. employer_cost_annual understated by approximately 1.60% of annual retribuzione for adherents.

    **Applies when:** `pension_fund_contribution` applies.

    **Remediation:** Add the Fon.Te. employee and employer rates to the CCNL pension fund data.

!!! warning "agenti-immobiliari-fiaip/apprentice_seniority · seniority · impact unknown · open"
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

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

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

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: CatA and CatB (Art. 164) not modelled as levels. These are special mixed-salary categories for agencies with ≤15 employees where workers receive commission income, modelled at 90% of level II and III respectively with mandatory commission minimum and 2% guarantee. Conditional on employer size and pay structure; not standard classification levels.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.ebnaip.it/ | altro | 2025-05-19 | [↗](https://www.ebnaip.it/) |

??? note "Coverage notes"
    Salary model: CONGLOBATED. Art. 158 explicitly lists the composition: paga base nazionale conglobata comprising paga base + contingenza ex art. 98 CCNL 11/6/97 + EDR accordo interconfederale 21/07/92 + elemento economico di 2° livello ex art. 95 CCNL 11/6/97. Art. 162 title: 'Paga base nazionale conglobata'. Modelled as base_salary (TimeSeries per level) with fixed_allowances: [] for all levels.
    
    CatA/CatB cross-verification: Art. 164 defines CatA = 90% of level II and CatB = 90% of level III for agencies ≤15 employees with commission-based pay. Cross-check at 01/05/2025: 0.9×2156.50=1940.85 (CatA matches), 0.9×1925.95=1733.355≈1733.36 (CatB matches). This independently confirms all four tranche values for levels II and III.
    
    hourly_divisor: 168 — confirmed from Art. 161 explicit text ('La quota oraria della retribuzione, si ottiene dividendo l'importo mensile per 168'). Also consistent with Art. 67 (hourly divisor = 168) and Art. 103 (standard weekly hours = 40).
    
    additional_months: 14 — Art. 168 (tredicesima, December) and Art. 169 (quattordicesima, 1 July) both explicit in CCNL. Art. 7 ter also references tredicesima and quattordicesima as separate institutes.
    
    Seniority: 10 scatti triennali (cadence_months=36, maximum_count=10). Amounts from Art. 157 CCNL: Q=33.05, I=30.99, II=28.41, III=25.31, IV=23.24, V=22.21, VI=21.17 EUR.
    
    Tranche arithmetic verification: Art. 163 prints four tables. Q: 2500.20+104.63=2604.83, +59.79=2664.62, +59.79=2724.41, +74.73=2799.14. Level IV: 1672.68+70.00=1742.68, +40.00=1782.68, +40.00=1822.68, +50.00=1872.68. Both reconcile exactly. Tabelle retributive values treated as authoritative.
    
    Apprenticeship: apprendistato professionalizzante, under-classification model (Art. 40, 46, 48 CCNL 19/05/2025). Q and I excluded per Art. 46. Levels II-V eligible, all 36 months per Art. 48. Art. 40: first half 2 levels below, second half 1 level below. Special rule for dest=V: 1 level below throughout (Art. 40 'Per l'apprendistato al 5° livello l'inquadramento è di 1 livello inferiore per tutto il periodo formativo'). Source: signed CCNL 19/05/2025, Art. 40, 46, 48.
    
    tax_sector: terziario. Signatories include FILCAMS-CGIL, FISASCAT-CISL and UILTUCS-UIL — the three national federations that represent the commerce/services sector and sign terziario contracts. 2026-terziario.json exists; no new TaxSector needed.
    
    first valid_from is 2025-05-01 (decorrenza del rinnovo per le tabelle retributive). agreement_date 2025-05-19 is the signature date; these differ per precedent (IC91: agreement_date 2023-02-28, first tranche 2021-01-01). April 2025 table from Art. 162 is the previgente table — not modelled as a period.
    
    Source provenance: values extracted from signed CCNL 19/05/2025 PDF distributed by FIAIP/EBNAIP. The direct PDF download URL was not recorded; the homepage https://www.ebnaip.it/ was used as the source anchor. All values verified page-by-page against the original document.
    

## Raw data

The contract file this page is generated from: [`agreement/agenti-immobiliari-fiaip.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/agenti-immobiliari-fiaip.json).

## Usage example

```python
--8<-- "docs/examples/agreement/agenti-immobiliari-fiaip/example.py"
```
