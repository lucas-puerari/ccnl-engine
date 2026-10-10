# CCNL per i dipendenti da autoscuole, scuole nautiche e studi di consulenza automobilistica

| | |
|---|---|
| **CNEL code** | `IC91` |
| **Sector** | autoscuole e consulenza automobilistica |
| **Tax sector** | `terziario` |
| **Last renewal** | 2023-02-28 |
| **Workers (est.)** | — |
| **Ruleset version** | `2026.1` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - UNASCA — Unione Nazionale Autoscuole Studi Consulenza Automobilistica
    - CONFARCA — Confederazione Autoscuole Riunite e Consulenti Automobilistici
    - FILT-CGIL
    - FIT-CISL
    - UILTRASPORTI

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
| **Limits of this contract** | bilateral_funds, health_fund_employer, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2023-02-28 |
| **Last verified** | — |
| **Latest salary tranche** | 2022-02-01 |

### Semplificazioni note

3 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Quadri — dirigenti intermedi con ampia discrezionalità e autonomia decisionale (legge 190/85) | € 1,577.20 | 2022-02-01 |
| `5` | 5° livello — impiegati tecnici e amministrativi con autonomia gestionale e responsabilità del proprio settore | € 1,227.87 | 2022-02-01 |
| `4` | 4° livello — impiegati con funzioni tecnicoamministrative e autonomia di iniziativa entro direttive prestabilite | € 1,057.07 | 2022-02-01 |
| `3` | 3° livello — impiegati con mansioni esecutive richiedenti conoscenze teorico-pratiche (es. insegnante di autoscuola) | € 987.04 | 2022-02-01 |
| `2` | 2° livello — impiegati con mansioni esecutive (es. responsabile di segreteria, istruttore di guida) | € 938.41 | 2022-02-01 |
| `1` | 1° livello — lavoratori con mansioni che richiedono semplici capacità pratiche (fattorino, addetto pulizie, usciere) | € 788.61 | 2022-02-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 23.76 |
| `5` | € 18.59 |
| `4` | € 16.01 |
| `3` | € 14.98 |
| `2` | € 14.46 |
| `1` | € 12.39 |

## Apprenticeship

**L1-autoscuole-24m** (type: `under_classification`)  
Destination levels: `1`

**L2-autoscuole-36m** (type: `under_classification`)  
Destination levels: `2`

**L3-autoscuole-48m** (type: `under_classification`)  
Destination levels: `3`

**L4-autoscuole-48m** (type: `under_classification`)  
Destination levels: `4`

**L5-autoscuole-48m** (type: `under_classification`)  
Destination levels: `5`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "autoscuole-unasca/fondo_est_health_fund · health_fund_employer · impact yes · open"
    SIMPLIFICATION: Fondo EST (Art. 46) supplementary health fund not modelled. Contribution: 15 EUR/month employer + 2 EUR/month employee. Not an INPS substitute. employer_cost_annual understated by 180 EUR/year.

    **Applies when:** `health_fund_employer` applies.

    **Remediation:** Model the Fondo EST contributions (15 EUR employer, 2 EUR employee per month).

!!! warning "autoscuole-unasca/ente_bilaterale_contribution · bilateral_funds · impact yes · open"
    SIMPLIFICATION: Ente Bilaterale di settore (Art. 7, from 01/09/2021: 2 EUR/month employer) not modelled. employer_cost_annual understated by 24 EUR/year.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Pass the 2 EUR monthly employer contribution as a bilateral fund event.

!!! warning "autoscuole-unasca/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "provisional_ruleset · irpef · impact unknown · open"
    The run reads a tax ruleset marked provisional: the sources of its year are not published yet (budget law of the year; regional and municipal surtax resolutions), so the values are those of the year before, carried over. Rules in force by statute (the IRPEF brackets of art. 11 and the deductions of art. 13 of the testo unico of D.Lgs. 117/2026) carry over unchanged; any change of the budget law is not applied.

    **Applies when:** `irpef` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional ruleset of the year with the values of its published sources, drop its provisional flag, then resolve this limitation.

!!! warning "provisional_inps_ruleset · inps_employer · impact unknown · open"
    The run reads an INPS ruleset marked provisional: the INPS circulars of its year are not published yet, so the rates, the massimale and the minimale (and the hourly contributions of domestic work) are those of the year before, carried over. The indexed amounts change every January: the carried-over values understate them.

    **Applies when:** `inps_employer` applies; the run takes the engine code path.

    **Remediation:** Replace each provisional INPS ruleset of the year with the values of the INPS circulars of the year, drop its provisional flag, then resolve this limitation.

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2023-02-28 | [↗](https://www.unasca.it/PDF/ccnl/CCNL_AUTOSCUOLE_-_SCUOLE_NAUTICHE_-_STUDI_DI_CONSULENZA_AUTOMOBILISTICA_FIRMATO_IL_28-02-2023.pdf) |
| — | — | 2023-03-14 | [↗](https://www.unasca.it/PDF/ccnl/Verbale_di_Accordo_Rettifica_tabelle14-03-2023.pdf) |

??? note "Coverage notes"
    Salary model: SPLIT. Paga base (minimo tabellare) is a time series with 3 tranches (2021-01-01, 2021-09-01, 2022-02-01). Contingenza (frozen) and EDR (10.33) are fixed_allowances per level. Q level additionally carries indennità di funzione 25.82 EUR (Art. 6). Source: verbale di rettifica 14/03/2023 (authoritative; annuls salary table in main CCNL).
    
    Verbale di rettifica 14/03/2023: level 5 increment per tranche = 34.67 EUR (not 32.67 as printed in first table of both main CCNL and verbale). The second table of the verbale prints derived totals: 1158.53+34.67+34.67+445.84+10.33=1684.04 confirming 34.67. lavoro-economia.it propagated the typo and shows 1680.04 for a-regime; the correct value is 1684.04.
    
    hourly_divisor: 170 — confirmed from Art. 13 comma 3 CCNL ('dividendo la retribuzione mensile per 170'). Consistent with Art. 9 comma 1: weekly hours 39h = 39x52/12 ≈ 169h rounded to 170.
    
    additional_months: 14 — Art. 18 (tredicesima, Natale) and Art. 19 (quattordicesima, luglio) both explicit in CCNL.
    
    Seniority: 5 scatti biennali (cadence_months=24, maximum_count=5). Amounts from Art. 17 CCNL: Q=23.76, 5°=18.59, 4°=16.01, 3°=14.98, 2°=14.46, 1°=12.39 EUR.
    
    Contingenza values from Art. 13 CCNL, Art. 4 (frozen since 1993 interconfederale): Q=452.81, 5°=445.84, 4°=442.41, 3°=439.83, 2°=439.83, 1°=437.56 EUR.
    
    EDR: 10.33 EUR/month, uniform all levels. Elemento Distinto della Retribuzione from 1992 interconfederale CGIL/CISL/UIL/Confindustria (ITL 20,000 converted). Confirmed absorbed in verbale totals: per-level Art. 12 EDR amounts do not appear as additive — verbale derived totals match paga base + contingenza + 10.33 + (Q: 25.82) exactly.
    
    Q indennità di funzione: 25.82 EUR/month x 14 mensilità. PRIMARY SOURCE confirmed from Art. 6 CCNL ('Ai dipendenti classificati come quadri spetta un’indennità di funzione pari a euro 25,82 mensili lorde per quattordici mensilità').
    
    Apprenticeship: apprendistato professionalizzante, under-classification model (Art. 43 CCNL). Q excluded. Level 1: 24 months all at destination (no levels below available). Level 2: 36 months (0-23 at 1-below, 24-35 at dest). Levels 3-5: 48 months (0-15 at 2-below, 16-31 at 1-below, 32-47 at dest). Source: Art. 43 CCNL 28/02/2023.
    
    tax_sector: terziario. Following IC35 (autorimesse) precedent for transport/services CCNL with UNASCA/CONFARCA. Sector uses standard terziario INPS rates.
    
    Contract in ultra-vigenza since 01/01/2024 (expired 31/12/2023 per Art. 50). Negotiations broke down July 2026. Salary amounts remain operative per Art. 2074 c.c.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/autoscuole-unasca.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/autoscuole-unasca.py"
```
