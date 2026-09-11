# CCNL Chimica e Affini PMI — Unionchimica Confapi

| | |
|---|---|
| **CNEL code** | `B018` |
| **Sector** | chimica |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~56k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionchimica — Unione Italiana Industria Chimica PMI (Confapi)
    - FILCTEM-CGIL — Federazione Italiana Lavoratori Chimica Tessile Energia Manifatturiero
    - FEMCA-CISL — Federazione Energia Moda Chimica Affini
    - UILTEC-UIL — Unione Italiana Lavoratori Tecnologie Energie Chimica

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
| `H` | Level H — senior managers, top technical executives (quadri) | € 3,168.51 | — |
| `G` | Level G — managers, senior professionals, department heads | € 2,973.58 | — |
| `F` | Level F — senior technical staff, team leaders | € 2,703.06 | — |
| `E` | Level E — specialist workers, junior technical staff | € 2,444.03 | — |
| `D` | Level D — highly skilled operai, senior impiegati | € 2,267.00 | — |
| `C` | Level C — skilled operai, standard impiegati | € 2,033.35 | — |
| `B` | Level B — semi-skilled operai and lower-grade impiegati | € 1,830.43 | — |
| `A` | Level A — entry workers, unskilled, first-time employees | € 1,690.69 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 10.33 |
| `B` | € 11.88 |
| `C` | € 12.91 |
| `D` | € 13.94 |
| `E` | € 15.49 |
| `F` | € 18.08 |
| `G` | € 20.66 |
| `H` | € 23.24 |

## Apprenticeship

**professionalizzante_C_H** (type: `under_classification`)  
Destination levels: `C`, `D`, `E`, `F`, `G`, `H`

**professionalizzante_B** (type: `under_classification`)  
Destination levels: `B`

**professionalizzante_A** (type: `under_classification`)  
Destination levels: `A`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SINGLE TRANCHE ONLY. Only the 1 January 2026 tranche is modelled. The 4 subsequent tranches (Apr 2027, Dec 2027, Jun 2028, Dec 2028) are not accessible from primary source at time of extraction. Update with official amounts when the renewal text becomes available.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=181) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimum contractual (minimo tabellare). Levels H, G, F, E carry fixed_allowances: H has indennità di funzione (IND_FUN, EUR 160.00); G, F, E have aggiunta personale (AGG_PERSONALE, EUR 25.82 / 15.49 / 5.16). All allowances are TFR-relevant and contribution-relevant (default).
    
    RENEWAL: Unionchimica Confapi CCNL signed 23 February 2026, effective 1 January 2026 – 31 December 2028. Five tranches: 1 Jan 2026, 1 Apr 2027, 1 Dec 2027, 1 Jun 2028, 1 Dec 2028. Source: kitech.it B018.
    
    LEVELS: 8 professional levels A (lowest) to H (highest). Scala parametrale: H=100 reference, descending. All levels confirmed from kitech.it Jan 2026 table.
    
    CNEL CODE: B018 (Unionchimica Confapi). Distinct from B011 (Federchimica) which covers large-firm chemical-pharmaceutical. B018 covers PMI (piccole e medie imprese) chemical sector.
    
    TAX SECTOR: INDUSTRIA (existing). Standard INPS industria rates apply (2026-industria.json). No bilateral fund substitutes INPS in this contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: kitech.it B018 mensilità aggiuntive field.
    
    SENIORITY: biennale (24 months), maximum 5 scatti. Per-level EUR amounts from kitech.it Jan 2026 table: A=10.33, B=11.88, C=12.91, D=13.94, E=15.49, F=18.08, G=20.66, H=23.24.
    
    CHIMICA-CONCIA SUB-SECTOR SCOPE. Unionchimica Confapi covers three sub-sectors with different hourly divisors: Chimica-Concia (175), Plastica-Gomma (169), Abrasivi-Ceramica-Vetro (173). Only Chimica-Concia (divisor 175) is modelled — deliberate scope choice. The level codes and salary amounts are identical across all sub-sectors; only the hourly divisor differs.
    
    HOURLY DIVISOR 175: confirmed by cross-reference with CCNL Federchimica B011 (kitech.it), which independently uses 175 for chemical-pharmaceutical industry (same contractual week = 40h, 40×52/12=173.33 rounded to 175 via industry convention). No primary contractual clause directly retrieved but cross-verified via B011.
    
    APPRENTICESHIP. Apprendistato professionalizzante per sotto-inquadramento (D.Lgs. 81/2015). Durata massima 36 mesi, uniforme per tutti i livelli e sub-settori. Struttura: primo periodo (mesi 1-10) a 2 livelli sotto la destinazione; secondo periodo (mesi 11 a fine contratto) a 1 livello sotto la destinazione; al termine dell'apprendistato l'inquadramento finale è riconosciuto. Tre track modellati: professionalizzante_C_H (C-H, schema standard 2→1), professionalizzante_B (destinazione B: capped ad A per assenza di livelli inferiori, periodo unico), professionalizzante_A (destinazione A: resta ad A per tutta la durata). Fonte primaria: schede CNEL B018 direzionelavoro.it (ottobre 2023), voce (g) art. 1 Cap. I. Confermato invariato dal rinnovo 23/02/2026 (Confapi Padova circolare): apprendistato non oggetto di modifica.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/chimica-affini-pmi-unionchimica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/chimica-affini-pmi-unionchimica.py"
```
