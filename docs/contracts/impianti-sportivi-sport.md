# CCNL Impianti e Attività Sportive Profit e No-profit

| | |
|---|---|
| **CNEL code** | `H077` |
| **Sector** | impianti sportivi, palestre e attività sportive |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-01-12 |
| **Workers (est.)** | 35533 |
| **Ruleset version** | `2024.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - CUSI
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| `Q` | Quadro | € 2,083.49 | — |
| `I` | Primo livello | € 1,989.04 | — |
| `II` | Secondo livello | € 1,807.04 | — |
| `III` | Terzo livello | € 1,636.42 | — |
| `IV` | Quarto livello | € 1,506.82 | — |
| `V` | Quinto livello | € 1,413.42 | — |
| `VI` | Sesto livello | € 1,336.82 | — |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**apprendistato_II_III_IV_36mesi** (type: `under_classification`)  
Destination levels: `II`, `III`, `IV`

**apprendistato_V_36mesi_semplificato** (type: `under_classification`)  
Destination levels: `V`

**apprendistato_VI_24mesi_semplificato** (type: `under_classification`)  
Destination levels: `VI`

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    SIMPLIFICATION: Seniority. Il CCNL 2024 non contiene disposizioni su scatti di anzianita (parola 'scatti' assente dall'intero PDF). Regime transitorio: i lavoratori in forza al 22/12/2015 conservano un superminimo personale decrescente fino al 31/10/2029 (Art. 116 norma transitoria). Non modellato: dimensione hire-date non disponibile. Gli importi kitech (EUR 21.69-28.92) si riferiscono agli scatti ante-2015. Modellato: maximum_count=0.

!!! warning ""
    SIMPLIFICATION: Apprendistato livello V (Art. 30). Il livello V ha ordine 2 e il livello a ordine 0 non esiste; il primo semestre a 2 livelli sotto non e applicabile. SEMPLIFICAZIONE: primo semestre a 1 livello sotto (VI). L'apprendista percepisce piu del previsto contrattualmente nella prima meta. L'intera durata (36 mesi) e al livello VI.

!!! warning ""
    SIMPLIFICATION: Apprendistato livello VI (Art. 30 + Art. 37). Art. 30 prevedeva il primo semestre al VII livello, che il rinnovo 2024 ha eliminato. SEMPLIFICAZIONE: l'intera durata apprendistato VI (24 mesi) e al livello di destinazione VI (levels_below=0). L'apprendista percepisce piu del previsto contrattualmente.

!!! warning ""
    SIMPLIFICATION: Straordinario diurno. Art. 83 prevede 15% per ore 41-48 e 20% per ore oltre 48 settimanali. Modellato solo il 15% (caso dominante). Banda 20% (oltre 48h) non modellata.

!!! warning ""
    SIMPLIFICATION: Integrazione malattia (Art. 103). Struttura contrattuale: giorni 1-3 a carico del datore (100%), giorni 4-20 integrazione al 75%, giorni 21+ integrazione al 100%. La granularita 'giorno' non e modellabile nel schema SicknessRules (usa mesi). Modellato: carenza_integration_rate=1.0, full_pay_integration_rate=1.0 (allineato alla fase finale). La finestra al 75% (gg. 4-20) non e modellata; il motore sovrastima la retribuzione per eventi di malattia breve.

!!! warning ""
    SIMPLIFICATION: Divisore orario. Art. 120 prevede 173 (40h) e 195 (45h). Solo il divisore 173 e modellato. Le assunzioni a 45h settimanali non sono gestite.

!!! warning ""
    SIMPLIFICATION: Cumulo notturno. Art. 83 ult. comma: 'Le varie maggiorazioni previste dal presente articolo non sono cumulabili tra loro' — esclude la cumulabilita tra i soli supplementi interni all'Art. 83 (15%/20%/30%/50%). Il supplemento del 10% di Art. 84 e un articolo separato e non e esplicitamente escluso dalla cumulabilita. Il motore applica entrambi alle ore notturne straordinarie (60% totale). Se le parti intendono il 50% inclusivo del 10%, il motore sovrastima di 10 punti sulle ore OT notturne.

!!! warning ""
    SIMPLIFICATION: Quattordicesima transitoria. Art. 116 norma transitoria: i lavoratori in forza al 22/12/2015 ricevono un superminimo personale assorbibile equivalente alla quattordicesima folded-in (rata mensile decrescente fino al 31/10/2029). Per la popolazione corrente (post-2015): 13 mensilita. La quattordicesima residuale per i lavoratori ante-2015 non e modellata.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2024-01-12 | [↗](https://www.sindacato.it/il-ccnl-impianti-sportivi-o-lavoratori-dello-sport/) |
| — | — | 2024-01-12 | [↗](https://www.cusi.it/wp-content/uploads/2024/02/CCNL-Sport-2024-2026.pdf) |
| — | — | 2024-01-12 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=13) |

??? note "Coverage notes"
    CCNL H077 Impianti Sportivi e Palestre, rinnovo 12/01/2024 (vigenza 01/01/2024-31/12/2026). 7 livelli: Q (quadro) + livelli I-VI. Art. 121 CCNL dice 'sei livelli' perche Q e categoria quadro sopra la scala ordinaria. Conglobato confermato da ilccnl.it (contingenza=0.00, terzo elemento=0.00 su 4 livelli). Divisore orario 173 da Art. 120 (40h settimanali).
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/impianti-sportivi-sport.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/impianti-sportivi-sport.py"
```
