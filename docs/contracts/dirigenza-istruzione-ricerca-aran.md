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

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CNEL S325 stimato per analogia (S305=comparto IR, S325=area dirigenza IR, seguendo S005/S025, S105/S125, S205/S225). Non verificato su fonti primarie CNEL.

!!! warning ""
    Hourly divisor 165 = 38h/settimana × 52/12 (stima per dirigenza PA).

!!! warning ""
    Period 1 valid_from=2021-01-01 corrisponde all'ultima tranche del CCNL 2019-2021 (+135€/mese da 1/1/2021). Il CCNL 2019-2021 è stato firmato retroattivamente il 7/8/2024.

!!! warning ""
    Seconda fascia include categorie eterogenee (dirigenti scolastici, direttori università e AOU, dirigenti II fascia enti ricerca). Modellate come unico livello per mancanza di tabellare differenziato nella fonte disponibile.

!!! warning ""
    Nessun straordinario: principio onnicomprensività dirigenti PA. overtime_bands vuoto.

!!! warning ""
    Assenza non retribuita: prassi PA divisore 30 (mensile/30/giorno). Modellato con by_30.

!!! warning ""
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13+ modellati con SicknessTier. Il tasso è selezionato in base al cumulative_sick_days all'inizio del periodo; periodi di paga a cavallo di una soglia mensile ricevono un unico tasso. Comporto max 18 mesi = 540 gg.

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
