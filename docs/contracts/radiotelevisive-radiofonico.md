# CCNL Radiotelevisivo — Settore Radiofonico

| | |
|---|---|
| **CNEL code** | `G091` |
| **Sector** | radiotelevisione — settore radiofonico |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-01-08 |
| **Workers (est.)** |  |
| **Ruleset version** | `—` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Confindustria Radio Televisioni
    - ANICA
    - SLC-CGIL
    - FISTEL-CISL
    - UIL-COM

## Coverage

### Funzionalità

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | 🔲 not_implemented |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-01-08 |
| **Last verified** | — |
| **Next salary event** | 2027-06-01 |

### Semplificazioni note

1 semplificazione documentata.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `6` | 6° livello | € 1,751.23 | 2027-06-01 |
| `5` | 5° livello | € 1,571.02 | 2027-06-01 |
| `4` | 4° livello | € 1,292.26 | 2027-06-01 |
| `3` | 3° livello | € 1,103.70 | 2027-06-01 |
| `2` | 2° livello | € 931.68 | 2027-06-01 |
| `1` | 1° livello | € 778.55 | 2027-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 12.39 |
| `2` | € 12.91 |
| `3` | € 15.49 |
| `4` | € 16.01 |
| `5` | € 18.08 |
| `6` | € 19.63 |

## Apprenticeship

**professionalizzante_breve** (type: `percentage`)  
Destination levels: `2`  
percentage: 0.90

**professionalizzante_esteso** (type: `percentage`)  
Destination levels: `3`, `4`, `5`, `6`  
percentage: 1.00

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    INPS rates reuse existing 2026-industria.json (tax_sector=industria). No bilateral fund substitution for broadcasting sector identified; standard Confindustria INPS rates apply.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-01-08 | [↗](https://www.confindustriaradiotv.it/) |

??? note "Coverage notes"
    CCNL Radiotelevisivo 2026 signed 08/01/2026 in Roma. Employer: Confindustria Radio Televisioni (pres. Antonio Marano) and ANICA (pres. Alessandro Usai). Unions: SLC-CGIL (Sindacato Lavoratori della Comunicazione), FISTEL-CISL (Federazione Informazioni Spettacolo e Telecomunicazioni), UIL-COM (UIL Comunicazione). Signatories sourced from Art. 1, page 7 of CCNL PDF.
    
    Source anchor: https://www.confindustriaradiotv.it/ is the employer association homepage; a direct PDF permalink was not published. PDF read locally as ccnl_radiotv_2026.pdf (81 MB, read 2026-09-12).
    
    SPLIT model: paga base (minimo tabellare, Art. 43) + contingenza congelata al 1° novembre 1991 (Allegato A). EDR not present in 2026 CCNL.
    
    DUAL-SECTOR contract: Settore Radiofonico (6 livelli) modelled separately from Settore Televisivo Multimediale (9 livelli) in radiotelevisive-televisivo.json because merged file violates the engine monotonicity constraint (see TV file).
    
    Radio sector has two new tranches only: 01/01/2026 and 01/06/2027. No 01/01/2028 tranche for Radio (TV has three tranches). The pre-2026 CCNL column values (from the 2022 contract) are not modelled.
    
    Apprenticeship (Art. 27): Radio L3+ table on page 43 of the PDF labels both apprenticeship rows as '2° livello CCNL' (apparent typo). Reconciled using Art. 27 page 37 cross-reference: TV L3 <-> Radio L2 (24 months), TV L4 <-> Radio L3, TV L5 <-> Radio L4, TV L6 <-> Radio L5, TV L7 <-> Radio L6. Second row is Radio L3+ (60 months). This is a source-document typo reconciled via Art. 27 intra-document cross-reference.
    
    Radio L4 scatto (16.01) verified directly from Art. 46 page 75 of CCNL PDF. Does not follow pattern Radio L3=TV L3=15.49, Radio L5=TV L4=18.08; 16.01 is explicitly listed in the Radio sector table as '4° ivello' (PDF typo).
    
    Apprenticeship open tail: the final period of each track has months_until=null as required by the engine schema (validate_open_sequence enforces open-ended last period). Radio breve track (L2, max 24 months) ends {18, null, 0.90}; esteso track (L3-L6, max 60 months) ends {36, null, 1.00}.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/radiotelevisive-radiofonico.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/radiotelevisive-radiofonico.py"
```
