# CCNL Impianti e Attività Sportive Profit e No-profit

| | |
|---|---|
| **CNEL code** | `H077` |
| **Sector** | impianti sportivi, palestre e attività sportive |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-01-12 |
| **Workers (est.)** | 35533 |
| **Ruleset version** | `2024.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CUSI
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
| **Limits of this contract** | base_salary, overtime, sickness |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-01-12 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-07-01 |

### Semplificazioni note

8 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,083.49 | 2026-07-01 |
| `I` | Primo livello | € 1,989.04 | 2026-07-01 |
| `II` | Secondo livello | € 1,807.04 | 2026-07-01 |
| `III` | Terzo livello | € 1,636.42 | 2026-07-01 |
| `IV` | Quarto livello | € 1,506.82 | 2026-07-01 |
| `V` | Quinto livello | € 1,413.42 | 2026-07-01 |
| `VI` | Sesto livello | € 1,336.82 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**apprendistato_II_III_IV_36mesi** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`  
under-level: `1`

**apprendistato_V_36mesi_semplificato** (type: `under_classification`)  
Destination levels: `V`  
under-level: `1`

**apprendistato_VI_24mesi_semplificato** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "impianti-sportivi-sport/pre_2015_superminimo_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Seniority. Il CCNL 2024 non contiene disposizioni su scatti di anzianita (parola 'scatti' assente dall'intero PDF). Regime transitorio: i lavoratori in forza al 22/12/2015 conservano un superminimo personale decrescente fino al 31/10/2029 (Art. 116 norma transitoria). Non modellato: dimensione hire-date non disponibile. Gli importi kitech (EUR 21.69-28.92) si riferiscono agli scatti ante-2015. Modellato: maximum_count=0.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the decreasing personal superminimo of Art. 116 behind a hire-date fact.

!!! warning "impianti-sportivi-sport/level_v_first_semester_overpaid · base_salary · impact yes · open"
    SIMPLIFICATION: Apprendistato livello V (Art. 30). Il livello V ha ordine 2 e il livello a ordine 0 non esiste; il primo semestre a 2 livelli sotto non e applicabile. SEMPLIFICAZIONE: primo semestre a 1 livello sotto (VI). L'apprendista percepisce piu del previsto contrattualmente nella prima meta. L'intera durata (36 mesi) e al livello VI.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in V.

    **Remediation:** Pay the first semester of the level V track at the contractual level once the classification allows it.

!!! warning "impianti-sportivi-sport/level_vi_whole_track_at_destination · base_salary · impact yes · open"
    SIMPLIFICATION: Apprendistato livello VI (Art. 30 + Art. 37). Art. 30 prevedeva il primo semestre al VII livello, che il rinnovo 2024 ha eliminato. SEMPLIFICAZIONE: l'intera durata apprendistato VI (24 mesi) e al livello di destinazione VI (levels_below=0). L'apprendista percepisce piu del previsto contrattualmente.

    **Applies when:** `base_salary` applies; contract type in apprentice; level in VI.

    **Remediation:** Confirm the level VI track after the 2024 renewal and model its first semester.

!!! warning "impianti-sportivi-sport/overtime_over_48h_band_missing · overtime · impact yes · open"
    SIMPLIFICATION: Straordinario diurno. Art. 83 prevede 15% per ore 41-48 e 20% per ore oltre 48 settimanali. Modellato solo il 15% (caso dominante). Banda 20% (oltre 48h) non modellata.

    **Applies when:** `overtime` applies.

    **Remediation:** Model the 20% band over 48 weekly hours, or pass the multiplier on the overtime event.

!!! warning "impianti-sportivi-sport/integration_75_days_4_20 · sickness · impact yes · open"
    SIMPLIFICATION: Integrazione malattia (Art. 103). Struttura contrattuale: giorni 1-3 a carico del datore (100%), giorni 4-20 integrazione al 75%, giorni 21+ integrazione al 100%. La granularita 'giorno' non e modellabile nel schema SicknessRules (usa mesi). Modellato: carenza_integration_rate=1.0, full_pay_integration_rate=1.0 (allineato alla fase finale). La finestra al 75% (gg. 4-20) non e modellata; il motore sovrastima la retribuzione per eventi di malattia breve.

    **Applies when:** `sickness` applies.

    **Remediation:** Express the day-based integration of Art. 103 (75% on days 4-20, 100% from day 21) in the sickness rule, then resolve this limitation.

!!! warning "impianti-sportivi-sport/night_overtime_cumulation · overtime · impact unknown · open"
    SIMPLIFICATION: Cumulo notturno. Art. 83 ult. comma: 'Le varie maggiorazioni previste dal presente articolo non sono cumulabili tra loro' — esclude la cumulabilita tra i soli supplementi interni all'Art. 83 (15%/20%/30%/50%). Il supplemento del 10% di Art. 84 e un articolo separato e non e esplicitamente escluso dalla cumulabilita. Il motore applica entrambi alle ore notturne straordinarie (60% totale). Se le parti intendono il 50% inclusivo del 10%, il motore sovrastima di 10 punti sulle ore OT notturne.

    **Applies when:** `overtime` applies.

    **Remediation:** Confirm with the parties whether the 50% night overtime band includes the 10% night supplement of Art. 84.

!!! warning "impianti-sportivi-sport/pre_2015_fourteenth_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Quattordicesima transitoria. Art. 116 norma transitoria: i lavoratori in forza al 22/12/2015 ricevono un superminimo personale assorbibile equivalente alla quattordicesima folded-in (rata mensile decrescente fino al 31/10/2029). Per la popolazione corrente (post-2015): 13 mensilita. La quattordicesima residuale per i lavoratori ante-2015 non e modellata.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the residual quattordicesima of Art. 116 behind a hire-date fact.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Divisore orario. Art. 120 prevede 173 (40h) e 195 (45h). Solo il divisore 173 e modellato. Le assunzioni a 45h settimanali non sono gestite.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-01-12 | [↗](https://www.sindacato.it/il-ccnl-impianti-sportivi-o-lavoratori-dello-sport/) |
| — | — | 2024-01-12 | [↗](https://www.cusi.it/wp-content/uploads/2024/02/CCNL-Sport-2024-2026.pdf) |
| — | — | 2024-01-12 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=13) |

??? note "Coverage notes"
    CCNL H077 Impianti Sportivi e Palestre, rinnovo 12/01/2024 (vigenza 01/01/2024-31/12/2026). 7 livelli: Q (quadro) + livelli I-VI. Art. 121 CCNL dice 'sei livelli' perche Q e categoria quadro sopra la scala ordinaria. Conglobato confermato da ilccnl.it (contingenza=0.00, terzo elemento=0.00 su 4 livelli). Divisore orario 173 da Art. 120 (40h settimanali).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/impianti-sportivi-sport.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/impianti-sportivi-sport.py"
```
