# CCNL Comparto Funzioni Centrali — Triennio 2022-2024

| | |
|---|---|
| **CNEL code** | `S005` |
| **Sector** | Pubblica Amministrazione — Comparto Funzioni Centrali |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-01-27 |
| **Workers (est.)** | ~250k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - CISL
    - CONFSAL UNSA
    - CONFSAL
    - FLP
    - CGS
    - CONFINTESA FP
    - CONFINTESA
    - UIL PA
    - UIL

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
| **Limits of this contract** | inps_employer |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-01-27 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-01-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `ELEVATE_PROFESSIONALITA` | Area Elevate Professionalità | € 3,107.21 | 2027-01-01 |
| `FUNZIONARI` | Area Funzionari ed Elevata Qualificazione — Funzionari | € 2,275.39 | 2027-01-01 |
| `ASSISTENTI` | Area Assistenti | € 1,873.56 | 2027-01-01 |
| `OPERATORI` | Area Operatori | € 1,780.57 | 2027-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "funzioni-centrali-aran/ctps_rates_proxy · inps_employer · impact unknown · open"
    aliquote INPS CTPS (ex-INPDAP) — dipendente 8,80%, datore 24,20% — da proxy kitech.it 2026; verificare circolare INPS annuale per valori esatti.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the CTPS rates against the annual INPS circular.

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
| — | — | 2025-01-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2025/01/CCNL_L_C_FC_2022_2024.pdf) |
| — | — | 2026-08-06 | [↗](https://cislfp.it/2026/08/06/ccnl-funzioni-centrali-2025-2027-aumenti-busta-paga/) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    apprendistato assente dal CCNL vigente (fonte primaria: indice ARAN CCNL 2022-2024, Art. 1-38 senza capitolo apprendistato) e dal CCNL Ministeri 12/6/2003 richiamato dall'Art. 38 Conferme, che esclude espressamente gli apprendisti dall'ambito di applicazione (fonte secondaria: olympus.uniurb.it); quadro normativo PA D.Lgs. 165/2001 non prevede apprendistato ex D.Lgs. 81/2015.
    
    CCNL Funzioni Centrali 2025-2027 (S005) firmato definitivamente il 2026-08-06; in vigore dal 2026-08-07. Incrementi retroattivi al 1/1/2025 e 1/1/2026 liquidati con gli stipendi di agosto/settembre 2026. Tre periodi aggiornati: 2025-01-01, 2026-01-01, 2027-01-01. Fonte: CISL FP (cislfp.it), testo ARAN definitivo non ancora pubblicato su aranagenzia.it al 2026-09-09.
    
    codice CNEL S005 confermato da tre fonti secondarie convergenti: lavoro-economia.it (intestazione pagina "CCNL Comparto Funzioni Centrali [Cnel: S005]"), blia.it (ID S005-209278), contratticcnl.it (/ccnl/s005/). Verificato 2026-09-09.
    
    retribuzione tabellare conglobata dal 1/1/2024 per 13 mensilità (Tabella 2, Art. 30 CCNL 2022-2024); tranche precedente dal 9/5/2022 derivata per sottrazione degli incrementi Tabella 1.
    
    divisore orario 156 (settimana di 36h) — Art. 29 c.3 CCNL 2022-2024 fonte primaria. Verifica: OPERATORI 1653,97/156=10,60; ASSISTENTI 1740,36/156=11,16; FUNZIONARI 2113,59/156=13,55.
    
    progressione economica non automatica — differenziali stipendiali assegnati per graduatoria (Art. 16 CCNL 2022-2024); seniority_increments.maximum_count=0.
    
    sub-settori ENAC, ANSFISA, ANSV e AGID hanno tabelle retributive proprie (Tabelle 3-6 CCNL) non modellate — out_of_scope per implementazione standard.
    
    PENSION FUND. Perseo Sirio (1% + 1% of the retribuzione utile ai fini del TFR). Enrolment is a fact: the silenzio-assenso of the hires from 2 January 2019 (accordo ARAN 16/09/2021) is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/funzioni-centrali-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/funzioni-centrali-aran.py"
```
