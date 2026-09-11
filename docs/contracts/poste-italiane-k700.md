# CCNL Poste Italiane S.p.A. (personale non dirigente)

| | |
|---|---|
| **CNEL code** | `K700` |
| **Sector** | Servizi postali |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-23 |
| **Workers (est.)** | ~117k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - POSTE ITALIANE S.p.A.
    - SLP-CISL
    - SLC-CGIL
    - UIL Poste

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
| `A1` | Livello A — posizione retributiva A1 | € 2,169.37 | — |
| `A2` | Livello A — posizione retributiva A2 | € 1,926.89 | — |
| `B` | Livello B | € 1,652.98 | — |
| `C` | Livello C | € 1,522.56 | — |
| `D` | Livello D | € 1,452.20 | — |
| `E` | Livello E | € 1,287.61 | — |
| `F` | Livello F | € 1,154.49 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B`, `C`, `D`, `E`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: EDR (elemento distintivo della retribuzione) omitted. Art. 65 I qualifies it as 'ove spettante'; amount not stated in Allegato 9 or CCNL body. Legacy entitlement for pre-privatization workers only.

!!! warning ""
    SIMPLIFICATION: INPS industria rates applied. Poste Italiane employees are enrolled in the Fondo Quiescenza Poste (INPS special fund, Art. 7 L. 335/1995; merged from IPOST 2012). Correct rates differ from standard industria rates. Verify against INPS Fondo Quiescenza Poste documentation. Verified 2026-09-09: INPS website confirms Fondo Quiescenza Poste exists for Poste Italiane SpA but specific aliquote not publicly listed on INPS portal in machine-readable form.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-07-23 | [↗](https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = minimo tabellare (Allegato 9, changes each tranche); fixed_allowances = contingenza (per-level, frozen) + indennità di funzione for A1/A2 (months_per_year=12).
    
    Hourly divisor 156 from Art. 65 III: retribuzione base oraria = mensile / 156. Cross-check: 36h/week × 52/12 = 156 h/month (Art. 26 normal workweek = 36h).
    
    Additional months: 14. Art. 67 tredicesima: base = posizione retributiva + contingenza + EDR — funzione excluded. Art. 68 quattordicesima: same explicit enumeration. Both articles confirm funzione not in mensilità aggiuntive.
    
    Seniority: no traditional scatti di anzianità for new hires. Retribuzione individuale di anzianità (D.P.R. 335/1990) is a legacy element for pre-privatization workers only (Art. 25 CCNL). Model: cadence_months=24, maximum_count=0.
    
    A1/A2 levels: paga base and contingenza are identical for staff and produzione; funzione differs (Art. 21 CCNL). Modeled as two-tier allowances: base rate (staff, unconditional) + produzione delta via role="produzione". Pass Employee(roles=frozenset(["produzione"])) to add the differential.
    
    Apprenticeship: Art. 24 CCNL — under_classification, inquadrato al livello immediatamente inferiore per l'intera durata (max 36 mesi). Destinations B, C, D, E. Level A excluded (Quadri e coordinamento/controllo). Level F excluded (lowest, no level below).
    
    Headcount: ~116,801 workers (CNEL/INPS archive, K700).
    
    INDENNITA DI FUNZIONE — PRODUZIONE DIFFERENTIAL: Staff rate (A1: 333.33/mo, A2: 187.50/mo) is unconditional. Produzione workers receive an additional delta (A1: +58.34, A2: +45.83) via IND_FUNZIONE_A*_PROD_DELTA with role="produzione". Total produzione: A1=391.67, A2=233.33 (Art. 21 CCNL K700). Callers: pass Employee(roles=frozenset(['produzione'])) for the higher rate.
    
    SIMPLIFICATION: industria CIGO (1.70-2.00%) included in employer INPS rate. Poste Italiane is not a manufacturing firm and is not CIGO-subject; actual employer cost is lower. Verify against INPS circ. for the correct Poste INPS classification.
    
    SIMPLIFICATION: Legacy retribuzione individuale di anzianità (D.P.R. 335/1990) and posizioni economiche differenziate (CCNL 1997) not modeled.
    
    SIMPLIFICATION: Salary tranche 01/07/2024–31/08/2025 covered by one-time 'anticipo sui futuri miglioramenti economici' (lump sum, September 2024). Engine carries paga base at 2024-07-23 level (same as pre-renewal) for that window.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/poste-italiane-k700.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/poste-italiane-k700.py"
```
