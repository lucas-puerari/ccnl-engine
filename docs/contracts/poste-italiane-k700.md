# CCNL Poste Italiane S.p.A. (personale non dirigente)

| | |
|---|---|
| **CNEL code** | `K700` |
| **Sector** | Servizi postali |
| **Tax sector** | `industria` |
| **Last renewal** | 2024-07-23 |
| **Workers (est.)** | ~117k |
| **Ruleset version** | `2026.2` |
| **Extraction** | 🤖 AI-assisted |
| **Verification** | 🔴 Unverified |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - POSTE ITALIANE S.p.A.
    - SLP-CISL
    - SLC-CGIL
    - UIL Poste

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
| **Limits of this contract** | base_salary, inps_employer |

### Verifica

| | |
|---|---|
| **Readiness** | 🧪 Exploratory |
| **Confidence** | 🔴 Unverified |
| **Last human review** | — |

### Freschezza

| | |
|---|---|
| **Last renewal** | 2024-07-23 |
| **Last verified** | — |
| **Latest salary tranche** | 2027-12-01 |

### Semplificazioni note

2 semplificazioni documentate.
Vedi [Known simplifications](#known-simplifications) per i dettagli.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A — posizione retributiva A1 | € 2,169.37 | 2027-12-01 |
| `A2` | Livello A — posizione retributiva A2 | € 1,926.89 | 2027-12-01 |
| `B` | Livello B | € 1,652.98 | 2027-12-01 |
| `C` | Livello C | € 1,522.56 | 2027-12-01 |
| `D` | Livello D | € 1,452.20 | 2027-12-01 |
| `E` | Livello E | € 1,287.61 | 2027-12-01 |
| `F` | Livello F | € 1,154.49 | 2027-12-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 0 increments

## Apprenticeship

**professionalizzante** (type: `under_classification`)  
Destination levels: `B`, `C`, `D`, `E`  
under-level: `1`

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "poste-italiane-k700/edr_pre_privatization · base_salary · impact yes · open"
    SIMPLIFICATION: EDR (elemento distintivo della retribuzione) omitted. Art. 65 I qualifies it as 'ove spettante'; amount not stated in Allegato 9 or CCNL body. Legacy entitlement for pre-privatization workers only.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the EDR for pre-privatization workers once its amount is sourced.

!!! warning "poste-italiane-k700/fondo_quiescenza_poste_rates · inps_employer · impact unknown · open"
    SIMPLIFICATION: INPS industria rates applied. Poste Italiane employees are enrolled in the Fondo Quiescenza Poste (INPS special fund, Art. 7 L. 335/1995; merged from IPOST 2012). Correct rates differ from standard industria rates. Verify against INPS Fondo Quiescenza Poste documentation. Verified 2026-09-09: INPS website confirms Fondo Quiescenza Poste exists for Poste Italiane SpA but specific aliquote not publicly listed on INPS portal in machine-readable form.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Source the Fondo Quiescenza Poste rates and apply them in place of the industria rates.

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
| — | — | 2024-07-23 | [↗](https://www.uilposte.it/wp-content/uploads/2025/01/CCNL-Posteitaliane-Uilposte2024.pdf) |

??? note "Coverage notes"
    Salary model: split. base_salary = minimo tabellare (Allegato 9, changes each tranche); fixed_allowances = contingenza (per-level, frozen) + indennità di funzione for A1/A2 (months_per_year=12).
    
    Hourly divisor 156 from Art. 65 III: retribuzione base oraria = mensile / 156. Cross-check: 36h/week × 52/12 = 156 h/month (Art. 26 normal workweek = 36h).
    
    Additional months: 14. Art. 67 tredicesima: base = posizione retributiva + contingenza + EDR — funzione excluded. Art. 68 quattordicesima: same explicit enumeration. Both articles confirm funzione not in mensilità aggiuntive.
    
    Seniority: no traditional scatti di anzianità for new hires. Retribuzione individuale di anzianità (D.P.R. 335/1990) is a legacy element for pre-privatization workers only (Art. 25 CCNL). Model: cadence_months=24, maximum_count=0.
    
    A1/A2 levels: paga base and contingenza are identical for staff and produzione; funzione differs (Art. 21 CCNL). Modeled as two-tier allowances: base rate (staff, unconditional) + produzione delta via role="produzione". Pass Employee(roles=frozenset(["produzione"])) to add the differential.
    
    Apprenticeship: Art. 24 CCNL — under_classification, inquadrato al livello immediatamente inferiore per l'intera durata (max 36 mesi). Destinations B, C, D, E. Level A excluded (Quadri e coordinamento/controllo). Level F excluded (lowest, no level below).
    
    Headcount: ~116,801 workers (CNEL/INPS archive, K700).
    
    INDENNITA DI FUNZIONE — PRODUZIONE DIFFERENTIAL: Staff rate (A1: 333.33/mo, A2: 187.50/mo) is unconditional. Produzione workers receive an additional delta (A1: +58.34, A2: +45.83) via IND_FUNZIONE_A*_PROD_DELTA with role="produzione". Total produzione: A1=391.67, A2=233.33 (Art. 21 CCNL K700). Callers: pass Employee(roles=frozenset(['produzione'])) for the higher rate.
    
    SIMPLIFICATION: industria CIGO (1.70-2.00%) included in employer INPS rate. Poste Italiane is not a manufacturing firm and is not CIGO-subject; actual employer cost is lower. Verify against INPS circ. for the correct Poste INPS classification.
    
    SIMPLIFICATION: Legacy retribuzione individuale di anzianità (D.P.R. 335/1990) and posizioni economiche differenziate (CCNL 1997) not modeled.
    
    SIMPLIFICATION: Salary tranche 01/07/2024–31/08/2025 covered by one-time 'anticipo sui futuri miglioramenti economici' (lump sum, September 2024). Engine carries paga base at 2024-07-23 level (same as pre-renewal) for that window.
    

## Raw data

??? note "Full JSON (provenance artifact)"
    ```json
    --8<-- "src/ccnl_engine/knowledge/contract/agreement/poste-italiane-k700.json"
    ```

## Usage example

```python
--8<-- "docs/examples/contracts/poste-italiane-k700.py"
```
