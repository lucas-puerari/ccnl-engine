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

[← Contracts index](index.md)

??? note "Signatories"
    - Federterme — Federazione Italiana delle Industrie Termali, delle Acque Minerali e del Benessere Termale
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1SA` | Primo livello super A — quadri e impiegati direttivi di massima specializzazione | € 2,111.72 | — |
| `1SB` | Primo livello super B — quadri e impiegati direttivi di alta specializzazione | € 1,979.64 | — |
| `1` | Impiegati di ordine superiore e lavoratori con mansioni direttive | € 1,794.86 | — |
| `2` | Impiegati di concetto e lavoratori con mansioni di concetto | € 1,469.32 | — |
| `3` | Lavoratori con mansioni qualificate che richiedono adeguata preparazione tecnico-pratica | € 1,231.76 | — |
| `4S` | Lavoratori specializzati con specifiche capacità superiori (4° Super) | € 1,161.39 | — |
| `4` | Lavoratori specializzati con specifiche capacità tecniche e pratiche | € 1,126.20 | — |
| `5` | Lavoratori adibiti a mansioni che richiedono normale pratica e conoscenze | € 1,002.82 | — |
| `6` | Lavoratori con mansioni elementari e di semplice attesa o custodia | € 879.97 | — |

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

**L4-L4S-terme-24m** (type: `under_classification`)  
Destination levels: `4S`, `4`

**L3-terme-36m** (type: `under_classification`)  
Destination levels: `3`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: EDR 10.32 (PDF Art. 83) vs 10.33 (kitech, statutory). Used 10.33. Impact: EUR 0.01/mese.

!!! warning ""
    SIMPLIFICATION: tax_sector='terziario'. Following H05B (Federturismo Confindustria) precedent. Federterme is Confindustria-affiliated; sector uses terziario INPS rates. Not verified against INPS circular. Impact on employer_cost_annual.

!!! warning ""
    SIMPLIFICATION: Fondi bilaterali non modellati (EBITERME, FONTUR assistenza sanitaria). Contributi datoriali non quantificati. employer_cost_annual sottostimato.

!!! warning ""
    SIMPLIFICATION: Apprendistato livelli 1SA, 1SB, 1, 2 non modellati — Art. 13 non specifica durata né trattamento economico per questi livelli.

!!! warning ""
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
    
    Apprenticeship: apprendistato professionalizzante (Art. 13), under-classification model. Three tracks: L5 (18 months, first half at L6, second half at midpoint L6-L5); L4+L4S (24 months, first half 2 below, second half 1 below); L3 (36 months, first half 2 below, second half 1 below). Higher levels (1SA, 1SB, 1, 2) have no duration specified in Art. 13 and are not modelled.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/aziende-termali-federterme.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/aziende-termali-federterme.py"
```
