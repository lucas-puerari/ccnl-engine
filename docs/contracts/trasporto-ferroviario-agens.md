# CCNL Attività Ferroviarie — AGENS

| | |
|---|---|
| **CNEL code** | `I320` |
| **Sector** | trasporto |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-22 |
| **Workers (est.)** | ~75k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - AGENS — Aziende Aderenti alla Sezione Ferroviaria di Conftrasporto
    - FILT-CGIL — Federazione Italiana Lavoratori Trasporti
    - FIT-CISL — Federazione Italiana Trasporti
    - Uiltrasporti
    - FAST-Confsal — Federazione Autonoma Sindacati Trasporti
    - UGL Ferrovieri
    - ORSA Ferrovie

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
| `Q1` | Level Q1 — railway quadri (senior management), with IND_FUN function allowance | € 2,826.07 | — |
| `Q2` | Level Q2 — railway quadri (middle management), with IND_FUN function allowance | € 2,483.02 | — |
| `A` | Level A — senior railway managers, strategic operational leadership | € 2,401.34 | — |
| `B1` | Level B1 — railway department managers, senior management roles | € 2,286.99 | — |
| `B2` | Level B2 — railway section managers, intermediate management roles | € 2,188.97 | — |
| `B3` | Level B3 — railway supervisors, operational management duties | € 2,156.31 | — |
| `C1` | Level C1 — senior railway professionals, team coordination roles | € 2,107.30 | — |
| `C2` | Level C2 — railway professionals, specialist operational coordination | € 2,074.62 | — |
| `D1` | Level D1 — senior railway technicians, advanced professional duties | € 2,041.95 | — |
| `D2` | Level D2 — experienced railway technicians, intermediate professional roles | € 1,976.62 | — |
| `D3` | Level D3 — qualified railway technicians, standard professional duties | € 1,943.94 | — |
| `E1` | Level E1 — specialised railway workers, technical operational duties | € 1,911.26 | — |
| `E2` | Level E2 — skilled railway workers, certified operational roles | € 1,829.60 | — |
| `E3` | Level E3 — semi-skilled railway workers, qualified operational tasks | € 1,796.91 | — |
| `F1` | Level F1 — basic railway workers, standard operational tasks | € 1,666.23 | — |
| `F2` | Level F2 — entry-level railway workers, unskilled support tasks | € 1,633.56 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 47.19 |
| `Q2` | € 38.27 |
| `A` | € 35.95 |
| `B1` | € 33.62 |
| `B2` | € 31.77 |
| `B3` | € 31.30 |
| `C1` | € 29.91 |
| `C2` | € 29.45 |
| `D1` | € 28.42 |
| `D2` | € 25.64 |
| `D3` | € 25.22 |
| `E1` | € 24.34 |
| `E2` | € 22.66 |
| `E3` | € 22.66 |
| `F1` | € 18.58 |
| `F2` | € 18.22 |

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    PRE-JUN 2025 PERIOD NOT MODELLED. The CCNL contractual coverage runs 2024-01-01 to 2026-12-31. The Jan 2024 – May 2025 wage gap was compensated by a lump-sum una tantum paid in Aug 2025 (per redigo.info), explicitly stated as having no effect on any contractual institute ('non avranno riflessi su alcun istituto contrattuale'). Salary periods therefore start 01/06/2025. Engine queries with as_of before Jun 2025 will return the Jun 2025 values, which overstate actual pay for that window.

!!! warning ""
    FONDO DI SOLIDARIETA FERROVIE. A 0.20% solidarity fund contribution applies (split approximately 2/3 employer, 1/3 employee) per the bilateral solidarity fund for the railway sector. Not modelled; adds approximately 0.067% to employee cost and 0.133% to employer cost above the standard INDUSTRIA INPS rates.

!!! warning ""
    SENIORITY AMOUNTS PRE-JUN 2025. Per-level scatto amounts are sourced from lavoro-economia.it/kitech.it representing the Jun 2026 table. Whether identical values applied in the Jun 2025 and Nov 2025 tranches is unconfirmed. Modelled as constant from 01/06/2025.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-05-22 | [↗](https://ilccnl.it/ccnl/ferrovie/ferrovie-attivita-ferroviarie/tabelleretributive) |
| — | — | 2025-05-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=299) |
| — | — | 2025-05-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx) |
| — | — | 2025-05-22 | [↗](https://www.redigo.info/2025/05/ccnl-ferrovie-rinnovo-2025) |
| — | — | 2025-05-22 | [↗](https://www.leggeinchiaro.it/ccnl-ferrovie) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. ilccnl.it salary table shows contingenza=0.00 and terzo elemento=0.00 for all 16 levels. kitech.it confirms additive structure: Q1 base tabellare=2826.07 + IND_FUN=250.00 total, Q2 base=2483.02 + IND_FUN=130.00 total. Two aggregator sources (ilccnl.it, kitech.it) agree on the decomposition, establishing the function allowances are additive to the conglobated base. Primary CCNL text (AGENS/FILT-CGIL) was not directly retrieved; all parameters derive from aggregator tables.
    
    SIGNATORIES: AGENS (employer association, Conftrasporto affiliate) + FILT-CGIL/FIT-CISL/Uiltrasporti/FAST-Confsal/UGL Ferrovieri/ORSA Ferrovie (workers). CNEL code I320. The operating companies (FS Italiane, Trenitalia, RFI) are AGENS members; AGENS is the formal signatory.
    
    HOURLY DIVISOR: 160, verbatim from ilccnl.it salary table. Standard for 40h/week contractual regime (160 = 40 × 4).
    
    ADDITIONAL MONTHS: 14 — tredicesima + quattordicesima, confirmed from lavoro-economia.it and redigo.info (rinnovo May 2025).
    
    SENIORITY: biennial (cadence 24 months), maximum 7 scatti. Per-level EUR amounts from lavoro-economia.it and kitech.it (both aggregators). NOTE: E2 and E3 show identical scatto amounts (22.66) in both aggregator sources; unconfirmed against the primary CCNL text and should be verified before relying on E2/E3 seniority amounts.
    
    FUNCTION ALLOWANCES (IND_FUN): Q1 receives +250.00/month, Q2 receives +130.00/month. Modelled as fixed_allowances with code IND_FUN effective from first salary tranche (01/06/2025). Two aggregator sources (ilccnl.it, kitech.it) agree the allowances are additive to the base tabellare.
    
    APPRENTICESHIP. I320 specifies apprendistato professionalizzante (max 36 months per Art. 29 Parte Generale). Per leggeinchiaro.it, retributive percentages are defined in the Piano Formativo Individuale (PFI) on a per-worker basis and are not published as a contract-level table. No fixed percentage or under-classification track exists in the CCNL text; the apprenticeship array is therefore empty by contract structure, not by modelling omission. Analogous to public-sector contracts where apprendistato is excluded from scope.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/trasporto-ferroviario-agens.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/trasporto-ferroviario-agens.py"
```
