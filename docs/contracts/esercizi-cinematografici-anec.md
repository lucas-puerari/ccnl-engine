# CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)

| | |
|---|---|
| **CNEL code** | `G211` |
| **Sector** | cinema |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANEC
    - FISTel CISL
    - UILCOM UIL

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
| **Limits of this contract** | inps_employer, seniority |

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
| **Latest salary tranche** | 2025-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `QA` | Quadro A — Multiplex/Megaplex (parametro 240) | € 2,103.45 | 2025-07-01 |
| `QB` | Quadro B — Multiplex/Megaplex (parametro 220) | € 1,970.12 | 2025-07-01 |
| `Q` | Quadro — Monosala/Multisala (parametro 220) | € 1,970.12 | 2025-07-01 |
| `F` | Livello F — Multiplex/Megaplex (parametro 185) | € 1,736.47 | 2025-07-01 |
| `5S` | V livello superiore — Monosala/Multisala (parametro 185) | € 1,736.47 | 2025-07-01 |
| `5` | V livello — Monosala/Multisala (parametro 176) | € 1,677.32 | 2025-07-01 |
| `E` | Livello E — Multiplex/Megaplex (parametro 165) | € 1,603.17 | 2025-07-01 |
| `4` | IV livello — Monosala/Multisala (parametro 159) | € 1,563.49 | 2025-07-01 |
| `D` | Livello D — Multiplex/Megaplex (parametro 150) | € 1,503.61 | 2025-07-01 |
| `C` | Livello C — Multiplex/Megaplex (parametro 140) | € 1,436.95 | 2025-07-01 |
| `3` | III livello — Monosala/Multisala (parametro 132) | € 1,383.48 | 2025-07-01 |
| `B` | Livello B — Multiplex/Megaplex (parametro 122) | € 1,316.62 | 2025-07-01 |
| `2` | II livello — Monosala/Multisala (parametro 112) | € 1,249.95 | 2025-07-01 |
| `A` | Livello A — Multiplex/Megaplex (parametro 100) | € 1,170.00 | 2025-07-01 |
| `1` | I livello — Monosala/Multisala (parametro 100) | € 1,170.00 | 2025-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 13.26 |
| `A` | € 13.26 |
| `2` | € 14.37 |
| `B` | € 15.38 |
| `3` | € 16.34 |
| `C` | € 17.11 |
| `D` | € 18.07 |
| `4` | € 18.96 |
| `E` | € 19.52 |
| `5` | € 20.62 |
| `5S` | € 21.45 |
| `F` | € 21.45 |
| `Q` | € 24.82 |
| `QB` | € 24.82 |
| `QA` | € 26.75 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `A`, `2`, `B`, `3`, `C`, `D`, `4`, `E`, `5`, `5S`, `F`, `Q`, `QB`, `QA`  
percentage: 0.90

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "esercizi-cinematografici-anec/fpls_rates_approximated · inps_employer · impact unknown · open"
    SIMPLIFICATION: tax_sector=TERZIARIO. Cinema exhibition employees (esercizio cinematografico) were historically under ENPALS (now FPLS — Fondo Pensione Lavoratori dello Spettacolo dell'INPS, Art. 12 comma 6 of this CCNL). The FPLS contribution regime differs from ordinary terziario. terziario rates are used as an approximation pending a dedicated cinema-FPLS tax file.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Add a dedicated FPLS contribution ruleset for cinema exhibition employees.

!!! warning "esercizi-cinematografici-anec/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-16 | [↗](https://www.fistelcisl.it/wp-content/uploads/2025/10/CCNL-Esercizi-cinematografici-2023-2026.pdf) |

??? note "Coverage notes"
    Two parallel level systems in the same contract (one CNEL code G211): Monosala/Multisala (7 levels: 1,2,3,4,5,5S,Q with parametri 100/112/132/159/176/185/220) and Multiplex/Megaplex (8 levels: A,B,C,D,E,F,QB,QA with parametri 100/122/140/150/165/185/220/240). The 15 levels are interleaved by salary for ordering (non-decreasing constraint). Levels 1 and A share identical salaries (parametro 100), as do 5S and F (parametro 185) and Q and QB (parametro 220). Level QA (parametro 240) is Multiplex/Megaplex only. The 'order' field is a global salary rank across both classification scales and is not a promotion ladder.
    
    Level code aliases in the PDF: monosala Q is also written 'VI Qua' in the paga table header and '6' in Tabella B. Code 'Q' (Tabella A label) is used consistently here.
    
    Workers: 6,427 (ADAPT 18th Report, CNEL aggiornamento 31/12/2023).
    
    Primary source: CCNL Esercizi Cinematografici 2023-2026 (FISTel CISL, signed 16/10/2025). Art. 54: period 01/01/2023-31/12/2026. Three salary tranches: 01/01/2023, 01/11/2024, 01/07/2025 from salary tables (pages 59-65 of the PDF). Baseline (31/12/2022 column) used only for increment verification, not modelled as a separate period.
    
    Hourly divisor 173: Art. 63 Dichiarazione a verbale (explicit formula: 'la retribuzione oraria si ottiene dividendo quella mensile per il coefficiente 173'). Daily divisor 26 also from Art. 63.
    
    Additional months 14: Art. 20 (tredicesima, December) and Art. 21 (quattordicesima, paid 1 luglio each year).
    
    Seniority (Art. 22): biennale (cadence 24 months), maximum 5 scatti. Amounts from Tabella A (appended to CCNL). Cross-verified against Art. 62 (Indennita di Cassa 'Sola P.B.' table): Tabella A formula is 5% of frozen paga base (Art. 62 column) plus a fixed addend (3.62 for monosala L3, confirming 12.72+3.62=16.34). The salary table bottom row shows 16.26 for monosala L3 (IV scatto basis) — this is a typographic error; Tabella A value 16.34 is authoritative.
    
    Apprenticeship (Art. 16): percentage type, 70%/80%/90% for years 1/2/3 of the apprenticeship, calculated on the minimo salariale of the classification level. In vigore dal 01/01/2018. Applicable to all 15 levels (Art. 16 states no level exclusion).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/esercizi-cinematografici-anec.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/esercizi-cinematografici-anec.py"
```
