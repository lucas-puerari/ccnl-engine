# CCNL Industria Turistica (Federturismo Confindustria)

| | |
|---|---|
| **CNEL code** | `H05B` |
| **Sector** | turismo — alberghi, campeggi, villaggi e strutture ricettive |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-01-01 |
| **Workers (est.)** | ~40k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Federturismo Confindustria
    - FILCAMS-CGIL
    - FISASCAT-CISL
    - UILTuCS

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | seniority, trattamento_integrativo |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 36 verified / 10 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-01-01 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2027-04-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The paga base nazionale conglobata (art. 110) of the nine levels against the Federturismo circular of 16 January 2025 that prints the tables agreed in the renewal of 21 December 2024. | corrected | Federturismo Confindustria, a signatory, prints in its circular of 16 January 2025 the paga base nazionale conglobata of art. 110 'condivise' by the parties for 01/01/2025, 01/06/2025, 01/05/2026 and 01/04/2027 (PDF pp. 1-2, rows A1-D1 on p. 1, D2 on p. 2): the 36 minimi of the file are checked against the general table, not the separate tables of the imprese di viaggi e turismo e congressi (different tranches) or the aziende alberghiere minori (art. 178).<br>The file's values were derived parametrically from A1 and D2 (an aggregator); 11 of them differ by one cent from the printed table and are corrected.<br>The ruleset names this source, published by Federturismo Confindustria, a signatory: source_type contracting_party.<br>Corrected to the printed table: A2 2025-01-01: 2164.27 -> 2164.26; A2 2027-04-01: 2315.87 -> 2315.88; B1 2025-01-01: 2016.87 -> 2016.88; B1 2027-04-01: 2158.18 -> 2158.17; C1 2025-06-01: 1771.22 -> 1771.21; C1 2027-04-01: 1861.27 -> 1861.28; C3 2025-01-01: 1540.03 -> 1540.02; C3 2025-06-01: 1568.17 -> 1568.16; C3 2027-04-01: 1647.90 -> 1647.91; D1 2025-01-01: 1481.04 -> 1481.05; D1 2027-04-01: 1584.79 -> 1584.80. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `A1` | Livello A1 | € 2,500.91 | 2027-04-01 |
| `A2` | Livello A2 | € 2,315.88 | 2027-04-01 |
| `B1` | Livello B1 | € 2,158.17 | 2027-04-01 |
| `B2` | Livello B2 | € 1,973.12 | 2027-04-01 |
| `C1` | Livello C1 | € 1,861.28 | 2027-04-01 |
| `C2` | Livello C2 | € 1,756.59 | 2027-04-01 |
| `C3` | Livello C3 | € 1,647.91 | 2027-04-01 |
| `D1` | Livello D1 | € 1,584.80 | 2027-04-01 |
| `D2` | Livello D2 | € 1,464.57 | 2027-04-01 |

## Seniority increments

**Cadence:** every 36 months  
**Maximum:** 6 increments

| Level | Increment (monthly) |
|---|---:|
| `D2` | € 30.47 |
| `D1` | € 31.25 |
| `C3` | € 32.54 |
| `C2` | € 33.05 |
| `C1` | € 34.86 |
| `B2` | € 36.15 |
| `B1` | € 37.70 |
| `A2` | € 39.25 |
| `A1` | € 40.80 |

## Apprenticeship

**professionalizzante** (type: `percentage`)  
Destination levels: `D2`, `D1`, `C3`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "industria-turistica-federturismo/seniority_cadence_unconfirmed · seniority · impact unknown · open"
    SENIORITY CADENCE: file uses 36 months. Search for H05B 2025 suggests 'ogni due anni di servizio' (24 months) for this contract (lavoro-economia.it H05B, adapt.it). Contrasts with Confcommercio turismo (H05A) which changed from 36 to 48 in 2024 renewal. Cadence needs confirmation from primary CCNL H05B text; if 24 months, file needs correction. Maximum scatti: 6 (confirmed).

    **Applies when:** `seniority` applies.

    **Remediation:** Confirm the seniority cadence (36 or 24 months) against the H05B text.

!!! warning "industria-turistica-federturismo/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! warning "industria-turistica-federturismo/tourism_special_supplement · trattamento_integrativo · impact yes · open"
    TRATTAMENTO INTEGRATIVO SPECIALE (L. 199/2025 art. 1 cc. 18-20, Gazzetta Ufficiale text, https://www.gazzettaufficiale.it/atto/serie_generale/caricaArticolo?art.codiceRedazionale=26A00149&art.dataPubblicazioneGazzetta=2026-01-21&art.flagTipoArticolo=0&art.idArticolo=1&art.idGruppo=1&art.idSottoArticolo=1&art.idSottoArticolo1=10&art.progressivo=1&art.versione=1, page sha256 e05f6f864509f87e7488cdae075fe3a1f2632f6f4577b87ee05479a1ed193c1d): from 1 January to 30 September 2026 the workers of the esercizi di somministrazione di alimenti e bevande (L. 287/1991 art. 5) and of the 'comparto del turismo, ivi inclusi gli stabilimenti termali', with employment income of 2025 not above 40,000 EUR, receive 'un trattamento integrativo speciale, che non concorre alla formazione del reddito, pari al 15 per cento delle retribuzioni lorde corrisposte in relazione al lavoro notturno e alle prestazioni di lavoro straordinario [...] effettuate nei giorni festivi'. The employer pays it 'su richiesta del lavoratore' (c. 20), a fact the request has no field for: the engine does not pay it, so the net pay of a worker who asked for it is understated.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add the worker's request of c. 20 to the request, pay 15% of the night and holiday overtime pay of the run as a credit, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! warning "apprenticeship_pct_undeclared_components · base_salary · impact unknown · open"
    A percentage apprenticeship reduces every fixed allowance whose apprenticeship_pct_relevant flag the data leaves at its default, together with the base salary. Whether the CCNL applies the percentage to that allowance (an EDR, a contingenza, a function allowance) was not sourced. The run is affected when such an allowance is in the apprentice's pay.

    **Applies when:** `base_salary` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source, for each CCNL, the elements the apprenticeship percentage applies to and set apprenticeship_pct_relevant on every allowance; the limitation then no longer applies to its runs.

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
| A1 and D2 confirmed at 01/05/2026. Intermediate levels derived via parametric ratio and independently verified to <EUR 0.02. | tabella_retributiva | 2025-01-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx?CodiceCateg=H05B) |

??? note "Coverage notes"
    CCNL H05B — Federturismo Confindustria. Conglobated model. 9 levels: D2-D1-C3-C2-C1-B2-B1-A2-A1. Divisor 172, 14 months. Function allowances: A1+75 EUR, A2+70 EUR (14 months). Seniority 36-month cadence, max 6.
    
    INPS: uses 2026-terziario.json (TaxSector.TERZIARIO). Same classification as H052 turismo-federalberghi.
    
    SALARY VALUES: parametric derivation verified to <0.02 EUR accuracy across all levels. A1 and D2 taken directly from source; all others derived via stable level-coefficient ratios.
    
    PRE-2025 NOT MODELLED: the CCNL H05B renewal starts Jan 2025; series begins 2025-01-01. Prior CCNL salary tables exist but are out of scope for the current engine version (coverage starts at renewal date). This is a deliberate scope decision.
    
    APPRENTICESHIP: under_classification 2 levels below destination is a contract-specific rule not representable in the engine schema (single under_levels value, not per-destination-level). Modelled as 100% passthrough by design.
    

## Raw data

The contract file this page is generated from: [`agreement/industria-turistica-federturismo.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/industria-turistica-federturismo.json).

## Usage example

```python
--8<-- "docs/examples/agreement/industria-turistica-federturismo/example.py"
```
