# CCNL Metalmeccanica - Cooperative

| | |
|---|---|
| **CNEL code** | `C016` |
| **Sector** | metalmeccanico cooperativo |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~28k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Legacoop Produzione e Servizi
    - Confcooperative Lavoro e Servizi
    - AGI Produzione e Lavoro
    - FIM-CISL
    - FIOM-CGIL
    - UILM-UIL

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
| `A1` | Livello A1 — quadro superiore, massima responsabilita gestionale | € 3,177.92 | — |
| `B3` | Livello B3 — quadro intermedio, caposquadra o coordinatore di gruppo | € 2,883.46 | — |
| `B2` | Livello B2 — specialista senior o responsabile di funzione | € 2,651.95 | — |
| `B1` | Livello B1 — specialista o tecnico con responsabilita di progetto | € 2,471.90 | — |
| `C3` | Livello C3 — tecnico o impiegato di concetto con autonomia operativa | € 2,306.18 | — |
| `C2` | Livello C2 — operatore polivalente, mansioni di concetto | € 2,153.36 | — |
| `C1` | Livello C1 — operatore specializzato, mansioni tecnico-pratiche | € 2,108.77 | — |
| `D2` | Livello D2 — operatore qualificato, mansioni esecutive | € 2,064.18 | — |
| `D1` | Livello D1 — operatore comune, mansioni semplici e ripetitive | € 1,861.42 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `D1` | € 21.59 |
| `D2` | € 25.05 |
| `C1` | € 25.90 |
| `C2` | € 26.75 |
| `C3` | € 29.64 |
| `B1` | € 32.43 |
| `B2` | € 36.41 |
| `B3` | € 40.96 |
| `A1` | € 45.96 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `D2`, `C1`, `C2`, `C3`, `B1`, `B2`, `B3`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP: percentages (85/90/95% over 36 months) modelled as C011 Federmeccanica (accordo 20/04/2021). No independent C016-specific source found in 2025 renewal documentation. Checked: ecnews.it (renewal article), dottrinalavoro.it, ilccnl.it (two URL paths), kitech.it CodiceCateg=48. Destination levels D2-B3 mirror C011; D1 and A1 excluded as in C011.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-07-22 | [↗](https://geps.it/rinnovo-ccnl-metalmeccanica-cooperative-2025-2028-10377/) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=48) |
| — | — | 2025-07-22 | [↗](https://www.fiom-cgil.it/net/cooperative/trattativa-coop/11211-ccnl-cooperative-incrementi-salariali-e-nuovi-minimi-retributivi) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2025-07-22 by Legacoop Produzione e Servizi, Confcooperative Lavoro e Servizi, AGI Produzione e Lavoro with FIM-CISL, FIOM-CGIL and UILM-UIL. Validity 17/06/2025-30/06/2028. First tranche retroactive to 2025-06-01.
    
    CONGLOBATED MINIMUMS: base_salary values are the consolidated 'minimi contrattuali', incorporating all salary components (paga base, contingenza, EDR) into a single figure, consistent with the metalmeccanici industry practice adopted since 1993. No separate contingenza or EDR column appears in any source table.
    
    FIXED ALLOWANCES: A1 (+180 EUR indennita di funzione) and B3 (+120 EUR indennita di funzione) are paid in addition to base_salary, per kitech.it (CodiceCateg=48), which lists them as separate columns. C011 (Federmeccanica) omits these from its JSON; C016 models them explicitly for accuracy.
    
    SENIORITY: biennali scatti (cadence 24 months), maximum 5 per level. Amounts per level confirmed on kitech.it CodiceCateg=48.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). No quattordicesima in any source. Consistent with C011 federmeccanica structure.
    
    HOURLY DIVISOR: 173 h/month (40 h/week standard, same as C011). Confirmed on kitech.it.
    
    INPS: employer rates from 2026-industria.json (same tax sector as C011). Cooperative employers may have different INPS addizionale rates; this is a SIMPLIFICATION — verify against INPS circular for cooperative sector if precise employer cost is critical.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/metalmeccanica-cooperative.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/metalmeccanica-cooperative.py"
```
