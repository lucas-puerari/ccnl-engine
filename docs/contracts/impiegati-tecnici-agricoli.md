# CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti

| | |
|---|---|
| **CNEL code** | `A021` |
| **Sector** | agricoltura |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-06-18 |
| **Workers (est.)** | ~80k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confagricoltura — Confederazione Generale dell'Agricoltura Italiana
    - CIA — Confederazione Italiana Agricoltori
    - Coldiretti — Confederazione Nazionale Coldiretti
    - FLAI-CGIL — Federazione Lavoratori Agroindustria
    - CONFEDERDIA — Confederazione Italiana dei Dirigenti e delle Alte Professionalità dell'Agricoltura
    - FAI-CISL — Federazione Agro Alimentare
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

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
| `1Q` | Livello 1Q — Quadri (dirigenti intermedi con autonomia gestionale) | € 1,788.38 | — |
| `1` | Livello 1 — Funzionari e tecnici direttivi con responsabilita di settore | € 1,686.76 | — |
| `2` | Livello 2 — Tecnici specializzati, impiegati di concetto superiore | € 1,541.41 | — |
| `3` | Livello 3 — Tecnici e impiegati con funzioni di concetto di grado superiore | € 1,417.89 | — |
| `4` | Livello 4 — Impiegati con mansioni di concetto o amministrative qualificate | € 1,335.93 | — |
| `5` | Livello 5 — Impiegati d'ordine con compiti esecutivi | € 1,278.60 | — |
| `6` | Livello 6 — Impiegati d'ordine di prima nomina, manovalanza di fatica | € 1,217.23 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 12 increments

| Level | Increment (monthly) |
|---|---:|
| `1Q` | € 33.05 |
| `1` | € 33.05 |
| `2` | € 29.44 |
| `3` | € 26.86 |
| `4` | € 24.79 |
| `5` | € 23.76 |
| `6` | € 22.21 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SINGLE TRANCHE. Only one salary tranche (01/07/2024) was found at time of extraction. If the 2024-2027 quadriennio provides additional tranches, update base_salary periods accordingly.

!!! warning ""
    INPS CONTRIBUTION BASE. INPS contributions for agricultural impiegati OTI are legally computed on the retribuzione convenzionale (set annually by INPS decree, DL 338/1989 Art. 1), not on the actual contractual salary. This engine applies rates to actual gross salary; net INPS figures are indicative only.

!!! warning ""
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and Agrifondo (supplementary pension) bilateral contributions are not modelled.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-18 | [↗](https://www.contratticcnl.it/ccnl/a021/) |
| — | — | 2024-06-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=3) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (levels 1-6). Single base_salary per level with no separate contingenza or EDR columns in the lavoro-economia.it table (consistent with A011 agricultural model). Level 1Q additionally carries an indennità di funzione of 100.00 EUR/month, additive to the base tabellare (source: lavoro-economia.it/ccnl/ccnl.aspx?c=3 showing 1Q total=1888.38 'with function allowance', decomposed as base 1788.38 + IND_FUN 100.00).
    
    RENEWAL: CCNL signed 18/06/2024 (quadriennio 2024-2027). Single salary tranche effective 01/07/2024. No subsequent tranches found at time of extraction.
    
    CNEL CODE: A021. Source: contratticcnl.it/ccnl/a021/.
    
    LEVELS: 7 levels (1Q, 1, 2, 3, 4, 5, 6). Level 1Q = Quadri (managerial cadre). Levels 1-6 = Impiegati/Tecnici from senior professional to entry-level clerk. Level 6 corresponds to first-year apprentice destination baseline.
    
    HOURLY DIVISOR: 169 hours/month. Formula: 39 h/week x 52 weeks / 12 = 169.00. Consistent with operai-agricoli-florovivaisti (A011) which also uses 169 for the 39h/week agricultural regime.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Standard for impiegati in the agricultural sector.
    
    SENIORITY: biennale (cadence 24 months), maximum 12 scatti. Per-level EUR amounts: 1Q and 1 = 33.05, 2 = 29.44, 3 = 26.86, 4 = 24.79, 5 = 23.76, 6 = 22.21. Levels 1Q and 1 share the same scatto amount.
    
    TAX SECTOR: AGRICOLTURA. INPS rates follow Gestione Previdenziale Speciale Agricola (impiegati OTI). Reuses 2026-agricoltura.json.
    
    APPRENTICESHIP. A021 specifica apprendistato professionalizzante per D.Lgs. 81/2015. Le percentuali retributive sono definite nel Piano Formativo Individuale (PFI) concordato tra le parti del singolo rapporto di lavoro e non pubblicate come tabella contrattuale. Non esiste una tabella fissa di percentuali nel testo del CCNL: l'array apprenticeship è vuoto per struttura contrattuale, non per omissione di modellazione. Analogo ai contratti pubblici dove l'apprendistato è escluso dall'ambito di applicazione. (Fonte: contratticcnl.it/ccnl/a021, leggeinchiaro.it CCNL A021.)
    
    INDENNITA DI FUNZIONE: level 1Q receives +100.00 EUR/month additive to base_salary 1788.38. Modelled as fixed_allowance code IND_FUN. Source: lavoro-economia.it/ccnl/ccnl.aspx?c=3 (total 1888.38 'with function allowance').
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/impiegati-tecnici-agricoli.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/impiegati-tecnici-agricoli.py"
```
