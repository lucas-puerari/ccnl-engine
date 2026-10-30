# CCNL Impianti e Attività Sportive Profit e No-profit

| | |
|---|---|
| **CNEL code** | `H077` |
| **Sector** | impianti sportivi, palestre e attività sportive |
| **Family** | `sport` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-01-12 |
| **Workers (est.)** | 35533 |
| **Ruleset version** | `2024.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CUSI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, overtime, sickness, workplace_injury |

8 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 32 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-01-12 |
| **Last review** | — |
| **Latest salary tranche** | 2026-07-01 |

## Review history

No review is recorded.

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
    SIMPLIFICATION: Seniority. Il CCNL 2024 non contiene disposizioni su scatti di anzianita (parola 'scatti' assente dall'intero PDF). Regime transitorio: i lavoratori in forza al 22/12/2015 conservano un superminimo personale decrescente fino al 31/10/2029 (Art. 116 norma transitoria). Non modellato. Gli importi kitech (EUR 21.69-28.92) si riferiscono agli scatti ante-2015. Modellato: maximum_count=0. Allowances can depend on the date in service (Allowance.in_service_on, individual) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the decreasing personal superminimo of Art. 116 as an allowance with in_service_on 2015-12-22.

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
    SIMPLIFICATION: Integrazione malattia (Art. 103). Struttura contrattuale: giorni 1-3 a carico del datore (100%), giorni 4-20 integrazione al 75%, giorni 21+ integrazione al 100%. Modellato: carenza_integration_rate=1.0, full_pay_integration_rate=1.0 (allineato alla fase finale). La finestra al 75% (gg. 4-20) non e modellata; il motore sovrastima la retribuzione per eventi di malattia breve. The sickness rules can hold day bands (sickness_rules.day_bands): the gap is in the data only (review of 2026-10-30).

    **Applies when:** `sickness` applies.

    **Remediation:** Add the day bands of Art. 103 (75% on days 4-20, 100% from day 21) to sickness_rules.day_bands, then resolve this limitation.

!!! warning "impianti-sportivi-sport/long_week_divisor_195 · workplace_injury · impact unknown · open"
    SIMPLIFICATION: Divisore orario. Art. 120 prevede 173 (40h) e 195 (45h). Solo il divisore 173 e modellato. Le assunzioni a 45h settimanali non sono gestite.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the 195 divisor of the 45-hour week (Art. 120), set hourly_divisor_weekly_hours=40, and use the divisor of the stated week in the INAIL daily base.

!!! warning "impianti-sportivi-sport/night_overtime_cumulation · overtime · impact unknown · open"
    SIMPLIFICATION: Cumulo notturno. Art. 83 ult. comma: 'Le varie maggiorazioni previste dal presente articolo non sono cumulabili tra loro' — esclude la cumulabilita tra i soli supplementi interni all'Art. 83 (15%/20%/30%/50%). Il supplemento del 10% di Art. 84 e un articolo separato e non e esplicitamente escluso dalla cumulabilita. Il motore applica entrambi alle ore notturne straordinarie (60% totale). Se le parti intendono il 50% inclusivo del 10%, il motore sovrastima di 10 punti sulle ore OT notturne.

    **Applies when:** `overtime` applies.

    **Remediation:** Confirm with the parties whether the 50% night overtime band includes the 10% night supplement of Art. 84.

!!! warning "impianti-sportivi-sport/pre_2015_fourteenth_missing · base_salary · impact yes · open"
    SIMPLIFICATION: Quattordicesima transitoria. Art. 116 norma transitoria: i lavoratori in forza al 22/12/2015 ricevono un superminimo personale assorbibile equivalente alla quattordicesima folded-in (rata mensile decrescente fino al 31/10/2029). Per la popolazione corrente (post-2015): 13 mensilita. La quattordicesima residuale per i lavoratori ante-2015 non e modellata; it may be the same element as pre_2015_superminimo_missing, which a reading of Art. 116 settles. Allowances can depend on the date in service (Allowance.in_service_on) (review of 2026-10-30).

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Read Art. 116 and model the residual quattordicesima as an allowance with in_service_on 2015-12-22, or resolve it as part of pre_2015_superminimo_missing.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato of a month not worked in full without the pay of a whole month, an unknown worker category, or a lavoratore dello spettacolo without the pay of the last daily contributions (SpettacoloSicknessBase). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Derive the base from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabella retributiva completa 4 tranche (01/01/2024, 01/07/2024, 01/07/2025, 01/07/2026). Livelli Q–VI. Retribuzione conglobata (contingenza=0, terzo elemento=0). 13 mensilità (tredicesima). Modello confermato da ilccnl.it e kitech.it. | tabella_retributiva | 2024-01-12 | [↗](https://www.sindacato.it/il-ccnl-impianti-sportivi-o-lavoratori-dello-sport/) |
| CUSI PDF 2024-2026. Art. 116: retribuzione normale conglobata (componente a). Art. 119: divisore giornaliero 26. Art. 120: divisore orario 173 (40h settimanali) o 195 (45h settimanali) — solo 173 modellato. Art. 121: tabella livelli I–VI più quadro Q. Art. 125: tredicesima mensilità. Art. 30: apprendistato sotto-inquadramento (2 livelli primo semestre, 1 livello secondo semestre). Art. 37: durate apprendistato II–VI. Art. 83: straordinario 15%/20%/30%/50%. Art. 84: notturno ordinario 10%. Art. 85: ferie 26 giorni lavorativi. Art. 102: comporto 180 giorni. Art. 103: integrazione malattia 100%/75%/100%. | altro | 2024-01-12 | [↗](https://www.cusi.it/wp-content/uploads/2024/02/CCNL-Sport-2024-2026.pdf) |
| Kitech tabella 01/07/2026: conferma IND_FUN Q = EUR 60.00 (13 mensilità). Scatto anzianità da EUR 21.69 (VI) a EUR 28.92 (Q) — transitional amounts ante-22/12/2015; no new scatti under 2024 CCNL. | tabella_retributiva | 2024-01-12 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=13) |

??? note "Coverage notes"
    CCNL H077 Impianti Sportivi e Palestre, rinnovo 12/01/2024 (vigenza 01/01/2024-31/12/2026). 7 livelli: Q (quadro) + livelli I-VI. Art. 121 CCNL dice 'sei livelli' perche Q e categoria quadro sopra la scala ordinaria. Conglobato confermato da ilccnl.it (contingenza=0.00, terzo elemento=0.00 su 4 livelli). Divisore orario 173 da Art. 120 (40h settimanali).
    

## Raw data

The contract file this page is generated from: [`agreement/impianti-sportivi-sport.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/impianti-sportivi-sport.json).

## Usage example

```python
--8<-- "docs/examples/agreement/impianti-sportivi-sport/example.py"
```
