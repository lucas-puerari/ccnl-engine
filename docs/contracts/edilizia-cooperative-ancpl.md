# CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)

| | |
|---|---|
| **CNEL code** | `F016` |
| **Sector** | Edilizia |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-02-21 |
| **Workers (est.)** | ~90000 |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCPL-Legacoop Costruzioni
    - Confcooperative Lavoro e Servizi
    - AGCI
    - FILLEA-CGIL
    - FILCA-CISL
    - FENEAL-UIL

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ✅ implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last verified** | — |
| **Next salary event** | 2027-03-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8Q` | Livello 8Q — quadro senior | € 2,962.99 | 2027-03-01 |
| `8` | Livello 8 — impiegato direttivo senior / tecnico | € 2,962.99 | 2027-03-01 |
| `7Q` | Livello 7Q — quadro | € 2,484.90 | 2027-03-01 |
| `7` | Livello 7 — impiegato direttivo | € 2,484.90 | 2027-03-01 |
| `6` | Livello 6 — impiegato di concetto | € 2,133.34 | 2027-03-01 |
| `5` | Livello 5 — impiegato qualificato / caposquadra | € 1,812.16 | 2027-03-01 |
| `4` | Livello 4 — operaio super-specializzato / impiegato ordine | € 1,621.99 | 2027-03-01 |
| `3` | Livello 3 — operaio specializzato | € 1,508.81 | 2027-03-01 |
| `2` | Livello 2 — operaio qualificato | € 1,354.72 | 2027-03-01 |
| `1` | Livello 1 — operaio comune (manovale) | € 1,185.21 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.22 |
| `2` | € 8.22 |
| `3` | € 8.99 |
| `4` | € 9.62 |
| `5` | € 10.46 |
| `6` | € 12.85 |
| `7` | € 13.94 |
| `7Q` | € 13.94 |
| `8` | € 16.53 |
| `8Q` | € 16.53 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6`, `7`, `8`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Apprenticeship provisions for Q levels (7Q, 8Q) are not modelled; quadri are not typically hired as apprentices in the cooperative construction sector.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-02-21 | [↗](https://www.studiocani.com/ccnl-edilizia-industria-e-cooperative-aumento-dei-minimi-dal-1-marzo/) |
| — | — | 2025-02-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=124) |

??? note "Coverage notes"
    SPLIT MODEL: paga_base (changes each tranche) + contingenza (frozen) + EDR (frozen at 10.33). Tranches: 01/02/2025, 01/03/2026, 01/03/2027. Jointly renewed with ANCE industry contract on 21/02/2025; validity 01/02/2025 to 30/06/2028.
    
    10 LEVELS: 1-8 plus 7Q and 8Q (quadri). Levels 7Q/8Q share paga base with 7/8 but add Indennita' di Funzione = EUR 170.00/month (fixed, not varying by tranche).
    
    SENIORITY: 5 scatti biennali (24-month cadence, max 5). For blue-collar workers (levels 1-4), seniority is governed by the Cassa Edile APE system; engine uses the tabular scatti as an approximation.
    
    ADDITIONAL_MONTHS: 13 (Christmas bonus). The cooperative sector has a gratifica feriale component administered through the Cassa Edile (~8.5% of gross), modelled separately. Engine uses 13 months consistent with the edilizia framework.
    
    CASSA EDILE: for blue-collar workers, holidays (8.5%) and Christmas bonus (10%) accrue through the Cassa Edile system. The employer_cost_annual underestimates by ~18.5% of gross for blue-collar workers.
    
    INPS: reuses 2026-edilizia.json (proxy rates). Cassa Edile contribution (~18.5%) is separate and not included.
    
    APPRENTICESHIP: single standard percentage track (Art. 92 CCNL), destination levels 2-8 (level 1 and Q levels excluded). Schedule: 72%/72%/78%/78%/85%/90% over 36 months then 100%. Same framework as jointly-renewed ANCE-cooperative CCNL.
    
    T3 INCREASES (01/03/2027) DERIVED: the studiocani.com source confirms T1 and T2 values; T3 amounts are computed from the parametro structure (L1=+50, L2=+57, L3=+63.50, L4=+68.25, L5=+76.50, L6=+90, L7=+105, L8=+125) — same as T2 amounts per the 3-tranche renewal.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/edilizia-cooperative-ancpl.json"
    ```

## Usage example

```python
--8 < --"docs/examples/contracts/edilizia-cooperative-ancpl.py"
```
