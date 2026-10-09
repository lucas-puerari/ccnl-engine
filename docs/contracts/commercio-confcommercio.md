# CCNL Terziario, Distribuzione e Servizi (Confcommercio)

| | |
|---|---|
| **CNEL code** | `H011` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-28 |
| **Workers (est.)** | ~800k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confcommercio
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-03-28 |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2027-02-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,313.29 | 2027-02-01 |
| `1` | 1st level | € 2,083.84 | 2027-02-01 |
| `2` | 2nd level | € 1,802.50 | 2027-02-01 |
| `3` | 3rd level | € 1,540.66 | 2027-02-01 |
| `4` | 4th level | € 1,332.46 | 2027-02-01 |
| `5` | 5th level | € 1,203.83 | 2027-02-01 |
| `6` | 6th level | € 1,080.77 | 2027-02-01 |
| `7` | 7th level | € 925.31 | 2027-02-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `1` | € 24.84 |
| `2` | € 22.83 |
| `3` | € 21.95 |
| `4` | € 20.66 |
| `5` | € 20.30 |
| `6` | € 19.73 |
| `7` | € 19.47 |

## Apprenticeship

**livelli_2_5** (type: `under_classification`)  
Destination levels: `2`, `3`, `4`, `5`

**livello_6** (type: `under_classification`)  
Destination levels: `6`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "commercio-confcommercio/apprentice_seniority · seniority · impact unknown · open"
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
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Terziario Distribuzione e Servizi 2024-2027 (rinnovo 22/03/2024, accordo integrativo 28/03/2024) | tabella_retributiva | 2024-03-28 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-commercio-2024-2027/) |
| CCNL Terziario Distribuzione e Servizi — Testo Unico 2019 (rinnovo 22/03/2024) | associazione | 2024-03-22 | [↗](https://www.confcommercio.it/-/ccnl-terziario-distribuzione-servizi-testo-unico-2019) |

??? note "Coverage notes"
    'contingenza_edr' is the tables' 'Contingenza + EDR' column (contingenza frozen since November 1993 per L. 438/1992 plus EDR 10,33); 'terzo_elemento_nazionale' is the 2,07 EUR element of Art. 215.
    
    Indennità di funzione Quadri 260,76 EUR (Art. 129, 14 mensilità; the literal sum of the increments is 260,77, the tables carry 260,76); VII livello 'altri elementi' 5,16 EUR.
    
    INPS: see tax/data/2026-terziario.json notes.
    
    CNEL code H011 confirmed by Il Sole 24 Ore / INPS UNIEMENS reference.
    
    Salary tables: five tranches of the rinnovo 22/03/2024 (paga base dal 1/4/2024, 1/3/2025, 1/11/2025, 1/11/2026, 1/2/2027) taken from the official tabelle retributive as perfected by the Accordo integrativo 28/03/2024 (rounding fixes on Q, I, II, VI vs the 22/03 ipotesi), consolidated text at comuneportofinomare.it (Eutekne) cross-checked with lexplain.it.
    
    Seniority (Art. 205): ten triennial scatti; amounts Q 25,46, I 24,84, II 22,83, III 21,95, IV 20,66, V 20,30, VI 19,73, VII 19,47 (dal 1/1/1990, unchanged by the 2024 renewal).
    
    Apprenticeship (Art. 53 TU 2019, unchanged in 2024): sottoinquadramento, two levels below the destination for the first half and one level below for the second half; eligible destinations II-VI (Art. 62); durations II-V 36 months, VI 24 months (Art. 64). Track 'livelli_2_5' (18+18 months), track 'livello_6' (VII for the first 12 months; the second half stays at VII by the general one-level-below rule, lexplain.it reads it as VI: adopted the literal text). Art. 68 Tabella B profiles with 42/48-month durations and the farmacista di parafarmacia derogation (Accordo 31/10/2024) are profile-specific and not modelled.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/commercio-confcommercio.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/commercio-confcommercio.py"
```
