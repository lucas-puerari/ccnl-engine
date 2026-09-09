# CCNL per i lavoratori addetti all'industria orafa, argentiera e della gioielleria (Federorafi)

| | |
|---|---|
| **CNEL code** | `C021` |
| **Sector** | industria |
| **Tax sector** | `industria` |
| **Last renewal** | — |
| **Workers (est.)** | ~18k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Federorafi
    - Fim-Cisl
    - Fiom-Cgil
    - Uilm-Uil

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
| `7Q` | Level 7Q — top-level quadri | € 2,405.58 | — |
| `7` | Level 7 — quadri with significant managerial functions | € 2,405.58 | — |
| `6` | Level 6 — employees with managerial functions or specialist technicians | € 2,212.40 | — |
| `5S` | Level 5 Superior — workers with qualified executive autonomy | € 2,058.07 | — |
| `5` | Level 5 — highly specialised workers and white-collar employees | € 1,928.22 | — |
| `4` | Level 4 — specialist workers and qualified employees | € 1,804.87 | — |
| `3` | Level 3 — skilled workers and employees | € 1,734.59 | — |
| `2` | Level 2 — general workers and clerical employees | € 1,574.39 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `2` | € 21.59 |
| `3` | € 25.05 |
| `4` | € 26.75 |
| `5` | € 29.64 |
| `5S` | € 32.43 |
| `6` | € 36.41 |
| `7` | € 40.96 |
| `7Q` | € 40.96 |

## Apprenticeship

**professionalizzante_standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `5S`, `6`, `7`, `7Q`  
percentage: 0.95

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    JUNE 2025 TRANCHE from kitech.it (secondary source, category code 51). 10.54% increase consistent across all levels with the IPCA+TEM mechanism. Values: 2=1574.39, 3=1734.59, 4=1804.87, 5=1928.22, 5S=2058.07, 6=2212.40, 7=2405.58, 7Q=2405.58.

!!! warning ""
    FUNCTION ALLOWANCE levels 7 and 7Q from kitech.it (secondary source). Level 7: 59.39 EUR/month ('ind_funzione'); level 7Q: 114.00 EUR/month ('ind_funzione_quadri'). No accessible primary source found for these amounts.

!!! warning ""
    MINIMUM 7Q equals 7a for all tranches (the CCNL does not publish a separate table for 7Q, which is the quadri level with individual pay management).

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2021-12-23 | [↗](https://www.uilmnazionale.it/wp-content/uploads/2022/01/20211223-CCNL-Orafi-ipotesi-di-rinnovo-apprendistato-firmato.pdf) |
| — | — | 2017-05-18 | [↗](https://www.fim-cisl.it/wp-content/uploads/2021/03/CCNL-orafi-argentieri-18-5-2017.pdf) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=51) |

??? note "Coverage notes"
    SALARY MODEL: conglobated (table minimum inclusive of contingenza and EDR). Source: CCNL 2021 PDF (UILM, signed 23/12/2021), pay tables pp. 4-5. Three tranches from primary source (Jun 2022, Jun 2023, Dec 2024); fourth tranche (Jun 2025) from kitech.it (secondary).
    
    LEVEL 1a REMOVED from 1 June 2022. Art. 4 of the 2021 renewal: workers at level 1a are reclassified to level 2a. The minimum active level post-June 2022 is level 2 (formerly 2a, €1363.86/month). Source: CCNL 2021 PDF Art. 4.
    
    HOURLY DIVISOR 173: confirmed by three independent primary sources — (1) CCNL 2021 PDF Annex 9 apprenticeship ('divisore 173'); (2) CCNL 2017 PDF Art. parental leave ('un centosettantreesimo 1/173'); (3) back-calculation on level 7a tables: 2083.89 / 173 = 12.05 EUR/h.
    
    ADDITIONAL MONTHS: 13 (tredicesima). Source: CCNL 2021 PDF, Annex 9 Art. 7 which refers to the CCNL provisions on the tredicesima.
    
    SENIORITY INCREMENTS: primary source — CCNL 2017 PDF (draft agreement 18/05/2017), General Provisions Section Three 'Aumenti Periodici di Anzianità', 'Valori mensili in vigore dal 1° gennaio 2002'. Confirmed: biennial cadence (24 months), maximum 5 bienniums per category. The 2021 renewal did not modify the increment amounts (not mentioned in the renewal economic clauses). Level Superior (5S) increment = 32.43 EUR confirmed from primary source — value 13.43 on secondary aggregators is incorrect. 7Q increment = 40.96 assumed equal to 7a (no explicit distinction in primary source).
    
    APPRENTICESHIP: three-period percentage (85%/90%/95%), standard duration 36 months. Primary source: CCNL 2021 PDF Annex 9 'Apprendistato professionalizzante'. Art. 4 Annex 9: 85% (months 1-12), 90% (months 13-24), 95% (months 25-36). Divisor 173 confirmed in the same Annex. The 36 months are stated as maximum duration; shorter individual contracts would pro-rate the bands — modelled as a fixed standard track (full 36 months).
    
    ULTRA-ACTIVITY: the 2026 renewal (signed 10/02/2026) has economic effects from 01/10/2026. The 2021 contract governs economically until 30/09/2026. The 2002 increments (from CCNL 2017 PDF) remain operative throughout the modelled period as neither the 2021 nor the 2026 renewal modified them.
    
    INPS: industry sector rates from 2026-industria.json (existing file reused). Employee 9.19%; employer: ≤15 employees 30.13%, 16-50 employees 30.20%, >50 employees 30.50%.
    
    COMETA: supplementary pension fund (Art. 44 CCNL 2021 PDF). Employer 2.00% (from Dec 2024), employee 1.20%. Not modelled in the engine (Layer 3, out of scope).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/orafi-argentieri-industria-federorafi.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/orafi-argentieri-industria-federorafi.py"
```
