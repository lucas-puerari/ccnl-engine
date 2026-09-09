# CCNL Lavanderie Industriali (Assosistema Confindustria)

| | |
|---|---|
| **CNEL code** | `D0L1` |
| **Sector** | lavanderie-industriali |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~17k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Assosistema Confindustria
    - Filctem-CGIL
    - Femca-CISL
    - Uiltec-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `D2` | Livello D2 — quadri, executive management (L. 190/1985) | € 3,015.43 | — |
| `C3` | Livello C3 — senior managers, strategic operational responsibility | € 3,015.43 | — |
| `C2` | Livello C2 — area managers, planning and operational leadership | € 2,566.77 | — |
| `C1` | Livello C1 — senior specialists, supervisory and quality-control functions | € 2,275.64 | — |
| `B3` | Livello B3 — highly qualified workers, team coordination and process oversight | € 2,202.14 | — |
| `B2` | Livello B2 — specialist workers, multi-task roles with technical responsibility | € 2,012.94 | — |
| `B1` | Livello B1 — skilled workers, complex laundry and sterilisation operations | € 1,917.54 | — |
| `A3` | Livello A3 — qualified workers, autonomous standard operations | € 1,882.49 | — |
| `A2` | Livello A2 — semi-skilled workers, assisted operations | € 1,786.94 | — |
| `A1` | Livello A1 — entry-level workers, basic laundry operations | € 1,579.32 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 6.71 |
| `A2` | € 6.97 |
| `A3` | € 7.23 |
| `B1` | € 7.23 |
| `B2` | € 8.00 |
| `B3` | € 8.26 |
| `C1` | € 8.26 |
| `C2` | € 9.81 |
| `C3` | € 11.88 |
| `D2` | € 11.88 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `A3`, `B1`, `B2`, `B3`, `C1`, `C2`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `A2`, `C3`, `D2`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    DERIVED TRANCHE: Dec 2026 amounts derived from B1+20 using level coefficients (A1=0.7936, A2=0.9126, A3=0.9762, B1=1.0000, B2=1.0794, B3=1.2540, C1=1.2778, C2=1.5396, C3=D2=1.9762), verified as identical across all 4 historical tranches of the 2023-2025 agreement. Not independently confirmed from published Dec 2026 table.

!!! warning ""
    INCENTIVO DI MODULO: per-level amounts from lavoro-economia.it / previdenza-professionisti.it cross-confirmed for previgente CCNL. Assumed unchanged in 2026 renewal. No published 2026 text shows a change.

!!! warning ""
    SENIORITY AMOUNTS: assumed unchanged in 2026 renewal. Sources reflect previgente CCNL values. 2026 renewal public summary does not mention changes to scatti amounts.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-05-19 | [↗](https://www.assosistema.it/11527-2/) |
| — | — | 2026-05-19 | [↗](https://ilccnl.it/contratto/ccnl/lavanderie---industria) |
| — | — | 2026-05-19 | [↗](https://www.iqnotizie.it/notizia/IQ47433/) |
| — | — | 2026-05-19 | [↗](https://previdenza-professionisti.it/) |

??? note "Coverage notes"
    SECTOR SCOPE: both turismo and sanitario comparti. Pre-2026 the two sectors had distinct tranche dates (sanitario ~9 months behind turismo), but converged to identical minimi by Apr 2025 (sanitario) / Oct 2025 (turismo). The 2026-2028 rinnovo (19 May 2026) applies a single undifferentiated table labelled SANITARIO_TURISMO by Assosistema — confirmed by Assosistema circular title 'Costo medio orario CCNL Lavanderie industriali SANITARIO_TURISMO Aree ABCD tranche 2026'. This contract covers workers in both comparti from 2026-05-01.
    
    SALARY MODEL: split. base_salary = minimo tabellare (contingenza conglobata since 2008, confirmed in CCNL text). fixed_allowances per level = INCENTIVO_DI_MODULO (frozen, level-specific constant). D2 also receives INDENNITA_FUNZIONE 130.00 EUR/month. A1 has no incentivo di modulo (0 EUR). Verified: B1 May 2026 = 1897.54; B1/173 = 10.97 (non-integer, consistent with split). C2 May 2026 = 2535.98; (2535.98+93.44)/173 = 15.20 (matches ilccnl.it hourly for C2).
    
    MODELLED TRANCHES: 2026-05-01 (source-confirmed from ilccnl.it, iqnotizie.it, previdenza-professionisti.it, all concordant); 2026-12-01 (derived: +20 EUR on B1, other levels proportional using coefficient vector verified across 4 historical tranches 2023-2025). Oct 2027 (+50 EUR B1) and Oct 2028 (+60 EUR B1) announced but table not published — not modelled.
    
    AGREEMENT DATE: 2026-05-19 is ipotesi di accordo date. Ratification (scioglimento della riserva) was due by 2026-06-19 per Assosistema circular. Definitive signing date not independently confirmed; 2026-05-19 used in sources.
    
    SENIORITY: biennale (cadence_months=24), maximum 5 scatti. Per-level amounts from previdenza-professionisti.it (Assosistema D0L1 table): A1=6.71, A2=6.97, A3=7.23, B1=7.23, B2=8.00, B3=8.26, C1=8.26, C2=9.81, C3=11.88, D2=11.88. Cross-confirmed by lavoro-economia.it (identical amounts). Amounts from previgente CCNL assumed unchanged in 2026 renewal.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it and lavoro-economia.it. No quattordicesima.
    
    INPS: uses 2026-industria.json (industria sector, Assosistema Confindustria). Bilateral funds FASIIL (health) and PREVIMODA (pension) are supplementary to INPS, not substituting. Employer INPS rate unaffected.
    
    APPRENTICESHIP: under_classification professionalizzante only. Two tracks per previdenza-professionisti.it (Assosistema D0L1, 2023 rules assumed unchanged in 2026 renewal): 36-month track (destinations A3..C2, periods: 0-12 at 2 levels below, 12-24 at 1 level below, 24+ at destination); 24-month track (destinations A2, C3, D2, periods: 0-12 at 1 level below, 12+ at destination). A1 excluded (no destination below it). Alta formazione and qualifica/diploma apprenticeship not modelled.
    
    APPRENTICESHIP ALLOWANCES: engine draws INCENTIVO_DI_MODULO from the effective pay level, not the destination level. An apprentice at A3 destination (month 6, pay level A1) receives 0.00 allowances because A1 has no incentivo. An apprentice at B1 destination (month 18, pay level A3) receives 57.00 EUR (A3 incentivo). Verified by compute sweep across all five boundary cases (A3/m6, A2/m6, B1/m18, C2/m30, D2/m18).
    
    SOURCE CAVEAT: previdenza-professionisti.it entry uses a domain-level URL; the exact deep-link page was not captured. Data cross-confirmed by lavoro-economia.it for seniority amounts.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/lavanderie-industriali-assosistema.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/lavanderie-industriali-assosistema.py"
```
