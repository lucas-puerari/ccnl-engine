# CCNL Materiali da Costruzione PMI — Lapidei (CONFAPI ANIEM)

| | |
|---|---|
| **CNEL code** | `F020` |
| **Sector** | Industria materiali da costruzione — Lapidei piccola industria |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-09-09 |
| **Workers (est.)** | ~5000 |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFAPI ANIEM
    - FILLEA-CGIL
    - FENEAL-UIL
    - FILCA-CISL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | inps_employer, pension_fund_contribution |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 0 derived / 70 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-09-09 |
| **Last review** | — |
| **Latest salary tranche** | 2025-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Livello 1 — Lavoratori con funzioni direttive apicali e autonomia decisionale (quadri, dirigenti) | € 2,795.46 | 2025-01-01 |
| `2` | Livello 2 — Lavoratori con responsabilità di unità organizzativa (responsabili amministrazione/produzione) | € 2,587.54 | 2025-01-01 |
| `3` | Livello 3 — Lavoratori di concetto e coordinamento (responsabili uffici, capi reparto/impianto) | € 2,202.40 | 2025-01-01 |
| `4` | Livello 4 — Lavoratori con rilevante preparazione tecnico-pratica (capi linea, tecnici specializzati) | € 2,096.25 | 2025-01-01 |
| `5` | Livello 5 — Lavoratori specializzati (caposquadra, escavatoristi, scalpellini artistici) | € 2,014.85 | 2025-01-01 |
| `6` | Livello 6 — Lavoratori qualificati con capacità tecnico-pratiche (minatori, scalpellini, gruisti) | € 1,925.43 | 2025-01-01 |
| `7` | Livello 7 — Lavoratori con normali capacità (cavatori, operai di cantiere, addetti linee produzione) | € 1,813.41 | 2025-01-01 |
| `8` | Livello 8 — Lavoratori addetti a mansioni semplici (pulizie, manovalanza, prima assunzione) | € 1,613.14 | 2025-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `8` | € 6.76 |
| `7` | € 7.57 |
| `6` | € 8.31 |
| `5` | € 8.99 |
| `4` | € 9.60 |
| `3` | € 10.14 |
| `2` | € 11.83 |
| `1` | € 12.76 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "materiali-costruzione-lapidei-confapi/contractual_fund_partial · pension_fund_contribution · impact unknown · open"
    The Fondapi contractual contribution (5 EUR riparametrati a month) is owed on every run that pays the month, in full. The Scheda and the circolare operativa of Fondapi state no rule for a partly employed month, a part-time worker or the extra months: a partial month or part time pays the full amount, an extra-month run none.

    **Applies when:** `pension_fund_contribution` applies; the run takes the engine code path.

    **Remediation:** Source the rule of the accordo of 10 November 2020 for a partial month and part time and model it, then remove this note.

!!! warning "materiali-costruzione-lapidei-confapi/cigo_rate_by_activity · inps_employer · impact yes · open"
    CIGO: the operai of the stone-working firms owe 3.30% ('operai delle imprese dell'industria e artigianato lapidei', D.Lgs. 148/2015 art. 13 c. 1 (Normattiva, text in force on 2026-10-14, https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2015-09-14;148~art13!vig=2026-10-14, snapshot sha256 3f7019a244e01d36ac8e7c9e25bcf058c777c8ed758418ba261d83867672c46a), lett. d); the industria table charges the 1.70% / 2.00% of lett. a-b, so the employer contributions of an operaio are understated by 1.60 or 1.30 points. Impiegati and quadri owe the 1.70% / 2.00% of lett. e-f the table already charges.

    **Applies when:** `inps_employer` applies; category in operaio.

    **Remediation:** Model the CIGO of D.Lgs. 148/2015 art. 13 c. 1 by activity (edile, lapidei) apart from the tax sector, then remove this note.

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
    SIMPLIFICATION: Apprenticeship not modelled. Art. 3 defines three periods (0-12 months 2 levels below, 12-24 months 1 level below, 24-36 months destination pay) with a special 18-month track for L6 and destination pay in period 3. The engine supports ApprenticeshipUnderClassification with levels_below periods, but L6's shorter duration and period-3 destination-pay override require per-destination customisation not yet extracted from source. Deferred pending dedicated source review.

!!! note ""
    SIMPLIFICATION: Work rules (overtime, leave, sickness) not modelled. Discipline lapidei spans multiple articles; scope deferred.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-09-09 | [↗](https://www.fenealuil.it/wp-content/uploads/2026/02/CCNL_MaterialiCostruzione_testo-completo.pdf) |

??? note "Coverage notes"
    SCOPE: Lapidei subsector only. Laterizi and Cemento subsectors have different level codes and salary structures; not modelled in this file.
    
    SALARY MODEL: split. Art. 25 Lapidei: contingenza congelata e conglobata nei minimi (Minimo = paga base + contingenza frozen). fixed_allowances: EDR 10.33 EUR (tutti i livelli) and supermin.coll 7.75 EUR (livello 8 only).
    
    SALARY HISTORY: 6 tranches from Allegato V (accordo 25.1.2024) and Art. 25 Lapidei dal 1.1.2025. Periods: 1.4.2019, 1.9.2020, 1.2.2021, 1.1.2022, 1.1.2024, 1.1.2025 (open). Source: CCNL testo completo FENEAL-UIL.
    
    HOURLY DIVISOR: 174. Art. 24 Disciplina Lapidei: 'Le quote orarie degli elementi mensilizzati della retribuzione si ottengono dividendo gli elementi stessi per 174'.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Art. 73 Disciplina Lapidei: gratifica natalizia annuale pari a una mensilita'.
    
    SENIORITY: 5 scatti biennali (cadence 24 months). Art. 26 Lapidei: importi fissi calcolati al 5% dei minimi 1980 e trasformati in cifra fissa. Amounts: L1=12.76, L2=11.83, L3=10.14, L4=9.60, L5=8.99, L6=8.31, L7=7.57, L8=6.76.
    
    SIGNATORIES: CONFAPI ANIEM + FILLEA-CGIL + FENEAL-UIL + FILCA-CISL. Testo definitivo signed 9 settembre 2025. Contract period 1.7.2022-30.6.2025.
    

## Raw data

The contract file this page is generated from: [`agreement/materiali-costruzione-lapidei-confapi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/materiali-costruzione-lapidei-confapi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/materiali-costruzione-lapidei-confapi/example.py"
```
