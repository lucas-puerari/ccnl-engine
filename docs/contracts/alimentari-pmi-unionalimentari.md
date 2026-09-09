# CCNL Dipendenti Piccola e Media Industria Alimentare (Unionalimentari-Confapi)

| | |
|---|---|
| **CNEL code** | `E018` |
| **Sector** | Alimentare |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-28 |
| **Workers (est.)** | ~35k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - UNIONALIMENTARI-CONFAPI
    - FAI-CISL
    - FLAI-CGIL
    - UILA-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | — out_of_scope |
| **L3 — Work rules** | ✅ implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri (executive staff) | € 2,870.86 | — |
| `1` | 1st level — senior specialists and team leaders | € 2,770.86 | — |
| `2` | 2nd level — skilled specialists | € 2,409.42 | — |
| `3` | 3rd level — intermediate skilled workers | € 1,987.80 | — |
| `4` | 4th level — qualified workers | € 1,746.87 | — |
| `5` | 5th level — semi-skilled workers | € 1,566.15 | — |
| `6` | 6th level — standard production workers | € 1,445.65 | — |
| `7` | 7th level — basic production workers | € 1,325.20 | — |
| `8` | 8th level — entry-level workers, simple repetitive tasks | € 1,204.73 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 54.62 |
| `1` | € 51.42 |
| `2` | € 44.71 |
| `3` | € 36.89 |
| `4` | € 32.42 |
| `5` | € 29.06 |
| `6` | € 26.83 |
| `7` | € 24.59 |
| `8` | € 22.35 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Settore panificazione industriale (7 levels: 1, 3A, 3B, 4, 5, 6, plus viaggiatori) not modeled — separate salary tables; only settore alimentare 9 levels implemented.

!!! warning ""
    SIMPLIFICATION: Tranche 3 (01/04/2027) and tranche 4 (01/01/2028) not modeled. The circular text states tranche 3 as EUR 32 at parametro 137 (level 8 equivalent), but the per-level table shows the same 74.09 EUR increment as all other tranches for every level including level 4. Text and table are irreconcilable without a clarification from Unionalimentari. Engine returns Jan 2026 amounts for dates on or after 2026-01-01.

!!! warning ""
    SIMPLIFICATION: EGR (elemento di garanzia retributiva) increase of EUR 10 at parametro 137 from 01/01/2027 not modeled — amount per level not yet in a confirmed per-level table.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-28 | [↗](https://www.unionalimentari.com/) |
| — | — | 2021-04-01 | [↗](https://www.lavorofacile.it/) |

??? note "Coverage notes"
    Salary model: split. base_salary = paga base (changes each tranche); fixed_allowances = contingenza (per-level, frozen since 1993 Protocol) + EDR 10.33 (all levels, per Protocol 31/07/1992 Art. 1.1).
    
    Hourly divisor 173 confirmed from primary source: Art. 4.3 CCNL text (lavorofacile.it). Cross-check: level 8 Jan 2026 total = 1204.73 + 514.74 + 10.33 = 1729.80; 1729.80 / 173 = 10.00 EUR/h exactly. Art. 4.4 sets the normal workweek at 39h; computing 39 x 52 / 12 = 169h/month, not 173. The CCNL resolves this by stating the coefficient explicitly in Art. 4.3 — the arithmetic cross-check confirms 173 is the operative value.
    
    Additional months: 14 confirmed from Art. 4.1 CCNL text (mensilita: 14). Art. 5.3 = tredicesima, Art. 5.4 = quattordicesima.
    
    Seniority: 5 biennali per Art. 5.5 CCNL text (settore alimentare). Fixed EUR amounts from 2021 CCNL; 2025 Unionalimentari circular (28/05/2025) makes no mention of changes to scatti amounts.
    
    Salary tranches from CIRCOLARE ILLUSTRATIVA ACCORDO 28 MAGGIO 2025 (Unionalimentari official circular): tranche 1 = 01/06/2025, tranche 2 = 01/01/2026, tranche 3 = 01/04/2027 (not modeled), tranche 4 = 01/01/2028 (not modeled).
    
    Apprenticeship: Art. 8.1 CCNL — under-classification model, levels 1 through 7, multi-period per destination level. Complex schedule not publicly parsed in full. layer_2 = out_of_scope.
    
    Headcount: ~34,646 workers (CNEL archive, E018).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/alimentari-pmi-unionalimentari.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/alimentari-pmi-unionalimentari.py"
```
