# CCNL Comparto Istruzione e Ricerca 2022-2024 — ARAN

| | |
|---|---|
| **CNEL code** | `S305` |
| **Sector** | Pubblica Amministrazione |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-12-23 |
| **Workers (est.)** | ~1,2M |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - FLC CGIL
    - CISL FSUR
    - UIL SCUOLA RUA
    - GILDA UNAMS
    - SNALS CONFSAL

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
| `FUNZIONARIO_ED_ESPERTO` | ATA: Funzionario ed esperto (ex dsga, direttori servizi generali) | € 1,960.65 | — |
| `DOCENTE_SECONDARIA` | Docente secondaria I grado (PE/Ed.Fisica) e secondaria II (laurea) | € 1,866.79 | — |
| `DOCENTE_INFANZIA_PRIMARIA` | Docente scuola dell'infanzia e primaria; docente secondaria II (diploma) | € 1,724.65 | — |
| `ASSISTENTE` | ATA: Assistente amministrativo, assistente tecnico, cuoco, infermiere | € 1,496.85 | — |
| `OPERATORE` | ATA: Operatore scolastico (nuovo profilo dal 1/5/2024 CCNL 18/1/2024) | € 1,375.38 | — |
| `COLLABORATORE_SCOLASTICO` | ATA: Collaboratore scolastico (ex bidello, ex commesso) | € 1,342.82 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    CNEL S305 confermato per comparto, include tutte le sezioni (scuola, università, ricerca, AFAM).

!!! warning ""
    Hourly divisor 156 = 36h/settimana × 52/12. I docenti hanno orario cattedra (18h/settimana insegnamento), non direttamente comparabile. Il divisore si applica per l'hourly_rate indicativo.

!!! warning ""
    Base salary = fascia 0-8 anni (entry level). Le 6 fasce di anzianità (0-8, 9-14, 15-20, 21-27, 28-34, 35+) non sono scatti automatici ma bande per anzianità di servizio. Fascia superiore non modellata.

!!! warning ""
    seniority maximum_count=0 (fasce non sono scatti automatici nell'accezione del CCNL privato). Per la fascia di anzianità corretta, usare negotiated_ral o livello dedicato.

!!! warning ""
    DOCENTE_SECONDARIA aggrega secondaria I grado e secondaria II (laurea) che condividono lo stesso tabellare entry. DOCENTE_INFANZIA_PRIMARIA aggrega anche secondaria II (diploma) con stesso tabellare entry.

!!! warning ""
    valid_from period 1 = 2022-01-01 (inizio validità del triennio). Il previgente CCNL 2019-2021 aveva stabilito i valori pre-2024; la data esatta di firma del CCNL 2019-2021 non è disponibile dalla fonte e viene approssimata.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-12-23 | [↗](https://www.notiziedellascuola.it/legislazione-e-dottrina/indice-cronologico/2025/dicembre/CCNL_ARAN_20251223_NIR-1/ann1) |
| — | — | — | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=494) |

??? note "Coverage notes"
    Platea ~1,2M: ~800k docenti (infanzia, primaria, secondaria I e II), ~230k ATA scuola, ~130k personale università e ricerca, ~80k AFAM (quifinanza.it).
    
    Indennità di funzione (IF) docenti: da ~200€ a ~313€/mese a seconda dell'ordine (da CCNL 23/12/2025). Non modellata come fixed_allowance per eterogeneità tra ordini (SIMPLIFICATION).
    
    Layer 2 implemented. Part-time: engine scales by part_time_pct. Fixed-term: PA is excluded from NASpI addizionale (lavoratori delle pubbliche amministrazioni in statutory exclusion list per INPS guidance); fixed_term_additional_rate=0.000 in tax file. Apprenticeship: no ARAN CCNL defines percentage or under-classification tracks; narrow high-qualification form under D.Lgs. 81/2015 Art. 47 exists for research profiles but is not operationalized in any examined CCNL.
    
    Personale università, ricerca e AFAM: non modellato separatamente (trattamento retributivo distinto con sezioni specifiche nel CCNL). SIMPLIFICATION: unico JSON copre principalmente la scuola.
    
    Stipendio tabellare annuo da Tabella A2 CCNL 23/12/2025 allegato ufficiale (notiziedellascuola.it). Valori fascia 0-8 anni da 1/1/2024.
    
    Pre-2024: back-calcolato sottraendo incremento mensile (Tabella A1) × 13. Esempio COLLABORATORE: 17.456,64 - 85,74×13 = 16.342,02€/anno = 1.257,08€/mese.
    
    CNEL S305 da kitech.it per comparto Istruzione e Ricerca personale docente. Confermato coerente con S325 (area dirigenza IR).
    
    COLLABORATORE_SCOLASTICO — Tab A2 0-8: 17.456,64€/anno; incremento Tab A1: 85,74€/mese.
    
    OPERATORE — Tab A2 0-8: 17.879,93€/anno; incremento: 87,82€/mese (nuovo profilo da 1/5/2024).
    
    ASSISTENTE — Tab A2 0-8: 19.459,12€/anno; incremento: 95,58€/mese.
    
    DOCENTE_INFANZIA_PRIMARIA — Tab A2 0-8: 22.420,48€/anno; incremento: 110,12€/mese. Copre anche docente secondaria II diploma (stesso valore tabellare).
    
    DOCENTE_SECONDARIA — Tab A2 0-8: 24.268,28€/anno; incremento: 119,20€/mese. Copre secondaria I grado, secondaria II laurea (stessi valori entry). Incremento secondaria II laurea: 119,20 (0-8) ma diverge per fasce superiori (136,18 per fascia 9-14).
    
    FUNZIONARIO_ED_ESPERTO — Tab A2 0-8: 25.488,37€/anno; incremento: 125,19€/mese.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/istruzione-ricerca-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/istruzione-ricerca-aran.py"
```
