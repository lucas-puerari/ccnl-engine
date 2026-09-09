# CCNL Servizi Postali in Appalto (FISE-ARE)

| | |
|---|---|
| **CNEL code** | `K721` |
| **Sector** | Servizi postali in appalto e recapito |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-12-21 |
| **Workers (est.)** | ~1k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - FISE-ARE
    - SLC-CGIL
    - SLP-CISL
    - UILPOSTE-UIL

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
| `1` | Livello 1 (Par. 166) | € 1,875.95 | — |
| `2` | Livello 2 (Par. 139) | € 1,650.74 | — |
| `3S` | Livello 3 Super (Par. 127) | € 1,549.72 | — |
| `3` | Livello 3 (Par. 122) | € 1,509.09 | — |
| `4S` | Livello 4 Super (Par. 116) | € 1,457.90 | — |
| `4` | Livello 4 (Par. 110) | € 1,409.19 | — |
| `5` | Livello 5 (Par. 100) | € 1,325.69 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 10 increments

## Apprenticeship

**professionalizzante - dest livello 1** (type: `under_classification`)  
Destination levels: `1`

**professionalizzante - dest livello 2** (type: `under_classification`)  
Destination levels: `2`

**professionalizzante - dest livello 3** (type: `under_classification`)  
Destination levels: `3`

**professionalizzante - dest livello 4** (type: `under_classification`)  
Destination levels: `4`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: indennità integrativa Art. 34 modelled as unconditional fixed allowance. Art. 34 restricts it to companies without second-level bargaining that don't pay other economic treatments verified over 4 years. Kitech totals confirm its inclusion in the national contractual floor.

!!! warning ""
    SIMPLIFICATION: L4S impiegati seniority amount (52.44) sourced from kitech.it proxy; the corresponding cell in the primary source PDF (p.85) is partially obscured by an adhesive note in the scan.

!!! warning ""
    SIMPLIFICATION: dest 5° apprenticeship not modelled — Allegato 10 places dest 5° apprentices at level 5 for the full 24-month duration (zero salary reduction; no structural levels_below > 0 is applicable).

!!! warning ""
    SIMPLIFICATION: dest 3S° and dest 4S° apprenticeship not modelled — Allegato 10 names only ordinal destinations 1°-5°; S-level destinations are unaddressed in the accord text.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-12-21 | [↗](https://slp-cisl.it/wp-content/uploads/2025/09/CCNL-SERVIZI-POSTALI-versione-stampa-250624.pdf) |
| — | — | 2023-12-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=K721) |

??? note "Coverage notes"
    CCNL Servizi Postali in Appalto signed 21/12/2023. Salary model: split — base_salary = paga tabellare + contingenza; fixed_allowances = indennità integrativa Art. 34 (frozen Dec 2013) + EDR 10.33. Verified: L1 Dec2025 (1875.95+75.62+10.33)/173=1961.90/173=11.34 EUR/h ✓.
    
    7 levels (1=highest, 5=lowest): 1(Par.166), 2(Par.139), 3S(Par.127), 3(Par.122), 4S(Par.116), 4(Par.110), 5(Par.100). 3 tranches: 01/01/2024, 01/01/2025, 01/12/2025. Allegato 1 (p.84), primary source.
    
    Hourly divisor 173 (Art. 33 explicit, p.50). Additional months: 14 — tredicesima (Art. 37) + quattordicesima (Art. 38).
    
    Seniority Art. 35: dual model. Operai (Art. 35A): single premio after 24mo company service (max=1), amounts frozen at 31/12/1994 tabellare (L2=56.66, L3S=51.71, L3=49.70, L4S=47.24, L4=44.94, L5=40.72). Impiegati (Art. 35B): biennale (cadence=24mo), first scatto after 48mo, max=10 (5.55% biennale capped at 60%), amounts frozen at 2001 reference (L1=71.79, L2=62.62, L3=56.86, L4S=52.44 (kitech proxy), L5=49.40). L1 operai: no seniority. L3S, L4 impiegati: no seniority. API caller must supply scenario.category=operaio/impiegato to trigger correct amounts.
    
    Apprenticeship (Allegato 10, 15/01/2013 accord, p.132-133): under_classification. Dest 1°: first 18mo at 3° (lb=3), next 18mo at 2° (lb=1). Dest 2°: first 18mo at 4° (lb=4), next 18mo at 3° (lb=2). Dest 3°: first 18mo at 5° (lb=3), next 18mo at 4° (lb=2). Dest 4°: whole period at 5° (lb=1). Non-uniform lb due to S levels interspersed.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/servizi-postali-appalto-fise.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/servizi-postali-appalto-fise.py"
```
