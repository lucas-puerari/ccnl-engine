# CCNL Area Dirigenza Funzioni Centrali 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S025` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-10-28 |
| **Workers (est.)** | ~30k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - CISL FP
    - ANMI ASSOMED SIVEMP FPM
    - CIDA FC
    - FLEPAR
    - UIL PA
    - UNADIS
    - DIRSTAT FIALP UNSA

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
| `PRIMA_FASCIA` | Dirigenti di prima fascia (dirigenti generali): ministeri, agenzie | € 4,908.30 | — |
| `SECONDA_FASCIA` | Dirigenti di seconda fascia (non generali): ministeri, agenzie fiscali, INPS, INAIL | € 3,846.60 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-10-28 | [↗](https://trasparenza.lavoro.gov.it/archiviofile/minlavoro/2025_10_28_CCNL_A_FC_2022-2024_Pubblicazione-1%20vigente.pdf) |

??? note "Coverage notes"
    Retribuzione di posizione parte fissa: prima fascia 42.598,20€/anno (Art. 23 c.5); seconda fascia 14.515,11€/anno (Art. 26 c.5). Variabile per incarico, non modellata (SIMPLIFICATION).
    
    Nessuno scatto automatico di anzianità per i dirigenti. maximum_count=0.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    CNEL S025 inferito dalla struttura coerente dei codici ARAN: S005=comparto FC (confermato da sessione precedente), S025=area dirigenza FC, S105=comparto FL (confermato), S205=comparto Sanità (confermato), S225=area dirigenza Sanità (confermato). Il pattern S*05/S*25 (comparto/area) è consistente per tutti i comparti verificati.
    
    Hourly divisor 165 = 38h/settimana × 52/12 = 164.67 ≈ 165 (CCNL FC 2022-2024 / CCNL 09/03/2020 Art. per l'orario settimanale della dirigenza PA). L'orario dei dirigenti non è soggetto a controllo puntuale, ma 38h è il riferimento contrattuale standard per la PA.
    
    Valori mensili arrotondati: prima fascia 60.102,87/13 = 4.623,299 → 4.623,30€; dopo rinnovo 63.807,87/13 = 4.908,298 → 4.908,30€. Seconda fascia: 47.015,77/13 = 3.616,598 → 3.616,60€; dopo rinnovo 50.005,77/13 = 3.846,598 → 3.846,60€. Tutti derivano aritmeticamente dai valori annui certificati nel testo CCNL.
    
    Due livelli (PRIMA_FASCIA / SECONDA_FASCIA) per lo stipendio tabellare. La retribuzione di posizione (fissa e variabile per incarico) e la retribuzione di risultato non sono modellate — out_of_scope strutturale per tutti i dirigenti PA. Il file cattura la componente stipendio tabellare che è uniforme per fascia.
    
    Straordinario (Art. 71 CCNL FC) applicabile solo ai dirigenti privi di incarico di struttura complessa. I dirigenti con incarico complesso non percepiscono OT (assorbito da retribuzione di risultato). Questo è un limite strutturale: il motore non distingue dirigenti con/senza incarico complesso; si assume il caso base (privi di incarico).
    
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13-18, comporto max 18 mesi (540 gg) — Art. 19 CCNL FC 09/03/2020. Modellato con SicknessTier. Periodi di paga a cavallo di soglia mensile ricevono un unico tasso (engine limitation accettabile).
    
    Stipendio tabellare da testo ufficiale CCNL 28/10/2025 (Ministero del Lavoro, Art. 23 e Art. 26).
    
    Prima fascia — Art. 23 comma 1: previgente 60.102,87€/anno (CCNL 16/11/2023); incremento +285€/mese × 13 = +3.705€/anno; nuovo valore 63.807,87€/anno = 4.908,30€/mese per 13 mensilità.
    
    Seconda fascia — Art. 26 comma 1: previgente 47.015,77€/anno (CCNL 16/11/2023); incremento +230€/mese × 13 = +2.990€/anno; nuovo valore 50.005,77€/anno = 3.846,60€/mese per 13 mensilità.
    
    Firma 28/10/2025. FP CGIL non ha firmato (indicato come 'non firmato' nel frontespizio). CGIL confederale non ha firmato.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-funzioni-centrali-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-funzioni-centrali-aran.py"
```
