# CCNL Area Sanità 2022-2024 — ARAN (Dirigenti Sanitari: psicologi, farmacisti, biologi, fisici, chimici)

| | |
|---|---|
| **CNEL code** | `S225` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2026-02-27 |
| **Workers (est.)** | ~37k |
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
| `DIRIGENTE` | Dirigente sanitario SSN (psicologo, farmacista, biologo, fisico, chimico, dirigente professioni sanitarie) | € 3,846.60 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    Hourly divisor 165 = 38h/settimana × 52/12 (approssimazione per dirigenza SSN, CCNL 23.1.2024 Art. 27).

!!! warning ""
    Pre-31/12/2024 specificità sanitaria (104,34€/mese) calcolata per differenza: 124,19 - 17,90 (incremento stimato dalla fonte secondaria openssn, GOAL-plan) = approssimazione; il valore esatto del CCNL 23.1.2024 Art. 66 non è verificato.

!!! warning ""
    Pre-2024 tabellare 3.616,60€/mese = back-calculation dal valore 2024 sottraendo +230€.

!!! warning ""
    CNEL S225 da fonte secondaria (ilccnl.it). Non riportato nel testo ARAN.

!!! warning ""
    Questo file e 'dirigenza-sanitaria-medico-veterinaria-aran.json' derivano dallo stesso CCNL Area Sanità 27.02.2026 (unico testo contrattuale). La distinzione in due file riflette le diverse indennità di specificità applicabili alle due popolazioni dirigenziali.

!!! warning ""
    Malattia: 100% mesi 1-9, 90% mesi 10-12, 50% mesi 13+ modellati con SicknessTier. Il tasso è selezionato in base al cumulative_sick_days all'inizio del periodo; periodi di paga a cavallo di una soglia mensile ricevono un unico tasso. Comporto max 18 mesi = 540 gg.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-27 | [↗](https://www.aranagenzia.it/wp-content/uploads/2026/02/2026.02.27-CCNL-Area-sanita-2022-2024-3.pdf) |
| — | — | 2026-02-28 | [↗](https://openssn.marcopingitore.it/ccnl-dirigenza-sanitaria-2022-2024/2026/02/28/9222/) |
| — | — | — | [↗](https://ilccnl.it/ccnl/dirigenti---dirigenza-medica-e-veterinaria/dirigenti---sanita-medici-e-veterinari-dal-010195) |

??? note "Coverage notes"
    Retribuzione di posizione (Art. 14): obbligatoria ma variabile per tipo incarico. Non modellata — out_of_scope.
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Nessuno scatto automatico di anzianità. maximum_count=0.
    
    Stipendio tabellare da Art. 11 CCNL 27.02.2026: incremento +230€/mese da 1/1/2024, valore a regime 50.005,77€/anno per 13 mensilità = 3.846,60€/mese.
    
    Indennità specificità sanitaria dal 31/12/2024: Art. 15 comma 3 CCNL 27.02.2026, rideterminata in 1.614,46€/anno per 13 mensilità = 124,19€/mese. Applicazione: dirigenti sanitari non medici.
    
    Tredicesima mensilità: Art. 11 comma 1 ('per 13 mensilità').
    
    Campo di applicazione: Art. 1 CCNL 27.02.2026. Questo file modella la componente non medico-veterinaria (psicologi, farmacisti, biologi, fisici, chimici, dirigenti professioni sanitarie).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/dirigenza-sanitaria-area-sanita-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/dirigenza-sanitaria-area-sanita-aran.py"
```
