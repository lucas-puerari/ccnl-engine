# CCNL Gas e Acqua — Utilitalia/Proxigas/Anfida/Assogas

| | |
|---|---|
| **CNEL code** | `K321` |
| **Sector** | gas e acqua |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-08 |
| **Workers (est.)** | ~65k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Utilitalia
    - Proxigas
    - Anfida
    - Assogas
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| **Last renewal** | 2025-05-08 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-07-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Level Q (Quadri) — par. 200.74 — managerial, highest responsibility | € 3,577.47 | 2026-07-01 |
| `8` | Level 8 — par. 181.29 — senior expert, broad managerial-technical responsibility | € 3,230.84 | 2026-07-01 |
| `7` | Level 7 — par. 167.50 — expert, advanced coordination | € 2,985.08 | 2026-07-01 |
| `6` | Level 6 — par. 153.69 — senior specialist, technical-organisational roles | € 2,738.97 | 2026-07-01 |
| `5` | Level 5 — par. 139.96 — highly skilled, broad autonomy | € 2,494.28 | 2026-07-01 |
| `4` | Level 4 — par. 131.42 — specialist, complex tasks requiring expertise | € 2,342.01 | 2026-07-01 |
| `3` | Level 3 — par. 122.95 — skilled operative, autonomous in standard tasks | € 2,191.09 | 2026-07-01 |
| `2` | Level 2 — par. 111.15 — semi-skilled, partial autonomy | € 1,980.76 | 2026-07-01 |
| `1` | Level 1 — par. 100 — unskilled, non-autonomous, routine operations | € 1,782.14 | 2026-07-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 0.00 |
| `2` | € 0.00 |
| `3` | € 0.00 |
| `4` | € 0.00 |
| `5` | € 0.00 |
| `6` | € 0.00 |
| `7` | € 0.00 |
| `8` | € 0.00 |
| `Q` | € 0.00 |

## Apprenticeship

**professionalizzante_24** (type: `percentage`)  
Destination levels: `7`, `8`  
percentage: 1.00

**professionalizzante_30** (type: `percentage`)  
Destination levels: `2`, `4`, `5`, `6`  
percentage: 1.00

**professionalizzante_36** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "gas-acqua-utilitalia/industria_rates_proxy · inps_employer · impact unknown · open"
    INPS: reuses 2026-industria.json. Gas and water utilities (aziende private del settore gas-acqua) are classified under 'attività industriali' for INPS contribution purposes. Employer associations Utilitalia and Proxigas are Confindustria-aligned. SIMPLIFICATION: exact INPS circular for this sector not verified; 2026-industria.json rates used as proxy.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the INPS rates of the gas-water sector against the annual INPS circular.

!!! warning "gas-acqua-utilitalia/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-09-30 | [↗](https://sosvavsrl.it/media/attachments/2024/05/24/ccnl.pdf) |
| — | — | 2025-05-08 | [↗](https://ilccnl.it/contratto/ccnl/gas-e-acqua---aziende-private-dal-010102) |
| — | — | 2025-05-08 | [↗](https://www.filctemcgil.it/index.php/notiziario/news/gas-acqua) |

??? note "Coverage notes"
    SALARY MODEL: conglobated contingenza ('minimi tabellari integrati') with EDR 10.33 shown separately. Confirmed from scheda riassuntiva PDF (CCNL 30/09/2022, sosvavsrl.it), section heading 'Minimi tabellari integrati'. EDR is a fixed statutory element (frozen since 1997, Accordo interconfederale) shown as a distinct line in all salary tables; modelled as fixed_allowance for each level.
    
    HOURLY DIVISOR: 167. Stated explicitly in §4.3 of the PDF scheda riassuntiva: 'Coefficiente orario: 167'. Corresponds to 38h 30min contractual week (§4.4). Back-calculation: L1(2024-09-01)=1677.64/167=10.05 EUR/h.
    
    ADDITIONAL MONTHS: 14 (tredicesima + quattordicesima). Stated in §4.1: 'Mensilità: 14'. Tredicesima confirmed §5.3, quattordicesima confirmed §5.4.
    
    SENIORITY: abolished from 31/12/2015 (§5.5 CCNL K321). Frozen as 'elemento ad personam non riassorbibile' at the individual amount accrued as at 31/12/2015 — individual per-worker, not derivable from level. Workers hired after 2015 earn no seniority. Modelled as maximum_count=0 (all amounts 0.00), which is the correct model for new hires. The frozen elemento for pre-2016 hires is a structural engine limitation: it requires per-worker historical data not available from the CCNL alone.
    
    LEVEL Q ALLOWANCE: Indennità di funzione 51.65 EUR/month (12 mensilità) per §2.1 of the CCNL PDF. Shown separately from minimo and EDR in all salary tables.
    
    COVERAGE: CCNL covers approximately 50,000 workers in about 600 private gas and water distribution companies (source: filctemcgil.it, 2025 renewal announcement). CNEL code K321.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/gas-acqua-utilitalia.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/gas-acqua-utilitalia.py"
```
