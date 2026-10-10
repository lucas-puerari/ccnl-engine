# CCNL Comparto Sanità 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S205` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-10-27 |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - UIL FPL
    - FIALS
    - NURSIND
    - NURSING UP

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
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-10-27 |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2024-01-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATA_QUALIFICAZIONE` | Elevata qualificazione (ex area DS dirigenza) | € 2,886.21 | 2024-01-01 |
| `PROFESSIONISTI` | Professionisti della salute e funzionari (ex area D/DS) | € 2,076.58 | 2024-01-01 |
| `ASSISTENTI` | Assistenti (ex area C/C1) | € 1,913.48 | 2024-01-01 |
| `OPERATORI` | Operatori (ex area B/B1) | € 1,795.45 | 2024-01-01 |
| `SUPPORTO` | Personale di supporto (ex area A/A1) | € 1,701.59 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "sanita-aran/pre_2024_back_calculated_tables · base_salary · impact unknown · open"
    PRE-2024 BACK-CALCULATED. Nov 2022 values derived by subtracting Tabella 1a increments from Jan 2024 amounts (support −115, operatori −120, assistenti −127, collaboratori −127, funzionari −129, elevata qualificazione −185 approx). Primary CCNL 2019-2021 text not verified directly. 2022-2023 anticipation payments not modelled as intermediate periods.

    **Applies when:** `base_salary` applies; before 2024-01-01.

    **Remediation:** Source the 2019-2021 salary tables from the signed CCNL text instead of back-calculating them.

!!! warning "sanita-aran/renewal_2025_2027_not_modelled · base_salary · impact unknown · open"
    2025-2027 RENEWAL NOT YET MODELLED. An ipotesi di CCNL 2025-2027 was signed by ARAN on 29 July 2026 with retroactive effect from 1 January 2025. Increases (monthly, 13 mensilità) from Jan 2024 base: support +41.40 (Jan 2025)/+82.80 (Jan 2026)/+106.70 (Jan 2027); operatori +43.70/+87.40/+112.60; assistenti +46.60/+93.20/+120.00; funzionari +50.50/+101.10/+130.20; elevata qualificazione +70.20/+140.50/+181.00. Not yet modelled — ipotesi pending comitato di settore, Governo, and Corte dei conti certification.

    **Applies when:** `base_salary` applies; from 2025-01-01.

    **Remediation:** Model the 2025-2027 increases once the ipotesi is certified and signed.

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
    Agreement date 2025-10-27 (firma definitiva) per ARAN press release. The PDF used is the Ipotesi from 14.01.2025; salary tables are identical to the final signed version.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-01-14 | [↗](https://www.quotidianosanita.it/allegati/allegato1736872056.pdf) |
| — | — | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=400) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Seniority via DEP (Differenziali Economici di Professionalità) per Art. 60 Fondo incarichi: selective procedure, not automatic — maximum_count=0.
    
    Indennità di specificità infermieristica (Art. 62, Tabella 3) not modelled as fixed_allowance — applies only to specific nursing profiles (infermieri, ostetriche), not universally to all area members.
    
    CNEL code S205 confirmed via multiple secondary sources: lavoro-economia.it lists 'CCNL Comparto Sanità [Cnel: S205]', kitech.it and ilccnl.it concur. Not stated in the official ipotesi PDF text; CNEL archive not separately verified.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    Salary tables from Ipotesi CCNL Comparto Sanità 2022-2024 (ARAN, 14.01.2025, definitively signed October 2025). Art. 58 comma 1 (increments from 1.1.2024 per Tabella 1a), Art. 58 comma 2 (annual amounts from Tabella 2a). Monthly values = Tabella 2a / 12.
    
    Tranche 1 (2022-11-02) values back-calculated from CCNL 2.11.2022 base by subtracting Tabella 1a increments. 2022-2023 anticipation payments (Art. 47-bis D.Lgs. 165/2001) not modelled as separate periods (SIMPLIFICATION).
    
    Hourly divisor 156 from Art. 26 comma 1 (36h/week standard working time for comparto Sanità).
    
    13 mensilità from Art. 57 (Tredicesima mensilità) of this CCNL.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/sanita-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sanita-aran.py"
```
