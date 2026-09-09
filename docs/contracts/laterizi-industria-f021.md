# CCNL Laterizi e Manufatti Cementizi - Industria

| | |
|---|---|
| **CNEL code** | `F021` |
| **Sector** | industria |
| **Tax sector** | `edilizia` |
| **Last renewal** | — |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Ceramica Raggruppamento Laterizi
    - Assobeton
    - FENEAL-UIL
    - FILCA-CISL
    - FILLEA-CGIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ASQ` | Quadri AS — Impiegati inquadrati al livello AS con responsabilita di coordinamento e gestione di settori fondamentali | € 2,588.66 | — |
| `AS` | AS — Impiegati con funzioni direttive e discrezionalita di poteri | € 2,588.66 | — |
| `A` | A — Impiegati con funzioni autonome di guida e coordinamento | € 2,176.82 | — |
| `B` | B — Impiegati e Operai con mansioni di concetto o manutenzione impianti con coordinamento | € 1,776.77 | — |
| `CS` | CS — Operai specializzati con interventi elettrici/elettronici o coordinamento squadra | € 1,681.04 | — |
| `C` | C — Impiegati e Operai con autonomia esecutiva e conoscenze professionali specifiche | € 1,599.23 | — |
| `D` | D — Impiegati con mansioni d'ordine e Operai con capacita tecnico-pratiche | € 1,485.67 | — |
| `E` | E — Impiegati con mansioni esecutive generiche e Operai con capacita pratica di mestiere | € 1,377.67 | — |
| `F` | F — Operai con semplici conoscenze conseguibili con breve pratica (incl. superminimo 4.13 EUR) | € 1,178.55 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `ASQ` | € 14.72 |
| `AS` | € 14.72 |
| `A` | € 11.71 |
| `B` | € 9.60 |
| `CS` | € 8.70 |
| `C` | € 8.32 |
| `D` | € 7.87 |
| `E` | € 7.23 |
| `F` | € 6.79 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `ASQ`, `AS`, `A`, `B`

**professionalizzante_30** (type: `under_classification`)  
Destination levels: `CS`, `C`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `D`

**professionalizzante_12** (type: `under_classification`)  
Destination levels: `E`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP — level E period 1: the CCNL Art. 9 prescribes 2 levels below destination for period 1 in all tracks. For destination E (order=2), 2 below would reach order=0 which does not exist. Engine level_by_order raises ValueError for missing orders. SIMPLIFICATION: E track period 1 uses levels_below=1 (pay at level F, order=1), the lowest available level below E. Duration: 6+6 months.

!!! warning ""
    ASQ SENIORITY: thaler.it seniority table lists AS, A, B, CS, C, D, E, F amounts but not ASQ separately. SIMPLIFICATION: ASQ uses the same scatto amount as AS (14.72 EUR/biennio).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-05-31 | [↗](https://www.filcacisl.it/sindacato/wp-content/uploads/2022/06/Ccnl-laterizi-manufatti-industria-31-5-2022.pdf) |
| — | — | 2025-10-31 | [↗](https://www.filleacgil.net/images/ORGANIZZAZIONE/CONTRATTI_E_TABELLE/LATERIZI/Ipotesi_di_Accordo_Rinnovo_CCNL_Laterizi_e_manufatti_31.10.2025.pdf) |
| — | — | 2022-05-31 | [↗](https://www.filcacisl.it/sindacato/wp-content/uploads/2025/02/Tabella-retributiva-CCNL-Laterizi-INDUSTRIA-DA-FEBBRAIO-2025.pdf) |
| — | — | 2020-02-12 | [↗](https://lawinsider.com/it/contracts/euRWxUzbye9) |
| — | — | — | [↗](https://www.thaler.it/assets/files/Transparenzdekret/Laterizi_-_Aziende_industriali.pdf) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = paga tabellare (TEM), varying by level and tranche. fixed_allowances per level: CONTINGENZA (frozen since 1993 Protocol) + EDR (10.33 EUR, all levels). Level AS also carries Indennita di funzione quadri (51.65 EUR) — applied to ASQ level only. Source: FILCA-CISL tabella retributiva (2022 and 2025 renewals); thaler.it parametri contrattuali.
    
    SALARY TABLE: 2022 contract (decorrenza 01/04/2022, signed 31/05/2022): 3 tranches at 01/07/2022, 01/10/2023, 01/02/2025. 2025 contract (decorrenza 01/10/2025, signed 31/10/2025): 4 tranches at 01/10/2025, 01/07/2026, 01/07/2027, 01/07/2028. Sources: FILCA-CISL salary tables (primary).
    
    HOURLY DIVISOR: 174. Source: thaler.it parametri contrattuali ('Divisori Giornaliero: 174'). Consistent with 40h/week standard (40 x 52 / 12 = 173.33 rounded to 174) and confirmed by filleacgil.it lapidei CCNL text referencing the same divisor.
    
    APPRENTICESHIP: under_classification, Art. 9 Apprendistato professionalizzante from 12/02/2020 CCNL organic text (lawinsider.com/it/contracts/euRWxUzbye9). Checked 2022 renewal (modified articles: 13, 14, 21, 31, 33, 35bis, 35ter, 52 — Art. 9 absent) and 2025 renewal (modified articles: 3, 4, 9bis, 13, 21, 32, 33, 35bis, 35ter, 53, 55, 66 — Art. 9 absent). Art. 9 unchanged in both renewals; 2020 text governs.
    
    LEVEL F SUPERMINIMO: FILCA-CISL table note: 'Nel livello F e compreso l'importo di euro 4,13 a titolo di superminimo.' The 4.13 EUR is already embedded in the base_salary values for level F across all tranches. No separate fixed_allowance added.
    
    ASQ LEVEL: distinct classification from AS. Quadri (ASQ) hold the same paga tabellare as AS but additionally receive the Indennita di funzione quadri (51.65 EUR/month). Source: thaler.it 'Livelli e Qualifiche' table and 'Indennita funzione quadri: 51.65 euro mensili lordi'. FILCA-CISL salary table groups AS+quadri in a single row labelled 'A S' with Supermin.individ.=51.65; lavoro-economia.it c=131 shows separate ASQ and AS totals.
    
    ARCO FUND: employer complementary pension contribution from 01/07/2026 = 1.90%, from 01/01/2028 = 2.00% (2025 renewal Art. 55). The ARCO base is: paga tabellare + contingenza + EDR + indennita funzione quadri (where applicable). Not modelled in employer_funds (TFR-based bilateral fund, not captured by the current engine schema).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/laterizi-industria-f021.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/laterizi-industria-f021.py"
```
