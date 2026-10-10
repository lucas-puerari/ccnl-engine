# CCNL Radiotelevisivo — Settore Televisivo Multimediale

| | |
|---|---|
| **CNEL code** | `G091` |
| **Sector** | radiotelevisione — settore televisivo multimediale |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-01-08 |
| **Workers (est.)** |  |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Radio Televisioni
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UIL-COM

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
| **Last renewal** | 2026-01-08 |
| **Last verified** | — |
| **Latest salary tranche** | 2028-01-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `9` | 9° livello | € 2,282.56 | 2028-01-01 |
| `8` | 8° livello | € 2,092.44 | 2028-01-01 |
| `7` | 7° livello | € 1,929.62 | 2028-01-01 |
| `6` | 6° livello | € 1,840.62 | 2028-01-01 |
| `5` | 5° livello | € 1,696.00 | 2028-01-01 |
| `4` | 4° livello | € 1,425.96 | 2028-01-01 |
| `3` | 3° livello | € 1,190.33 | 2028-01-01 |
| `2` | 2° livello | € 1,046.74 | 2028-01-01 |
| `1` | 1° livello | € 902.11 | 2028-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.39 |
| `2` | € 12.91 |
| `3` | € 15.49 |
| `4` | € 18.08 |
| `5` | € 19.63 |
| `6` | € 21.17 |
| `7` | € 21.69 |
| `8` | € 22.72 |
| `9` | € 24.79 |

## Apprenticeship

**professionalizzante_breve** (type: `percentage`)  
Destination levels: `3`  
percentage: 0.90

**professionalizzante_esteso** (type: `percentage`)  
Destination levels: `4`, `5`, `6`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "radiotelevisive-televisivo/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
    INPS rates reuse existing 2026-industria.json (tax_sector=industria). No bilateral fund substitution for broadcasting sector identified; standard Confindustria INPS rates apply.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-08 | [↗](https://www.confindustriaradiotv.it/) |

??? note "Coverage notes"
    CCNL Radiotelevisivo 2026 signed 08/01/2026 in Roma. Employer: Confindustria Radio Televisioni (pres. Antonio Marano) and ANICA (pres. Alessandro Usai). Unions: SLC-CGIL (Sindacato Lavoratori della Comunicazione), FISTEL-CISL (Federazione Informazioni Spettacolo e Telecomunicazioni), UIL-COM (UIL Comunicazione). Signatories sourced from Art. 1, page 7 of CCNL PDF.
    
    Source anchor: https://www.confindustriaradiotv.it/ is the employer association homepage; a direct PDF permalink was not published. PDF read locally as ccnl_radiotv_2026.pdf (81 MB, read 2026-09-12).
    
    SPLIT model: paga base (minimo tabellare, Art. 43) + contingenza congelata al 1° novembre 1991 (Allegato A). EDR not present in 2026 CCNL.
    
    DUAL-SECTOR contract: Settore Televisivo Multimediale (9 livelli) and Settore Radiofonico (6 livelli) modelled in two separate files because the engine's monotonicity validator (higher order >= higher salary at every tranche date) rejects a merged 15-level file: at 01/01/2026 Radio L2 (868.41) > TV L1 (835.62) and Radio L6 (1632.31) > TV L5 (1571.00), inverting the relative ordering set at the CCNL base date.
    
    TV sector has three new tranches: 01/01/2026, 01/06/2027, 01/01/2028. Radio sector has only two: 01/01/2026, 01/06/2027 (no 01/01/2028 tranche). The pre-2026 CCNL column values (from the 2022 contract) are not modelled.
    
    Hourly divisor 173 sourced from Art. 43. Verified on levels 3, 5, 7: none of the three back-calculations from the published hourly rate yield a conglobated total — values are paga base only, confirming the split model.
    
    Apprenticeship (Art. 27): professionalizzante, percentage type. TV L3 max 24 months; TV L4-L6 max 48-60 months (same % schedule). Levels L7-L9 not accessible via apprenticeship per Art. 27.
    
    Apprenticeship open tail: Art. 27 sets 24-month max for L3 (breve track). The final period {18, null, 0.90} cannot be closed to {18, 24, 0.90} because the engine schema requires the last apprenticeship period to be open-ended (validate_open_sequence). A query past month 24 is outside the contract duration and should not arise in normal use.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/radiotelevisive-televisivo.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/radiotelevisive-televisivo.py"
```
