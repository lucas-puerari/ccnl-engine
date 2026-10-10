# CCNL Chimica e Affini PMI — Unionchimica Confapi

| | |
|---|---|
| **CNEL code** | `B018` |
| **Sector** | chimica |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-02-23 |
| **Workers (est.)** | ~56k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Unionchimica — Unione Italiana Industria Chimica PMI (Confapi)
    - FILCTEM-CGIL — Federazione Italiana Lavoratori Chimica Tessile Energia Manifatturiero
    - FEMCA-CISL — Federazione Energia Moda Chimica Affini
    - UILTEC-UIL — Unione Italiana Lavoratori Tecnologie Energie Chimica

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
| **Limits of this contract** | base_salary, seniority |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2026-02-23 |
| **Last verified** | — |
| **Latest salary tranche** | 2026-01-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `H` | Level H — senior managers, top technical executives (quadri) | € 3,168.51 | 2026-01-01 |
| `G` | Level G — managers, senior professionals, department heads | € 2,973.58 | 2026-01-01 |
| `F` | Level F — senior technical staff, team leaders | € 2,703.06 | 2026-01-01 |
| `E` | Level E — specialist workers, junior technical staff | € 2,444.03 | 2026-01-01 |
| `D` | Level D — highly skilled operai, senior impiegati | € 2,267.00 | 2026-01-01 |
| `C` | Level C — skilled operai, standard impiegati | € 2,033.35 | 2026-01-01 |
| `B` | Level B — semi-skilled operai and lower-grade impiegati | € 1,830.43 | 2026-01-01 |
| `A` | Level A — entry workers, unskilled, first-time employees | € 1,690.69 | 2026-01-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A` | € 10.33 |
| `B` | € 11.88 |
| `C` | € 12.91 |
| `D` | € 13.94 |
| `E` | € 15.49 |
| `F` | € 18.08 |
| `G` | € 20.66 |
| `H` | € 23.24 |

## Apprenticeship

**professionalizzante_C_H** (type: `under_classification`)  
Destination levels: `C`, `D`, `E`, `F`, `G`, `H`  
under-level: `1`

**professionalizzante_B** (type: `under_classification`)  
Destination levels: `B`  
under-level: `1`

**professionalizzante_A** (type: `under_classification`)  
Destination levels: `A`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "chimica-affini-pmi-unionchimica/tranches_2027_2028 · base_salary · impact yes · open"
    SINGLE TRANCHE ONLY. Only the 1 January 2026 tranche is modelled. The 4 subsequent tranches (Apr 2027, Dec 2027, Jun 2028, Dec 2028) are not accessible from primary source at time of extraction. Update with official amounts when the renewal text becomes available.

    **Applies when:** `base_salary` applies; from 2027-04-01.

    **Remediation:** Add the April 2027, December 2027, June 2028 and December 2028 tranches from the renewal text.

!!! warning "chimica-affini-pmi-unionchimica/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

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

!!! warning "tfr_compensation_apprentice_guarantee_fund · inps_employer · impact yes · open"
    An apprentice whose TFR goes to a pension fund or to the Fondo Tesoreria takes the 0.28-point relief of D.L. 203/2005 art. 8, but not the exemption from the 0.20% Fondo di garanzia contribution of D.Lgs. 252/2005 art. 10 c. 2: no source found says whether the apprentice rate (10% of L. 296/2006 art. 1 c. 773 plus NASpI and the integration funds) holds a Fondo di garanzia share to exempt. The employer contributions of the run may be overstated by 0.20% of the INPS base.

    **Applies when:** `inps_employer` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Find an INPS source on the Fondo di garanzia share of the apprentice rate, then exempt it with the other workers or record that none is due.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| — | — | 2026-02-23 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=181) |

??? note "Coverage notes"
    SALARY MODEL: split. base_salary = minimum contractual (minimo tabellare). Levels H, G, F, E carry fixed_allowances: H has indennità di funzione (IND_FUN, EUR 160.00); G, F, E have aggiunta personale (AGG_PERSONALE, EUR 25.82 / 15.49 / 5.16). All allowances are TFR-relevant and contribution-relevant (default).
    
    RENEWAL: Unionchimica Confapi CCNL signed 23 February 2026, effective 1 January 2026 – 31 December 2028. Five tranches: 1 Jan 2026, 1 Apr 2027, 1 Dec 2027, 1 Jun 2028, 1 Dec 2028. Source: kitech.it B018.
    
    LEVELS: 8 professional levels A (lowest) to H (highest). Scala parametrale: H=100 reference, descending. All levels confirmed from kitech.it Jan 2026 table.
    
    CNEL CODE: B018 (Unionchimica Confapi). Distinct from B011 (Federchimica) which covers large-firm chemical-pharmaceutical. B018 covers PMI (piccole e medie imprese) chemical sector.
    
    TAX SECTOR: INDUSTRIA (existing). Standard INPS industria rates apply (2026-industria.json). No bilateral fund substitutes INPS in this contract.
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: kitech.it B018 mensilità aggiuntive field.
    
    SENIORITY: biennale (24 months), maximum 5 scatti. Per-level EUR amounts from kitech.it Jan 2026 table: A=10.33, B=11.88, C=12.91, D=13.94, E=15.49, F=18.08, G=20.66, H=23.24.
    
    CHIMICA-CONCIA SUB-SECTOR SCOPE. Unionchimica Confapi covers three sub-sectors with different hourly divisors: Chimica-Concia (175), Plastica-Gomma (169), Abrasivi-Ceramica-Vetro (173). Only Chimica-Concia (divisor 175) is modelled — deliberate scope choice. The level codes and salary amounts are identical across all sub-sectors; only the hourly divisor differs.
    
    HOURLY DIVISOR 175: confirmed by cross-reference with CCNL Federchimica B011 (kitech.it), which independently uses 175 for chemical-pharmaceutical industry (same contractual week = 40h, 40×52/12=173.33 rounded to 175 via industry convention). No primary contractual clause directly retrieved but cross-verified via B011.
    
    APPRENTICESHIP. Apprendistato professionalizzante per sotto-inquadramento (D.Lgs. 81/2015). Durata massima 36 mesi, uniforme per tutti i livelli e sub-settori. Struttura: primo periodo (mesi 1-10) a 2 livelli sotto la destinazione; secondo periodo (mesi 11 a fine contratto) a 1 livello sotto la destinazione; al termine dell'apprendistato l'inquadramento finale è riconosciuto. Tre track modellati: professionalizzante_C_H (C-H, schema standard 2→1), professionalizzante_B (destinazione B: capped ad A per assenza di livelli inferiori, periodo unico), professionalizzante_A (destinazione A: resta ad A per tutta la durata). Fonte primaria: schede CNEL B018 direzionelavoro.it (ottobre 2023), voce (g) art. 1 Cap. I. Confermato invariato dal rinnovo 23/02/2026 (Confapi Padova circolare): apprendistato non oggetto di modifica.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/chimica-affini-pmi-unionchimica.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/chimica-affini-pmi-unionchimica.py"
```
