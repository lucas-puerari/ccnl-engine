# CCNL Gomma e Plastica Industria (Federazione Gomma Plastica)

| | |
|---|---|
| **CNEL code** | `B371` |
| **Sector** | gomma-plastica |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~90k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federazione Gomma Plastica
    - FILCTEM-CGIL
    - FEMCA-CISL
    - UILTEC-UIL

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
| `Q` | Q — senior manager grade (quadro under L. 190/1985), highest responsibility | € 2,664.67 | — |
| `A` | A — quadro, highly specialised technical or functional expert | € 2,508.94 | — |
| `B` | B — technical or administrative manager, high professional grade | € 2,366.94 | — |
| `C` | C — department head, white-collar employee with operational autonomy | € 2,335.85 | — |
| `D` | D — team leader, qualified technical/administrative employee | € 2,306.50 | — |
| `E` | E — highly skilled worker, expert technical employee | € 2,213.42 | — |
| `F` | F — skilled worker, technical employee (CCNL reference level) | € 2,156.12 | — |
| `G` | G — qualified worker 2nd category, white-collar employee | € 2,009.25 | — |
| `H` | H — qualified worker 1st category, clerical staff | € 1,916.08 | — |
| `I` | I — elementary tasks, simple operations with brief training | € 1,722.59 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 20.14 |
| `A` | € 18.59 |
| `B` | € 16.53 |
| `C` | € 16.53 |
| `D` | € 16.53 |
| `E` | € 13.94 |
| `F` | € 13.94 |
| `G` | € 13.43 |
| `H` | € 11.88 |
| `I` | € 10.33 |

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `G`, `F`, `E`, `D`, `C`, `B`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    TRANCHE DATES 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026 from lexplain.it and kitech.it. Future tranches 01.04.2027, 01.04.2028, 01.12.2028 from the rinnovo 10.12.2025 (fiscoetasse.com, paserio.it): F +60, +60, +15; other levels derived parametrically via the stable coefficients (possible ±0.01 EUR rounding differences).

!!! warning ""
    APPRENTICESHIP under_classification (art. apprendistato professionalizzante CCNL Gomma e Plastica; rule from contratticcnl.it: the apprentice cannot be classified more than two levels below the destination). Track 'professionalizzante' for destinations G, F, E, D, C, B: 0-12 months two levels below, 12-24 one level below, then destination. The 12/12 boundaries are an approximation (no public monthly table). H (only one level below exists), I, A and Q are not modelled as destinations.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | — | [↗](https://www.lexplain.it/tabelle-retributive-gomma-plastica/) |
| — | — | 2025-12-10 | [↗](https://www.contratticcnl.it/gomma-plastica/tabelle-retributive/) |
| — | — | 2026-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=156) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (TEM — Trattamento Economico Minimo). All base_salary values incorporate paga base, contingenza, and EDR in a single figure. Evidence: the F/level coefficient ratio is stable to 4 decimal places across all 4 tranches (2023-2026), which is only possible in a fully parametric (conglobated) system. fixed_allowances is empty for all levels except Q.
    
    CONGLOBATED CHECK: coefficient ratios computed as level_value / F_value for all tranches. Q/F=1.2359, A/F=1.1636, B/F=1.0978, C/F=1.0834, D/F=1.0697, E/F=1.0266, G/F=0.9319, H/F=0.8887, I/F=0.7989 — identical across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026. This confirms conglobated model.
    
    SENIORITY amounts unchanged across 01.01.2023, 01.01.2024, 01.04.2025, 01.01.2026: the January 2023 rinnovo and December 2025 rinnovo both addressed only TEM (minimi tabellari) and left Art.23 (scatti di anzianità) untouched. Amounts at kitech.it/lavoro-economia.it apply from at least 01.01.2023 onward. Source: rinnovo 10.12.2025 full text (filctemcgil.it); rinnovo Jan 2023 summary (terzomillennio.uil.it); no source reports scatti change in either rinnovo.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Federazione Gomma Plastica is a member of Confindustria; CIGO applicable pursuant to D.Lgs. 148/2015.
    
    ADDITIONAL MONTHS: 13 (tredicesima). A quattordicesima is not provided for by the CCNL Gomma e Plastica Industria.
    
    HOURLY DIVISOR 173 derived from the standard formula (40h/week x 52 / 12 = 173.33 rounded to 173); secondary sources (contratticcnl.it, fiscoetasse.com) confirm the 40h week but the contractual clause was not retrieved directly.
    
    Q LEVEL INDENNITA' DI FUNZIONE 50.00 EUR/month (quadri ex L. 190/1985), cross-verified at April 2025 (lexplain.it total 2473.68 vs contratticcnl.it TEM 2423.68). valid_from set to 2023-01-01 for consistency with the first modelled tranche; not verified whether the amount was already 50 EUR in 2023.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/gomma-plastica-federazione-gomma-plastica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/gomma-plastica-federazione-gomma-plastica.py"
```
