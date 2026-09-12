# CCNL per i dipendenti delle imprese artigiane esercenti servizi di pulizia, disinfezione, disinfestazione, derattizzazione e sanificazione

| | |
|---|---|
| **CNEL code** | `K521` |
| **Sector** | pulizia artigianato |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-12-17 |
| **Workers (est.)** | ~84505 |
| **Ruleset version** | `2025.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Confartigianato Imprese di Pulizia
    - CNA Costruzioni — CNA Imprese di Pulizia
    - Casartigiani
    - CLAAI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTRASPORTI-UIL

## Coverage

| Layer | Status |
|---|---|
| **L1 — Gross** | ✅ implemented |
| **L2 — Net** | ✅ implemented |
| **L3 — Work rules** | ⚠️ partial |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Quadri e impiegati direttivi | € 1,884.88 | — |
| `2` | Impiegati di concetto | € 1,727.84 | — |
| `3S` | Impiegati di concetto (superiore) | € 1,674.70 | — |
| `3` | Impiegati d'ordine, operai specializzati | € 1,617.33 | — |
| `4` | Impiegati d'ordine, operai qualificati | € 1,528.89 | — |
| `5` | Operai comuni | € 1,479.97 | — |
| `6` | Guardiani, uscieri, custodi | € 1,425.64 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 30.47 |
| `2` | € 26.85 |
| `3S` | € 23.76 |
| `3` | € 21.17 |
| `4` | € 18.59 |
| `5` | € 17.04 |
| `6` | € 15.49 |

## Apprenticeship

**1-gruppo-4anni-L5** (type: `percentage`)  
Destination levels: `5`  
percentage: 1.00

**2-gruppo-3anni-L3S-L3** (type: `percentage`)  
Destination levels: `3S`, `3`  
percentage: 0.90

**3-gruppo-18mesi-L4-L5** (type: `percentage`)  
Destination levels: `4`, `5`  
percentage: 0.90

**4-gruppo-impiegati-30mesi-L4-L2** (type: `percentage`)  
Destination levels: `4`, `3`, `2`  
percentage: 0.90

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: IND_FUN (EUR 25.82/mese) — il PDF non specifica il numero di mensilità. months_per_year=null (eredita 13). Impatto: ±25.82 EUR/anno se la risposta vera è 12 mensilità.

!!! warning ""
    SIMPLIFICATION: Percentuali apprendistato da PDF 2022. Il rinnovo dic 2025 estende scatti anzianità agli apprendisti ma non menziona variazioni alle aliquote. Rischio: basso.

!!! warning ""
    SIMPLIFICATION: L2 scatto anzianità = 26.85 EUR (PDF 2022). Kitech lug 2026 riporta 26.86 EUR. Usato PDF come fonte primaria. Impatto: EUR 0.01/mese.

!!! warning ""
    SIMPLIFICATION: tax_sector='terziario'. Aliquote INPS artigiane (datoriali) non verificate per 2026. Impatto su employer_cost_annual.

!!! warning ""
    SIMPLIFICATION: Fondi bilaterali non modellati (Fondo sanitario EUR 10.42*12 + bilateralità EUR 11.65*12). employer_cost_annual sottostimato di ~EUR 267/anno.

!!! warning ""
    SIMPLIFICATION: Apprendistato — livelli con doppia appartenenza a gruppi diversi (L5: gruppi 1 e 3; L4: gruppi 3 e 4; L3: gruppi 2 e 4). Il contratto distingue per contenuto professionale, non per livello. Engine usa first-match in ordine di dichiarazione: L5 -> gruppo 1 (70/80/90/100, 4 anni), L4 -> gruppo 3 (65/80/90, 18 mesi), L3 -> gruppo 2 (70/80/90, 3 anni). Rischio: basso (usato solo per scenari apprendistato, non per il test di integrazione).

!!! warning ""
    SIMPLIFICATION: Soglia settimanale ore straordinarie (OT_DIURNO) non modellata (hour_threshold_per_week=null). Il contratto prevede scatto dopo 40h/settimana e limite annuale 200h. Coverage work_rules gia' marcata partial.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2022-10-27 | [↗](https://ce-mu.it/rapportolavoro/contratti/cms_magazine/uploads/Pulizia_Artigianato_Accordo_Rinnovo_27.10.22.pdf) |
| — | — | 2025-12-17 | [↗](unavailable) |

??? note "Coverage notes"
    Salary model: CONGLOBATO. Contingenza=0 e EDR=0 conglobati dal 1.10.2014. Confermato da ilccnl.it luglio 2026: Paga Base 1693.84 | Contingenza 0 | Terzo Elemento 0 | Totale 1693.84 per livello 1.
    
    hourly_divisor: 173 — da sezione PARAMETRI E COEFFICIENTI CONTRATTUALI PDF 2022: 'Divisore orario 173, orario 40 ore su 5 giorni'.
    
    additional_months: 13 (tredicesima, entro 20 dicembre). Quattordicesima non prevista: PDF 2022 sezione parametri: 'Altre mensilità aggiuntive: non previste'.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Importi mensili da PDF 2022: 1=30.47, 2=26.85, 3S=23.76, 3=21.17, 4=18.59, 5=17.04, 6=15.49 EUR. Il rinnovo dic 2025 estende gli scatti agli apprendisti dal 1.1.2026.
    
    Identità CCNL K521: tabella Dec 2024 (PDF direzionelavoro.it 2022) + tranches rinnovo 2025 (Confartigianato) → tabella lug 2026 verificata su tutti e 7 i livelli con kitech CodiceCateg=83 (match al centesimo). Contratto Conflavoro PMI/Fesica Confsal del 26.7.2024 è un CCNL separato non confederale e non corrisponderebbe a questa struttura. FILCAMS dic 2025: livello 1 a regime (dic 2029) = 1884.88 EUR — confermato (ratio Dec2024_L1/Dec2024_L5 a 4 dec = 1.2736).
    
    Reproportioning: tranche_Li = round(tranche_L5 * round(Dec2024_Li/Dec2024_L5, 4), 2). Nessuna tabella parametri ufficiali per livello nel contratto. Ratios: 1=1.2736, 2=1.1675, 3S=1.1316, 3=1.0928, 4=1.0331, 5=1.0000, 6=0.9633.
    
    Gap 2025: il vecchio CCNL scadeva 31.12.2024; il nuovo decorre economicamente dal 1.1.2026. La serie salariale ha un periodo senza aggiornamento 1.12.2024–31.12.2025 (valore costante). Dec 2029 incluso: accordo rinnovo indica esplicitamente il 7° scatto.
    
    EDAR (Elemento Distinto e Aggiuntivo della Retribuzione): EUR 15.00 flat, 26 mesi da 1.11.2022, soli lavoratori in forza al 27.10.2022. Scaduto dic 2024. Non rientra in nessun istituto contrattuale incl. TFR. Non modellato.
    
    INDENNITÀ SPECIALE (tabella per-livello nel PDF: L1=126.55→131.55 EUR): corrisposta solo al personale addetto alla riscossione con responsabilità di bollette/fatture > EUR 4.648/giorno. Condizionale, non universale. Non modellata. Totale ilccnl.it lug 2026 = Paga Base conferma assenza di elementi obbligatori aggiuntivi.
    
    Fonte 2022 PDF: ce-mu.it/rapportolavoro/contratti/cms_magazine/uploads/Pulizia_Artigianato_Accordo_Rinnovo_27.10.22.pdf — verificata e scaricata il 2026-09-12. Tranches Nov 2022 — Dec 2024 da questo documento.
    
    Fonte accordo rinnovo 2025 (Confartigianato, 17 dic 2025): URL non raggiungibile il 2026-09-12. Tranches Jan 2026 — Dec 2029 verificate incrociatamente con kitech CodiceCateg=83 (Jul 2026, tutti e 7 i livelli, match al centesimo) e ilccnl.it Jul 2026 (L1: Paga Base=Totale=1693.84). Accesso originale: 2026-09-12.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/pulizia-artigianato-confartigianato.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/pulizia-artigianato-confartigianato.py"
```
