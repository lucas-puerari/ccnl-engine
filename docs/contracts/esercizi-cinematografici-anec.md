# CCNL Esercizi Cinematografici e Cinema-Teatrali (ANEC)

| | |
|---|---|
| **CNEL code** | `G211` |
| **Sector** | cinema |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~6k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANEC
    - FISTel CISL
    - UILCOM UIL

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
| `QA` | Quadro A — Multiplex/Megaplex (parametro 240) | € 2,103.45 | — |
| `QB` | Quadro B — Multiplex/Megaplex (parametro 220) | € 1,970.12 | — |
| `Q` | Quadro — Monosala/Multisala (parametro 220) | € 1,970.12 | — |
| `F` | Livello F — Multiplex/Megaplex (parametro 185) | € 1,736.47 | — |
| `5S` | V livello superiore — Monosala/Multisala (parametro 185) | € 1,736.47 | — |
| `5` | V livello — Monosala/Multisala (parametro 176) | € 1,677.32 | — |
| `E` | Livello E — Multiplex/Megaplex (parametro 165) | € 1,603.17 | — |
| `4` | IV livello — Monosala/Multisala (parametro 159) | € 1,563.49 | — |
| `D` | Livello D — Multiplex/Megaplex (parametro 150) | € 1,503.61 | — |
| `C` | Livello C — Multiplex/Megaplex (parametro 140) | € 1,436.95 | — |
| `3` | III livello — Monosala/Multisala (parametro 132) | € 1,383.48 | — |
| `B` | Livello B — Multiplex/Megaplex (parametro 122) | € 1,316.62 | — |
| `2` | II livello — Monosala/Multisala (parametro 112) | € 1,249.95 | — |
| `A` | Livello A — Multiplex/Megaplex (parametro 100) | € 1,170.00 | — |
| `1` | I livello — Monosala/Multisala (parametro 100) | € 1,170.00 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 13.26 |
| `A` | € 13.26 |
| `2` | € 14.37 |
| `B` | € 15.38 |
| `3` | € 16.34 |
| `C` | € 17.11 |
| `D` | € 18.07 |
| `4` | € 18.96 |
| `E` | € 19.52 |
| `5` | € 20.62 |
| `5S` | € 21.45 |
| `F` | € 21.45 |
| `Q` | € 24.82 |
| `QB` | € 24.82 |
| `QA` | € 26.75 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `1`, `A`, `2`, `B`, `3`, `C`, `D`, `4`, `E`, `5`, `5S`, `F`, `Q`, `QB`, `QA`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: tax_sector=TERZIARIO. Cinema exhibition employees (esercizio cinematografico) were historically under ENPALS (now FPLS — Fondo Pensione Lavoratori dello Spettacolo dell'INPS, Art. 12 comma 6 of this CCNL). The FPLS contribution regime differs from ordinary terziario. terziario rates are used as an approximation pending a dedicated cinema-FPLS tax file.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-16 | [↗](https://www.fistelcisl.it/wp-content/uploads/2025/10/CCNL-Esercizi-cinematografici-2023-2026.pdf) |

??? note "Coverage notes"
    Two parallel level systems in the same contract (one CNEL code G211): Monosala/Multisala (7 levels: 1,2,3,4,5,5S,Q with parametri 100/112/132/159/176/185/220) and Multiplex/Megaplex (8 levels: A,B,C,D,E,F,QB,QA with parametri 100/122/140/150/165/185/220/240). The 15 levels are interleaved by salary for ordering (non-decreasing constraint). Levels 1 and A share identical salaries (parametro 100), as do 5S and F (parametro 185) and Q and QB (parametro 220). Level QA (parametro 240) is Multiplex/Megaplex only. The 'order' field is a global salary rank across both classification scales and is not a promotion ladder.
    
    Level code aliases in the PDF: monosala Q is also written 'VI Qua' in the paga table header and '6' in Tabella B. Code 'Q' (Tabella A label) is used consistently here.
    
    Workers: 6,427 (ADAPT 18th Report, CNEL aggiornamento 31/12/2023).
    
    Primary source: CCNL Esercizi Cinematografici 2023-2026 (FISTel CISL, signed 16/10/2025). Art. 54: period 01/01/2023-31/12/2026. Three salary tranches: 01/01/2023, 01/11/2024, 01/07/2025 from salary tables (pages 59-65 of the PDF). Baseline (31/12/2022 column) used only for increment verification, not modelled as a separate period.
    
    Hourly divisor 173: Art. 63 Dichiarazione a verbale (explicit formula: 'la retribuzione oraria si ottiene dividendo quella mensile per il coefficiente 173'). Daily divisor 26 also from Art. 63.
    
    Additional months 14: Art. 20 (tredicesima, December) and Art. 21 (quattordicesima, paid 1 luglio each year).
    
    Seniority (Art. 22): biennale (cadence 24 months), maximum 5 scatti. Amounts from Tabella A (appended to CCNL). Cross-verified against Art. 62 (Indennita di Cassa 'Sola P.B.' table): Tabella A formula is 5% of frozen paga base (Art. 62 column) plus a fixed addend (3.62 for monosala L3, confirming 12.72+3.62=16.34). The salary table bottom row shows 16.26 for monosala L3 (IV scatto basis) — this is a typographic error; Tabella A value 16.34 is authoritative.
    
    Apprenticeship (Art. 16): percentage type, 70%/80%/90% for years 1/2/3 of the apprenticeship, calculated on the minimo salariale of the classification level. In vigore dal 01/01/2018. Applicable to all 15 levels (Art. 16 states no level exclusion).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/esercizi-cinematografici-anec.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/esercizi-cinematografici-anec.py"
```
