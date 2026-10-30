# CCNL Agenzie di Viaggio e Turismo — Fiavet/Confcommercio

| | |
|---|---|
| **CNEL code** | `H052` |
| **Sector** | Turismo (agenzie di viaggio) |
| **Family** | `turismo` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-26 |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Fiavet (Federazione Italiana Associazioni Imprese Viaggi e Turismo)
    - Federviaggio
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority, trattamento_integrativo |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 69 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-07-26 |
| **Last review** | — |
| **Latest salary tranche** | 2027-12-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A — Top management function | € 2,495.21 | 2027-12-01 |
| `QB` | Quadro B — Management function | € 2,310.11 | 2027-12-01 |
| `1` | Level 1 — Conceptual employee with managerial functions | € 2,152.33 | 2027-12-01 |
| `2` | Level 2 — Conceptual employee | € 1,967.21 | 2027-12-01 |
| `3` | Level 3 — Qualified employee | € 1,855.32 | 2027-12-01 |
| `4` | Level 4 — Employee | € 1,750.69 | 2027-12-01 |
| `5` | Level 5 — Qualified clerical employee | € 1,641.83 | 2027-12-01 |
| `6S` | Level 6S — Super clerical employee | € 1,578.72 | 2027-12-01 |
| `6` | Level 6 — Clerical employee | € 1,556.35 | 2027-12-01 |
| `7` | Level 7 — Auxiliary staff | € 1,458.41 | 2027-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `QA` | € 40.80 |
| `QB` | € 39.25 |
| `1` | € 37.70 |
| `2` | € 36.15 |
| `3` | € 34.86 |
| `4` | € 33.05 |
| `5` | € 32.54 |
| `6S` | € 31.25 |
| `6` | € 30.99 |
| `7` | € 30.47 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `4`, `5`, `6S`, `6`, `7`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "agenzie-viaggio-fiavet/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "agenzie-viaggio-fiavet/tourism_special_supplement · trattamento_integrativo · impact yes · open"
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-20, Gazzetta Ufficiale text, https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=1&art.versione=1, page sha256 e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d): from 1 January to 30 September 2026 the workers of the esercizi di somministrazione di alimenti e bevande (L. 287/1991 art. 5) and of the 'comparto del turismo, ivi inclusi gli stabilimenti termali', with employment income of 2025 not above 40,000 EUR, receive 'un trattamento integrativo speciale, che non concorre alla formazione del reddito, pari al 15 per cento delle retribuzioni lorde corrisposte in relazione al lavoro notturno e alle prestazioni di lavoro straordinario [...] effettuate nei giorni festivi'. The employer pays it 'su richiesta del lavoratore' (c. 20), a fact the request has no field for: the engine does not pay it, so the net pay of a worker who asked for it is understated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the worker's request of c. 20 to the request, pay 15% of the night and holiday overtime pay of the run as a credit, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
    Levels QA and QB (Quadri) excluded from the apprenticeship track (apprenticeship not applicable to Quadri by law).

!!! note ""
    Layer 3 (overtime, night shifts, public holidays) out of scope. Partly superseded: work_rules now holds overtime bands (OT_DIURNO, OT_NOTTURNO, OT_FESTIVO), leave and sickness rules; only the supplements on ordinary night and holiday hours are left to the caller, who states them (review of 2026-10-30).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Base CCNL 2019 — Art. 146 (hourly divisor 172), Art. 64 (apprendistato 80/85/90%), Art. 156 (scatti di anzianita triennali) | altro | 2019-07-11 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2019//20108.pdf) |
| Rinnovo 2024 — tabelle retributive tutti i livelli e tutte le tranche 2024-2027, Art. 157 tredicesima, Art. 158 quattordicesima | altro | 2024-07-26 | [↗](https://cdcpcnelblg01sa.blob.core.windows.net/archivio/2024//20108.pdf) |

??? note "Coverage notes"
    Salary tables 2024-2027 from CCNL renewal of 26 July 2024 (CNEL PDF). Six tranches: Jun-24, Jul-24, Sep-25, Sep-26, Jun-27, Dec-27.
    
    Hourly divisor 172 from Art. 146 CCNL base 2019 (CNEL PDF doc 20108). Same basis as the Confcommercio tourism sector.
    
    14 additional monthly payments from Art. 157 (thirteenth month) and Art. 158 (fourteenth month) of the 2024 renewal.
    
    Triennial seniority increments (Art. 156 CCNL 2019): 36-month cadence, maximum 6 increments. Per-level amounts from the table attached to the 2024 renewal.
    
    Percentage-based apprenticeship from Art. 64 CCNL 2019 (OCR pages 32-33): first year 80%, second year 85%, third year 90%.
    
    CNEL code H052 confirmed from kitech.it CodiceCateg=81 (Confcommercio tourism sector, travel agencies included).
    

## Raw data

The contract file this page is generated from: [`agreement/agenzie-viaggio-fiavet.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/agenzie-viaggio-fiavet.json).

## Usage example

```python
--8<-- "docs/examples/agreement/agenzie-viaggio-fiavet/example.py"
```
