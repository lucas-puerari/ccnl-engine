# CCNL Comparto Funzioni Locali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S105` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~400k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - UIL FPL
    - CSA RAL

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
| `FUNZIONARI_EQ` | Funzionari ed Elevata Qualificazione (ex Area D) | € 2,092.84 | — |
| `ISTRUTTORI` | Istruttori (ex Area C) | € 1,928.23 | — |
| `OPERATORI_ESPERTI` | Operatori Esperti (ex Area B) | € 1,715.27 | — |
| `OPERATORI` | Operatori (ex Area A) | € 1,646.09 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CNEL code S105 from secondary source (lavoro-economia.it). Not stated in official PDF.

!!! warning ""
    Pre-2024 base values derived by back-calculation; 2022-2023 anticipation payments (Art. 47-bis D.Lgs. 165/2001) not modelled as intermediate periods.

!!! warning ""
    Indennità di comparto post-conglobamento (Tabella C col.4) fully charged to Fondo risorse decentrate — not modelled as a fixed_allowance (varies by administration and is not a universal fixed amount).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-23 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/CCNL-Comparto-2022-2024-23-02-26.pdf) |
| — | — | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=396) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Seniority via differenziali stipendiali (Art. 14 and Art. 78 CCNL 16.11.2022): selective procedure, not automatic — maximum_count=0.
    
    Salary tables from CCNL Comparto Funzioni Locali 2022-2024 (ARAN, 23.02.2026). Art. 56 Tabella A (monthly increments per 13 months) and Tabella B (annual amounts per 12 months + 13th). Monthly values = Tabella B / 12.
    
    Tranche 1 (2022-11-16) values back-calculated from CCNL 16.11.2022 base by subtracting Tabella A col.1 increments from 2024-01-01 values. The 2022 and 2023 anticipation payments (Art. 56, alinea 1-2) are not modelled as separate tabellare periods.
    
    Tranche 3 (2027-01-01) from parziale conglobamento indennità di comparto (Art. 60): Tabella B col.2 / 12. Effective from 1 January of the year following CCNL signature (2026 → 2027-01-01).
    
    Hourly divisor 156 from Art. 74 CCNL 16.11.2022 (36h/week standard working time for comparto Funzioni Locali).
    
    13 mensilità confirmed by Art. 56 comma 1 terzo alinea ('per tredici mensilità') and Tabella A header.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/funzioni-locali-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/funzioni-locali-aran.py"
```
