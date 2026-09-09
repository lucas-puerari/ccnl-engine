# DPR 24 marzo 2025, n. 53 — Forze di Polizia ad ordinamento civile (Triennio 2022-2024)

| | |
|---|---|
| **CNEL code** | `N/A` |
| **Sector** | Pubblica Sicurezza — Forze di Polizia ad ordinamento civile |
| **Tax sector** | `pubblica-amministrazione` |
| **Last renewal** | 2025-03-24 |
| **Workers (est.)** | ~130k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |

[← Contracts index](index.md)

??? note "Signatories"
    - Presidenza del Consiglio dei Ministri
    - SIULP
    - SAP
    - SIAP
    - FSP Polizia di Stato
    - Federazione COISP-MOSAP
    - SILP CGIL
    - SAPPE
    - SINAPPE
    - OSAPP
    - UILPA PP
    - USPP
    - CISL FNS

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
| `COMM_CAPO` | Commissario Capo (param 150,50) | € 2,451.90 | — |
| `SOST_COMM_COORD` | Sostituto Commissario Coordinatore (param 148,00) | € 2,411.17 | — |
| `COMMISSARIO` | Commissario (param 148,00) | € 2,411.17 | — |
| `SOST_COMM` | Sostituto Commissario (param 143,50) | € 2,337.85 | — |
| `ISP_SUP_8A` | Ispettore Superiore con 8 anni di qualifica (param 140,00) | € 2,280.83 | — |
| `ISP_SUPERIORE` | Ispettore Superiore (param 137,50) | € 2,240.10 | — |
| `VICE_COMM` | Vice Commissario (param 136,75) | € 2,227.89 | — |
| `ISP_CAPO` | Ispettore Capo (param 133,50) | € 2,174.94 | — |
| `SOV_CAPO_COORD` | Sovrintendente Capo Coordinatore (param 131,00) | € 2,134.21 | — |
| `ISPETTORE` | Ispettore (param 131,00) | € 2,134.21 | — |
| `SOV_CAPO_4A` | Sovrintendente Capo con 4 anni di qualifica (param 125,75) | € 2,048.68 | — |
| `VICE_ISP` | Vice Ispettore (param 124,75) | € 2,032.39 | — |
| `SOV_CAPO` | Sovrintendente Capo (param 124,25) | € 2,024.24 | — |
| `ASSISTENTE_CAPO_COORD` | Assistente Capo Coordinatore (param 121,50) | € 1,979.44 | — |
| `SOVRINTENDENTE` | Sovrintendente (param 121,50) | € 1,979.44 | — |
| `ASSISTENTE_CAPO_5A` | Assistente Capo con 5 anni di qualifica (param 117,00) | € 1,906.13 | — |
| `VICE_SOV` | Vice Sovrintendente (param 116,75) | € 1,902.05 | — |
| `ASSISTENTE_CAPO` | Assistente Capo (param 116,50) | € 1,897.98 | — |
| `ASSISTENTE` | Assistente (param 112,00) | € 1,824.67 | — |
| `AGENTE_SCELTO` | Agente Scelto (param 108,50) | € 1,767.65 | — |
| `AGENTE` | Agente (param 105,25) | € 1,714.70 | — |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

These are deliberate modelling approximations. Read them before using this contract in a sensitive context.

!!! warning ""
    cnel_code = 'N/A' — il CNEL non assegna codici agli accordi DPR-based (questo comparto è escluso dalla contrattazione collettiva ordinaria ex D.Lgs. 195/1995 e resta in regime di diritto pubblico). Il CNEL medesimo non include questo comparto nel proprio archivio contratti.

!!! warning ""
    aliquote INPS/CTPS — dipendente 8,80%, datore 24,20% — proxy dal file 2026-pubblica-amministrazione.json già presente; verificare circolare INPS annuale per valori esatti (regime CTPS ex-INPDAP, identico a PA ordinaria).

!!! warning ""
    valori mensili arrotondati col metodo a due passi (annual = round(param × punto, 2); monthly = round(annual / 12, 2)) per allineamento con le tavole dell'ipotesi di accordo 18/12/2024. Differenza massima da calcolo diretto: 1 centesimo.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2025-03-24 | [↗](https://www.normattiva.it/atto/caricaDettaglioAtto?atto.dataPubblicazioneGazzetta=2025-04-18&atto.codiceRedazionale=25G00046&atto.articolo.numero=0&atto.articolo.sottoArticolo=1&atto.articolo.sottoArticolo1=0&qId=1ede7c71-4666-4c74-b496-2391fce88e7f) |
| — | — | 2024-12-18 | [↗](https://nazionale.autonomidipolizia.it/wp-content/uploads/2024/12/ipotesi-accordo-18-12-2024.pdf) |

??? note "Coverage notes"
    Primo accordo DPR-based nel repository. Il Comparto Sicurezza-Difesa è disciplinato dal D.Lgs. 195/1995 — non da ARAN né da CCNL. Gli accordi sindacali sono recepiti con DPR (non con CCNL). DPR 53/2025 copre Polizia di Stato (97.931 effettivi, fonte poliziadistato.it 2024) e Corpo di Polizia Penitenziaria (~31.000 effettivi, fonte Rapporto Antigone 2025 / DAP): totale ~129.000 dipendenti.
    
    Perimetro DPR 53/2025 — Art. 1: personale non dirigente delle Forze di polizia ad ordinamento civile (Polizia di Stato) e militare (Polizia Penitenziaria). Forze Armate (Esercito, Marina, Aeronautica), Carabinieri e Guardia di Finanza non rientrano.
    
    Modello parametrico. Stipendio mensile = param × punto_parametrale_annuo / 12. Punto parametrale: T1 183,6993 €/anno (1/4/2022), T2 184,0659 €/anno (1/7/2022–31/12/2023), T3 195,50 €/anno (1/1/2024–). Fonte: Art. 6 DPR 53/2025 e ipotesi di accordo 18/12/2024.
    
    Conglobazione confermata — IIS conglobata dal 1/1/2005 (D.Lgs. 193/2003). fixed_allowances: [] per tutti i livelli.
    
    `order` assegnato per parametro crescente, non per gerarchia di carriera. Tre inversioni strutturali: Vice Sovrintendente (116,75) > Assistente Capo (116,50); Vice Ispettore (124,75) > Sovrintendente Capo (124,25); Vice Commissario (136,75) < Sostituto Commissario (143,50). Tre parità: SOVRINTENDENTE/ASSISTENTE_CAPO_COORD (121,50), ISPETTORE/SOV_CAPO_COORD (131,00), COMMISSARIO/SOST_COMM_COORD (148,00).
    
    divisore orario 156 (36h/settimana) — DPR 18 giugno 2002 n. 164 (orario di lavoro Polizia di Stato), 36h × 52 / 12 = 156. Stessa derivazione degli altri contratti PA.
    
    Tredicesima mensilità prevista — additional_months = 13.
    
    Progressione economica non per scatti automatici sulla paga base, bensì per avanzamento di qualifica e tramite assegno funzionale (Art. 54 D.Lgs. 195/1995) maturato a 17, 27 e 32 anni di servizio. seniority_increments.maximum_count = 0.
    
    Apprendistato assente — il reclutamento avviene per concorso pubblico (D.Lgs. 195/1995 art. 6). apprenticeship: [].
    
    validity.valid_from = 2022-01-01 (inizio periodo normativo ex Art. 1 DPR 53/2025). Gli effetti retributivi iniziano il 2022-04-01 (prima tranche stipendiale), che coincide con la data valid_from del primo periodo base_salary.
    
    Firmatari Polizia di Stato: SIULP, SAP, SIAP, FSP Polizia di Stato (ES-LS-CONSAP-M.P.), Federazione COISP-MOSAP, SILP CGIL. Firmatari Polizia Penitenziaria: SAPPE, SINAPPE, OSAPP, UILPA PP, USPP, CISL FNS. Fonte: testo DPR 53/2025.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/forze-polizia-ordinamento-civile.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/forze-polizia-ordinamento-civile.py"
```
