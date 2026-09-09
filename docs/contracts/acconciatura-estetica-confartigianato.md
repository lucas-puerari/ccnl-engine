# CCNL Acconciatura ed Estetica — Confartigianato/CNA

| | |
|---|---|
| **CNEL code** | `H515` |
| **Sector** | acconciatura ed estetica |
| **Tax sector** | `artigianato` |
| **Last renewal** | — |
| **Workers (est.)** | ~95k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Benessere-Acconciatori
    - CNA Unione Benessere e Sanità
    - Casartigiani
    - CLAAI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| `1` | Level 1 — technical director / senior supervisor | € 1,722.76 | — |
| `2` | Level 2 — specialist worker / technical supervisor | € 1,573.78 | — |
| `3` | Level 3 — qualified worker (hairdresser/beautician) | € 1,492.00 | — |
| `4` | Level 4 — auxiliary worker / entry-level apprentice | € 1,406.73 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `4` | € 7.23 |
| `3` | € 7.75 |
| `2` | € 8.26 |
| `1` | € 9.30 |

## Apprenticeship

**gruppo_1** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_2** (type: `percentage`)  
Destination levels: `3`  
percentage: 1.00

**gruppo_3** (type: `percentage`)  
Destination levels: `2`  
percentage: 0.85

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    APPRENTICESHIP Gruppo 2 (manicure/pedicure → level 3, max 18 months, 70%/80%/100%), track 'gruppo_2': the three percentages are mapped to 6-month periods (0-6, 6-12, 12-18). Select with Apprentice(track='gruppo_2'); without a track name level 3 is ambiguous.

!!! warning ""
    APPRENTICESHIP DURATION (TAB.3): the 6-month reduction for post-secondary qualification holders (Gruppo 1: 54 months instead of 60) is not modelled; the standard 60-month table applies.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-05-20 | [↗](https://www.confartigianatomarcatrevigiana.it/wp-content/uploads/2024/09/ccnl-benessere-app.prof-fino-30.9.24.pdf) |
| — | — | 2024-05-20 | [↗](https://www.studiomion.it/tabelle-retributive/tabelle-retributive-acconciatura-estetica/) |
| — | — | — | [↗](https://www.ilccnl.it/contratto/acconciatura-estetica/) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (minimi tabellari conglobati — contingenza and EDR fully absorbed). Back-calculation: May 2024 L3=1379.00/173=7.97 EUR/h; L2=1454.58/173=8.41 EUR/h; L1=1592.29/173=9.20 EUR/h — consistent divisor confirms conglobated model (lexplain.it + ilccnl.it).
    
    TRANCHE DATES: four tranches — 2024-05-01 (retroactive, renewal signed 20 May 2024), 2025-01-01, 2026-01-01, 2026-10-01. Source: studiomion.it salary tables; cross-checked ilccnl.it for Jan 2026 values.
    
    HOURLY DIVISOR: 173, derived from 40-hour work week (Art. 12 CCNL). Formula: 40 h/week × 52/12 = 173.33, rounded to 173 per contract usage. Confirmed: 1379.00/7.97=173.0 (L3 May 2024).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: ilccnl.it Art. 40; informaimpresa.it ('tredici mensilità' explicitly stated as basis for Responsabile Tecnico allowance calculation).
    
    SENIORITY: biennale (every 24 months), maximum 5 scatti. Per-level amounts: L1=9.30, L2=8.26, L3=7.75, L4=7.23 EUR/scatto. Source: ilccnl.it (current database), cross-checked CISL 2013 PDF (amounts unchanged by 2024 renewal, which only introduced a 6 EUR apprentice-specific scatto).
    
    APPRENTICESHIP Gruppo 1 (acconciatori, estetisti, tricologi, tatuatori → destination level 3, max 5 years), track 'gruppo_1'. Primary source: Confartigianato Marca Trevigiana PDF (ccnl-benessere-app.prof-fino-30.9.24.pdf) for the pre-Oct-2024 table; post-Oct-2024 update (filcams.cgil.it + fisascat.it) raised months 1-12 from 65% to 70%, making months 1-18 uniformly 70%. Modelled table: 0-18=70%, 18-24=78%, 24-36=85%, 36-48=90%, 48-54=95%, 54+=100%.
    
    APPRENTICE SENIORITY: apprentice-specific scatto of 6 EUR (Art. 25 of the 2024 renewal, from 2024-10-01) modelled as seniority_increments.apprentice_amount.
    
    RESPONSABILE TECNICO: 100 EUR x 13 mensilità for workers designated Responsabile Tecnico at level 1 or 2, modelled as a role-scoped allowance (role 'responsabile_tecnico').
    
    PRE-MAY-2024 SALARY: the final tranche of the 2022 renewal (from 2023-02-01: L1=1511.46, L2=1380.74, L3=1309.00, L4=1234.19) is modelled; earlier periods are not.
    
    INPS: reuses 2026-artigianato.json (ARTIGIANATO sector).
    
    APPRENTICESHIP Gruppo 3 (impiegati amministrativi, destination level 2, 3 anni / 6 semestri): 70/70/70/78/85/85 per semester. Source: consulenza.it circolare acconciatura 2024; lexplain.it tabella apprendistato acconciatori (medium-high confidence: two concordant secondary sources; primary accordo tables not online).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/acconciatura-estetica-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/acconciatura-estetica-confartigianato.py"
```
