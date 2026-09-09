# CCNL Area Dirigenza Funzioni Locali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S125` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~13k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - FEDIRETS
    - CISL FP
    - UIL FPL
    - UNSCP

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
| `DIRIGENTE` | Dirigente enti locali (RAL, PTA, Segretari comunali fascia A e B) | € 3,846.60 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CNEL S125 da fonte secondaria (ilccnl.it). Non verificato su fonti primarie ARAN.

!!! warning ""
    Hourly divisor 165 = 38h/settimana × 52/12 (stima per dirigenza PA). Orario effettivo dirigenti non fisso.

!!! warning ""
    Tabellare pre-2024 stimato per back-calculation. Testo CCNL 2022-2024 non disponibile in formato leggibile (PDF ARAN protetto da accesso diretto).

!!! warning ""
    Un unico livello DIRIGENTE modella dirigenti RAL, PTA e segretari fascia A/B (stesso tabellare 50.005,77€/anno). I segretari fascia C sono esclusi per mancanza di fonte primaria sul tabellare esatto.

!!! warning ""
    Nessun straordinario: principio onnicomprensività dirigenti PA. overtime_bands vuoto.

!!! warning ""
    Assenza non retribuita: prassi PA divisore 30 (mensile/30/giorno). Modellato con by_30.

!!! warning ""
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13+ modellati con SicknessTier. Il tasso è selezionato in base al cumulative_sick_days all'inizio del periodo; periodi di paga a cavallo di una soglia mensile ricevono un unico tasso. Comporto max 18 mesi = 540 gg.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-23 | [↗](https://www.truenumbers.it/ccnl-dirigenti-enti-locali-aumenti-arretrati/) |
| — | — | 2026-02-23 | [↗](https://www.logospa.it/contratto-dirigenza-funzioni-locali-2022-2024-tutte-le-novita-su-stipendi-e-normativa/) |
| — | — | — | [↗](https://ilccnl.it/ccnl/dirigenti---funzioni-locali/dirigenti---enti-locali-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione: variabile per tipo incarico e ente, non modellata (SIMPLIFICATION). Totale mensile medio include posizione: +491€ RAL, +400€ segretari, +377€ PTA (include tabellare + posizione + altro).
    
    Segretari comunali e provinciali fascia C (neo-assunti): incremento tabellare +184€/mese (vs +230€ delle altre fasce), valore stimato 49.407,77€/anno = 3.800,60€/mese. Non modellati come livello separato per mancanza di fonte primaria verificata.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    Stipendio tabellare da fonte secondaria (truenumbers.it, logospa.it): valore a regime dall'1.1.2024 = 50.005,77€/anno per 13 mensilità = 3.846,60€/mese. Incremento +230€/mese per dirigenti e segretari comunali fascia A e B.
    
    Tabellare pre-2024 (47.015,77€/anno = 3.616,60€/mese) back-calcolato: 50.005,77 - 230×13 = 47.015,77. Stesso valore base del CCNL Area Sanità e Area Funzioni Centrali (ARAN allinea tabellari tra aree dirigenziali).
    
    Signatari: ARAN, FEDIRETS, CISL FP, UIL FPL, UNSCP. CGIL non ha firmato (truenumbers.it).
    
    Contratto applicato a ~13.000 dirigenti: 5.500 dirigenti RAL, 5.200 dirigenti PTA (enti locali sanitari), 2.300 segretari comunali e provinciali (truenumbers.it). Platea GOAL.md (~40k) era sovrastimata.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-funzioni-locali-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-funzioni-locali-aran.py"
```
