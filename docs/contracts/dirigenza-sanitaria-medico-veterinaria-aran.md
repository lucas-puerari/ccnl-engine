# CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)

| | |
|---|---|
| **CNEL code** | `S225` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-27 |
| **Workers (est.)** | ~100k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
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
| **Limits of this contract** | base_salary |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-02-27 |
| **Last verified** | — |
| **Latest salary tranche** | 2024-01-01 |

### Semplificazioni note

5 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

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

    **Remediation:** Resolved: sick days are classified one by one (ccnl_engine.payroll.domain.sick_days); tested with an episode crossing the threshold of a tier within one month.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

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

### Without monetary impact

!!! note ""
    Hourly divisor 165 = 38h/settimana × 52/12, arrotondato. Art. 27 CCNL 23.1.2024 (Orario di lavoro dei dirigenti) non modificato dal CCNL 27.02.2026. Il divisore 165 è un'approssimazione — i dirigenti SSN non hanno un orario fisso misurabile.

!!! note ""
    Questo file modella solo la componente medico-veterinaria del CCNL Area Sanità 27.02.2026. Il medesimo CCNL copre anche altri dirigenti sanitari (psicologi, farmacisti, biologi, fisici, chimici), modellati in 'dirigenza-sanitaria-area-sanita-aran.json'. Entrambi i file condividono codice CNEL S225.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/2026.02.27-CCNL-Area-sanita-2022-2024-3.pdf) |
| — | — | 2026-02-28 | [↗](https://openssn.marcopingitore.it/ccnl-dirigenza-sanitaria-2022-2024/2026/02/28/9222/) |
| — | — | — | [↗](https://ilccnl.it/ccnl/dirigenti---dirigenza-medica-e-veterinaria/dirigenti---sanita-medici-e-veterinari-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione (Art. 14): obbligatoria ma variabile per tipo incarico (UOC, UOSD, professionale, ecc.). Non modellata — parte fissa per incarico assegnato in sede aziendale; out_of_scope per il motore.
    
    Indennità per incarico di direzione di struttura complessa (Art. 16): 11.157€/anno per 13 mensilità. Non modellata come fixed_allowance — assegnata solo ai direttori di SC, non a tutti i dirigenti.
    
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

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-sanitaria-medico-veterinaria-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-sanitaria-medico-veterinaria-aran.py"
```
