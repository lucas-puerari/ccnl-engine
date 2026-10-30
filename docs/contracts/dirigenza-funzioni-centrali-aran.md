# CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S025` |
| **Sector** | Pubblica Amministrazione |
| **Family** | `dirigenza-pubblica` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | ~30k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - ANMI ASSOMED SIVEMP FPM
    - CIDA FC
    - FLEPAR
    - UIL PA
    - UNADIS
    - DIRSTAT FIALP UNSA

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 13 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-10-28 |
| **Last review** | — |
| **Latest salary tranche** | 2024-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `PRIMA_FASCIA` | Dirigenti di prima fascia (dirigenti generali): ministeri, agenzie | € 4,908.30 | 2024-01-01 |
| `SECONDA_FASCIA` | Dirigenti di seconda fascia (non generali): ministeri, agenzie fiscali, INPS, INAIL | € 3,846.60 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dirigenza-funzioni-centrali-aran/position_pay_fixed_part · base_salary · impact yes · open"
    Retribuzione di posizione parte fissa: prima fascia 42.598,20€/anno (Art. 23 c.5); seconda fascia 14.515,11€/anno (Art. 26 c.5). Variabile per incarico, non modellata (SIMPLIFICATION).

    **Applies when:** `base_salary` applies.

    **Remediation:** Model the retribuzione di posizione parte fissa (Art. 23 c.5, Art. 26 c.5) as a fixed allowance per fascia over 13 months.

!!! warning "dirigenza-funzioni-centrali-aran/position_variable_and_result_pay · base_salary · impact yes · open"
    Due livelli (PRIMA_FASCIA / SECONDA_FASCIA) per lo stipendio tabellare. La retribuzione di posizione (fissa e variabile per incarico) e la retribuzione di risultato non sono modellate — out_of_scope strutturale per tutti i dirigenti PA. Il file cattura la componente stipendio tabellare che è uniforme per fascia.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Accept the parte variabile of the posizione and the retribuzione di risultato as caller-stated amounts (individual element / variable pay) and open a limitation until then.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato who did not work that whole month, an unknown worker category, or a sector INPS regime (spettacolo). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the base of an impiegato's partial month (point 11.2 letters d-f), of the sector regimes, and from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| Testo ufficiale CCNL Area Funzioni Centrali 2022-2024. Art. 23: stipendio tabellare dirigenti I fascia = 63.807,87€/anno da 1/1/2024 (prev. 60.102,87€). Art. 26: stipendio tabellare dirigenti II fascia = 50.005,77€/anno da 1/1/2024 (prev. 47.015,77€, CCNL 16/11/2023). Firma 28/10/2025 — firmatari: CISL FP, ANMI ASSOMED SIVEMP FPM, CIDA FC, FLEPAR, UIL PA, UNADIS, DIRSTAT FIALP UNSA. FP CGIL non ha firmato. | altro | 2025-10-28 | [↗](https://trasparenza.lavoro.gov.it/archiviofile/minlavoro/2025_10_28_CCNL_A_FC_2022-2024_Pubblicazione-1%20vigente.pdf) |

??? note "Coverage notes"
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    Layer 2 implemented. Part-time: the engine scales the pay by Employment.weekly_hours over full_time_weekly_hours. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in knowledge/sector/2026/pubblica-amministrazione.json. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL (review of 2026-10-30).
    
    CNEL S025 inferito dalla struttura coerente dei codici ARAN: S005=comparto FC (confermato da sessione precedente), S025=area dirigenza FC, S105=comparto FL (confermato), S205=comparto Sanità (confermato), S225=area dirigenza Sanità (confermato). Il pattern S*05/S*25 (comparto/area) è consistente per tutti i comparti verificati.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL FC 2022-2024 / CCNL 09/03/2020 Art. per l'orario settimanale della dirigenza PA). L'orario dei dirigenti non è soggetto a controllo puntuale, ma 38h è il riferimento contrattuale standard per la PA.
    
    Valori mensili arrotondati: prima fascia 60.102,87/13 = 4.623,299 → 4.623,30€; dopo rinnovo 63.807,87/13 = 4.908,298 → 4.908,30€. Seconda fascia: 47.015,77/13 = 3.616,598 → 3.616,60€; dopo rinnovo 50.005,77/13 = 3.846,598 → 3.846,60€. Tutti derivano aritmeticamente dai valori annui certificati nel testo CCNL.
    
    Straordinario (Art. 71 CCNL FC) applicabile solo ai dirigenti privi di incarico di struttura complessa. I dirigenti con incarico complesso non percepiscono OT (assorbito da retribuzione di risultato). Questo è un limite strutturale: il motore non distingue dirigenti con/senza incarico complesso; si assume il caso base (privi di incarico).
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — Art. 19 CCNL FC 09/03/2020. Modellato con SicknessTier; il tasso si applica giorno per giorno secondo il mese di malattia (mesi di 30 giorni), anche nei periodi di paga a cavallo di soglia (review of 2026-10-30).
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    Stipendio tabellare da testo ufficiale CCNL 28/10/2025 (Ministero del Lavoro, Art. 23 e Art. 26).
    
    Prima fascia — Art. 23 comma 1: previgente 60.102,87€/anno (CCNL 16/11/2023); incremento +285€/mese × 13 = +3.705€/anno; nuovo valore 63.807,87€/anno = 4.908,30€/mese per 13 mensilità.
    
    Seconda fascia — Art. 26 comma 1: previgente 47.015,77€/anno (CCNL 16/11/2023); incremento +230€/mese × 13 = +2.990€/anno; nuovo valore 50.005,77€/anno = 3.846,60€/mese per 13 mensilità.
    
    Firma 28/10/2025. FP CGIL non ha firmato (indicato come 'non firmato' nel frontespizio). CGIL confederale non ha firmato.
    

## Raw data

The contract file this page is generated from: [`agreement/dirigenza-funzioni-centrali-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dirigenza-funzioni-centrali-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dirigenza-funzioni-centrali-aran/example.py"
```
