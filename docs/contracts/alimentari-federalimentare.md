# CCNL per i lavoratori dell'industria alimentare (Federalimentare)

| | |
|---|---|
| **CNEL code** | `E012` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~145k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federalimentare
    - FLAI-CGIL
    - FAI-CISL
    - UILA-UIL

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
| `1S` | 1S level — senior managers and executives (under L. 190/1985 for workers classified as Quadri) | € 2,836.32 | — |
| `1` | 1st level — managers with significant managerial and directional responsibilities | € 2,466.34 | — |
| `2` | 2nd level — intermediate managers and workers with coordination responsibilities | € 2,034.77 | — |
| `3A` | 3A level — specialist workers with significant operational responsibilities | € 1,788.12 | — |
| `3` | 3rd level — specialist workers with operational autonomy | € 1,603.17 | — |
| `4` | 4th level — qualified workers with specific tasks and limited responsibilities | € 1,479.82 | — |
| `5` | 5th level — qualified workers with simple executive tasks | € 1,356.52 | — |
| `6` | 6th level — entry-level workers, simple operations | € 1,233.20 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1S` | € 51.42 |
| `1` | € 44.71 |
| `2` | € 36.89 |
| `3A` | € 32.42 |
| `3` | € 29.06 |
| `4` | € 26.83 |
| `5` | € 24.59 |
| `6` | € 22.35 |

## Apprenticeship

**professionalizzante_36** (type: `under_classification`)  
Destination levels: `4`, `3`, `3A`, `2`, `1`

**professionalizzante_24** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    IAR tranche September 2027: the CCNL sets +11 EUR at level 4; per-level amounts are derived by scaling +11 with the level's IAR ratio to level 4 (the IAR is parametric), rounded to the cent. Official per-level tables were not published at extraction time.

!!! warning ""
    APPRENTICESHIP under_classification (Art. 21 CCNL, renewal 01/03/2024; period structure from afi-ipl.org): 36-month track for destinations 4, 3, 3A, 2, 1 (0-10 months two levels below, 10-22 one level below, then destination); 24-month track for destination 5 (0-10 months at level 6, then level 5). Level 6 and 1S are not apprenticeship destinations. The 10/22-month boundaries are as reported by the source; the contract text refers to 'first/second/third period'.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-03-01 | [↗](https://flaiveneto.it/rinnovato-il-ccnl-industria-alimentare/) |
| — | — | — | [↗](https://www.direzionelavoro.it/wp-content/uploads/2023/10/Alimentari-industria-CNEL-E012.pdf) |
| — | — | — | [↗](https://sindacato.it/ccnl-alimentari-industria/) |
| — | — | — | [↗](https://www.kitech.it/tabelle-retributive-alimentari-industria) |
| — | — | — | [↗](https://www.afi-ipl.org/agenda-apprendisti/industria-alimentare/) |

??? note "Coverage notes"
    SALARY MODEL: split (base pay/TEM + contingency allowance + EDR + IAR as separate allowances). TEM varies by level and tranche; contingency frozen from 31/07/1992 (Government-social partners Protocol); EDR fixed at 10.33 EUR for all levels (Agreement 31/07/1992). IAR (Additional Pay Increment) remains a separate component of the TEC — not absorbed into TEM (confirmed by FLAI Veneto: 'the CCNL renews and redefines the TEC as the sum of TEM and IAR'). TEM source: sindacato.it (2024 salary tables). IAR source: flaiveneto.it.
    
    CONTINGENCY ALLOWANCE: amounts from lexplain.it and kitech.it — confirmed by two independent sources. Values identical to the previous contracts (frozen since 1993). 1S=545.72, 1=538.70, 2=530.51, 3A=525.83, 3=522.32, 4=519.99, 5=517.65, 6=515.31.
    
    FUNCTION ALLOWANCE 1S: 100 EUR/month for level-1S workers classified as Quadri (L. 190/1985), modelled as an allowance with role 'quadro' (compute(..., roles={'quadro'})).
    
    ADDITIONAL MONTHS: 14 (thirteenth + fourteenth month payment). Source: FLAI Veneto, confirmed by lexplain.it.
    
    SENIORITY: biennial cadence (24 months), maximum 5 increments. Post-2024-renewal amounts from FLAI Veneto (renewal 01/03/2024). valid_from 2023-12-01 assumed equal to the first TEM tranche; sources do not explicitly confirm the effective date of increments (alternative: 2024-03-01, signing date).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/alimentari-federalimentare.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/alimentari-federalimentare.py"
```
