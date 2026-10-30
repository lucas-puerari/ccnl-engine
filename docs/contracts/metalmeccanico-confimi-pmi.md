# CCNL Metalmeccanici Piccola Industria (CONFIMI IMPRESA MECCANICA)

| | |
|---|---|
| **CNEL code** | `C01A` |
| **Sector** | metalmeccanico |
| **Family** | `metalmeccanica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | ~100k |
| **Ruleset version** | `2025.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CONFIMI IMPRESA MECCANICA
    - FIM-CISL
    - UILM-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | overtime |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 44 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-28 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2028-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 38 - Tredicesima mensilità (p. 119): "Nel caso di inizio o di cessazione del rapporto di lavoro durante il corso dell'anno il lavoratore, ha diritto a tanti dodicesimi dell'ammontare della tredicesima mensilità quanti sono i mesi di anzianità di servizio presso l'azienda. La frazione di mese superiore ai 15 giorni va considerata a questi effetti come mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9Q` | Category 9Q — senior quadro (senior management), with funzione quadro allowance | € 3,272.42 | 2028-06-01 |
| `9` | Category 9 — expert specialist, senior impiegato direttivo; includes elemento retributivo | € 3,272.42 | 2028-06-01 |
| `8Q` | Category 8Q — quadro (middle management), with funzione quadro allowance | € 2,943.48 | 2028-06-01 |
| `8` | Category 8 — senior specialist or impiegato direttivo; includes elemento retributivo | € 2,943.48 | 2028-06-01 |
| `7` | Category 7 — expert specialist, university-level role or equivalent experience | € 2,706.26 | 2028-06-01 |
| `6` | Category 6 — senior specialist, team coordinator or technical reference | € 2,521.94 | 2028-06-01 |
| `5` | Category 5 — highly skilled worker, autonomous complex tasks | € 2,351.35 | 2028-06-01 |
| `4` | Category 4 — specialist worker, complex independent operations | € 2,195.29 | 2028-06-01 |
| `3` | Category 3 — skilled worker, qualified operations | € 2,103.44 | 2028-06-01 |
| `2` | Category 2 — semi-skilled worker, standard repetitive operations | € 1,896.80 | 2028-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `6` | € 32.43 |
| `7` | € 36.41 |
| `8` | € 40.95 |
| `8Q` | € 40.95 |
| `9` | € 45.96 |
| `9Q` | € 45.96 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "metalmeccanico-confimi-pmi/overtime_bands_from_confapi · overtime · impact unknown · open"
    WORK RULES: overtime bands and absence rules modelled on the standard industry framework consistent with the CONFAPI PMI metalmeccanica CCNL (C018), which shares the same legislative base. Verify specific CONFIMI provisions before applying.

    **Applies when:** `overtime` applies.

    **Remediation:** Verify the overtime bands against the CONFIMI CCNL text.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

### Without monetary impact

!!! note ""
    APPRENTICESHIP OMITTED: Art. 10 CCNL (2022-01-01 update) provides an under_classification model where the destination cat.3 requires initial classification at 90% of cat.2 salary (a hybrid percentage+under_classification mechanism not directly supported). Apprenticeship omitted from this model; affected employers should refer to the CCNL text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=445 | tabella_retributiva | 2025-10-28 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=445) |
| https://www.consulentidellavoro.ts.it/index.php/circolari-e-news/172-tabelle-stipendi-ccnl-metalmeccanica-confimi-pmi-aggiornamento-2026-2027-2028 | tabella_retributiva | 2025-10-28 | [↗](https://www.consulentidellavoro.ts.it/index.php/circolari-e-news/172-tabelle-stipendi-ccnl-metalmeccanica-confimi-pmi-aggiornamento-2026-2027-2028) |
| https://www.fim-cisl.it/2025/10/29/metalmeccanica-piccola-industria-firmato-il-rinnovo-del-ccnl-confimi/ | altro | 2025-10-28 | [↗](https://www.fim-cisl.it/2025/10/29/metalmeccanica-piccola-industria-firmato-il-rinnovo-del-ccnl-confimi/) |
| https://www.direzionelavoro.it/sites/default/files/files_pubblici/Accordo%20C01A%20CONFIMI.pdf | altro | — | [↗](https://www.direzionelavoro.it/sites/default/files/files_pubblici/Accordo%20C01A%20CONFIMI.pdf) |

??? note "Coverage notes"
    CONGLOBATED MODEL (levels 2-7): base_salary = total minimo tabellare per the CONFIMI table (paga base + contingenza + EDR all consolidated). fixed_allowances is empty for levels 2-7.
    
    ELEMENTO RETRIBUTIVO (levels 8, 9, 8Q, 9Q): per the official CNEL/CONFIMI text, categories 8 and 9 carry an 'elemento retributivo' of EUR 59.39/month fixed alongside the minimo. Modelled as a fixed_allowance with code ELEMENTO_RETRIBUTIVO.
    
    FUNZIONE QUADRO (levels 8Q, 9Q): quadri in cat.8 receive EUR 49.06/month and in cat.9 EUR 69.72/month as 'funzione quadro'. Modelled as fixed_allowance FUNZIONE_QUADRO. Amounts treated as perpetual; future tranche indexation not sourced.
    
    CATEGORY ELIMINATION: Art. of the CCNL eliminated Category 1 from 2022-01-01; workers formerly in cat.1 automatically moved to cat.2. This JSON models levels 2-9 (plus 8Q/9Q) as in force from 2026-06-01.
    
    SALARY TRANCHES: the October 2025 renewal schedules the first increase at 2026-06-01 (no tranche at signature). Three tranches modelled: 2026-06-01, 2027-06-01, 2028-06-01.
    
    HOURLY DIVISOR: 173 hours/month (40 h/week x 52/12). Confirmed by kitech.it and the official CCNL text for calculation of hourly pay.
    
    MONTHLY PAYMENTS: 13 (tredicesima only). Source: ilccnl.it and official CNEL PDF.
    
    SENIORITY: 5 biennali. Amounts from the official CNEL C01A text: cat.2=21.59, cat.3=25.05, cat.4=26.75, cat.5=29.64, cat.6=32.43, cat.7=36.41, cat.8=40.95, cat.9=45.96. Levels 8Q and 9Q use the same scatto as cat.8 and cat.9 respectively.
    
    INPS: uses 2026-industria.json. Standard industry rates.
    

## Raw data

The contract file this page is generated from: [`agreement/metalmeccanico-confimi-pmi.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/metalmeccanico-confimi-pmi.json).

## Usage example

```python
--8<-- "docs/examples/agreement/metalmeccanico-confimi-pmi/example.py"
```
