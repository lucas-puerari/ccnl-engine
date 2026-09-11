# CCNL Scuole Private Laiche (ANINSEI-Assoscuola)

| | |
|---|---|
| **CNEL code** | `T231` |
| **Sector** | istruzione privata laica |
| **Tax sector** | `terziario` |
| **Last renewal** | — |
| **Workers (est.)** | ~25k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ANINSEI
    - Assoscuola
    - UIL Scuola RUA
    - CONFSAL-SNALS
    - ANIEF

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
| `VIII_B` | Livello VIII B — quadro superiore con massima responsabilita gestionale | € 1,819.62 | — |
| `VIII_A` | Livello VIII A — quadro superiore, direttore o responsabile di sede | € 1,725.56 | — |
| `VII` | Livello VII — quadro intermedio, responsabile di plesso o coordinatore | € 1,646.17 | — |
| `VI` | Livello VI — docente coordinatore o tecnico senior con responsabilita | € 1,619.64 | — |
| `V` | Livello V — docente o impiegato di concetto con autonomia operativa | € 1,619.64 | — |
| `IV` | Livello IV — impiegato o tecnico di concetto | € 1,519.52 | — |
| `III` | Livello III — operatore specializzato, mansioni tecnico-pratiche | € 1,446.24 | — |
| `II` | Livello II — operatore qualificato, mansioni esecutive di supporto | € 1,379.61 | — |
| `I` | Livello I — personale ausiliario e operatore generico | € 1,347.46 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 0.00 |
| `II` | € 0.00 |
| `III` | € 0.00 |
| `IV` | € 0.00 |
| `V` | € 0.00 |
| `VI` | € 0.00 |
| `VII` | € 0.00 |
| `VIII_A` | € 0.00 |
| `VIII_B` | € 0.00 |

## Apprenticeship

**professionalizzante_36** (type: `percentage`)  
Destination levels: `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII_A`, `VIII_B`  
percentage: 1.00

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-06-15 | [↗](https://foe.it/files/2024/07/CCNL-ANINSEI_2024-2027cd.pdf) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2024-06-15 by ANINSEI and Assoscuola with UIL Scuola RUA, CONFSAL-SNALS and ANIEF. Validity 01/01/2024-31/12/2027. Economic effects from 01/01/2025.
    
    CONGLOBATED MINIMUMS (Art. 23): contingenza maturata al 30/11/1991 comprensiva dell'EDR e' inglobata nella retribuzione tabellare (Art. 22). Values are fully conglobated — no separate contingenza or EDR column.
    
    SALARY TABLE (Art. 22): four tranches. Carry-over base from old CCNL 2021-2023 dal 01/09/2023 applies from 2024-06-15 to 2024-12-31. All four tranches read directly from Art. 22 table in PDF (pdftotext -layout, pages 51-53).
    
    HOURLY DIVISOR (Art. 27): 165 h/month for 38h/week full-time. The contract table lists divisors for reduced weekly hours (36h=156, 34h=147, 32h=139, 24h=104, 21h=91, 18h=78); each is 165 scaled by hours/38, matching part_time_pct equivalents. hourly_divisor=165 is exact — no simplification.
    
    ADDITIONAL MONTHS (Art. 21): 13 (tredicesima only, paid by 16 December).
    
    SENIORITY (Art. 24): salario di anzianita frozen as of 2025-01-01, milestone-based (hire-date brackets). Workers with 2+ years continuous service at 01/01/2025 receive 20 EUR/month; pre-2002 hires up to 90 EUR/month (grandfathered). New hires after ~2023-01-01 receive nothing. maximum_count=0 correctly models new-hire case (zero seniority). The engine cadence model cannot express hire-date milestones: long-tenure workers are understated. Structural engine limitation — no data gap.
    
    APPRENTICESHIP (Art. 9.7): percentages 85/90/100% over 36 months confirmed from Art. 9.7 of ANINSEI CCNL 2024-2027 PDF. Destination level list not specified in available pages; all nine levels modelled as destinations (conservative assumption — no restriction applied). This may overstate eligible levels but never understates payroll cost.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/scuole-private-laiche-aninsei.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/scuole-private-laiche-aninsei.py"
```
