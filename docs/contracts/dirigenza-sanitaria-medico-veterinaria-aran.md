# CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Medici e Veterinari SSN)

| | |
|---|---|
| **CNEL code** | `S225` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-27 |
| **Workers (est.)** | ~100k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - ANAAO ASSOMED
    - FEDERAZIONE CIMO-FESMED
    - AAROI EMAC
    - FASSID
    - FVM
    - UIL FPL
    - FEDERAZIONE CISL MEDICI

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
| `DIRIGENTE` | Dirigente medico o veterinario SSN (rapporto esclusivo o non esclusivo) | € 3,846.60 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Hourly divisor 165 = 38h/settimana × 52/12, arrotondato. Art. 27 CCNL 23.1.2024 (Orario di lavoro dei dirigenti) non modificato dal CCNL 27.02.2026. Il divisore 165 è un'approssimazione — i dirigenti SSN non hanno un orario fisso misurabile.

!!! warning ""
    Pre-31/12/2024 specificità medico-veterinaria (704,88€/mese) calcolata per differenza dal valore a regime 728,15€ sottraendo il presunto incremento 23,27€/mese × 13 = 302,51€/anno. L'importo pre-2024 è una stima basata sulle comunicazioni GOAL-plan (fonte secondaria); il valore esatto del CCNL 23.1.2024 Art. 65 non è verificato.

!!! warning ""
    Pre-2024 tabellare 3.616,60€/mese = 47.015,77€/anno ricavato sottraendo l'incremento di 230€/mese (× 13) dal valore 2024. Il valore del CCNL 19.12.2019 (base periodo 1) è stimato in assenza di consultazione del testo del previgente contratto.

!!! warning ""
    Questo file modella solo la componente medico-veterinaria del CCNL Area Sanità 27.02.2026. Il medesimo CCNL copre anche altri dirigenti sanitari (psicologi, farmacisti, biologi, fisici, chimici), modellati in 'dirigenza-sanitaria-area-sanita-aran.json'. Entrambi i file condividono codice CNEL S225.

!!! warning ""
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13+ modellati con SicknessTier. Il tasso è selezionato in base al cumulative_sick_days all'inizio del periodo; periodi di paga a cavallo di una soglia mensile ricevono un unico tasso. Comporto max 18 mesi = 540 gg.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/2026.02.27-CCNL-Area-sanita-2022-2024-3.pdf) |
| — | — | 2026-02-28 | [↗](https://openssn.marcopingitore.it/ccnl-dirigenza-sanitaria-2022-2024/2026/02/28/9222/) |
| — | — | — | [↗](https://ilccnl.it/ccnl/dirigenti---dirigenza-medica-e-veterinaria/dirigenti---sanita-medici-e-veterinari-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione (Art. 14): obbligatoria ma variabile per tipo incarico (UOC, UOSD, professionale, ecc.). Non modellata — parte fissa per incarico assegnato in sede aziendale; out_of_scope per il motore.
    
    Indennità per incarico di direzione di struttura complessa (Art. 16): 11.157€/anno per 13 mensilità. Non modellata come fixed_allowance — assegnata solo ai direttori di SC, non a tutti i dirigenti.
    
    Clausola di garanzia retribuzione di posizione (Art. 17): minima garantita per anzianità. Non modellata — variabile per anzianità e valutazione.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità per i dirigenti. Cadence=1 e maximum_count=0 riflettono l'assenza di progression automatica.
    
    CNEL S225 confermato da contratticcnl.it (/ccnl/s225/: "CCNL dell'Area Sanità (dirigenti)", deposito 19/12/2019, ARAN). Verificato 2026-09-09.
    
    Rinnovo 2025-2027: ARAN ha convocato primo tavolo il 22/07/2026 presentando quantificazione economica con risorse ordinarie pari al 5,40%. Trattativa in corso al 2026-09-09; nessun accordo firmato. Fonte: consulentidellavoro.vi.it, vet33.it.
    
    Stipendio tabellare da Art. 11 CCNL 27.02.2026: incremento +230€/mese da 1/1/2024, valore a regime 50.005,77€/anno per 13 mensilità = 3.846,60€/mese. Art. 11 riferisce Art. 61 comma 3 CCNL 23.1.2024 come base preesistente.
    
    Indennità specificità medico-veterinaria dal 31/12/2024: Art. 15 comma 1 CCNL 27.02.2026, rideterminata in 9.466,00€/anno per 13 mensilità = 728,15€/mese. Applicazione: dirigenti medici e veterinari.
    
    Tredicesima mensilità: Art. 11 comma 1 ('per 13 mensilità'), confermato per tabellare e specificità.
    
    Campo di applicazione: Art. 1 CCNL 27.02.2026 — dirigenti medici, sanitari, veterinari e professioni sanitarie SSN. Questo file modella la sola componente medico-veterinaria.
    
    Signatari: frontespizio CCNL 27.02.2026. CGIL FP non ha firmato.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-sanitaria-medico-veterinaria-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-sanitaria-medico-veterinaria-aran.py"
```
