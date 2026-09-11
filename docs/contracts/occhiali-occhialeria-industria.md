# CCNL Occhiali e Occhialeria — Industria (ANFAO)

| | |
|---|---|
| **CNEL code** | `D271` |
| **Sector** | industria occhialeria e ottica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~20k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🟢 Verified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANFAO
    - Filctem-CGIL
    - Femca-CISL
    - UilTEC-UIL

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
| `Q` | Quadro — Lavoratori con responsabilita di direzione e coordinamento (Art. 2095 c.c.) | € 2,680.72 | — |
| `6` | Livello 6 — Lavoratori con autonomia decisionale e competenze trasversali elevate | € 2,670.80 | — |
| `5S` | Livello 5 Super — Lavoratori con funzioni tecniche o di supervisione avanzata | € 2,540.00 | — |
| `5` | Livello 5 — Lavoratori con funzioni di controllo o alta specializzazione | € 2,453.48 | — |
| `4S` | Livello 4 Super — Lavoratori con elevata specializzazione o coordinamento | € 2,280.32 | — |
| `4` | Livello 4 — Lavoratori polivalenti o con responsabilita tecnica | € 2,187.96 | — |
| `3S` | Livello 3 Super — Lavoratori specializzati di livello superiore | € 2,125.83 | — |
| `3` | Livello 3 — Lavoratori specializzati con autonomia operativa | € 2,082.62 | — |
| `2` | Livello 2 — Lavoratori qualificati con conoscenze specifiche | € 1,966.32 | — |
| `1` | Livello 1 — Lavoratori addetti a mansioni semplici e ripetitive | € 1,712.04 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 6.84 |
| `2` | € 7.36 |
| `3` | € 7.80 |
| `3S` | € 7.80 |
| `4` | € 8.26 |
| `4S` | € 8.26 |
| `5` | € 9.76 |
| `5S` | € 9.76 |
| `6` | € 11.65 |
| `Q` | € 11.65 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `1`, `2`, `3`, `3S`, `4`, `4S`, `5`, `5S`, `6`, `Q`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP: 2026 rinnovo (signed 30/01/2026) explicitly 'abroga la ripartizione in percentuale in relazione agli step professionali' (edotto.com). Pre-2026 CCNL used a percentage system. Post-2026 replacement type is not confirmed from a D271 primary source — the cognate piccola industria (ccnlportatili.it) uses sotto-inquadramento (2 levels below for first 12m, 1 level below for next 12m, then destination). Modelled as 100% passthrough for all levels pending primary source confirmation; this is a conservative over-estimate for the 2026-2028 period.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-04 | [↗](https://italpaghe.ilccnl.it/ccnl/occhiali---industria/occhiali---industria/tabelleretributive) |
| — | — | 2026-01-30 | [↗](https://www.cisl.it/ccnl-occhiali-sindacati-sottoscritta-ipotesi-accordo-per-rinnovo-contratto-204e-laumento-del-complessivo-triennio-2026-2028/) |

??? note "Coverage notes"
    CCNL signed 04/12/2023 valid 01/01/2023-31/12/2025; renewed 30/01/2026 valid 01/01/2026-31/12/2028 (ANFAO+Filctem-CGIL+Femca-CISL+UilTEC-UIL).
    
    CONGLOBATED (since 01/01/2009): contingenza and EDR are inglobated into the tabular minimum. Single base_salary column per level; no separate contingenza allowance.
    
    Level Q (Quadro): indennita di funzione +82.63 EUR/month on top of the tabular minimum (all tranches). Modelled as INDENNITA_FUNZIONE fixed allowance, months_per_year=13.
    
    HOURLY DIVISOR: 173 (standard 40h/week). Shift workers on 6x6 turns use divisor 156; engine models the 173 case uniformly.
    
    SENIORITY: 5 biennali (24-month) scatti. Per-level amounts (EUR): 1=6.84, 2=7.36, 3=3S=7.80, 4=4S=8.26, 5=5S=9.76, 6=Q=11.65.
    
    LEVEL 1 sub-level: the CCNL provides automatic advancement from entry sub-level (L1 ingresso) to L1 standard after 6 months. The file models only the post-advance minimum throughout, which is the relevant value for permanent workers and for workers beyond their 6th month. The entry sub-level undervaluation during the first 6 months is a deliberate structural simplification.
    
    TRANCHES 01/10/2026 through 01/11/2028: L4 reference increments confirmed from primary source (CISL communique CCNL occhialeria 30/01/2026: +30, +50, +45, +20 EUR at L4). All-level amounts derived via the parametric ratio matrix from confirmed 01/03/2026 per-level deltas. The CCNL occhialeria uses a declared parametric system; parametric derivation is contractually consistent.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/occhiali-occhialeria-industria.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/occhiali-occhialeria-industria.py"
```
