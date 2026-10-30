# CCNL Impiegati e Tecnici Agricoli — Confagricoltura/CIA/Coldiretti

| | |
|---|---|
| **CNEL code** | `A021` |
| **Sector** | agricoltura |
| **Family** | `agricoltura` |
| **Tax sector** | `agricoltura` |
| **Last renewal** | 2024-06-18 |
| **Workers (est.)** | ~80k |
| **Ruleset version** | `2026.2` |
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

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, inps_employer |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 7 verified / 8 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-06-18 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2024-07-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi nazionali di stipendio mensile conglobato of the seven categories against the signed CCNL of 18 June 2024. | confirmed | Art. 31, Tab. 1 (PDF p. 35, signed scan with text layer, read on the page image): the minimi nazionali di stipendio mensile conglobato from 01/07/2024 for Q and categories 1-6 match the 7 values of the file (file 1Q = Q, 1-6 = 1°-6°); they move to verified. Q is printed as 1.788,38 without the indennità di funzione, which Art. 18 lett. b (p. 24, 'una indennità mensile pari a 100 euro, da corrispondersi per 14 mensilità') grants on top, as the file models it.<br>Art. 31 (p. 34) applies the 5% from 1/04/2024 and 1.9% from 1/01/2025 to the stipendi contrattuali of the territorial contracts, not to the national minimi; Tab. 1 has a single date, 01/07/2024 (for territorial contracts renewed under the CCNL 7/07/2021 the minimi apply from the date of their next renewal and no later than 1/01/2027, p. 35). The coverage note that calls the 2025 tranche of the national table missing is wrong: there is no 2025 national minimo, and the open-ended period is correct.<br>The national minimo is conglobated (minimo base + contingenza + EDR, footnote p. 34 citing the Verbale 4.6.2008), matching the file's base_salary; territorial contracts may set higher stipendi contrattuali, and the minimo di stipendio integrativo is outside this table.<br>The ruleset names this source, published by FLAI-CGIL, a signatory: source_type contracting_party. |

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

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Pass the EBAN and Agrifondo contributions as bilateral fund events, or model them.

!!! warning "impiegati-tecnici-agricoli/apprentice_inps_rates_unsourced · inps_employer · impact unknown · open"
    APPRENTICE INPS RATES: the apprentice rates of the sector (agricoltura) apply the 10% of L. 296/2006 art. 1 c. 773 plus the 1.61% NASpI, but no source found settles the disoccupazione and CISOA contributions of agricultural apprentices (INPS circ. 43/2026 gives no apprentice rates). The contributions of an apprentice may differ.

    **Applies when:** `inps_employer` applies; contract type in apprentice.

    **Remediation:** Source the apprentice rates of agricoltura (an INPS circular or an association table of 2026), mark the apprentice block of contribution/2026/agricoltura.json derived, then remove this note.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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

!!! warning "inps_minimum_base_exempt_category · inps_employer · impact unknown · open"
    D.L. 463/1983 art. 7 c. 5 keeps the operai agricoli out of the 9.50% minimum daily base, and the run applies no minimum to them. Tabella A of INPS circ. 6/2026 still lists 51.70 for the operai agricoli, 'non soggetto all'adeguamento' of art. 7 c. 1; no source found says whether it is a floor of their contribution base. A base below it may understate the contributions.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Source the role of the 51.70 of the operai agricoli (INPS circ. 43/2026 on the agricultural contributions, or the minimum daily wages of art. 1 L. 389/1989), then apply it as their minimum or record that none applies.

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CNEL code A021, agreement date 18/06/2024, effective 01/07/2024. Contract covers impiegati, tecnici and quadri in agricultural sector. Expiry 31/12/2027. | altro | 2024-06-18 | [↗](https://www.contratticcnl.it/ccnl/a021/) |
| Salary levels: 1Q=1888.38 (base 1788.38 + IND_FUN 100.00), 1=1686.76, 2=1541.41, 3=1417.89, 4=1335.93, 5=1278.60, 6=1217.23. Hourly divisor 169. Daily divisor 26. Additional months 14 (tredicesima + quattordicesima). Seniority: biennale (24 months), 12 scatti, per-level amounts confirmed. Level 1Q listed as 1888.38 'with function allowance'; confirmed base 1788.38 + IND_FUN 100.00. | tabella_retributiva | 2024-06-18 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=3) |

??? note "Coverage notes"
    SALARY MODEL: conglobated retribuzione tabellare minima (levels 1-6). Single base_salary per level with no separate contingenza or EDR columns in the lavoro-economia.it table (consistent with A011 agricultural model). Level 1Q additionally carries an indennità di funzione of 100.00 EUR/month, additive to the base tabellare (source: lavoro-economia.it/ccnl/ccnl.aspx?c=3 showing 1Q total=1888.38 'with function allowance', decomposed as base 1788.38 + IND_FUN 100.00).
    
    RENEWAL: CCNL signed 18/06/2024 (quadriennio 2024-2027). One salary tranche modelled, effective 01/07/2024; the +1.9% tranche of 01/01/2025 is not modelled (tranche_2025_01_missing) (review of 2026-10-30)
    
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

The contract file this page is generated from: [`agreement/impiegati-tecnici-agricoli.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/impiegati-tecnici-agricoli.json).

## Usage example

```python
--8<-- "docs/examples/agreement/impiegati-tecnici-agricoli/example.py"
```
