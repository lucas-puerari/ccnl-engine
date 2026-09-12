# CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso

| | |
|---|---|
| **CNEL code** | `H0B1` |
| **Sector** | agenzie immobiliari |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-19 |
| **Workers (est.)** | — |
| **Ruleset version** | `—` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FIAIP — Federazione Italiana Agenti Immobiliari Professionali
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| `Q` | Quadri — lavoratori con funzioni direttive e responsabilità di unità operative o locali (legge 190/85) | € 2,799.14 | — |
| `I` | 1° livello — lavoratori con elevata professionalità e autonomia tecnica e gestionale | € 2,583.51 | — |
| `II` | 2° livello — lavoratori con funzioni di coordinamento e autonomia operativa di rilievo | € 2,317.37 | — |
| `III` | 3° livello — lavoratori con mansioni qualificate che richiedono specifica preparazione professionale | € 2,069.63 | — |
| `IV` | 4° livello — lavoratori con mansioni esecutive richiedenti preparazione specifica o pratica acquisita | € 1,872.68 | — |
| `V` | 5° livello — lavoratori con mansioni esecutive semplici o di supporto operativo | € 1,750.97 | — |
| `VI` | 6° livello — lavoratori con mansioni elementari o di ausilio generale | € 1,623.19 | — |

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

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Q indennità di funzione (Art. 162 footnote) not modelled. Amount: 250 EUR/month × 12 mensilità, for quadri with responsibility over operational or local units ('nei casi di responsabilità di unità operative o di unità locali'). Excluded because: (1) conditional on role attribute, not universal for level Q; (2) 12 mensilità conflicts with additional_months=14; (3) conglobated model requires fixed_allowances: []. employer_cost_annual may be understated by up to 3000 EUR/year for qualifying Q employees.

!!! warning ""
    SIMPLIFICATION: QSC and Quota Forfettaria (Art. 11) not modelled. QSC: 1.90% of monthly retribuzione × 14 mensilità (0.30% employee + 1.60% employer), paid to EBNAIP. Quota Forfettaria: 12 EUR/month × 12 mensilità, employer only. Both go to the bilateral entity; the QSC constitutes retribuzione ordinaria for TFR purposes (Art. 11). Modelling would require percentage-based bilateral fund logic not yet implemented. employer_cost_annual understated by (QSC employer portion + 144 EUR/year).

!!! warning ""
    SIMPLIFICATION: CatA and CatB (Art. 164) not modelled as levels. These are special mixed-salary categories for agencies with ≤15 employees where workers receive commission income, modelled at 90% of level II and III respectively with mandatory commission minimum and 2% guarantee. Conditional on employer size and pay structure; not standard classification levels.

!!! warning ""
    SIMPLIFICATION: Apprendistato specialistico (Art. 55) not modelled. Two-year fast-track for workers holding the mediazione immobiliare exam: 24 months starting at 5° and ending at 3°. Intermediate classification not specified in the article. Modelled only under the four standard Art. 40/48 tracks.

!!! warning ""
    SIMPLIFICATION: Una tantum payments (01/09/2025 and 01/05/2026) for employees hired before 01/01/2024 not modelled. One-time payments only; not part of ongoing monthly retribuzione.

!!! warning ""
    SIMPLIFICATION: Fondo Fon.Te. supplementary pension (Art. 15) not modelled. Voluntary adhesion. Employee: 0.55% of TFR-eligible retribuzione; employer: 1.55% + 0.05% quota associativa. employer_cost_annual understated by approximately 1.60% of annual retribuzione for adherents.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-19 | [↗](https://www.ebnaip.it/) |

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

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/agenti-immobiliari-fiaip.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenti-immobiliari-fiaip.py"
```
