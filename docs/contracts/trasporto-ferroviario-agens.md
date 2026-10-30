# CCNL Attività Ferroviarie — AGENS

| | |
|---|---|
| **CNEL code** | `I320` |
| **Sector** | trasporto |
| **Family** | `trasporti-logistica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2025-05-22 |
| **Workers (est.)** | ~75k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - AGENS — Aziende Aderenti alla Sezione Ferroviaria di Conftrasporto
    - FILT-CGIL — Federazione Italiana Lavoratori Trasporti
    - FIT-CISL — Federazione Italiana Trasporti
    - Uiltrasporti
    - FAST-Confsal — Federazione Autonoma Sindacati Trasporti
    - UGL Ferrovieri
    - ORSA Ferrovie

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, inps_employer, seniority |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 49 verified / 7 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-05-22 |
| **Last review** | 2026-10-18 |
| **Latest salary tranche** | 2026-06-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The accrual rule of the tredicesima (fractions of a month) against the full CCNL text. | corrected | Art. 70 - Tredicesima e quattordicesima mensilità (p. 119): "il lavoratore ha diritto a tanti dodicesimi dell'ammontare della tredicesima e/o della quattordicesima mensilità, quanti sono i mesi interi di servizio prestati presso l’azienda nei 12 mesi antecedenti quello di erogazione. La frazione di mese superiore a quindici giorni va considerata a questi effetti come mese intero.". Added: more_than 15 (the file applied the engine default, at least 15 days). |
| 2026-10-18 | claude-opus-5-5 (ai) | The base salaries (minimi contrattuali mensili) of all 16 posizioni retributive for the tranches from 1.6.2025, 1.11.2025 and 1.6.2026 against the pay table of the CCNL text of 22 May 2025 published by ORSA Ferrovie, a signatory union. | confirmed | Art. 68 punto 3 (PDF p. 117, printed p. 116) prints the minimi contrattuali mensili of the 16 posizioni retributive Q1-F2 in three columns (dal 1°.6.2025, dal 1°.11.2025, dal 1°.6.2026); all 48 file values match the printed table.<br>Art. 68 punto 3.1: "Gli importi dei minimi contrattuali di cui sopra sono comprensivi dell'ex indennità di contingenza (...) nonché dell'E.D.R. di cui al Protocollo Interconfederale del 31 luglio 1992 e dell'E.D.R. di cui all'accordo nazionale del 24.1.2008." This confirms the conglobated base_salary model of the file.<br>The indennità di funzione Quadri (art. 71) is a separate element of pay (art. 68 punto 1.2 c), so the file's Q1/Q2 base_salary correctly excludes it. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q1` | Level Q1 — railway quadri (senior management), with IND_FUN function allowance | € 2,826.07 | 2026-06-01 |
| `Q2` | Level Q2 — railway quadri (middle management), with IND_FUN function allowance | € 2,483.02 | 2026-06-01 |
| `A` | Level A — senior railway managers, strategic operational leadership | € 2,401.34 | 2026-06-01 |
| `B1` | Level B1 — railway department managers, senior management roles | € 2,286.99 | 2026-06-01 |
| `B2` | Level B2 — railway section managers, intermediate management roles | € 2,188.97 | 2026-06-01 |
| `B3` | Level B3 — railway supervisors, operational management duties | € 2,156.31 | 2026-06-01 |
| `C1` | Level C1 — senior railway professionals, team coordination roles | € 2,107.30 | 2026-06-01 |
| `C2` | Level C2 — railway professionals, specialist operational coordination | € 2,074.62 | 2026-06-01 |
| `D1` | Level D1 — senior railway technicians, advanced professional duties | € 2,041.95 | 2026-06-01 |
| `D2` | Level D2 — experienced railway technicians, intermediate professional roles | € 1,976.62 | 2026-06-01 |
| `D3` | Level D3 — qualified railway technicians, standard professional duties | € 1,943.94 | 2026-06-01 |
| `E1` | Level E1 — specialised railway workers, technical operational duties | € 1,911.26 | 2026-06-01 |
| `E2` | Level E2 — skilled railway workers, certified operational roles | € 1,829.60 | 2026-06-01 |
| `E3` | Level E3 — semi-skilled railway workers, qualified operational tasks | € 1,796.91 | 2026-06-01 |
| `F1` | Level F1 — basic railway workers, standard operational tasks | € 1,666.23 | 2026-06-01 |
| `F2` | Level F2 — entry-level railway workers, unskilled support tasks | € 1,633.56 | 2026-06-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 7 increments

| Level | Increment (monthly) |
|---|---:|
| `Q1` | € 47.19 |
| `Q2` | € 38.27 |
| `A` | € 35.95 |
| `B1` | € 33.62 |
| `B2` | € 31.77 |
| `B3` | € 31.30 |
| `C1` | € 29.91 |
| `C2` | € 29.45 |
| `D1` | € 28.42 |
| `D2` | € 25.64 |
| `D3` | € 25.22 |
| `E1` | € 24.34 |
| `E2` | € 22.66 |
| `E3` | € 22.66 |
| `F1` | € 18.58 |
| `F2` | € 18.22 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "trasporto-ferroviario-agens/e2_e3_seniority_amounts · seniority · impact unknown · open"
    SENIORITY: biennial (cadence 24 months), maximum 7 scatti. Per-level EUR amounts from lavoro-economia.it and kitech.it (both aggregators). NOTE: E2 and E3 show identical scatto amounts (22.66) in both aggregator sources; unconfirmed against the primary CCNL text and should be verified before relying on E2/E3 seniority amounts.

    **Applies when:** `seniority` applies; level in E2, E3.

    **Remediation:** Verify the E2 and E3 scatto amounts against the primary CCNL text.

!!! warning "trasporto-ferroviario-agens/pre_june_2025_tables · base_salary · impact yes · open"
    PRE-JUN 2025 PERIOD NOT MODELLED. The CCNL contractual coverage runs 2024-01-01 to 2026-12-31. The Jan 2024 – May 2025 wage gap was compensated by a lump-sum una tantum paid in Aug 2025 (per redigo.info), explicitly stated as having no effect on any contractual institute ('non avranno riflessi su alcun istituto contrattuale'). Salary periods therefore start 01/06/2025. A run before 1 June 2025 reads no salary table and fails (SeriesGapError, outside the validity window of the file); the window declared for completeness starts on 1 January 2026, so only an arrears or history computation would need the earlier tables (review of 2026-10-30).

    **Applies when:** `base_salary` applies; before 2025-06-01.

    **Remediation:** Model the January 2024 - May 2025 salary tables if an arrears or history computation needs them.

!!! warning "trasporto-ferroviario-agens/fondo_solidarieta_ferrovie · inps_employer · impact yes · open"
    FONDO DI SOLIDARIETA FERROVIE. Contribution rate 0.20% confirmed: 2/3 a carico di Ferrovie (datore, ≈0.133%), 1/3 a carico dei lavoratori (≈0.067%). Source: INPS circolare (confirmed by inps.it/fondo-ferrovie-dello-stato and consulenza.it). Not modelled in the data (parameters.solidarity_fund is null although the engine supports it); adds approximately 0.067% to employee cost and 0.133% to employer cost above the standard INDUSTRIA INPS rates. (review of 2026-10-30)

    **Applies when:** `inps_employer` applies.

    **Remediation:** Set parameters.solidarity_fund (code fondo_ferrovie, employer_rate 0.00133, employee_rate 0.00067, sourced from the INPS circular), as studi-professionali-confprofessioni does.

!!! warning "trasporto-ferroviario-agens/seniority_amounts_before_june_2026 · seniority · impact unknown · open"
    SENIORITY AMOUNTS PRE-JUN 2025. Per-level scatto amounts are sourced from lavoro-economia.it/kitech.it representing the Jun 2026 table. Whether identical values applied in the Jun 2025 and Nov 2025 tranches is unconfirmed. Modelled as constant from 01/06/2025.

    **Applies when:** `seniority` applies; before 2026-06-01.

    **Remediation:** Confirm the seniority amounts of the June 2025 and November 2025 tranches.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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
| Tabelle retributive I320. Three tranches: 01/06/2025, 01/11/2025, 01/06/2026. Hourly divisor 160. Contingenza=0.00, terzo elemento=0.00 for all levels confirming conglobated model. | altro | 2025-05-22 | [↗](https://ilccnl.it/ccnl/ferrovie/ferrovie-attivita-ferroviarie/tabelleretributive) |
| Seniority increments confirmed: 7 scatti biennali (24 months cadence), per-level EUR amounts from current table. Additional months 14 (tredicesima + quattordicesima) confirmed. | altro | 2025-05-22 | [↗](https://www.lavoro-economia.it/ccnl/ccnl.aspx?c=299) |
| Cross-confirmation of function allowances Q1=250.00, Q2=130.00 additive to base tabellare. Seniority per-level amounts cross-confirmed with lavoro-economia.it. | altro | 2025-05-22 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx) |
| Una tantum for Jan 2024-May 2025 gap explicitly stated as non-reflective on any contractual institute. Three salary tranches Jun 2025 / Nov 2025 / Jun 2026 confirmed. Additional months 14 cross-confirmed. | altro | 2025-05-22 | [↗](https://www.redigo.info/2025/05/ccnl-ferrovie-rinnovo-2025) |
| Apprenticeship: apprendistato professionalizzante max 36 months. Pay rates are defined in the Piano Formativo Individuale (PFI) per worker, not as a contract-level table. Source of MISSING coverage determination. | altro | 2025-05-22 | [↗](https://www.leggeinchiaro.it/ccnl-ferrovie) |

??? note "Coverage notes"
    SALARY MODEL: conglobated. ilccnl.it salary table shows contingenza=0.00 and terzo elemento=0.00 for all 16 levels. kitech.it confirms additive structure: Q1 base tabellare=2826.07 + IND_FUN=250.00 total, Q2 base=2483.02 + IND_FUN=130.00 total. Two aggregator sources (ilccnl.it, kitech.it) agree on the decomposition, establishing the function allowances are additive to the conglobated base. Primary CCNL text (AGENS/FILT-CGIL) was not directly retrieved; all parameters derive from aggregator tables.
    
    SIGNATORIES: AGENS (employer association, Conftrasporto affiliate) + FILT-CGIL/FIT-CISL/Uiltrasporti/FAST-Confsal/UGL Ferrovieri/ORSA Ferrovie (workers). CNEL code I320. The operating companies (FS Italiane, Trenitalia, RFI) are AGENS members; AGENS is the formal signatory.
    
    HOURLY DIVISOR: 160, verbatim from ilccnl.it salary table. Standard for 40h/week contractual regime (160 = 40 × 4).
    
    ADDITIONAL MONTHS: 14 — tredicesima + quattordicesima, confirmed from lavoro-economia.it and redigo.info (rinnovo May 2025).
    
    FUNCTION ALLOWANCES (IND_FUN): Q1 receives +250.00/month, Q2 receives +130.00/month. Modelled as fixed_allowances with code IND_FUN effective from first salary tranche (01/06/2025). Two aggregator sources (ilccnl.it, kitech.it) agree the allowances are additive to the base tabellare.
    
    APPRENTICESHIP. I320 specifies apprendistato professionalizzante (max 36 months per Art. 29 Parte Generale). Per leggeinchiaro.it, retributive percentages are defined in the Piano Formativo Individuale (PFI) on a per-worker basis and are not published as a contract-level table. No fixed percentage or under-classification track exists in the CCNL text; the apprenticeship array is therefore empty by contract structure, not by modelling omission. Analogous to public-sector contracts where apprendistato is excluded from scope.
    

## Raw data

The contract file this page is generated from: [`agreement/trasporto-ferroviario-agens.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/trasporto-ferroviario-agens.json).

## Usage example

```python
--8<-- "docs/examples/agreement/trasporto-ferroviario-agens/example.py"
```
