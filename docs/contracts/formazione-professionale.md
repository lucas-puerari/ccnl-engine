# CCNL Formazione Professionale (CNOS-FAP/CIOFS-FP/FORMA/CNF)

| | |
|---|---|
| **CNEL code** | `T261` |
| **Sector** | formazione professionale |
| **Family** | `istruzione-formazione` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2024-03-01 |
| **Workers (est.)** | ~19.8k |
| **Ruleset version** | `2026.1` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - CNOS-FAP
    - CIOFS-FP
    - FORMA
    - CNF
    - FLC-CGIL
    - FLC-CISL (CISL Scuola)
    - UIL Scuola RUA
    - SNALS-CONFSAL
    - ANIEF

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ✅ |
| **Limits of this contract** | absence, leave, sickness |

3 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🟢 Verified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 0 verified / 33 derived / 1 assumed / 1 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2024-03-01 |
| **Last review** | — |
| **Latest salary tranche** | 2025-09-01 |

## Review history

No review is recorded.

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `IX` | Livello IX — dirigente o quadro con massima responsabilita gestionale | € 3,222.79 | 2025-09-01 |
| `VIII` | Livello VIII — quadro superiore, direttore di centro o responsabile senior | € 2,627.71 | 2025-09-01 |
| `VII` | Livello VII — coordinatore didattico o responsabile di progetto complesso | € 2,440.58 | 2025-09-01 |
| `VI` | Livello VI — formatore senior o responsabile di area | € 2,331.43 | 2025-09-01 |
| `V` | Livello V — formatore o tecnico con autonomia operativa | € 2,057.63 | 2025-09-01 |
| `IV` | Livello IV — impiegato di concetto o tecnico qualificato | € 1,975.16 | 2025-09-01 |
| `III` | Livello III — operatore specializzato, mansioni tecnico-pratiche | € 1,834.59 | 2025-09-01 |
| `II` | Livello II — operatore qualificato, mansioni esecutive | € 1,730.71 | 2025-09-01 |
| `I` | Livello I — personale ausiliario e addetto a mansioni generiche | € 1,635.99 | 2025-09-01 |

## Seniority increments

**Cadence:** every 48 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `I` | € 30.00 |
| `II` | € 30.00 |
| `III` | € 30.00 |
| `IV` | € 40.00 |
| `V` | € 55.00 |
| `VI` | € 60.00 |
| `VII` | € 60.00 |
| `VIII` | € 60.00 |
| `IX` | € 60.00 |

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "formazione-professionale/leave_entitlement_rounded · leave · impact yes · open"
    LEAVE (Art. 43): 32 giorni lavorativi on 6-day week + 4 giorni festività soppresse. SIMPLIFICATION: stored as 26 working days on 5-day-week basis (32/1.2=26.67); festività soppresse 4 giorni are not modeled as a separate tier. Source: Art. 43 para 3-4 CCNL.

    **Applies when:** `leave` applies.

    **Remediation:** Model the 32 days on a 6-day week (or 26.67 on 5 days) and the 4 giorni of festività soppresse, with their pay when not taken.

!!! warning "formazione-professionale/sickness_second_tier_75 · sickness · impact yes · open"
    SICKNESS (Art. 50 para 4): 100% for 12 months, 75% for months 13-18. SIMPLIFICATION: second tier (75%) is not captured by the single max_duration_days field; stored as max_duration_days=365 (full-pay period only). Source: Art. 50 para 4 CCNL.

    **Applies when:** `sickness` applies.

    **Remediation:** Add SicknessTier rows (100% months 1-12, 75% months 13-18) and max_duration_days for 18 months.

!!! warning "formazione-professionale/daily_divisor_assumed · absence · impact unknown · open"
    DAILY DIVISOR: Art. 37 specifies 156 ore/month and 5-day week but does not state a daily divisor explicitly. SIMPLIFICATION: by_26 applied as standard for terziario contracts.

    **Applies when:** `absence` applies.

    **Remediation:** Source the daily quota of the CCNL (Art. 29 and 37) and set daily_divisor_method, then remove this limitation.

!!! warning "sickness_inps_daily_base · sickness · impact unknown · open"
    The INPS share of a sick day is the INPS rate times the CCNL daily quota of the current month, counted on the CCNL payable days, when the episode does not let the engine compute the INPS daily base: no SicknessEpisode.inps_base in its relapse chain, an operaio without the days worked or paid of the month before, an impiegato of a month not worked in full without the pay of a whole month, an unknown worker category, or a lavoratore dello spettacolo without the pay of the last daily contributions (SpettacoloSicknessBase). With the base, INPS pays its share on the retribuzione media globale giornaliera of the month before the illness and on calendar days (INPS circ. 134368/1981 point 11). The worker's total for the day is the same; the split between INPS indemnity (outside the contribution base) and employer integration may differ, and with it the contributions.

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Derive the base from the closing state of the engine's own runs so the caller need not state it, then resolve this limitation.

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
| https://www.cislscuola.it/download/ccnl-formazione-professionale-2024-2027/ | altro | 2024-03-01 | [↗](https://www.cislscuola.it/download/ccnl-formazione-professionale-2024-2027/) |

??? note "Coverage notes"
    RENEWAL: CCNL signed 2024-03-01 (CNEL-registered). Original text drafted 18/12/2023. Validity 01/01/2024-31/12/2027. Biennio economico 01/01/2024-31/12/2025.
    
    CONGLOBATED MINIMUMS (Art. 25): Art. 25-A lists 'stipendio tabellare' as the sole fundamental salary component. No contingenza or EDR column. Art. 29 defines hourly rate as 'retribuzione mensile/156' — the tabellare IS the total conglobated amount. fixed_allowances=[] for all levels.
    
    SALARY TABLE 1 (Art. 20): three tranches from primary CCNL PDF (cislscuola.it, signatory union). Tranche 0: 31/12/2023 carry-over from 01/01/2024. Tranche 1: +01/06/2024. Tranche 2 (secondo biennio): +01/09/2025. Second biennium negotiations collapsed 27/05/2026 — no further increase. valid_until=null on 2025-09-01 period is correct.
    
    HOURLY DIVISOR (Art. 29 para 6): 'retribuzione mensile/156'. Art. 29 para 4 states part-time pay is 'tanti trentaseiesimi' (36ths) of full pay, confirming 36h/week. 36x52/12=156. hourly_divisor=156 verified from contract text.
    
    ADDITIONAL MONTHS (Art. 27): tredicesima only, paid by 20 December each year. additional_months=13.
    
    SENIORITY — P.E.O.I. (Art. 21, Table 2): Progressione Economica Orizzontale Individuale. 5 quadrennial increments (cadence_months=48, maximum_count=5). Monthly amounts by level from Table 2: I=30, II=30, III=30, IV=40, V=55, VI=60, VII=60, VIII=60, IX=60. All from primary PDF.
    
    APPRENTICESHIP (Art. 7): Art. 7 para 3 delegates profile and salary definitions entirely to EBiNFoP within 30 days of signing. No specific salary model (percentage or under-classification) is defined in the CCNL text. apprenticeship=[] is correct — no under-classification or percentage model is established by the contract. SIMPLIFICATION: if EBiNFoP has since issued a framework, it is not captured here.
    
    INDENNITA (Art. 25 F-G): regional-bargaining indennita minima (700/1400 EUR) and sanita integrativa (7 EUR/month 'dalla data di attivazione dell accordo nazionale specifico'). These are not level-attached fixed allowances; excluded from fixed_allowances. No evidence the national sanita agreement has been activated.
    
    OVERTIME (Art. 39): three rates — diurno +15%, notturno or festivo +30%, notturno+festivo +50%. The combined notturno+festivo band (50%) is not in overtime_bands, although the engine supports it (OvertimeKind.NIGHT_HOLIDAY): such an event needs the caller's multiplier. Art. 41 para 3 (15% supplement for ordinary work at night or on holidays) is not modelled as a supplement band (supplement_bands): such an event needs the caller's amount (review of 2026-10-30)
    

## Raw data

The contract file this page is generated from: [`agreement/formazione-professionale.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/formazione-professionale.json).

## Usage example

```python
--8<-- "docs/examples/agreement/formazione-professionale/example.py"
```
