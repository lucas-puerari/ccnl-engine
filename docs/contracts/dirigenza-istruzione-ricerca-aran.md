# CCNL Area Dirigenza Istruzione e Ricerca 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S325` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-08-06 |
| **Workers (est.)** | ~8k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - ANP
    - FLC CGIL
    - CISL FSUR
    - DIRIGENTI SCUOLA
    - UIL SCUOLA RUA

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
| `PRIMA_FASCIA` | Dirigenti di prima fascia: enti di ricerca (INFN, CNR, ecc.) e ASI | € 4,908.30 | — |
| `SECONDA_FASCIA` | Dirigenti scolastici, direttori università e AFAM, dir. enti ricerca II fascia | € 3,846.59 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-08-06 | [↗](https://quifinanza.it/lavoro/ccnl-istruzione-ricerca-2022-2024-tabelle-retributive/1011686/) |
| — | — | 2024-08-07 | [↗](https://m.flcgil.it/contratti/documenti/istruzione-e-ricerca/ccnl-personale-area-dirigenza-istruzione-e-ricerca-2019-2021-del-7-agosto-2024.flc) |
| — | — | 2026-08-06 | [↗](https://www.flcgil.it/scuola/dirigenti/dirigenti-scolastici-siglato-in-via-definitiva-ccnl-area-istruzione-e-ricerca-2022-2024.flc) |

??? note "Coverage notes"
    Retribuzione di posizione parte fissa: seconda fascia 14.515,11€/anno (+1.170€/anno da 1/1/2024, era 13.345,11). Prima fascia 42.598,20€/anno. Variabile per incarico. Non modellata (SIMPLIFICATION).
    
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    CNEL S325 inferito dalla struttura coerente dei codici ARAN: S005/S025 (FC), S105/S125 (FL), S205/S225 (Sanità), S305/S325 (IR). I codici S005, S105, S205, S225, S305 sono verificati; S325 è inferito dal pattern *25=area dirigenza.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL Area IR 2022-2024 — stesso orario di riferimento delle altre aree ARAN dirigenza). Standard contrattuale PA.
    
    Period 1 valid_from=2021-01-01: corrisponde all'ultima tranche del CCNL Area IR 2019-2021 (+135€/mese da 1/1/2021), firmato retroattivamente il 7/8/2024. Valore 3.616,59€/mese (seconda fascia) confermato dalle note di fonte. Struttura storica documentata correttamente.
    
    Seconda fascia include categorie eterogenee (dirigenti scolastici, direttori università/AOU, dirigenti II fascia enti ricerca). Modellate come unico livello: il tabellare è uniforme per fascia (50.005,73€/anno dalla fonte disponibile). Scelta strutturale deliberata.
    
    Nessun straordinario: principio di onnicomprensività della retribuzione dirigenziale PA (Art. 3 D.Lgs. 165/2001). overtime_bands vuoto è corretto.
    
    Assenza non retribuita: prassi PA divisore 30 (mensile/30 per giorno di assenza). Modellato con by_30, coerente con le altre aree ARAN dirigenza.
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — CCNL Area IR 2022-2024 (stessa disciplina delle altre aree ARAN). Modellato con SicknessTier; periodi a cavallo di soglia ricevono un unico tasso (engine limitation accettabile).
    
    Tabellare previgente da CCNL Area Dirigenza Istruzione e Ricerca 2019-2021 (firmato 7/8/2024). Seconda fascia: 47.015,73€/anno = 3.616,594...€/mese → 3.616,59€. Prima fascia: 60.102,87€/anno = 4.623,298...€/mese → 4.623,30€.
    
    Incremento CCNL 2022-2024 (firmato 6/8/2026): seconda fascia +230€/mese × 13 = 50.005,73€/anno = 3.846,594...€/mese → 3.846,59€. Prima fascia +285€/mese × 13 = 63.807,87€/anno = 4.908,298...€/mese → 4.908,30€.
    
    Signatari (6/8/2026): ANP, FLC CGIL, CISL FSUR, Dirigenti Scuola, UIL Scuola RUA. ANCODIS non ha firmato (flcgil.it).
    
    Platea: ~7.550 dirigenti scolastici + ~360 direttori università/ricerca = ~7.910 totale (quifinanza.it).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-istruzione-ricerca-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-istruzione-ricerca-aran.py"
```
