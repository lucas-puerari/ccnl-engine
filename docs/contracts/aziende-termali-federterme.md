# CCNL per i lavoratori dipendenti delle aziende termali

| | |
|---|---|
| **CNEL code** | `K461` |
| **Sector** | turismo termale |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | — |
| **Ruleset version** | `2024.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federterme — Federazione Italiana delle Industrie Termali, delle Acque Minerali e del Benessere Termale
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS-UIL

## Coverage

### Funzionalità

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | base_salary, bilateral_funds, inps_employer, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2026-12-01 |

### Semplificazioni note

6 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

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

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the EBITERME and FONTUR contributions as a bilateral fund event, or source and model them.

!!! warning "aziende-termali-federterme/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Apprendistato livelli 1SA, 1SB, 1, 2 non modellati — Art. 13 non specifica durata né trattamento economico per questi livelli.

!!! note ""
    SIMPLIFICATION: Storia salariale ante 1 ottobre 2024 non modellata. Il precedente CCNL (scaduto 31 dicembre 2019) non è disponibile in formato leggibile.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-10-08 | [↗](https://ce-mu.it/rapportolavoro/contratti/cms_magazine/uploads/AziendeTermali_CCNL_2024_2027_08102024.pdf) |
| — | — | 2024-10-08 | [↗](https://www.filcams.cgil.it/page/aziende_termali) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=91) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series with 5 tranches (Oct 2024, Jun 2025, Dec 2025, Jun 2026, Dec 2026). Contingenza and EDR are frozen fixed_allowances. Source: AziendeTermali_CCNL_2024_2027 PDF Art. 82 (minimi tabellari) and Art. 83 (contingenza). Cross-verified with filcams.cgil.it/page/aziende_termali and kitech CodiceCateg=91.
    
    hourly_divisor: 173.33 — confirmed from PDF Art. 35 (Modalità di corresponsione della retribuzione): 'il minimo di paga base oraria moltiplicato per 173,33' and 'dividendo per 173,33 la retribuzione mensile'. Also confirmed in Art. 37 (13a e 14a mensilità): 'una 13a mensilità pari alla retribuzione mensile di fatto percepita (173,33 ore)'. Source: CCNL PDF pages 45 and 47.
    
    additional_months: 14 — Art. 37 explicitly states 13a (Natale) and 14a mensilità (giugno). Confirmed also from Art. 77 VIII which references '14 mensilità'. Source: CCNL PDF Art. 37, page 47.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from Art. 36 CCNL PDF page 46: 1SA/1SB=18.07, 1=16.01, 2=13.68, 3=12.13, 4S/4=11.62, 5=11.36, 6=10.58 EUR. PDF confirmed directly from scanned image.
    
    Contingenza values from Art. 83 CCNL PDF page 69 (frozen since November 1991 per Protocol 31/07/1992): 1SA=531.96, 1SB=531.38, 1=528.99, 2=521.47, 3=516.42, 4S=515.01, 4=514.86, 5=513.32, 6=510.89.
    
    EDR: 10.33 EUR/month (all levels). PDF Art. 83 states 10.32; operational value confirmed at 10.33 per kitech CodiceCateg=91 and statutory euro-conversion of ITL 20,000. 0.01 EUR/month discrepancy documented as SIMPLIFICATION.
    
    Apprenticeship: apprendistato professionalizzante (Art. 13), under-classification model. Three tracks: L5 (18 months, first half at L6, second half at midpoint L6-L5); L4+L4S (24 months, first half 2 below, second half 1 below); L3 (36 months, first half 2 below, second half 1 below). Higher levels (1SA, 1SB, 1, 2) have no duration specified in Art. 13 and are not modelled. Art. 13 lett. g (CCNL 2024-2027 PDF, p. 22): for the second half the pay of level 6 is 'maggiorato di un importo pari al 50% del differenziale previsto tra il 5° e il 6° livello': the engine pays the mean of the whole monthly pay (minimo, contingenza, EDR) of the two levels.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/aziende-termali-federterme.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/aziende-termali-federterme.py"
```
