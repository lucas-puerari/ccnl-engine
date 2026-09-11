# CCNL Comparto Sanità 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S205` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-10-27 |
| **Workers (est.)** | ~580k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - UIL FPL
    - FIALS
    - NURSIND
    - NURSING UP

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
| `ELEVATA_QUALIFICAZIONE` | Elevata qualificazione (ex area DS dirigenza) | € 2,886.21 | — |
| `PROFESSIONISTI` | Professionisti della salute e funzionari (ex area D/DS) | € 2,076.58 | — |
| `ASSISTENTI` | Assistenti (ex area C/C1) | € 1,913.48 | — |
| `OPERATORI` | Operatori (ex area B/B1) | € 1,795.45 | — |
| `SUPPORTO` | Personale di supporto (ex area A/A1) | € 1,701.59 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    PRE-2024 BACK-CALCULATED. Nov 2022 values derived by subtracting Tabella 1a increments from Jan 2024 amounts (support −115, operatori −120, assistenti −127, collaboratori −127, funzionari −129, elevata qualificazione −185 approx). Primary CCNL 2019-2021 text not verified directly. 2022-2023 anticipation payments not modelled as intermediate periods.

!!! warning ""
    Agreement date 2025-10-27 (firma definitiva) per ARAN press release. The PDF used is the Ipotesi from 14.01.2025; salary tables are identical to the final signed version.

!!! warning ""
    2025-2027 RENEWAL NOT YET MODELLED. An ipotesi di CCNL 2025-2027 was signed by ARAN on 29 July 2026 with retroactive effect from 1 January 2025. Increases (monthly, 13 mensilità) from Jan 2024 base: support +41.40 (Jan 2025)/+82.80 (Jan 2026)/+106.70 (Jan 2027); operatori +43.70/+87.40/+112.60; assistenti +46.60/+93.20/+120.00; funzionari +50.50/+101.10/+130.20; elevata qualificazione +70.20/+140.50/+181.00. Not yet modelled — ipotesi pending comitato di settore, Governo, and Corte dei conti certification.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-01-14 | [↗](https://www.quotidianosanita.it/allegati/allegato1736872056.pdf) |
| — | — | — | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=400) |

??? note "Coverage notes"
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Seniority via DEP (Differenziali Economici di Professionalità) per Art. 60 Fondo incarichi: selective procedure, not automatic — maximum_count=0.
    
    Indennità di specificità infermieristica (Art. 62, Tabella 3) not modelled as fixed_allowance — applies only to specific nursing profiles (infermieri, ostetriche), not universally to all area members.
    
    CNEL code S205 confirmed via multiple secondary sources: lavoro-economia.it lists 'CCNL Comparto Sanità [Cnel: S205]', kitech.it and ilccnl.it concur. Not stated in the official ipotesi PDF text; CNEL archive not separately verified.
    
    Salary tables from Ipotesi CCNL Comparto Sanità 2022-2024 (ARAN, 14.01.2025, definitively signed October 2025). Art. 58 comma 1 (increments from 1.1.2024 per Tabella 1a), Art. 58 comma 2 (annual amounts from Tabella 2a). Monthly values = Tabella 2a / 12.
    
    Tranche 1 (2022-11-02) values back-calculated from CCNL 2.11.2022 base by subtracting Tabella 1a increments. 2022-2023 anticipation payments (Art. 47-bis D.Lgs. 165/2001) not modelled as separate periods (SIMPLIFICATION).
    
    Hourly divisor 156 from Art. 26 comma 1 (36h/week standard working time for comparto Sanità).
    
    13 mensilità from Art. 57 (Tredicesima mensilità) of this CCNL.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/sanita-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/sanita-aran.py"
```
