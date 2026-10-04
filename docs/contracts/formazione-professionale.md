# CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)

| | |
|---|---|
| **CNEL code** | `T261` |
| **Sector** | formazione professionale |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~19.8k |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNOS-FAP
    - CIOFS-FP
    - FORMA
    - CNF
    - FLC-CGIL
    - FLC-CISL (CISL Scuola)
    - UIL Scuola RUA
    - SNALS-CONFSAL
    - ANIEF

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
| **Last renewal** | — |
| **Last verified** | — |
| **Latest salary tranche** | 2025-09-01 |

### Semplificazioni note

Nessuna semplificazione documentata.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `IX` | Livello IX — dirigente o quadro con massima responsabilita gestionale | € 3,222.79 | 2025-09-01 |
| `VIII` | Livello VIII — quadro superiore, direttore di centro o responsabile senior | € 2,627.71 | 2025-09-01 |
| `VII` | Livello VII — coordinatore didattico o responsabile di progetto complesso | € 2,440.58 | 2025-09-01 |
| `VI` | Livello VI — formatore senior o responsabile di area | € 2,331.43 | 2025-09-01 |
| `V` | Livello V — formatore o tecnico con autonomia operativa | € 2,057.63 | 2025-09-01 |
| `IV` | Livello IV — impiegato di concetto o tecnico qualificato | € 1,975.16 | 2025-09-01 |
| `III` | Livello III — operatore specializzato, mansioni tecnico-pratiche | € 1,834.59 | 2025-09-01 |
| `II` | Livello II — operatore qualificato, mansioni esecutive | € 1,730.71 | 2025-09-01 |
| `I` | Livello I — personale ausiliario e addetto a mansioni generiche | € 1,635.99 | 2025-09-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 30.00 |
| `II` | € 30.00 |
| `III` | € 30.00 |
| `IV` | € 40.00 |
| `V` | € 55.00 |
| `VI` | € 60.00 |
| `VII` | € 60.00 |
| `VIII` | € 60.00 |
| `IX` | € 60.00 |

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-03-01 | [↗](https://www.cislscuola.it/download/ccnl-formazione-professionale-2024-2027/) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2024-03-01 (CNEL-registered). Original text drafted 18/12/2023. Validity 01/01/2024-31/12/2027. Biennio economico 01/01/2024-31/12/2025.
    
    CONGLOBATED MINIMUMS (Art. 25): Art. 25-A lists 'stipendio tabellare' as the sole fundamental salary component. No contingenza or EDR column. Art. 29 defines hourly rate as 'retribuzione mensile/156' — the tabellare IS the total conglobated amount. fixed_allowances=[] for all levels.
    
    SALARY TABLE 1 (Art. 20): three tranches from primary CCNL PDF (cislscuola.it, signatory union). Tranche 0: 31/12/2023 carry-over from 01/01/2024. Tranche 1: +01/06/2024. Tranche 2 (secondo biennio): +01/09/2025. Second biennium negotiations collapsed 27/05/2026 — no further increase. valid_until=null on 2025-09-01 period is correct.
    
    HOURLY DIVISOR (Art. 29 para 6): 'retribuzione mensile/156'. Art. 29 para 4 states part-time pay is 'tanti trentaseiesimi' (36ths) of full pay, confirming 36h/week. 36x52/12=156. hourly_divisor=156 verified from contract text.
    
    ADDITIONAL MONTHS (Art. 27): tredicesima only, paid by 20 December each year. additional_months=13.
    
    SENIORITY — P.E.O.I. (Art. 21, Table 2): Progressione Economica Orizzontale Individuale. 5 quadrennial increments (cadence_months=48, maximum_count=5). Monthly amounts by level from Table 2: I=30, II=30, III=30, IV=40, V=55, VI=60, VII=60, VIII=60, IX=60. All from primary PDF.
    
    APPRENTICESHIP (Art. 7): Art. 7 para 3 delegates profile and salary definitions entirely to EBiNFoP within 30 days of signing. No specific salary model (percentage or under-classification) is defined in the CCNL text. apprenticeship=[] is correct — no under-classification or percentage model is established by the contract. SIMPLIFICATION: if EBiNFoP has since issued a framework, it is not captured here.
    
    INDENNITA (Art. 25 F-G): regional-bargaining indennita minima (700/1400 EUR) and sanita integrativa (7 EUR/month 'dalla data di attivazione dell accordo nazionale specifico'). These are not level-attached fixed allowances; excluded from fixed_allowances. No evidence the national sanita agreement has been activated.
    
    OVERTIME (Art. 39): three rates — diurno +15%, notturno or festivo +30%, notturno+festivo +50%. SIMPLIFICATION: the combined notturno+festivo band (50%) requires a multi-condition match not supported by the engine overtime_bands schema; that case is omitted. Art. 41 para 3 (15% supplement for ordinary work at night or on holidays) is not modeled — engine time_supplements captures overtime only.
    
    LEAVE (Art. 43): 32 giorni lavorativi on 6-day week + 4 giorni festività soppresse. SIMPLIFICATION: stored as 26 working days on 5-day-week basis (32/1.2=26.67); festività soppresse 4 giorni are not modeled as a separate tier. Source: Art. 43 para 3-4 CCNL.
    
    SICKNESS (Art. 50 para 4): 100% for 12 months, 75% for months 13-18. SIMPLIFICATION: second tier (75%) is not captured by the single max_duration_days field; stored as max_duration_days=365 (full-pay period only). Source: Art. 50 para 4 CCNL.
    
    DAILY DIVISOR: Art. 37 specifies 156 ore/month and 5-day week but does not state a daily divisor explicitly. SIMPLIFICATION: by_26 applied as standard for terziario contracts.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/formazione-professionale.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/formazione-professionale.py"
```
