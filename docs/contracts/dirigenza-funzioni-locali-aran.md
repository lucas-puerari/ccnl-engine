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
    
    CNEL S125 inferito dalla struttura coerente dei codici ARAN: S005/S025 (FC), S105/S125 (FL), S205/S225 (Sanità) — pattern *05=comparto, *25=area dirigenza. I codici S005, S105, S205 e S225 sono verificati; S125 è inferito dal pattern.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL Area FL 2022-2024 / CCNL 17/12/2020 Art. sull'orario). Standard contrattuale PA per la dirigenza. L'orario non è soggetto a controllo puntuale.
    
    Tabellare pre-2024 3.616,60€/mese = back-calculation: 50.005,77 - 230×13 = 47.015,77€/anno / 13 = 3.616,60€/mese. Incrociato con il valore identico confermato per Area FC e Area Sanità (ARAN allinea i tabellari tra le aree dirigenziali). Aritmeticamente esatto rispetto alle fonti secondarie verificate.
    
    Un unico livello DIRIGENTE modella dirigenti RAL, PTA e segretari fascia A/B (stesso tabellare 50.005,77€/anno). I segretari fascia C (incremento +184€/mese, valore stimato 3.800,60€/mese) sono esclusi — fonte primaria non disponibile in formato leggibile. Scelta strutturale deliberata.
    
    Nessun straordinario: principio di onnicomprensività della retribuzione dirigenziale PA (Art. 3 D.Lgs. 165/2001). overtime_bands vuoto è corretto per questa categoria.
    
    Assenza non retribuita: prassi PA divisore 30 (mensile/30 per giorno di assenza). Modellato con by_30, coerente con le altre aree ARAN.
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — CCNL Area FL 2022-2024 (stessa disciplina delle altre aree ARAN). Modellato con SicknessTier; periodi a cavallo di soglia ricevono un unico tasso (engine limitation accettabile).
    
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
