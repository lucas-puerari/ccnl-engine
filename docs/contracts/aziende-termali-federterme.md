# CCNL per i lavoratori dipendenti delle aziende termali

| | |
|---|---|
| **CNEL code** | `K461` |
| **Sector** | turismo termale |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-10-08 |
| **Workers (est.)** | — |
| **Ruleset version** | `2024.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federterme — Federazione Italiana delle Industrie Termali, delle Acque Minerali e del Benessere Termale
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, inps_employer, seniority, trattamento_integrativo |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 65 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-10-08 |
| **Last review** | — |
| **Latest salary tranche** | 2026-12-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1SA` | Primo livello super A — quadri e impiegati direttivi di massima specializzazione | € 2,111.72 | 2026-12-01 |
| `1SB` | Primo livello super B — quadri e impiegati direttivi di alta specializzazione | € 1,979.64 | 2026-12-01 |
| `1` | Impiegati di ordine superiore e lavoratori con mansioni direttive | € 1,794.86 | 2026-12-01 |
| `2` | Impiegati di concetto e lavoratori con mansioni di concetto | € 1,469.32 | 2026-12-01 |
| `3` | Lavoratori con mansioni qualificate che richiedono adeguata preparazione tecnico-pratica | € 1,231.76 | 2026-12-01 |
| `4S` | Lavoratori specializzati con specifiche capacità superiori (4° Super) | € 1,161.39 | 2026-12-01 |
| `4` | Lavoratori specializzati con specifiche capacità tecniche e pratiche | € 1,126.20 | 2026-12-01 |
| `5` | Lavoratori adibiti a mansioni che richiedono normale pratica e conoscenze | € 1,002.82 | 2026-12-01 |
| `6` | Lavoratori con mansioni elementari e di semplice attesa o custodia | € 879.97 | 2026-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1SA` | € 18.07 |
| `1SB` | € 18.07 |
| `1` | € 16.01 |
| `2` | € 13.68 |
| `3` | € 12.13 |
| `4S` | € 11.62 |
| `4` | € 11.62 |
| `5` | € 11.36 |
| `6` | € 10.58 |

## Apprenticeship

**L5-terme-18m** (type: `under_classification`)  
Destination levels: `5`  
under-level: `1`

**L4-L4S-terme-24m** (type: `under_classification`)  
Destination levels: `4S`, `4`  
under-level: `1`

**L3-terme-36m** (type: `under_classification`)  
Destination levels: `3`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "aziende-termali-federterme/edr_rounding_discrepancy · base_salary · impact unknown · open"
    SIMPLIFICATION: EDR 10.32 (PDF Art. 83) vs 10.33 (kitech, statutory). Used 10.33. Impact: EUR 0.01/mese.

    **Applies when:** `base_salary` applies.

    **Remediation:** Confirm whether the EDR is 10.32 (PDF Art. 83) or 10.33 (kitech) and align the data.

!!! warning "aziende-termali-federterme/terziario_inps_rates_unverified · inps_employer · impact unknown · open"
    SIMPLIFICATION: tax_sector='terziario'. Following H05B (Federturismo Confindustria) precedent. Federterme is Confindustria-affiliated; sector uses terziario INPS rates. Not verified against INPS circular. Impact on employer_cost_annual.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the terziario INPS rates for Federterme employers against the INPS circular.

!!! warning "aziende-termali-federterme/ebiterme_fontur_funds · bilateral_funds · impact yes · open"
    SIMPLIFICATION: Fondi bilaterali non modellati (EBITERME, FONTUR assistenza sanitaria). Contributi datoriali non quantificati. employer_cost_annual sottostimato.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the EBITERME and FONTUR contributions as a bilateral fund event, or source and model them.

!!! warning "aziende-termali-federterme/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "aziende-termali-federterme/tourism_special_supplement · trattamento_integrativo · impact yes · open"
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-20, Gazzetta Ufficiale text, https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=1&art.versione=1, page sha256 e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d): from 1 January to 30 September 2026 the workers of the esercizi di somministrazione di alimenti e bevande (L. 287/1991 art. 5) and of the 'comparto del turismo, ivi inclusi gli stabilimenti termali', with employment income of 2025 not above 40,000 EUR, receive 'un trattamento integrativo speciale, che non concorre alla formazione del reddito, pari al 15 per cento delle retribuzioni lorde corrisposte in relazione al lavoro notturno e alle prestazioni di lavoro straordinario [...] effettuate nei giorni festivi'. The employer pays it 'su richiesta del lavoratore' (c. 20), a fact the request has no field for: the engine does not pay it, so the net pay of a worker who asked for it is understated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the worker's request of c. 20 to the request, pay 15% of the night and holiday overtime pay of the run as a credit, then remove this note.

!!! note "apprenticeship_midpoint_allowances · base_salary · impact yes · resolved"
    A midpoint_to_destination period pays the mean of the whole monthly pay of the pay level and the destination level: base salary and every active fixed allowance (an allowance of one level counts as zero on the other); the base takes the rest of the rounded mean of the totals. A CCNL whose text leaves the averaged components open carries its own limitation <ccnl_id>/apprenticeship_midpoint_components, recorded on the midpoint path.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: CCNLs whose midpoint components are unsourced are tracked by their own apprenticeship_midpoint_components limitation.

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
    SIMPLIFICATION: Apprendistato livelli 1SA, 1SB, 1, 2 non modellati — Art. 13 non specifica durata né trattamento economico per questi livelli.

!!! note ""
    SIMPLIFICATION: Storia salariale ante 1 ottobre 2024 non modellata. Il precedente CCNL (scaduto 31 dicembre 2019) non è disponibile in formato leggibile.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://ce-mu.it/rapportolavoro/contratti/cms_magazine/uploads/AziendeTermali_CCNL_2024_2027_08102024.pdf | altro | 2024-10-08 | [↗](https://ce-mu.it/rapportolavoro/contratti/cms_magazine/uploads/AziendeTermali_CCNL_2024_2027_08102024.pdf) |
| https://www.filcams.cgil.it/page/aziende_termali | tabella_retributiva | 2024-10-08 | [↗](https://www.filcams.cgil.it/page/aziende_termali) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=91 | tabella_retributiva | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=91) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series with 5 tranches (Oct 2024, Jun 2025, Dec 2025, Jun 2026, Dec 2026). Contingenza and EDR are frozen fixed_allowances. Source: AziendeTermali_CCNL_2024_2027 PDF Art. 82 (minimi tabellari) and Art. 83 (contingenza). Cross-verified with filcams.cgil.it/page/aziende_termali and kitech CodiceCateg=91.
    
    hourly_divisor: 173.33 — confirmed from PDF Art. 35 (Modalità di corresponsione della retribuzione): 'il minimo di paga base oraria moltiplicato per 173,33' and 'dividendo per 173,33 la retribuzione mensile'. Also confirmed in Art. 37 (13a e 14a mensilità): 'una 13a mensilità pari alla retribuzione mensile di fatto percepita (173,33 ore)'. Source: CCNL PDF pages 45 and 47.
    
    additional_months: 14 — Art. 37 explicitly states 13a (Natale) and 14a mensilità (giugno). Confirmed also from Art. 77 VIII which references '14 mensilità'. Source: CCNL PDF Art. 37, page 47.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from Art. 36 CCNL PDF page 46: 1SA/1SB=18.07, 1=16.01, 2=13.68, 3=12.13, 4S/4=11.62, 5=11.36, 6=10.58 EUR. PDF confirmed directly from scanned image.
    
    Contingenza values from Art. 83 CCNL PDF page 69 (frozen since November 1991 per Protocol 31/07/1992): 1SA=531.96, 1SB=531.38, 1=528.99, 2=521.47, 3=516.42, 4S=515.01, 4=514.86, 5=513.32, 6=510.89.
    
    EDR: 10.33 EUR/month (all levels). PDF Art. 83 states 10.32; operational value confirmed at 10.33 per kitech CodiceCateg=91 and statutory euro-conversion of ITL 20,000. 0.01 EUR/month discrepancy documented as SIMPLIFICATION.
    
    Apprenticeship: apprendistato professionalizzante (Art. 13), under-classification model. Three tracks: L5 (18 months, first half at L6, second half at midpoint L6-L5); L4+L4S (24 months, first half 2 below, second half 1 below); L3 (36 months, first half 2 below, second half 1 below). Higher levels (1SA, 1SB, 1, 2) have no duration specified in Art. 13 and are not modelled. Art. 13 lett. g (CCNL 2024-2027 PDF, p. 22): for the second half the pay of level 6 is 'maggiorato di un importo pari al 50% del differenziale previsto tra il 5° e il 6° livello': the engine pays the mean of the whole monthly pay (minimo, contingenza, EDR) of the two levels.
    

## Raw data

The contract file this page is generated from: [`agreement/aziende-termali-federterme.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/aziende-termali-federterme.json).

## Usage example

```python
--8<-- "docs/examples/agreement/aziende-termali-federterme/example.py"
```
