# CCNL Attività Ferroviarie — AGENS

| | |
|---|---|
| **CNEL code** | `I320` |
| **Sector** | trasporto |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-22 |
| **Workers (est.)** | ~75k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGENS — Aziende Aderenti alla Sezione Ferroviaria di Conftrasporto
    - FILT-CGIL — Federazione Italiana Lavoratori Trasporti
    - FIT-CISL — Federazione Italiana Trasporti
    - Uiltrasporti
    - FAST-Confsal — Federazione Autonoma Sindacati Trasporti
    - UGL Ferrovieri
    - ORSA Ferrovie

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
| **Limits of this contract** | base_salary, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-05-22 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-06-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Level Q1 — railway quadri (senior management), with IND_FUN function allowance | € 2,826.07 | 2026-06-01 |
| `Q2` | Level Q2 — railway quadri (middle management), with IND_FUN function allowance | € 2,483.02 | 2026-06-01 |
| `A` | Level A — senior railway managers, strategic operational leadership | € 2,401.34 | 2026-06-01 |
| `B1` | Level B1 — railway department managers, senior management roles | € 2,286.99 | 2026-06-01 |
| `B2` | Level B2 — railway section managers, intermediate management roles | € 2,188.97 | 2026-06-01 |
| `B3` | Level B3 — railway supervisors, operational management duties | € 2,156.31 | 2026-06-01 |
| `C1` | Level C1 — senior railway professionals, team coordination roles | € 2,107.30 | 2026-06-01 |
| `C2` | Level C2 — railway professionals, specialist operational coordination | € 2,074.62 | 2026-06-01 |
| `D1` | Level D1 — senior railway technicians, advanced professional duties | € 2,041.95 | 2026-06-01 |
| `D2` | Level D2 — experienced railway technicians, intermediate professional roles | € 1,976.62 | 2026-06-01 |
| `D3` | Level D3 — qualified railway technicians, standard professional duties | € 1,943.94 | 2026-06-01 |
| `E1` | Level E1 — specialised railway workers, technical operational duties | € 1,911.26 | 2026-06-01 |
| `E2` | Level E2 — skilled railway workers, certified operational roles | € 1,829.60 | 2026-06-01 |
| `E3` | Level E3 — semi-skilled railway workers, qualified operational tasks | € 1,796.91 | 2026-06-01 |
| `F1` | Level F1 — basic railway workers, standard operational tasks | € 1,666.23 | 2026-06-01 |
| `F2` | Level F2 — entry-level railway workers, unskilled support tasks | € 1,633.56 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 47.19 |
| `Q2` | € 38.27 |
| `A` | € 35.95 |
| `B1` | € 33.62 |
| `B2` | € 31.77 |
| `B3` | € 31.30 |
| `C1` | € 29.91 |
| `C2` | € 29.45 |
| `D1` | € 28.42 |
| `D2` | € 25.64 |
| `D3` | € 25.22 |
| `E1` | € 24.34 |
| `E2` | € 22.66 |
| `E3` | € 22.66 |
| `F1` | € 18.58 |
| `F2` | € 18.22 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "trasporto-ferroviario-agens/pre_june_2025_tables · base_salary · impact yes · open"
    PRE-JUN 2025 PERIOD NOT MODELLED. The CCNL contractual coverage runs 2024-01-01 to 2026-12-31. The Jan 2024 – May 2025 wage gap was compensated by a lump-sum una tantum paid in Aug 2025 (per redigo.info), explicitly stated as having no effect on any contractual institute ('non avranno riflessi su alcun istituto contrattuale'). Salary periods therefore start 01/06/2025. Engine queries with as_of before Jun 2025 will return the Jun 2025 values, which overstate actual pay for that window.

    **Applies when:** `base_salary` applies; before 2025-06-01.

    **Remediation:** Model the pre-June 2025 salary tables, or reject dates before 1 June 2025.

!!! warning "trasporto-ferroviario-agens/seniority_amounts_before_june_2026 · seniority · impact unknown · open"
    SENIORITY AMOUNTS PRE-JUN 2025. Per-level scatto amounts are sourced from lavoro-economia.it/kitech.it representing the Jun 2026 table. Whether identical values applied in the Jun 2025 and Nov 2025 tranches is unconfirmed. Modelled as constant from 01/06/2025.

    **Applies when:** `seniority` applies; before 2026-06-01.

    **Remediation:** Confirm the seniority amounts of the June 2025 and November 2025 tranches.

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
| — | — | 2025-05-22 | [↗](https://ilccnl.it/ccnl/ferrovie/ferrovie-attivita-ferroviarie/tabelleretributive) |
| — | — | 2025-05-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=299) |
| — | — | 2025-05-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx) |
| — | — | 2025-05-22 | [↗](https://www.redigo.info/2025/05/ccnl-ferrovie-rinnovo-2025) |
| — | — | 2025-05-22 | [↗](https://www.leggeinchiaro.it/ccnl-ferrovie) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. ilccnl.it salary table shows contingenza=0.00 and terzo elemento=0.00 for all 16 levels. kitech.it confirms additive structure: Q1 base tabellare=2826.07 + IND_FUN=250.00 total, Q2 base=2483.02 + IND_FUN=130.00 total. Two aggregator sources (ilccnl.it, kitech.it) agree on the decomposition, establishing the function allowances are additive to the conglobated base. Primary CCNL text (AGENS/FILT-CGIL) was not directly retrieved; all parameters derive from aggregator tables.
    
    SIGNATORIES: AGENS (employer association, Conftrasporto affiliate) + FILT-CGIL/FIT-CISL/Uiltrasporti/FAST-Confsal/UGL Ferrovieri/ORSA Ferrovie (workers). CNEL code I320. The operating companies (FS Italiane, Trenitalia, RFI) are AGENS members; AGENS is the formal signatory.
    
    HOURLY DIVISOR: 160, verbatim from ilccnl.it salary table. Standard for 40h/week contractual regime (160 = 40 × 4).
    
    ADDITIONAL MONTHS: 14 — tredicesima + quattordicesima, confirmed from lavoro-economia.it and redigo.info (rinnovo May 2025).
    
    SENIORITY: biennial (cadence 24 months), maximum 7 scatti. Per-level EUR amounts from lavoro-economia.it and kitech.it (both aggregators). NOTE: E2 and E3 show identical scatto amounts (22.66) in both aggregator sources; unconfirmed against the primary CCNL text and should be verified before relying on E2/E3 seniority amounts.
    
    FUNCTION ALLOWANCES (IND_FUN): Q1 receives +250.00/month, Q2 receives +130.00/month. Modelled as fixed_allowances with code IND_FUN effective from first salary tranche (01/06/2025). Two aggregator sources (ilccnl.it, kitech.it) agree the allowances are additive to the base tabellare.
    
    APPRENTICESHIP. I320 specifies apprendistato professionalizzante (max 36 months per Art. 29 Parte Generale). Per leggeinchiaro.it, retributive percentages are defined in the Piano Formativo Individuale (PFI) on a per-worker basis and are not published as a contract-level table. No fixed percentage or under-classification track exists in the CCNL text; the apprenticeship array is therefore empty by contract structure, not by modelling omission. Analogous to public-sector contracts where apprendistato is excluded from scope.
    
    FONDO DI SOLIDARIETA FERROVIE. Contribution rate 0.20% confirmed: 2/3 a carico di Ferrovie (datore, ≈0.133%), 1/3 a carico dei lavoratori (≈0.067%). Source: INPS circolare (confirmed by inps.it/fondo-ferrovie-dello-stato and consulenza.it). Not modelled in the engine; adds approximately 0.067% to employee cost and 0.133% to employer cost above the standard INDUSTRIA INPS rates. This is a structural engine limitation, not a data gap.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/trasporto-ferroviario-agens.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/trasporto-ferroviario-agens.py"
```
