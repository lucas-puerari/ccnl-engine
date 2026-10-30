# CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)

| | |
|---|---|
| **CNEL code** | `S225` |
| **Sector** | Pubblica Amministrazione |
| **Family** | `dirigenza-pubblica` |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-27 |
| **Workers (est.)** | ~100k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - ANAAO ASSOMED
    - FEDERAZIONE CIMO-FESMED
    - AAROI EMAC
    - FASSID
    - FVM
    - UIL FPL
    - FEDERAZIONE CISL MEDICI

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, workplace_injury |

7 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 8 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-02-27 |
| **Last review** | — |
| **Latest salary tranche** | 2024-01-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DIRIGENTE` | Dirigente medico o veterinario SSN (rapporto esclusivo o non esclusivo) | € 3,846.60 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dirigenza-sanitaria-medico-veterinaria-aran/position_pay_missing · base_salary · impact yes · open"
    Retribuzione di posizione (Art. 14): obbligatoria ma variabile per tipo incarico (UOC, UOSD, professionale, ecc.). Non modellata — parte fissa per incarico assegnato in sede aziendale; out_of_scope per il motore.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Take the retribuzione di posizione (Art. 14) and its Art. 17 guaranteed minimum (note 7) as a worker fact by type of incarico.

!!! warning "dirigenza-sanitaria-medico-veterinaria-aran/complex_structure_allowance · base_salary · impact yes · open"
    Indennità per incarico di direzione di struttura complessa (Art. 16): 11.157€/anno per 13 mensilità. Non modellata come fixed_allowance — assegnata solo ai direttori di SC, non a tutti i dirigenti.

    **Applies when:** `base_salary` applies.

    **Remediation:** Add the 11.157 EUR/year (13 months) allowance of Art. 16 restricted to a role such as 'direttore_sc' (Allowance.role).

!!! warning "dirigenza-sanitaria-medico-veterinaria-aran/approximate_hourly_divisor · workplace_injury · impact unknown · open"
    Hourly divisor 165 = 38h/settimana × 52/12, arrotondato. Art. 27 CCNL 23.1.2024 (Orario di lavoro dei dirigenti) non modificato dal CCNL 27.02.2026. Il divisore 165 è un'approssimazione — i dirigenti SSN non hanno un orario fisso misurabile.

    **Applies when:** `workplace_injury` applies.

    **Remediation:** Source the divisor of Art. 27 (or the INAIL base of the SSN dirigenti) and replace 165, or mark the divisor as not applicable so the INAIL daily base is not derived from it.

!!! warning "dirigenza-sanitaria-medico-veterinaria-aran/specificita_pre_2025_estimated · base_salary · impact unknown · open"
    Pre-31/12/2024 specificità medico-veterinaria (704,88€/mese) calcolata per differenza dal valore a regime 728,15€ sottraendo il presunto incremento 23,27€/mese × 13 = 302,51€/anno. L'importo pre-2024 è una stima basata sulle comunicazioni GOAL-plan (fonte secondaria); il valore esatto del CCNL 23.1.2024 Art. 65 non è verificato.

    **Applies when:** `base_salary` applies; before 2024-12-31.

    **Remediation:** Source the exact Art. 65 amount of the CCNL 23.1.2024 for periods before 31/12/2024.

!!! warning "dirigenza-sanitaria-medico-veterinaria-aran/tabellare_pre_2024_estimated · base_salary · impact unknown · open"
    Pre-2024 tabellare 3.616,60€/mese = 47.015,77€/anno ricavato sottraendo l'incremento di 230€/mese (× 13) dal valore 2024. Il valore del CCNL 19.12.2019 (base periodo 1) è stimato in assenza di consultazione del testo del previgente contratto.

    **Applies when:** `base_salary` applies; before 2024-01-01.

    **Remediation:** Source the tabellare of the CCNL 19.12.2019 from the previgente contract text.

!!! note "dirigenza-sanitaria-medico-veterinaria-aran/single_rate_across_tier_threshold · sickness · impact yes · resolved"
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13+ modellati con SicknessTier. Il motore classifica ogni giorno di malattia con il mese dell'episodio in cui cade, quindi un periodo di paga a cavallo di una soglia mensile applica a ciascun giorno il proprio tasso. Comporto max 18 mesi = 540 gg.

    **Applies when:** `sickness` applies.

    **Remediation:** Resolved: sick days are classified one by one (ccnl_engine.sickness.day.rules); tested with an episode crossing the threshold of a tier within one month.

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

### Without monetary impact

!!! note ""
    Questo file modella solo la componente medico-veterinaria del CCNL Area Sanità 27.02.2026. Il medesimo CCNL copre anche altri dirigenti sanitari (psicologi, farmacisti, biologi, fisici, chimici), modellati in 'dirigenza-sanitaria-area-sanita-aran.json'. Entrambi i file condividono codice CNEL S225.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Area Sanità 2022-2024 (27.02.2026). Art. 11 (incrementi stipendio tabellare: +230€/mese da 1/1/2024, valore a regime 50.005,77€/anno per 13 mensilità). Art. 15 (indennità specificità medico-veterinaria rideterminata in 9.466,00€/anno per 13 mensilità dal 31/12/2024). Art. 14 (retribuzione di posizione). Campo di applicazione: dirigenti medici, sanitari, veterinari e professioni sanitarie SSN. | altro | 2026-02-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/2026.02.27-CCNL-Area-sanita-2022-2024-3.pdf) |
| Riepilogo economico del CCNL Area Sanità 2022-2024. Conferma importi tabellari e indennità. | altro | 2026-02-28 | [↗](https://openssn.marcopingitore.it/ccnl-dirigenza-sanitaria-2022-2024/2026/02/28/9222/) |
| SIMPLIFICATION: codice CNEL S225 da fonte secondaria (ilccnl.it). Non riportato nel testo ufficiale ARAN. | altro | — | [↗](https://ilccnl.it/ccnl/dirigenti---dirigenza-medica-e-veterinaria/dirigenti---sanita-medici-e-veterinari-dal-010195) |

??? note "Coverage notes"
    Clausola di garanzia retribuzione di posizione (Art. 17): minima garantita per anzianità. Non modellata — variabile per anzianità e valutazione.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità per i dirigenti. Cadence=1 e maximum_count=0 riflettono l'assenza di progression automatica.
    
    CNEL S225 confermato da contratticcnl.it (/ccnl/s225/: "CCNL dell'Area Sanità (dirigenti)", deposito 19/12/2019, ARAN). Verificato 2026-09-09.
    
    Rinnovo 2025-2027: ARAN ha convocato primo tavolo il 22/07/2026 presentando quantificazione economica con risorse ordinarie pari al 5,40%. Trattativa in corso al 2026-09-09; nessun accordo firmato. Fonte: consulentidellavoro.vi.it, vet33.it.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    Stipendio tabellare da Art. 11 CCNL 27.02.2026: incremento +230€/mese da 1/1/2024, valore a regime 50.005,77€/anno per 13 mensilità = 3.846,60€/mese. Art. 11 riferisce Art. 61 comma 3 CCNL 23.1.2024 come base preesistente.
    
    Indennità specificità medico-veterinaria dal 31/12/2024: Art. 15 comma 1 CCNL 27.02.2026, rideterminata in 9.466,00€/anno per 13 mensilità = 728,15€/mese. Applicazione: dirigenti medici e veterinari.
    
    Tredicesima mensilità: Art. 11 comma 1 ('per 13 mensilità'), confermato per tabellare e specificità.
    
    Campo di applicazione: Art. 1 CCNL 27.02.2026 — dirigenti medici, sanitari, veterinari e professioni sanitarie SSN. Questo file modella la sola componente medico-veterinaria.
    
    Signatari: frontespizio CCNL 27.02.2026. CGIL FP non ha firmato.
    

## Raw data

The contract file this page is generated from: [`agreement/dirigenza-sanitaria-medico-veterinaria-aran.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/dirigenza-sanitaria-medico-veterinaria-aran.json).

## Usage example

```python
--8<-- "docs/examples/agreement/dirigenza-sanitaria-medico-veterinaria-aran/example.py"
```
