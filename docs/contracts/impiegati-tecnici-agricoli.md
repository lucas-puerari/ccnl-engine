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
| **Readiness** | 🧪 Exploratory |

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
| **Limits of this contract** | base_salary, bilateral_funds |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-06-18 |
| **Last verified** | — |
| **Latest salary tranche** | 2024-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1Q` | Livello 1Q — Quadri (dirigenti intermedi con autonomia gestionale) | € 1,788.38 | 2024-07-01 |
| `1` | Livello 1 — Funzionari e tecnici direttivi con responsabilita di settore | € 1,686.76 | 2024-07-01 |
| `2` | Livello 2 — Tecnici specializzati, impiegati di concetto superiore | € 1,541.41 | 2024-07-01 |
| `3` | Livello 3 — Tecnici e impiegati con funzioni di concetto di grado superiore | € 1,417.89 | 2024-07-01 |
| `4` | Livello 4 — Impiegati con mansioni di concetto o amministrative qualificate | € 1,335.93 | 2024-07-01 |
| `5` | Livello 5 — Impiegati d'ordine con compiti esecutivi | € 1,278.60 | 2024-07-01 |
| `6` | Livello 6 — Impiegati d'ordine di prima nomina, manovalanza di fatica | € 1,217.23 | 2024-07-01 |

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

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "impiegati-tecnici-agricoli/tranche_2025_01_missing · base_salary · impact yes · open"
    TWO TRANCHES NOT FULLY MODELLED. The CCNL A021 (signed 18/06/2024) establishes two tranches: +5% retroactive to 01/04/2024 and +1,9% from 01/01/2025 (source: dottrinalavoro.it; FLAI PDF; ilccnl.it). The file models only the first tranche (valid_from 2024-07-01, which likely reflects the 01/04/2024 increase with the official CNEL deposit date). The 01/01/2025 tranche is missing: approximate values are L1~1718.81 (1686.76×1.019) but exact official amounts not yet retrieved. Update valid_from to 2024-04-01 and add 2025-01-01 periods when confirmed from official source.

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Add the 01/01/2025 tranche (+1.9%) from the official table and move the first tranche to 2024-04-01.

!!! warning "impiegati-tecnici-agricoli/eban_agrifondo_missing · bilateral_funds · impact yes · open"
    BILATERAL FUNDS. EBAN (Ente Bilaterale Agricolo Nazionale) and Agrifondo (supplementary pension) bilateral contributions are not modelled.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the EBAN and Agrifondo contributions as bilateral fund events, or model them.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

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
    
    INPS CONTRIBUTION BASE. The retribuzione convenzionale regime (INPS annual decree) applies to operai agricoli OTD/OTI (braccianti), NOT to impiegati agricoli. For impiegati OTI, contributions are computed on actual contractual salary pursuant to DL 338/1989 Art. 1 minimale (contribution base cannot fall below CCNL minimum). The engine applies rates to actual gross salary, which is correct for impiegati. Source: INPS Circ. 43/2026 covers operai only; standard regime applies to impiegati. (Confirmed by confagricolturapadova.it/wp-content/uploads/2020/02/Contributi_minimi_2020.pdf, laprevidenza.it.)
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/impiegati-tecnici-agricoli.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/impiegati-tecnici-agricoli.py"
```
