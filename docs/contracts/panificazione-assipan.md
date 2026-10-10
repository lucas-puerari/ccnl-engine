# CCNL Panificazione e Settori Affini — Industria (Assipan/Fiesa)

| | |
|---|---|
| **CNEL code** | `E023` |
| **Sector** | alimentare |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-02-26 |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assipan — Associazione Sindacale Panificatori Industriali
    - Fiesa-Assopanificatori — Federazione Italiana Esercenti Specializzati Alimentazione
    - Federpanificatori
    - FLAI-CGIL — Federazione Lavoratori Agro-industrie
    - FAI-CISL — Federazione Agroalimentare e Industriale
    - UILA-UIL — Unione Italiana Lavoratori Agroalimentari

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
| **Last renewal** | 2025-02-26 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-09-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `I` | Level I — managers, senior professionals, plant directors | € 2,458.99 | 2026-09-01 |
| `II` | Level II — supervisors, senior specialists, department coordinators | € 2,305.51 | 2026-09-01 |
| `IIIA` | Level IIIA — highly skilled workers, senior technicians, team leaders | € 2,162.35 | 2026-09-01 |
| `IIIB` | Level IIIB — specialist workers, master bakers, experienced technicians | € 2,046.31 | 2026-09-01 |
| `IV` | Level IV — skilled workers, qualified bakers and production workers | € 1,806.45 | 2026-09-01 |
| `V` | Level V — semi-skilled workers, basic production tasks under supervision | € 1,664.67 | 2026-09-01 |
| `VI` | Level VI — entry-level workers, no qualification required, unskilled tasks | € 1,481.15 | 2026-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 34.28 |
| `II` | € 31.67 |
| `IIIA` | € 29.25 |
| `IIIB` | € 27.24 |
| `IV` | € 22.91 |
| `V` | € 20.27 |
| `VI` | € 17.14 |

## Apprenticeship

**panif_track_a** (type: `percentage`)  
Destination levels: `I`, `II`, `IIIA`, `IIIB`, `IV`  
percentage: 0.90

**panif_track_b** (type: `percentage`)  
Destination levels: `V`  
percentage: 0.80

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "panificazione-assipan/apprentice_seniority · seniority · impact unknown · open"
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
| — | — | 2025-02-26 | [↗](https://www.assipan.it/contratto-collettivo-nazionale-lavoro/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. Art. 50 bis states the minimo tabellare is the conglobated figure (paga base + contingenza frozen 1 Nov 1991 + EDR) and that the quota oraria is obtained by dividing it by 173. The premio di produzione nazionale is articled separately in Art. 50 ter as a distinct element outside the conglobated minimum, therefore modelled as fixed_allowance per level.
    
    SIGNATORIES: Assipan/Fiesa-Assopanificatori/Federpanificatori (employer) — FLAI-CGIL/FAI-CISL/UILA-UIL (worker). CNEL code E023. NOTE: Aidepi is NOT a signatory to E023; Aidepi firms use CCNL Alimentari Industria (E012).
    
    HOURLY DIVISOR: 173, verbatim from Art. 50 bis: 'I minimi di cui sopra sono riferiti ad una prestazione di lavoro di 173 ore mensili. La quota oraria si ricava dividendo le retribuzioni per 173.'
    
    ADDITIONAL MONTHS: 14 — tredicesima (Art. 52, para 1) + quattordicesima (Art. 52, para 2, paid June 30). Both confirmed from Testo Unico 2025.
    
    SENIORITY: biennale (24 months), maximum 5 scatti. Amounts frozen since Aug 1, 1997 (Art. 51). Per-level EUR: I=34.28, II=31.67, IIIA=29.25, IIIB=27.24, IV=22.91, V=20.27, VI=17.14.
    
    PREMIO DI PRODUZIONE NAZIONALE: fixed cifra per level, frozen since Aug 1, 1995 (Art. 50 ter). All seven levels receive it. Modelled as fixed_allowance with code PREMIO_PROD.
    
    PREMIO DI PRODUZIONE FREQUENCY: modelled as monthly (14x). Evidence: (1) the prize is listed as component c) of 'trattamento economico' in Art. 50 bis alongside paga base — all components in that list are monthly recurring pay; (2) the prize amounts are in 'cifra mensile' (no 'annuale' qualifier); (3) the TFR computation clause includes it in the monthly average calculation, consistent with monthly payment; (4) the quattordicesima (Art. 53) uses the 'ultima mensilità percepita' which would include the prize if monthly. No evidence of single-annual-sum treatment found in the primary 2025 Testo Unico.
    
    APPRENTICESHIP: Art. 28 percentage model. Two tracks: Track A (levels I/II/IIIA/IIIB/IV) periods 0-12m=70%, 12-24m=80%, 24m+=90%; Track B (level V) periods 0-12m=70%, 12m+=80%. Level VI is excluded from apprendistato per Art. 28. Maximum contractual durations: I-IIIB=36m, IV=30m, V=24m — not enforced by engine but documented here. The 95% bracket (Art. 28, months 49+) is unreachable given max durations; omitted from both tracks.
    
    PRE-AFAC TRANCHE: now modelled. Confirmed from Testo Unico 2025 (assipan.it PDF, 26/02/2025), column 'Retribuzione al 31/01/2024': I=2102.30, II=1977.36, IIIA=1860.95, IIIB=1766.31, IV=1569.25, V=1452.44, VI=1302.81. These amounts are added as the 2023-01-01 period (valid until 31/01/2024) for all seven levels.
    
    HOURLY RATE ENGINE DISCREPANCY. Art. 50 bis defines the official quota oraria as minimo_tabellare/173 (base only). The engine computes hourly_rate = gross_monthly/173 where gross includes the PREMIO_PROD fixed_allowance. For level IIIB Sep 2026: official 2046.31/173 = 11.83 EUR/h; engine computes (2046.31+28.04)/173 = 11.99 EUR/h (diff +0.16). Structural engine limitation shared by all contracts with separate fixed allowances (no per-allowance hourly_relevant flag). Monthly and annual figures are unaffected.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/panificazione-assipan.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/panificazione-assipan.py"
```
