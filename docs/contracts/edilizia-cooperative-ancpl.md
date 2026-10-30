# CCNL Edilizia — Cooperative (ANCPL/Legacoop/Confcooperative/AGCI)

| | |
|---|---|
| **CNEL code** | `F016` |
| **Sector** | Edilizia |
| **Family** | `edilizia` |
| **Tax sector** | `edilizia` |
| **Last renewal** | 2025-02-21 |
| **Workers (est.)** | ~90000 |
| **Ruleset version** | `2026.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - ANCPL-Legacoop Costruzioni
    - Confcooperative Lavoro e Servizi
    - AGCI
    - FILLEA-CGIL
    - FILCA-CISL
    - FENEAL-UIL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | bilateral_funds, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 1 verified / 57 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-02-21 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-03-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 96 - Tredicesima mensilità (p. 96): "Nel caso di inizio o di cessazione del rapporto di lavoro nel corso dell'anno devono essere corrisposti tanti dodicesimi dell'ammontare della 13a mensilità per quanti sono i mesi di servizio prestato presso l'impresa. La frazione di mese non superiore ai 15 giorni non va considerata mentre deve essere considerata come mese intero la frazione di mese superiore ai 15 giorni.". Added: more_than 15 (the file applied the engine default, at least 15 days). |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `8Q` | Livello 8Q — quadro senior | € 2,962.99 | 2027-03-01 |
| `8` | Livello 8 — impiegato direttivo senior / tecnico | € 2,962.99 | 2027-03-01 |
| `7Q` | Livello 7Q — quadro | € 2,484.90 | 2027-03-01 |
| `7` | Livello 7 — impiegato direttivo | € 2,484.90 | 2027-03-01 |
| `6` | Livello 6 — impiegato di concetto | € 2,133.34 | 2027-03-01 |
| `5` | Livello 5 — impiegato qualificato / caposquadra | € 1,812.16 | 2027-03-01 |
| `4` | Livello 4 — operaio super-specializzato / impiegato ordine | € 1,621.99 | 2027-03-01 |
| `3` | Livello 3 — operaio specializzato | € 1,508.81 | 2027-03-01 |
| `2` | Livello 2 — operaio qualificato | € 1,354.72 | 2027-03-01 |
| `1` | Livello 1 — operaio comune (manovale) | € 1,185.21 | 2027-03-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `1` | € 8.22 |
| `2` | € 8.22 |
| `3` | € 8.99 |
| `4` | € 9.62 |
| `5` | € 10.46 |
| `6` | € 12.85 |
| `7` | € 13.94 |
| `7Q` | € 13.94 |
| `8` | € 16.53 |
| `8Q` | € 16.53 |

## Apprenticeship

**standard** (type: `percentage`)  
Destination levels: `2`, `3`, `4`, `5`, `6`, `7`, `8`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "edilizia-cooperative-ancpl/operai_seniority_ape · seniority · impact yes · open"
    SENIORITY: 5 scatti biennali (24-month cadence, max 5). For blue-collar workers (levels 1-4), seniority is governed by the Cassa Edile APE system; engine uses the tabular scatti as an approximation.

    **Applies when:** `seniority` applies; level in 1, 2, 3, 4.

    **Remediation:** Give levels 1-4 the operaio category with no scatti (APE paid by the Cassa Edile), or split the operai into their own file as edilizia-ance does.

!!! warning "edilizia-cooperative-ancpl/cassa_edile_accruals_missing · bilateral_funds · impact yes · open"
    CASSA EDILE: for blue-collar workers, holidays (8.5%) and Christmas bonus (10%) accrue through the Cassa Edile system. The employer_cost_annual underestimates by ~18.5% of gross for blue-collar workers.

    **Applies when:** `bilateral_funds` applies; level in 1, 2, 3, 4.

    **Remediation:** Model the operai with 12 monthly payments and the 18.5% Cassa Edile accrual (plus the provincial Cassa Edile contribution), as edilizia-ance does, then remove this limitation.

!!! warning "edilizia-cooperative-ancpl/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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

### Without monetary impact

!!! note ""
    SIMPLIFICATION: Apprenticeship provisions for Q levels (7Q, 8Q) are not modelled; quadri are not typically hired as apprentices in the cooperative construction sector.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.studiocani.com/ccnl-edilizia-industria-e-cooperative-aumento-dei-minimi-dal-1-marzo/ | tabella_retributiva | 2025-02-21 | [↗](https://www.studiocani.com/ccnl-edilizia-industria-e-cooperative-aumento-dei-minimi-dal-1-marzo/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=124 | tabella_retributiva | 2025-02-21 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=124) |

??? note "Coverage notes"
    SPLIT MODEL: paga_base (changes each tranche) + contingenza (frozen) + EDR (frozen at 10.33). Tranches: 01/02/2025, 01/03/2026, 01/03/2027. Jointly renewed with ANCE industry contract on 21/02/2025; validity 01/02/2025 to 30/06/2028.
    
    10 LEVELS: 1-8 plus 7Q and 8Q (quadri). Levels 7Q/8Q share paga base with 7/8 but add Indennita' di Funzione = EUR 170.00/month (fixed, not varying by tranche).
    
    ADDITIONAL_MONTHS: 13 (Christmas bonus). The cooperative sector has a gratifica feriale component administered through the Cassa Edile (~8.5% of gross), not modelled. Engine uses 13 months consistent with the edilizia framework (review of 2026-10-30)
    
    INPS: reuses 2026-edilizia.json (proxy rates). Cassa Edile contribution (~18.5%) is separate and not included.
    
    APPRENTICESHIP: single standard percentage track (Art. 92 CCNL), destination levels 2-8 (level 1 and Q levels excluded). Schedule: 72%/72%/78%/78%/85%/90% over 36 months then 100%. Same framework as jointly-renewed ANCE-cooperative CCNL.
    
    T3 INCREASES (01/03/2027) DERIVED: the studiocani.com source confirms T1 and T2 values; T3 amounts are computed from the parametro structure (L1=+50, L2=+57, L3=+63.50, L4=+68.25, L5=+76.50, L6=+90, L7=+105, L8=+125) — same as T2 amounts per the 3-tranche renewal.
    

## Raw data

The contract file this page is generated from: [`agreement/edilizia-cooperative-ancpl.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/edilizia-cooperative-ancpl.json).

## Usage example

```python
--8<-- "docs/examples/agreement/edilizia-cooperative-ancpl/example.py"
```
