# CCNL Attivita Minerarie (ASSORISORSE)

| | |
|---|---|
| **CNEL code** | `B282` |
| **Sector** | Industria estrattiva - Miniere, cave, saline, metallurgia estrattiva |
| **Tax sector** | `industria` |
| **Last renewal** | 2022-07-13 |
| **Workers (est.)** | ~3000 |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ASSORISORSE
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| **Limits of this contract** | base_salary, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2022-07-13 |
| **Last verified** | — |
| **Latest salary tranche** | 2025-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1S` | Livello 1 Super - Quadri direttivi e tecnici di alta specializzazione | € 3,037.95 | 2025-01-01 |
| `1` | Livello 1 - Impiegati direttivi e tecnici specializzati | € 2,991.12 | 2025-01-01 |
| `2` | Livello 2 - Impiegati di concetto e operai altamente specializzati | € 2,768.11 | 2025-01-01 |
| `3` | Livello 3 - Impiegati d ordine e operai specializzati | € 2,460.22 | 2025-01-01 |
| `4` | Livello 4 - Operai qualificati e addetti a mansioni specifiche | € 2,228.15 | 2025-01-01 |
| `5` | Livello 5 - Operai comuni con autonomia operativa | € 2,103.19 | 2025-01-01 |
| `6` | Livello 6 - Operai comuni | € 1,981.71 | 2025-01-01 |
| `7` | Livello 7 - Operai generici con mansioni semplici | € 1,856.57 | 2025-01-01 |
| `8` | Livello 8 - Operai ausiliari e addetti a cernita | € 1,705.38 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1S`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "attivita-minerarie-assorisorse/seniority_not_modelled · seniority · impact yes · open"
    SIMPLIFICATION: Seniority increments (scatti di anzianita) not modeled — Art. anzianita not found in scanned PDF pages available (OCR coverage pages 1-10, table on page 9). Seniority amounts are unknown.

    **Applies when:** `seniority` applies.

    **Remediation:** Source the seniority article and add the increments to the CCNL file.

!!! warning "attivita-minerarie-assorisorse/ocr_salary_values · base_salary · impact unknown · open"
    SIMPLIFICATION: Source PDF is scanned (image-based, CCITT compression). Salary values extracted via OCR (Ghostscript + Tesseract). Amounts verified by cross-checking parametrale ratios and incremental consistency.

    **Applies when:** `base_salary` applies.

    **Remediation:** Check the OCR-extracted salary values against a text source of the renewal protocol.

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
    SIMPLIFICATION: Work rules (overtime rates, leave, sickness) not modeled — source document is a renewal protocol covering salary increases and HSE provisions, not the full CCNL text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-07-13 | [↗](https://www.filctemcgil.it/images/download/CONTRATTI/miniere/220713_ATTIVITA%20MINERARIE_RINNOVO%20CCNL%202022-2025.pdf) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. Art. 17 shows Minimi di Retribuzione as a single total amount per level with no separate contingenza column. base_salary = total monthly minimum; fixed_allowances = [] for all levels.
    
    SALARY PERIODS: 4 tranches — baseline 2022-04-01 (pre-increase values); I tranche 2023-01-01; II tranche 2023-12-01; III tranche 2025-01-01. IPCA 9% applied over contract duration 2022-2025.
    
    SIGNATORIES: ASSORISORSE (Risorse Naturali ed Energie Sostenibili) + FILCTEM-CGIL + FEMCA-CISL + UILTEC-UIL. Agreement signed Roma, 13 luglio 2022. Renews CCNL 11 aprile 2019.
    
    HOURLY DIVISOR: 173 assumed (40h/week x 52/12 = 173.33 standard industria convention). Not explicitly confirmed from scanned PDF — verify against Art. orario.
    
    ADDITIONAL MONTHS: 13 assumed (tredicesima only, standard for Confindustria-affiliated mining). Not explicitly confirmed from scanned PDF — verify against Art. gratifica natalizia.
    
    COVERAGE: ~3,000 workers, ~70 enterprises (miniere, cave, saline, metallurgia estrattiva non-ferrosa). INPS code B282 active.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/attivita-minerarie-assorisorse.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/attivita-minerarie-assorisorse.py"
```
