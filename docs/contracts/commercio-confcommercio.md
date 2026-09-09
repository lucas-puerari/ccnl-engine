# CCNL Terziario, Distribuzione e Servizi (Confcommercio)

| | |
|---|---|
| **CNEL code** | `H011` |
| **Sector** | terziario |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-28 |
| **Workers (est.)** | ~800k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confcommercio
    - Filcams-CGIL
    - Fisascat-CISL
    - Uiltucs-UIL

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
| `Q` | Quadro | € 2,313.29 | — |
| `1` | 1st level | € 2,083.84 | — |
| `2` | 2nd level | € 1,802.50 | — |
| `3` | 3rd level | € 1,540.66 | — |
| `4` | 4th level | € 1,332.46 | — |
| `5` | 5th level | € 1,203.83 | — |
| `6` | 6th level | € 1,080.77 | — |
| `7` | 7th level | € 925.31 | — |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 10 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 25.46 |
| `1` | € 24.84 |
| `2` | € 22.83 |
| `3` | € 21.95 |
| `4` | € 20.66 |
| `5` | € 20.30 |
| `6` | € 19.73 |
| `7` | € 19.47 |

## Apprenticeship

**livelli_2_5** (type: `under_classification`)  
Destination levels: `2`, `3`, `4`, `5`

**livello_6** (type: `under_classification`)  
Destination levels: `6`

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| Tabelle retributive CCNL Terziario Distribuzione e Servizi 2024-2027 (rinnovo 22/03/2024, accordo integrativo 28/03/2024) | tabella_retributiva | 2024-03-28 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-commercio-2024-2027/) |
| CCNL Terziario Distribuzione e Servizi — Testo Unico 2019 (rinnovo 22/03/2024) | associazione | 2024-03-22 | [↗](https://www.confcommercio.it/-/ccnl-terziario-distribuzione-servizi-testo-unico-2019) |

??? note "Coverage notes"
    'contingenza_edr' is the tables' 'Contingenza + EDR' column (contingenza frozen since November 1993 per L. 438/1992 plus EDR 10,33); 'terzo_elemento_nazionale' is the 2,07 EUR element of Art. 215.
    
    Indennità di funzione Quadri 260,76 EUR (Art. 129, 14 mensilità; the literal sum of the increments is 260,77, the tables carry 260,76); VII livello 'altri elementi' 5,16 EUR.
    
    INPS: see tax/data/2026-terziario.json notes.
    
    CNEL code H011 confirmed by Il Sole 24 Ore / INPS UNIEMENS reference.
    
    Salary tables: five tranches of the rinnovo 22/03/2024 (paga base dal 1/4/2024, 1/3/2025, 1/11/2025, 1/11/2026, 1/2/2027) taken from the official tabelle retributive as perfected by the Accordo integrativo 28/03/2024 (rounding fixes on Q, I, II, VI vs the 22/03 ipotesi), consolidated text at comuneportofinomare.it (Eutekne) cross-checked with lexplain.it.
    
    Seniority (Art. 205): ten triennial scatti; amounts Q 25,46, I 24,84, II 22,83, III 21,95, IV 20,66, V 20,30, VI 19,73, VII 19,47 (dal 1/1/1990, unchanged by the 2024 renewal).
    
    Apprenticeship (Art. 53 TU 2019, unchanged in 2024): sottoinquadramento, two levels below the destination for the first half and one level below for the second half; eligible destinations II-VI (Art. 62); durations II-V 36 months, VI 24 months (Art. 64). Track 'livelli_2_5' (18+18 months), track 'livello_6' (VII for the first 12 months; the second half stays at VII by the general one-level-below rule, lexplain.it reads it as VI: adopted the literal text). Art. 68 Tabella B profiles with 42/48-month durations and the farmacista di parafarmacia derogation (Accordo 31/10/2024) are profile-specific and not modelled.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/commercio-confcommercio.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/commercio-confcommercio.py"
```
