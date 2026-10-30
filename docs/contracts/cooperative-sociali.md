# CCNL Cooperative Sociali (Confcooperative/Legacoop/AGCI)

| | |
|---|---|
| **CNEL code** | `T151` |
| **Sector** | servizi socio-assistenziali |
| **Family** | `socio-sanitario` |
| **Tax sector** | `terziario` |
| **Last renewal** | 2025-11-20 |
| **Workers (est.)** | ~380k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 👁 Reviewed |

[← Contracts index](index.md)

??? note "Signatories"
    - Confcooperative-Federsolidarietà
    - Legacoop Sociali
    - AGCI-Solidarietà
    - FP-CGIL
    - CISL-FPS
    - UIL-FPL

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, bilateral_funds, inps_employer |

4 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 62 verified / 1 derived / 0 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🟢 Verified | The confidence the ruleset declares as a whole |
| **Readiness** | 👁 Reviewed | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2025-11-20 |
| **Last review** | 2026-10-17 |
| **Latest salary tranche** | 2025-10-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-09-18 | maintainer (human) | Whole file. The values checked were not recorded. | confirmed | The review recorded no list of the documents it read. |
| 2026-10-13 | claude-opus-5-5 (ai) | Every payable rule read again in the Legacoopsociali full text 2025 of the CCNL Cooperative sociali 2023-2025, with the Legacoop circular of 1 February 2024 and the CNEL T151 deposits of 26 January and 5 March 2024, for the reviewed tier. | corrected | 83 records verified; the two aggregator sources replaced by the Legacoopsociali full text.<br>32 salary periods differed by 1-3 cents from Art. 76 (A1, B, C3, D1, D3, E1, E2, E2Q, F2, F2Q, and F1, F1Q from October 2025): corrected.<br>Ferie 26 working days on a six-day week (Art. 60), not 20.<br>Sickness: 100% of the normale retribuzione from day 1 to day 180 (Art. 71), no 50% carenza.<br>Apprenticeship: the OSS of C2 on the 18-month track (Art. 28 N.3); apprentices accrue no seniority (Art. 28 I.5): the apprentice_seniority limitation closed.<br>Added Previdenza Cooperativa (Art. 86: employer 1.5%, worker minimum 1% of the TFR base).<br>C3 seniority 20.66 stays derived: Art. 80 prints 20,63, the cost tables 20.66.<br>Absence by_26 stays derived: Art. 41 deducts hours at 1/165.<br>Open: the INPS rate of the cost tables (28.03%) vs terziario, and the type-B exemptions of L. 381/1991.<br>The CCNL expired on 31 December 2025; no renewal found through October 2026. |
| 2026-10-17 | claude-opus-5-5 (ai) | The INPS class of the employers of the CCNL against the INPS classification manual. | flagged | The activities of the social cooperatives of type A are classified by INPS in the terziario: CSC 70704 for 87.30.00, 88.10.00 and 88.91.00, 70706 for 87.20.00 (manual of May 2021, ATECO 2007, PDF pp. 265-266). The file applies the terziario rates: the class is confirmed.<br>The 28.03% of the Ministry cost tables (D.D. 30/2024) is still unexplained: no composition of the 2026 terziario rates gives it, and the tables state none. inps_rate_not_reconciled stays open; a cooperative may also fall in the DPR 602/1970 regime for its members, which the file does not model. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `F2Q` | Level F2Q — general director Quadro (with function allowance) | € 2,504.09 | 2025-10-01 |
| `F2` | Level F2 — general director / highest responsibility function | € 2,504.09 | 2025-10-01 |
| `F1Q` | Level F1Q — area director Quadro (with function allowance) | € 2,192.54 | 2025-10-01 |
| `F1` | Level F1 — area director / senior managerial function | € 2,192.54 | 2025-10-01 |
| `E2Q` | Level E2Q — senior manager Quadro (with function allowance) | € 1,985.42 | 2025-10-01 |
| `E2` | Level E2 — senior manager / service director | € 1,985.42 | 2025-10-01 |
| `E1` | Level E1 — junior manager / coordinator | € 1,839.15 | 2025-10-01 |
| `D3` | Level D3 — senior technician | € 1,839.15 | 2025-10-01 |
| `D2` | Level D2 — qualified technician | € 1,727.83 | 2025-10-01 |
| `D1` | Level D1 — junior technician | € 1,637.57 | 2025-10-01 |
| `C3` | Level C3: capo squadra, capo cuoco, coordinating assistente domiciliare / operatore socio-assistenziale (ex 5° livello) | € 1,637.57 | 2025-10-01 |
| `C2` | Level C2: Operatore Socio-Sanitario operating in socio-sanitary services and structures | € 1,591.06 | 2025-10-01 |
| `C1` | Level C1: operaio specializzato, cuoco, conducente, assistente domiciliare, operatore socio-assistenziale (ex 4° livello) | € 1,545.21 | 2025-10-01 |
| `B` | Level B — qualified auxiliary worker | € 1,436.79 | 2025-10-01 |
| `A2` | Level A2 — basic auxiliary worker | € 1,372.53 | 2025-10-01 |
| `A1` | Level A1 — generic entry-level worker | € 1,359.85 | 2025-10-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `A1` | € 11.62 |
| `A2` | € 13.43 |
| `B` | € 16.27 |
| `C1` | € 18.59 |
| `C2` | € 19.63 |
| `C3` | € 20.66 |
| `D1` | € 20.66 |
| `D2` | € 23.24 |
| `D3` | € 26.86 |
| `E1` | € 26.86 |
| `E2` | € 31.50 |
| `E2Q` | € 31.50 |
| `F1` | € 39.51 |
| `F1Q` | € 39.51 |
| `F2` | € 46.48 |
| `F2Q` | € 46.48 |

## Apprenticeship

**professionalizzante_18m** (type: `percentage`)  
Destination levels: `A2`, `C2`  
percentage: 1.00

**professionalizzante_24m** (type: `percentage`)  
Destination levels: `B`, `C1`, `C3`  
percentage: 1.00

**professionalizzante_36m** (type: `percentage`)  
Destination levels: `D1`, `D2`, `D3`, `E1`, `E2`  
percentage: 1.00

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "cooperative-sociali/inps_rate_not_reconciled · inps_employer · impact yes · open"
    INPS: the tax_sector terziario applies the terziario employer rates (29.31% to 30.11%), while the Ministry D.D. 30/2024 cost tables agreed by the signatories (PDF p. 186) apply 'Inps (28,03%)' to every level. Social cooperatives are classified by INPS by their activity; no primary INPS circular for their contribution set was read, so the difference is not reconciled. CLASS CHECKED 2026-10-17: the INPS Manuale di classificazione dei datori di lavoro (May 2021) gives CSC 70704 (terziario) to 87.30.00 strutture di assistenza residenziale per anziani e disabili, 88.10.00 assistenza sociale non residenziale and 88.91.00 asili nido, and 70706 (terziario) to 87.20.00: the class the file applies. The 28.03% of the cost tables matches no composition of the 2026 terziario rates, and the tables state none.

    **Applies when:** `inps_employer` applies.

    **Remediation:** Read the INPS classification of social cooperatives and model their employer rate set.

!!! warning "cooperative-sociali/type_b_disadvantaged_exemption · inps_employer · impact yes · open"
    TYPE-B COOPERATIVES: the contributions on the pay of the disadvantaged workers of type-B social cooperatives 'sono ridotte a zero' (L. 381/1991 art. 4 c. 3, PDF p. 248; c. 3-bis for detainees by decree). The request has no field for such a worker: the full rates apply.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Add a disadvantaged-worker input and zero the contributions of L. 381/1991 art. 4.

!!! warning "cooperative-sociali/coop_sociali_unmodelled_elements · base_salary · impact yes · open"
    NOT MODELLED AMOUNTS: the ETDR of the educatori (EUR 41, then 82 a month in 2025, Art. 47 and verbale 17 September 2025; the educatori socio-pedagogici move to D2 from 1 January 2026); the night allowance of EUR 12.39 / 6.20 per night and the 10% of night-only custody staff (Art. 54); 15% on Sunday and holiday ordinary hours (Art. 55); the 10% shift allowance (Art. 56); reperibilità in struttura EUR 77.47 a month plus EUR 20 a night (Art. 57); pronta disponibilità EUR 1.55 an hour (Art. 58); the indennità professionali (Art. 78) and the EUR 50 affiancamento allowance; the indennità di cassa EUR 30.99 (Art. 81); the extra 1/26 of a holiday on the rest day (Art. 59) and the 4 days of ex festività (Art. 60); the 26 hours of night workers' permessi (Art. 54); the PTR (Art. 10, outside every institute); the salari di primo ingresso of type B (Art. 2 B.4); the territorial gradualità agreements (Art. 77); the maternity integration (Art. 63); the 100% integration of work injury to day 180 (Art. 72); the EUR 10 quota d'iscrizione of Previdenza Cooperativa (Art. 86). Sickness: no integration during the prova (Art. 71, Art. 28 M) and the comporto of 12 months in three years are not inputs. Apprenticeship: the 24-month track of the educatore professionale with title (Art. 28 N.2) is not expressible by level.

    **Applies when:** a fact the request cannot express: never recorded on a run.

    **Remediation:** Model the ETDR, the night, shift and availability allowances, the professional allowances and the prova exclusion of sickness.

!!! warning "cooperative-sociali/asi_health_contribution · bilateral_funds · impact yes · open"
    HEALTH CONTRIBUTION: the ASI contribution of EUR 5, then 10 a month (Art. 87), is owed for every worker. Not modelled: the totals of every run are short of it.

    **Applies when:** `bilateral_funds` applies.

    **Remediation:** Model the ASI contribution per worker, then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

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
| CCNL Cooperative sociali 2023-2025, testo completo (edizione Legacoopsociali 2025) | associazione | 2025-11-20 | [↗](https://www.legacoopsociali.it/wp-content/uploads/low-LEGACOOP-Contratto-Collettivo-2025-COMPLETO.pdf) |
| Legacoop, circolare 1 febbraio 2024 (rev. 1.1): rinnovo del CCNL cooperative sociali, tabelle dei minimi | associazione | 2024-02-01 | [↗](https://www.legacoop.coop/wp-content/uploads/2024/03/20240307-circolare-rinnovo-CCNL-sociali_rev.1.1.pdf) |
| CNEL T151: verbale di accordo per il rinnovo del CCNL Cooperative sociali, 26 gennaio 2024 | cnel | 2024-01-26 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/179967) |
| CNEL T151: verbale di scioglimento della riserva, 5 marzo 2024, con le tabelle del costo | cnel | 2024-03-05 | [↗](https://archiviocontrattiapi.cnel.it/cne/cne-sa-0002/ricerca-api/ricerca/pubblica/accordi/scarica/accordi/183378) |

??? note "Coverage notes"
    CONSOLIDATED MINIMUMS: base_salary is the minimo contrattuale conglobato mensile of Art. 76 (PDF p. 106) of the Legacoopsociali full text 2025, the same figures as the Legacoop circular of 1 February 2024 and the Ministry D.D. 30/2024 cost tables. Hourly divisor 165 for 38 hours a week (Art. 75). Level B is position B1 of Art. 76.
    
    QUADRO LEVELS: levels E2Q, F1Q, F2Q are modelled as separate levels with fixed_allowances (function allowance EUR 77.47, EUR 154.94, EUR 232.41/month respectively). The base_salary is identical to the corresponding non-Q level; the allowance is fixed and unchanged across tranches. Seniority increments for Q levels carry the same amount as the corresponding base level.
    
    ADDITIONAL MONTHS: 13 until 31 December 2024 (thirteenth month only). From 1 January 2025: 13.5 (thirteenth month + fourteenth month equal to 50% of one monthly salary, paid in June, introduced by the 26 January 2024 renewal).
    
    TRANCHES: February 2024, October 2024 and October 2025 ('con la mensilità di febbraio 2024 / ottobre 2024 / ottobre 2025', verbale 26 January 2024, reserve lifted 5 March 2024). The CCNL 2023-2025 expired on 31 December 2025 (Art. 7); no renewal, una tantum or IVC was found through October 2026, so the October 2025 minimi stay in force.
    
    LEVELS WITH THE SAME BASE: C3 and D1 have identical minimums at each tranche (orders 6/7). D3 and E1 are identical (orders 9/10). Q levels (E2Q/F1Q/F2Q) have the same base as the non-Q level but the next order: the engine allows equal salaries between adjacent levels.
    
    SENIORITY INCREMENTS: one scatto per biennio, at most 5 (Art. 80, pp. 110-111). C3 is printed 20,63 in Art. 80 but 20.66 in the D.D. 30/2024 and CNEL cost tables and in the D1 row: 20.66 kept as derived. Apprentices accrue none (Art. 28 I.5, apprentice_amount 0); the recognised seniority of a qualified ex-apprentice starts at the end of the apprenticeship (caller's SeniorityFact).
    
    APPRENTICESHIP (professionalizzante, Art. 28 L and N, PDF pp. 59-60): category A (A2) and the OSS of C2 18 months (85% / 90% at month 10); categories B and C (B, C1, C3) 24 months (85% / 90% at month 13); D and E 36 months (85% / 90% at month 19), on the minimo of the target position. A1, F and the health profiles are excluded (Art. 28 B.3).
    

## Raw data

The contract file this page is generated from: [`agreement/cooperative-sociali.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/cooperative-sociali.json).

## Usage example

```python
--8<-- "docs/examples/agreement/cooperative-sociali/example.py"
```
