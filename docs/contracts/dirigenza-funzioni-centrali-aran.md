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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

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
