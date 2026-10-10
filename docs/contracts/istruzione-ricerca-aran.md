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
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ARAN
    - FLC CGIL
    - CISL FSUR
    - UIL SCUOLA RUA
    - GILDA UNAMS
    - SNALS CONFSAL

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
| **Limits of this contract** | base_salary, inps_employee, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | 2026-09-18 |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2025-12-23 |
| **Last verified** | 2026-09-18 |
| **Latest salary tranche** | 2024-01-01 |

### Semplificazioni note

7 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `FUNZIONARIO_ED_ESPERTO` | ATA: Funzionario ed esperto (ex dsga, direttori servizi generali) | € 1,960.65 | 2024-01-01 |
| `DOCENTE_SECONDARIA` | Docente secondaria I grado (PE/Ed.Fisica) e secondaria II (laurea) | € 1,866.79 | 2024-01-01 |
| `DOCENTE_DIPLOMATO_SECONDARIA` | Docente diplomato degli istituti secondari di II grado | € 1,724.65 | 2024-01-01 |
| `DOCENTE_INFANZIA_PRIMARIA` | Docente scuola dell'infanzia e primaria | € 1,724.65 | 2024-01-01 |
| `ASSISTENTE` | ATA: Assistente amministrativo, assistente tecnico, cuoco, infermiere | € 1,496.85 | 2024-01-01 |
| `OPERATORE` | ATA: Operatore scolastico (nuovo profilo dal 1/5/2024 CCNL 18/1/2024) | € 1,375.38 | 2024-01-01 |
| `COLLABORATORE_SCOLASTICO` | ATA: Collaboratore scolastico (ex bidello, ex commesso) | € 1,342.82 | 2024-01-01 |

## Seniority increments

**Cadence:** every 1 months  
**Maximum:** 0 increments

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "istruzione-ricerca-aran/higher_seniority_bands_missing · base_salary · impact yes · open"
    Base salary = fascia 0-8 anni (entry level). Le 6 fasce di anzianità (0-8, 9-14, 15-20, 21-27, 28-34, 35+) non sono scatti automatici ma bande per anzianità di servizio. Fascia superiore non modellata.

    **Applies when:** `base_salary` applies; seniority of at least 108 months.

    **Remediation:** Model the six seniority bands (fasce) of the tabellare.

!!! warning "istruzione-ricerca-aran/seniority_bands_not_increments · seniority · impact yes · open"
    seniority maximum_count=0 (fasce non sono scatti automatici nell'accezione del CCNL privato). Per la fascia di anzianità corretta, usare negotiated_ral o livello dedicato.

    **Applies when:** `seniority` applies; seniority of at least 108 months.

    **Remediation:** Model the seniority bands as band-dependent salary tables instead of maximum_count=0.

!!! warning "istruzione-ricerca-aran/period_1_start_approximated · base_salary · impact unknown · open"
    valid_from period 1 = 2022-01-01 (inizio validità del triennio). Il previgente CCNL 2019-2021 aveva stabilito i valori pre-2024; la data esatta di firma del CCNL 2019-2021 non è disponibile dalla fonte e viene approssimata.

    **Applies when:** `base_salary` applies; before 2024-01-01.

    **Remediation:** Source the signing date of the CCNL 2019-2021 for the start of period 1.

!!! warning "istruzione-ricerca-aran/enam_base · inps_employee · impact yes · open"
    The ENAM of a permanent teacher of the scuola dell'infanzia and primaria (L. 93/1957 art. 3: 1% of 80% of the stipendio) is computed on the whole minimum of the level; the stipendio it counts leaves out the IIS conglobata the retribuzione tabellare holds, which the bundle does not give apart: the contribution is overstated.

    **Applies when:** `inps_employee` applies; the run takes the engine code path.

    **Remediation:** Source the IIS conglobata of the profile, leave it out of the ENAM base, then remove this note.

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
    CNEL S305 confermato per comparto, include tutte le sezioni (scuola, università, ricerca, AFAM).

!!! note ""
    Hourly divisor 156 = 36h/settimana × 52/12. I docenti hanno orario cattedra (18h/settimana insegnamento), non direttamente comparabile. Il divisore si applica per l'hourly_rate indicativo.

!!! note ""
    DOCENTE_SECONDARIA aggrega secondaria I grado e secondaria II (laurea) che condividono lo stesso tabellare entry. DOCENTE_INFANZIA_PRIMARIA aggrega anche secondaria II (diploma) con stesso tabellare entry.

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
    
    PENSION FUND. Fondo Scuola Espero (1% + 1%); enrolment is a fact, the silenzio-assenso of the hires from 2019 is not inferred, nor the three months a fixed term needs to enrol. The TFR conferred stays a notional INPS accrual.
    
    ASSICURAZIONE SOCIALE VITA. The employers of this CCNL are Amministrazioni dello Stato (the State schools; the forze di polizia), which INPS circ. 104/2014 leaves out of the Assicurazione Sociale Vita (ex ENPDEP): meta.public_life_insurance is false.
    
    LEVELS. The Tabelle A1 and A2 of the CCNL 2022-2024 (from 1.1.2024) list 'Docente scuola dell'infanzia ed elementare' and 'Docente diplomato istituti sec. II grado' as two rows with the same amounts (22,420.48 a year in the first band): two levels with the same minimum, DOCENTE_INFANZIA_PRIMARIA and DOCENTE_DIPLOMATO_SECONDARIA, since only the first owes the ENAM.
    
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
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/istruzione-ricerca-aran.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/istruzione-ricerca-aran.py"
```
