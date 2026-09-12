# CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica

| | |
|---|---|
| **CNEL code** | `IC91` |
| **Sector** | autoscuole e consulenza automobilistica |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-02-28 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - UNASCA — Unione Nazionale Autoscuole Studi Consulenza Automobilistica
    - CONFARCA — Confederazione Autoscuole Riunite e Consulenti Automobilistici
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri — dirigenti intermedi con ampia discrezionalità e autonomia decisionale (legge 190/85) | € 1,577.20 | — |
| `5` | 5° livello — impiegati tecnici e amministrativi con autonomia gestionale e responsabilità del proprio settore | € 1,227.87 | — |
| `4` | 4° livello — impiegati con funzioni tecnicoamministrative e autonomia di iniziativa entro direttive prestabilite | € 1,057.07 | — |
| `3` | 3° livello — impiegati con mansioni esecutive richiedenti conoscenze teorico-pratiche (es. insegnante di autoscuola) | € 987.04 | — |
| `2` | 2° livello — impiegati con mansioni esecutive (es. responsabile di segreteria, istruttore di guida) | € 938.41 | — |
| `1` | 1° livello — lavoratori con mansioni che richiedono semplici capacità pratiche (fattorino, addetto pulizie, usciere) | € 788.61 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 23.76 |
| `5` | € 18.59 |
| `4` | € 16.01 |
| `3` | € 14.98 |
| `2` | € 14.46 |
| `1` | € 12.39 |

## Apprenticeship

**L1-autoscuole-24m** (type: `under_classification`)  
Destination levels: `1`

**L2-autoscuole-36m** (type: `under_classification`)  
Destination levels: `2`

**L3-autoscuole-48m** (type: `under_classification`)  
Destination levels: `3`

**L4-autoscuole-48m** (type: `under_classification`)  
Destination levels: `4`

**L5-autoscuole-48m** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Fondo EST (Art. 46) supplementary health fund not modelled. Contribution: 15 EUR/month employer + 2 EUR/month employee. Not an INPS substitute. employer_cost_annual understated by 180 EUR/year.

!!! warning ""
    SIMPLIFICATION: Ente Bilaterale di settore (Art. 7, from 01/09/2021: 2 EUR/month employer) not modelled. employer_cost_annual understated by 24 EUR/year.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-02-28 | [↗](https://www.unasca.it/PDF/ccnl/CCNL_AUTOSCUOLE_-_SCUOLE_NAUTICHE_-_STUDI_DI_CONSULENZA_AUTOMOBILISTICA_FIRMATO_IL_28-02-2023.pdf) |
| — | — | 2023-03-14 | [↗](https://www.unasca.it/PDF/ccnl/Verbale_di_Accordo_Rettifica_tabelle14-03-2023.pdf) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series with 3 tranches (2021-01-01, 2021-09-01, 2022-02-01). Contingenza (frozen) and EDR (10.33) are fixed_allowances per level. Q level additionally carries indennità di funzione 25.82 EUR (Art. 6). Source: verbale di rettifica 14/03/2023 (authoritative; annuls salary table in main CCNL).
    
    Verbale di rettifica 14/03/2023: level 5 increment per tranche = 34.67 EUR (not 32.67 as printed in first table of both main CCNL and verbale). The second table of the verbale prints derived totals: 1158.53+34.67+34.67+445.84+10.33=1684.04 confirming 34.67. lavoro-economia.it propagated the typo and shows 1680.04 for a-regime; the correct value is 1684.04.
    
    hourly_divisor: 170 — confirmed from Art. 13 comma 3 CCNL ('dividendo la retribuzione mensile per 170'). Consistent with Art. 9 comma 1: weekly hours 39h = 39x52/12 ≈ 169h rounded to 170.
    
    additional_months: 14 — Art. 18 (tredicesima, Natale) and Art. 19 (quattordicesima, luglio) both explicit in CCNL.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from Art. 17 CCNL: Q=23.76, 5°=18.59, 4°=16.01, 3°=14.98, 2°=14.46, 1°=12.39 EUR.
    
    Contingenza values from Art. 13 CCNL, Art. 4 (frozen since 1993 interconfederale): Q=452.81, 5°=445.84, 4°=442.41, 3°=439.83, 2°=439.83, 1°=437.56 EUR.
    
    EDR: 10.33 EUR/month, uniform all levels. Elemento Distinto della Retribuzione from 1992 interconfederale CGIL/CISL/UIL/Confindustria (ITL 20,000 converted). Confirmed absorbed in verbale totals: per-level Art. 12 EDR amounts do not appear as additive — verbale derived totals match paga base + contingenza + 10.33 + (Q: 25.82) exactly.
    
    Q indennità di funzione: 25.82 EUR/month x 14 mensilità. PRIMARY SOURCE confirmed from Art. 6 CCNL ('Ai dipendenti classificati come quadri spetta un’indennità di funzione pari a euro 25,82 mensili lorde per quattordici mensilità').
    
    Apprenticeship: apprendistato professionalizzante, under-classification model (Art. 43 CCNL). Q excluded. Level 1: 24 months all at destination (no levels below available). Level 2: 36 months (0-23 at 1-below, 24-35 at dest). Levels 3-5: 48 months (0-15 at 2-below, 16-31 at 1-below, 32-47 at dest). Source: Art. 43 CCNL 28/02/2023.
    
    tax_sector: terziario. Following IC35 (autorimesse) precedent for transport/services CCNL with UNASCA/CONFARCA. Sector uses standard terziario INPS rates.
    
    Contract in ultra-vigenza since 01/01/2024 (expired 31/12/2023 per Art. 50). Negotiations broke down July 2026. Salary amounts remain operative per Art. 2074 c.c.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/autoscuole-unasca.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autoscuole-unasca.py"
```
