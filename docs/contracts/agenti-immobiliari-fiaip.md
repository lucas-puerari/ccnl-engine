# CCNL per i dipendenti da agenti immobiliari professionali e mandatari a titolo oneroso

| | |
|---|---|
| **CNEL code** | `H0B1` |
| **Sector** | agenzie immobiliari |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-05-19 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FIAIP — Federazione Italiana Agenti Immobiliari Professionali
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| **Limits of this contract** | base_salary, bilateral_funds, pension_fund_contribution, seniority, una_tantum |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-05-19 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-05-01 |

### Semplificazioni note

7 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

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

!!! warning "agenti-immobiliari-fiaip/quadri_function_allowance · base_salary · impact yes · open"
    SIMPLIFICATION: Q indennità di funzione (Art. 162 footnote) not modelled. Amount: 250 EUR/month × 12 mensilità, for quadri with responsibility over operational or local units ('nei casi di responsabilità di unità operative o di unità locali'). Excluded because: (1) conditional on role attribute, not universal for level Q; (2) 12 mensilità conflicts with additional_months=14; (3) conglobated model requires fixed_allowances: []. employer_cost_annual may be understated by up to 3000 EUR/year for qualifying Q employees.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the Art. 162 Q function allowance (250 EUR x 12) as a role-gated allowance.

!!! warning "agenti-immobiliari-fiaip/ebnaip_qsc_and_flat_quota · bilateral_funds · impact yes · open"
    SIMPLIFICATION: QSC and Quota Forfettaria (Art. 11) not modelled. QSC: 1.90% of monthly retribuzione × 14 mensilità (0.30% employee + 1.60% employer), paid to EBNAIP. Quota Forfettaria: 12 EUR/month × 12 mensilità, employer only. Both go to the bilateral entity; the QSC constitutes retribuzione ordinaria for TFR purposes (Art. 11). Modelling would require percentage-based bilateral fund logic not yet implemented. employer_cost_annual understated by (QSC employer portion + 144 EUR/year).

    **Applies when:** a fact the request cannot express: never recorded on a run.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: CatA and CatB (Art. 164) not modelled as levels. These are special mixed-salary categories for agencies with ≤15 employees where workers receive commission income, modelled at 90% of level II and III respectively with mandatory commission minimum and 2% guarantee. Conditional on employer size and pay structure; not standard classification levels.

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
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/agenti-immobiliari-fiaip.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/agenti-immobiliari-fiaip.py"
```
