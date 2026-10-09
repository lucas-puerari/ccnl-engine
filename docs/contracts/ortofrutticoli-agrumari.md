# CCNL Ortofrutticoli ed Agrumari (Import-Export)

| | |
|---|---|
| **CNEL code** | `H341` |
| **Sector** | ortofrutticoli ed agrumari import-export |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-07-19 |
| **Workers (est.)** | ~60000 |
| **Ruleset version** | `2024.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Fruitimprese
    - FLAI-CGIL
    - FISASCAT-CISL
    - UILTUCS-UIL

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
| **Limits of this contract** | base_salary, leave, seniority, sickness |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-07-19 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-08-01 |

### Semplificazioni note

6 semplificazioni documentate. 2 feature mancanti.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadro | € 2,486.49 | 2027-08-01 |
| `1` | Primo livello | € 2,372.61 | 2027-08-01 |
| `2` | Secondo livello | € 2,096.50 | 2027-08-01 |
| `3` | Terzo livello | € 2,004.71 | 2027-08-01 |
| `4` | Quarto livello | € 1,815.64 | 2027-08-01 |
| `5` | Quinto livello | € 1,737.47 | 2027-08-01 |
| `6S` | Sesto livello superiore | € 1,700.37 | 2027-08-01 |
| `6` | Sesto livello | € 1,659.53 | 2027-08-01 |
| `7` | Settimo livello | € 1,595.96 | 2027-08-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 13 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 30.45 |
| `1` | € 29.40 |
| `2` | € 27.30 |
| `3` | € 27.30 |
| `4` | € 26.25 |
| `5` | € 26.25 |
| `6S` | € 25.20 |
| `6` | € 25.20 |
| `7` | € 25.20 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "ortofrutticoli-agrumari/seniority_assumed_constant · seniority · impact unknown · open"
    SIMPLIFICATION: Importi scatti anzianità assunti costanti per tutto il periodo 2024-2027. La fonte primaria (kitech.it giugno 2026) non indica data decorrenza; il rinnovo 2024 non menziona modifiche agli scatti.

    **Applies when:** `seniority` applies.

    **Remediation:** Source the effective dates of the seniority amounts.

!!! warning "ortofrutticoli-agrumari/ind_fun_assumed_constant · base_salary · impact unknown · open"
    SIMPLIFICATION: IND_FUN 154.94 EUR assunta costante dal 2024-01-01 senza adeguamenti. Allowance pre-euro congelata (300.000 lire). Nessuna fonte indica variazioni nel rinnovo 2024.

    **Applies when:** `base_salary` applies; level in Q.

    **Remediation:** Confirm the IND_FUN amount against the 2024 renewal text.

!!! warning "ortofrutticoli-agrumari/ind_fun_fourteen_months · base_salary · impact unknown · open"
    SIMPLIFICATION: IND_FUN assunta corrisposta su 14 mensilità (ereditato da additional_months contratto); months_per_year non specificato. Nessuna fonte accessibile indica il numero di mensilità dell'indennità. Impatto: ±154.94 EUR/anno livello Q se la vera risposta è 12 mensilità.

    **Applies when:** `base_salary` applies; level in Q; run kind in fourteenth.

    **Remediation:** Source the number of monthly payments of IND_FUN.

!!! warning "ortofrutticoli-agrumari/assumed_sickness_integration_rates · sickness · impact unknown · open"
    SIMPLIFICATION: Tassi integrazione malattia assunti 100% (carenza_integration_rate e full_pay_integration_rate). Fonti accessibili non riportano percentuali per H341. Comporto 180 giorni da snippet ricerca H341. Il motore può sovrastimare il supplemento datoriale durante la malattia.

    **Applies when:** `sickness` applies.

    **Remediation:** Source the carenza and integration rates of the CCNL and replace the assumed 100%.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days. INPS computes it on its own daily base (retribuzione media globale giornaliera of the month before) and on calendar days. The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Compute the INPS indemnity on the INPS daily base and calendar days of the INPS rules, with the pay of the month before, then resolve this limitation.

!!! warning "sickness_cumulation_window · sickness · impact unknown · open"
    The CCNL tier and the comporto are counted on the days of one episode and the relapses it continues. A CCNL that sums the sickness of separate episodes over a window (a calendar year, the last three years) can reach a lower tier or the end of the comporto earlier than the engine shows. The run is affected when an earlier episode outside the relapse chain is recorded.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Add the cumulation window of each CCNL to its sickness rule, with the source, and count the tier and the comporto over it.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax or INPS ruleset marked provisional: the sources of its year are not published yet (INPS circular on the massimale, minimale and rates of the year; regional and municipal surtax resolutions; budget law of the year), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; the indexed amounts (INPS massimale and minimale) do not, and any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Valori base_salary livelli 4, 5, 6S, 7 ai periodi non-giugno-2026 derivati via regola proporzionale (stesso aumento percentuale, da edotto.com/fisascat.it). Modello non-compounding: tranche_i = round(pre_rinnovo_livello * pct_i, 2), pct_i = tranche_L6_EUR / L6_pre. Back-solve unico su giugno 2026 confermato per tutti i 9 livelli. Rischio: zero (round-trip verificato).

!!! note ""
    SIMPLIFICATION: Apprendistato non modellato (apprenticeship=[]). Il rinnovo 2024 ha modificato la disciplina dell'apprendistato ma il testo consolidato è dietro paywall. Le fonti accessibili (aggregatori) non sono attribuibili con certezza al CCNL Fruitimprese H341 rispetto al CCNL Confsal/Fesica. Rischio: retribuzione apprendistato restituisce zero anziché un importo errato.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| CCNL Ortofrutta e Agrumi (Import-Export) — tabella retributiva CNEL H341 (lavoro-economia.it) | tabella_retributiva | 2024-07-19 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=72) |
| CCNL Ortofrutta ed Agrumi — tabella settembre 2024 con Contingenza=0 e EDR=0 (ilccnl.it) | tabella_retributiva | 2024-09-01 | [↗](https://ilccnl.it/contratto/ccnl/ortofrutticoli-ed-agrumari) |
| Kitech tabella retributiva CCNL Ortofrutta ed Agrumari — giugno 2026 | tabella_retributiva | 2026-06-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=72) |
| CCNL Ortofrutticolo — accordo di rinnovo 2024-2027 (Fisascat-CISL comunicato) | associazione | 2024-07-19 | [↗](https://www.fisascat.it/news/ccnl-ortofrutticolo) |
| Aziende ortofrutticole e agrumarie — siglato il rinnovo del CCNL (edotto.com) | associazione | 2024-07-19 | [↗](https://www.edotto.com/articolo/ortofrutticoli-agrumari-rinnovo-ccnl) |

??? note "Coverage notes"
    IND_FUN livello Q: 154.94 EUR/mese. Lavoro-economia.it c=72 mostra livello Q totale = 2551.53 = 2396.59 (base giugno 2026) + 154.94. Equivale a 300.000 lire (300.000/1936.27 = 154.94): allowance pre-euro congelata.
    
    Salary model: conglobato. ilccnl.it Sept 2024 table shows Contingenza=0.00 e EDR=0.00 per tutti i livelli. Divisore orario 173 confermato da lavoro-economia.it c=72 (CNEL H341) quota diretta: 'L'importo della retribuzione oraria si ottiene dividendo l'importo della retribuzione mensile per il divisore convenzionale 173'. Verifica aritmetica su 4 livelli: 1 (2286.83/13.22=173), 2 (2020.70/11.68=173), 3 (1932.23/11.17=173), 6 (1599.53/9.25=173).
    
    Identità c=72 = CNEL H341 = Fruitimprese: tabella giugno 2026 su lavoro-economia.it c=72 forward-verified su 9 livelli con tranches Fruitimprese (65+20+20 EUR a livello 6, da edotto.com e fisascat.it) con match al centesimo. Un tavolo Confsal/Fesica non riprodurrebbe questa struttura. Stipendianti: Fruitimprese + FLAI-CGIL, FISASCAT-CISL, UILTUCS-UIL (da ilccnl.it e consulentidellavoro.fi.it).
    
    14 mensilità (tredicesima + quattordicesima): lavoro-economia.it c=72 quote 'I lavoratori hanno diritto alla corresponsione di 14 mensilità'. Quattordicesima corrisposta entro luglio (fisascat.it comunicato 2024).
    
    Scatti anzianità: 13 aumenti triennali, lavoro-economia.it c=72 quote 'i lavoratori hanno diritto a maturare 13 aumenti triennali'. Importi mensili da kitech.it CodiceCateg=72 (tabella giugno 2026): Q=30.45, 1=29.40, 2=27.30, 3=27.30, 4=26.25, 5=26.25, 6S=25.20, 6=25.20, 7=25.20.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/ccnl/data/ortofrutticoli-agrumari.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/ortofrutticoli-agrumari.py"
```
