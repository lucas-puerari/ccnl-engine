# CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S325` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-08-06 |
| **Workers (est.)** | ~8k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - ANP
    - FLC CGIL
    - CISL FSUR
    - DIRIGENTI SCUOLA
    - UIL SCUOLA RUA

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
| **Limits of this contract** | — |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-08-06 |
| **Last verified** | — |
| **Latest salary tranche** | 2024-01-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `PRIMA_FASCIA` | Dirigenti di prima fascia: enti di ricerca (INFN, CNR, ecc.) e ASI | € 4,908.30 | 2024-01-01 |
| `SECONDA_FASCIA` | Dirigenti scolastici, direttori università e AFAM, dir. enti ricerca II fascia | € 3,846.59 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-08-06 | [↗](https://quifinanza.it/lavoro/ccnl-istruzione-ricerca-2022-2024-tabelle-retributive/1011686/) |
| — | — | 2024-08-07 | [↗](https://m.flcgil.it/contratti/documenti/istruzione-e-ricerca/ccnl-personale-area-dirigenza-istruzione-e-ricerca-2019-2021-del-7-agosto-2024.flc) |
| — | — | 2026-08-06 | [↗](https://www.flcgil.it/scuola/dirigenti/dirigenti-scolastici-siglato-in-via-definitiva-ccnl-area-istruzione-e-ricerca-2022-2024.flc) |

??? note "Coverage notes"
    Retribuzione di posizione parte fissa: seconda fascia 14.515,11€/anno (+1.170€/anno da 1/1/2024, era 13.345,11). Prima fascia 42.598,20€/anno. Variabile per incarico. Non modellata (SIMPLIFICATION).
    
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    CNEL S325 inferito dalla struttura coerente dei codici ARAN: S005/S025 (FC), S105/S125 (FL), S205/S225 (Sanità), S305/S325 (IR). I codici S005, S105, S205, S225, S305 sono verificati; S325 è inferito dal pattern *25=area dirigenza.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL Area IR 2022-2024 — stesso orario di riferimento delle altre aree ARAN dirigenza). Standard contrattuale PA.
    
    Period 1 valid_from=2021-01-01: corrisponde all'ultima tranche del CCNL Area IR 2019-2021 (+135€/mese da 1/1/2021), firmato retroattivamente il 7/8/2024. Valore 3.616,59€/mese (seconda fascia) confermato dalle note di fonte. Struttura storica documentata correttamente.
    
    Seconda fascia include categorie eterogenee (dirigenti scolastici, direttori università/AOU, dirigenti II fascia enti ricerca). Modellate come unico livello: il tabellare è uniforme per fascia (50.005,73€/anno dalla fonte disponibile). Scelta strutturale deliberata.
    
    Nessun straordinario: principio di onnicomprensività della retribuzione dirigenziale PA (Art. 3 D.Lgs. 165/2001). overtime_bands vuoto è corretto.
    
    Assenza non retribuita: prassi PA divisore 30 (mensile/30 per giorno di assenza). Modellato con by_30, coerente con le altre aree ARAN dirigenza.
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — CCNL Area IR 2022-2024 (stessa disciplina delle altre aree ARAN). Modellato con SicknessTier; periodi a cavallo di soglia ricevono un unico tasso (engine limitation accettabile).
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    PENSION FUND. Two funds: Fondo Scuola Espero for the dirigenti scolastici and Perseo Sirio for the dirigenti of universities and research bodies; PensionFundEnrolment.fund_code names the worker's.
    
    Tabellare previgente da CCNL Area Dirigenza Istruzione e Ricerca 2019-2021 (firmato 7/8/2024). Seconda fascia: 47.015,73€/anno = 3.616,594...€/mese → 3.616,59€. Prima fascia: 60.102,87€/anno = 4.623,298...€/mese → 4.623,30€.
    
    Incremento CCNL 2022-2024 (firmato 6/8/2026): seconda fascia +230€/mese × 13 = 50.005,73€/anno = 3.846,594...€/mese → 3.846,59€. Prima fascia +285€/mese × 13 = 63.807,87€/anno = 4.908,298...€/mese → 4.908,30€.
    
    Signatari (6/8/2026): ANP, FLC CGIL, CISL FSUR, Dirigenti Scuola, UIL Scuola RUA. ANCODIS non ha firmato (flcgil.it).
    
    Platea: ~7.550 dirigenti scolastici + ~360 direttori università/ricerca = ~7.910 totale (quifinanza.it).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-istruzione-ricerca-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-istruzione-ricerca-aran.py"
```
