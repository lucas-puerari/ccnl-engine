# CCNL Vigilanza Privata e Servizi Fiduciari FEDERDAT — GPG

| | |
|---|---|
| **CNEL code** | `HV17` |
| **Sector** | vigilanza privata — guardie particolari giurate (GPG) |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-05-04 |
| **Workers (est.)** | ~45k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - FEDERDAT
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| **Limits of this contract** | seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2023-05-04 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-12-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Livello Q (Quadro) | € 2,434.74 | 2026-12-01 |
| `I` | Livello I | € 2,086.89 | 2026-12-01 |
| `II` | Livello II | € 1,946.09 | 2026-12-01 |
| `III` | Livello III | € 1,723.31 | 2026-12-01 |
| `IV` | Livello IV | € 1,528.88 | 2026-12-01 |
| `V` | Livello V | € 1,450.44 | 2026-12-01 |
| `VI` | Livello VI (convenzionale) | € 1,350.44 | 2026-12-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `VI` | € 19.66 |
| `V` | € 20.52 |
| `IV` | € 21.13 |
| `III` | € 22.46 |
| `II` | € 23.83 |
| `I` | € 26.12 |
| `Q` | € 31.30 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `VI`, `V`, `IV`, `III`, `II`, `I`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "vigilanza-privata-federdat-gpg/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2024-02-16 | [↗](https://uiltucs.it/wp-content/uploads/2024/07/Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf) |

??? note "Coverage notes"
    CCNL HV17 FEDERDAT GPG section. Conglobated, 14 months, divisor 173. 7 levels. 6 tranches: 01/06/2023, 01/06/2024, 01/06/2025, 01/12/2025, 01/04/2026, 01/12/2026. Contract validity: 01/06/2023-31/12/2026.
    
    SENIORITY: amounts from UILTUCS tabelle PDF (Tabelle-CCNL-16.2.2024_firmato-2023-2026.pdf), cadence 36m: Q=31.30, I=26.12, II=23.83, III=22.46, IV=21.13, V=20.52, VI=19.66 EUR/scatto. July 9 2026 renewal (FEDERDAT-CONFIAL) increased maximum_count from 6 to 10; per-scatto amounts confirmed unchanged post-rinnovo (ilccnl.it shows same Q–III values after rinnovo). Amounts for IV–VI post-rinnovo not independently verified from a post-rinnovo primary source.
    
    Apprenticeship: 100% passthrough confirmed from CCNL FEDERDAT Art. 86: "L'Apprendista ha diritto per tutta la durata del periodo di apprendistato all'inquadramento e alla corrispondente retribuzione del livello finale di collocazione." (FESICA PDF, CCNL ISTITUTI AZIENDE VIGILANZA PRIVATA, Art. 86). Engine models this correctly as 100% of destination level salary.
    
    Level VI salary at 01/06/2024 (1185.44) is anomalously high vs prior tranche (1108.06) — confirmed by source as conventional riallineamento for level VI.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/vigilanza-privata-federdat-gpg.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/vigilanza-privata-federdat-gpg.py"
```
