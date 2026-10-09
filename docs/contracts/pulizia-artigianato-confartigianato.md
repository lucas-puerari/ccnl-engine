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
| **Readiness** | 🧪 Exploratory |

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

### Funzionalità

Derived from the capability registry, as in the [capability matrix](capability-matrix.md).

| | Functional coverage of a layer: its weakest capability |
|---|---|
| ✅ | Every capability native: computed from bundled rules and request facts |
| 📝 | At best caller-supplied: a capability takes a caller rate or amount |
| ⚠️ | A capability is partial: some variants only, or data the file lacks |
| 🔲 | A capability is unsupported: the engine does not compute it |

| Layer | Status |
|---|---|
| **L1 — Gross** | 🔲 |
| **L2 — Net** | 🔲 |
| **L3 — Work rules** | 🔲 |
| **Limits of this contract** | base_salary, bilateral_funds, holiday_work, inps_employer, leave, night_work, overtime, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-12-17 |
| **Last verified** | — |
| **Latest salary tranche** | 2029-12-01 |

### Semplificazioni note

8 semplificazioni documentate. 3 feature mancanti.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `1` | Quadri e impiegati direttivi | € 1,884.88 | 2029-12-01 |
| `2` | Impiegati di concetto | € 1,727.84 | 2029-12-01 |
| `3S` | Impiegati di concetto (superiore) | € 1,674.70 | 2029-12-01 |
| `3` | Impiegati d'ordine, operai specializzati | € 1,617.33 | 2029-12-01 |
| `4` | Impiegati d'ordine, operai qualificati | € 1,528.89 | 2029-12-01 |
| `5` | Operai comuni | € 1,479.97 | 2029-12-01 |
| `6` | Guardiani, uscieri, custodi | € 1,425.64 | 2029-12-01 |

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

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "pulizia-artigianato-confartigianato/ind_fun_months_per_year · base_salary · impact unknown · open"
    SIMPLIFICATION: IND_FUN (EUR 25.82/mese) — il PDF non specifica il numero di mensilità. months_per_year=null (eredita 13). Impatto: ±25.82 EUR/anno se la risposta vera è 12 mensilità.

    **Applies when:** `base_salary` applies; level in 1; run kind in thirteenth.

    **Remediation:** Source the number of yearly instalments of IND_FUN and set months_per_year.

!!! warning "pulizia-artigianato-confartigianato/apprenticeship_percentages_2022 · base_salary · impact unknown · open"
    SIMPLIFICATION: Percentuali apprendistato da PDF 2022. Il rinnovo dic 2025 estende scatti anzianità agli apprendisti ma non menziona variazioni alle aliquote. Rischio: basso.

    **Applies when:** `base_salary` applies; contract type in apprentice.

    **Remediation:** Verify the apprenticeship percentages against the December 2025 renewal.

!!! warning "pulizia-artigianato-confartigianato/level_2_seniority_amount · seniority · impact unknown · open"
    SIMPLIFICATION: L2 scatto anzianità = 26.85 EUR (PDF 2022). Kitech lug 2026 riporta 26.86 EUR. Usato PDF come fonte primaria. Impatto: EUR 0.01/mese.

    **Applies when:** `seniority` applies; level in 2.

    **Remediation:** Confirm the level 2 seniority amount (26.85 or 26.86 EUR) against the signed table.

!!! warning "pulizia-artigianato-confartigianato/artisan_inps_rates_unverified · inps_employer · impact unknown · open"
    SIMPLIFICATION: tax_sector='terziario'. Aliquote INPS artigiane (datoriali) non verificate per 2026. Impatto su employer_cost_annual.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Verify the 2026 employer INPS rates for artisan cleaning firms against the INPS circular.

!!! warning "pulizia-artigianato-confartigianato/health_and_bilateral_funds · bilateral_funds · impact yes · open"
    SIMPLIFICATION: Fondi bilaterali non modellati (Fondo sanitario EUR 10.42*12 + bilateralità EUR 11.65*12). employer_cost_annual sottostimato di ~EUR 267/anno.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the health-fund and bilateral contributions as a bilateral fund event, or model the funds.

!!! warning "pulizia-artigianato-confartigianato/overtime_weekly_threshold · overtime · impact unknown · open"
    SIMPLIFICATION: Soglia settimanale ore straordinarie (OT_DIURNO) non modellata (hour_threshold_per_week=null). Il contratto prevede scatto dopo 40h/settimana e limite annuale 200h. Coverage work_rules gia' marcata partial.

    **Applies when:** `overtime` applies.

    **Remediation:** Model the 40-hour weekly threshold and the 200-hour yearly cap of OT_DIURNO, or pass the multiplier on the overtime event.

!!! warning "pulizia-artigianato-confartigianato/apprentice_seniority · seniority · impact yes · open"
    APPRENTICE SENIORITY: the December 2025 renewal extends the seniority increments to apprentices from 2026-01-01 (see the seniority note), but the clause and its amounts are not modelled: the engine pays no increment during the apprenticeship. The run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Apprendistato — livelli con doppia appartenenza a gruppi diversi (L5: gruppi 1 e 3; L4: gruppi 3 e 4; L3: gruppi 2 e 4). Il contratto distingue per contenuto professionale, non per livello. Engine usa first-match in ordine di dichiarazione: L5 -> gruppo 1 (70/80/90/100, 4 anni), L4 -> gruppo 3 (65/80/90, 18 mesi), L3 -> gruppo 2 (70/80/90, 3 anni). Rischio: basso (usato solo per scenari apprendistato, non per il test di integrazione).

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
