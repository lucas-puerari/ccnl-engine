# CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)

| | |
|---|---|
| **CNEL code** | `S225` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-27 |
| **Workers (est.)** | ~37k |
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

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `DIRIGENTE` | Dirigente sanitario SSN (psicologo, farmacista, biologo, fisico, chimico, dirigente professioni sanitarie) | € 3,846.60 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "dirigenza-sanitaria-area-sanita-aran/specificita_pre_2025_estimated · base_salary · impact unknown · open"
    Pre-31/12/2024 specificità sanitaria (104,34€/mese) calcolata per differenza: 124,19 - 17,90 (incremento stimato dalla fonte secondaria openssn, GOAL-plan) = approssimazione; il valore esatto del CCNL 23.1.2024 Art. 66 non è verificato.

    **Applies when:** `base_salary` applies; before 2024-12-31.

    **Remediation:** Source the exact Art. 66 amount of the CCNL 23.1.2024 for periods before 31/12/2024.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/2026.02.27-CCNL-Area-sanita-2022-2024-3.pdf) |
| — | — | 2026-02-28 | [↗](https://openssn.marcopingitore.it/ccnl-dirigenza-sanitaria-2022-2024/2026/02/28/9222/) |
| — | — | — | [↗](https://ilccnl.it/ccnl/dirigenti---dirigenza-medica-e-veterinaria/dirigenti---sanita-medici-e-veterinari-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione (Art. 14): obbligatoria ma variabile per tipo incarico. Non modellata — out_of_scope.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità. maximum_count=0.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL Area Sanità 23.01.2024 Art. 27 conferma orario settimanale 38h per la dirigenza sanitaria SSN). Il valore 165 è il divisore contrattuale standard.
    
    Pre-2024 tabellare 3.616,60€/mese = back-calculation dal valore 2024 (3.846,60) sottraendo +230€ (Art. 11 CCNL 27.02.2026). L'incremento +230€ è riportato esplicitamente nel testo ufficiale ARAN; la back-calculation è quindi aritmeticamente esatta rispetto alla fonte primaria.
    
    CNEL S225 confermato: identico al CNEL del file gemello 'dirigenza-sanitaria-medico-veterinaria-aran.json' (stesso CCNL Area Sanità 27.02.2026). La fonte secondaria ilccnl.it riporta S225 consistente con la nomenclatura ARAN.
    
    Questo file e 'dirigenza-sanitaria-medico-veterinaria-aran.json' derivano dallo stesso CCNL Area Sanità 27.02.2026 (unico testo). La distinzione in due file è una scelta strutturale: le diverse indennità di specificità (Art. 15 c.1 per medici/veterinari vs Art. 15 c.3 per sanitari non medici) giustificano contratti separati nel motore.
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — Art. 38 CCNL 23.01.2024 Area Sanità. Modellato con SicknessTier; ogni giorno di malattia riceve il tasso del mese dell'episodio in cui cade, anche in un periodo di paga a cavallo di una soglia.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    Stipendio tabellare da Art. 11 CCNL 27.02.2026: incremento +230€/mese da 1/1/2024, valore a regime 50.005,77€/anno per 13 mensilità = 3.846,60€/mese.
    
    Indennità specificità sanitaria dal 31/12/2024: Art. 15 comma 3 CCNL 27.02.2026, rideterminata in 1.614,46€/anno per 13 mensilità = 124,19€/mese. Applicazione: dirigenti sanitari non medici.
    
    Tredicesima mensilità: Art. 11 comma 1 ('per 13 mensilità').
    
    Campo di applicazione: Art. 1 CCNL 27.02.2026. Questo file modella la componente non medico-veterinaria (psicologi, farmacisti, biologi, fisici, chimici, dirigenti professioni sanitarie).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-sanitaria-area-sanita-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-sanitaria-area-sanita-aran.py"
```
