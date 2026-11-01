# CCNL Carta e Cartone — Aziende Industriali (Assocarta)

| | |
|---|---|
| **CNEL code** | `G022` |
| **Sector** | carta-cartone |
| **Family** | `carta-grafica` |
| **Tax sector** | `industria` |
| **Last renewal** | 2026-02-10 |
| **Workers (est.)** | ~35k |
| **Ruleset version** | `2026.2` |
| **Readiness** | 🧪 Exploratory |

[← Contracts index](index.md)

??? note "Signatories"
    - Assocarta
    - Assografici
    - SLC-CGIL
    - Fistel-CISL
    - Uilcom-UIL
    - UGL-carta e stampa

## Coverage

Derived from the capability registry. The scenario features and the ones outside the input are the same for every contract: see the [capability matrix](capability-matrix.md).

| | Core payroll path of a contract |
|---|---|
| ✅ | Every core capability is computed from bundled rules and request facts |
| ⚠️ | The contract's data leave a core capability partial: see **Limits** |

| | |
|---|---|
| **Core payroll path** | ⚠️ |
| **Limits of this contract** | base_salary, seniority |

2 documented simplification(s) and 0 missing feature(s): see [Known simplifications](#known-simplifications).

## Assurance

| Axis | Value | What it says |
|---|---|---|
| **Extraction method** | 🤖 AI-assisted | How the values were read from the sources |
| **Extraction review** | 🔴 Unverified | Whether a person checked the extracted file against its sources |
| **Rule provenance** | 14 verified / 61 derived / 1 assumed / 0 missing | Payable rules of the file by the evidence behind each value ([statuses](../trust/provenance.md)) |
| **Ruleset confidence** | 🔴 Unverified | The confidence the ruleset declares as a whole |
| **Readiness** | 🧪 Exploratory | Whether runs of this contract can be paid in `operational` mode ([tiers](../trust/readiness.md)) |

## Freshness

| | |
|---|---|
| **Last renewal** | 2026-02-10 |
| **Last review** | 2026-10-31 |
| **Latest salary tranche** | 2028-09-01 |

## Review history

| Date | Reviewer | Scope | Outcome | Findings |
|---|---|---|---|---|
| 2026-10-18 | claude-opus-5-5 (ai) | The minimi di stipendio (TEM + Elemento di Modernizzazione Contrattuale) of the 13 levels: the 1 July 2024 tranche against the table of the ipotesi of 28 July 2021, and the four tranches of the ipotesi of 10 February 2026 (1/4/2026, 1/1/2027, 1/1/2028, 1/9/2028) derived from its C1 increments and parameter scale; both texts as deposited at CNEL. | corrected | The four tranches of the 2026 renewal (52 periods) are corrected upward by the level's EMC: the file built them on the TEM-only minimo (C1 1835.11 + 125 = 1960.11), dropping the Elemento di Modernizzazione Contrattuale of EUR 20 at C1 (EUR 32.68 at Q, 13.07 at E) that the file's own 2024-07-01 value includes. The signed ipotesi of 10 February 2026 (CNEL 246200, 8-page scan read on the page images) neither abolishes nor conglobates the EMC (Art. 100 bis) and does not amend Art. 49, which defines the stipendio contrattuale as TEM + EMC; it only adds increments 'parametrati su livello C1' of 125 (aprile 2026), 45 (gennaio 2027), 45 (gennaio 2028) and 60 (settembre 2028), p. 8. The signatories' unitary communiqué of 10 February 2026 gives an overall increase of 14,8% (EUR 291 package, 275 on the minimi); ADAPT's analysis (not a signatory) gives +275 = 14,82% on the previous minimo, which is 275 / 1855.11 (with the EMC), not 275 / 1835.11 (14,99%). The values are derived as previous minimo + increment x parameter / 153, with the parameters of the Art. 48 table on p. 3 (Q 250 ... C1 153 ... E 100, the same scale as the 2021 table). On 1/4/2026 the difference from the file equals the level's EMC (e.g. C1 1960.11 -> 1980.11, Q 2882.91 -> 2915.59, B2S +23.82 against an EMC of 23.80 because of a 2-cent rounding in the file's TEM base); on the later dates it also includes the reparametrisation error below. C1 differs by exactly 20.00 on all four dates.<br>The future tranches of the file (1/1/2027, 1/1/2028, 1/9/2028) were also reparametrised on the ratio of the 2026 minimi (level / C1) instead of the contractual parameter scale (level / 153): e.g. Q +66.19 instead of 45 x 250/153 = 73.53 on 1/1/2027, E +33.44 instead of 29.41; the error grows with the distance from C1 and reaches -0.37 net at E on 1/9/2028 after the EMC offset. The derivation uses the parameter scale the ipotesi refers to.<br>Ipotesi 28 luglio 2021 (CNEL 138131, p. 46, table image): the 'Minimi dal 1.7.2024' column (TEM + EMC cumulated) matches 12 of the 13 file values; C1S is 1.924,37 against 1924.38 in the file and is corrected.<br>The coverage note of the file (EMC 'absorbed' into the 2026 paga base, net +105 at C1) is not supported by the signed text and will contradict the corrected values: the maintainer must rewrite it (base_salary = TEM + EMC throughout).<br>The ruleset now names the CNEL deposit of the text signed by Assocarta, Assografici, SLC-CGIL, Fistel-CISL, Uilcom-UIL and UGL carta e stampa: source_type contracting_party.<br>Corrected to the printed table: C1S 2024-07-01: 1924.38 -> 1924.37; Q 2026-04-01: 2882.91 -> 2915.59; Q 2027-01-01: 2949.10 -> 2989.12; Q 2028-01-01: 3015.29 -> 3062.65; Q 2028-09-01: 3103.54 -> 3160.69; AS 2026-04-01: 2873.55 -> 2906.09; AS 2027-01-01: 2939.52 -> 2979.33; AS 2028-01-01: 3005.49 -> 3052.57; AS 2028-09-01: 3093.45 -> 3150.22; A 2026-04-01: 2521.80 -> 2549.50; A 2027-01-01: 2579.70 -> 2611.85; A 2028-01-01: 2637.60 -> 2674.20; A 2028-09-01: 2714.79 -> 2757.34; B1 2026-04-01: 2292.49 -> 2317.07; B1 2027-01-01: 2345.12 -> 2372.36; B1 2028-01-01: 2397.75 -> 2427.65; B1 2028-09-01: 2467.92 -> 2501.38; B2S 2026-04-01: 2234.61 -> 2258.43; B2S 2027-01-01: 2285.91 -> 2311.96; B2S 2028-01-01: 2337.21 -> 2365.49; B2S 2028-09-01: 2405.61 -> 2436.86; B2 2026-04-01: 2159.89 -> 2182.63; B2 2027-01-01: 2209.48 -> 2233.81; B2 2028-01-01: 2259.07 -> 2284.99; B2 2028-09-01: 2325.19 -> 2353.23; C1S 2026-04-01: 2034.87 -> 2055.91; C1S 2027-01-01: 2081.59 -> 2103.26; C1S 2028-01-01: 2128.31 -> 2150.61; C1S 2028-09-01: 2190.60 -> 2213.75; C1 2026-04-01: 1960.11 -> 1980.11; C1 2027-01-01: 2005.11 -> 2025.11; C1 2028-01-01: 2050.11 -> 2070.11; C1 2028-09-01: 2110.11 -> 2130.11; C2 2026-04-01: 1826.94 -> 1845.10; C2 2027-01-01: 1868.88 -> 1885.98; C2 2028-01-01: 1910.82 -> 1926.86; C2 2028-09-01: 1966.74 -> 1981.37; C3 2026-04-01: 1732.11 -> 1748.97; C3 2027-01-01: 1771.88 -> 1786.91; C3 2028-01-01: 1811.65 -> 1824.85; C3 2028-09-01: 1864.67 -> 1875.44; D1 2026-04-01: 1656.25 -> 1672.07; D1 2027-01-01: 1694.27 -> 1707.66; D1 2028-01-01: 1732.29 -> 1743.25; D1 2028-09-01: 1782.99 -> 1790.70; D2 2026-04-01: 1561.08 -> 1575.58; D2 2027-01-01: 1596.92 -> 1608.23; D2 2028-01-01: 1632.76 -> 1640.88; D2 2028-09-01: 1680.55 -> 1684.41; E 2026-04-01: 1456.61 -> 1469.67; E 2027-01-01: 1490.05 -> 1499.08; E 2028-01-01: 1523.49 -> 1528.49; E 2028-09-01: 1568.08 -> 1567.71. |
| 2026-10-31 | claude-opus-5-5 (ai) | The comporto and the sick pay of the CCNL counted over several illnesses (work_rules.sickness_rules), read on the signed text. | corrected | Art. 70 of the 2021 renewal (CNEL 138131, pp. 40-42) and Art. 89 of the impiegati: comporto 12 months, 180 days of 100% of the net pay and 6 months of 50%, all counted over the 36 months before each day of absence. The file kept 180 days of one illness: corrected to a cumulation over three years. |

## Salary table

Latest effective values per level (monthly gross, EUR).

| Level | Description | Base salary (monthly) | Effective from |
|---|---|---:|:---:|
| `Q` | Q — executive manager, maximum technical or managerial responsibility | € 3,160.69 | 2028-09-01 |
| `AS` | AS — special level, senior technical manager | € 3,150.22 | 2028-09-01 |
| `A` | A — 6th category worker, production process supervisor | € 2,757.34 | 2028-09-01 |
| `B1` | B1 — 5th category worker, highly qualified technician | € 2,501.38 | 2028-09-01 |
| `B2S` | B2S — 4th category worker (super), plant-responsible technician | € 2,436.86 | 2028-09-01 |
| `B2` | B2 — 4th category worker, technician with advanced specialisation | € 2,353.23 | 2028-09-01 |
| `C1S` | C1S — 3rd category worker (super), highly specialised operator | € 2,213.75 | 2028-09-01 |
| `C1` | C1 — 3rd category worker (higher grade), specialised operator | € 2,130.11 | 2028-09-01 |
| `C2` | C2 — 3rd category worker, assigned to specialised processing | € 1,981.37 | 2028-09-01 |
| `C3` | C3 — 3rd category worker, assigned to semi-specialised processing | € 1,875.44 | 2028-09-01 |
| `D1` | D1 — 2nd category worker (higher grade), qualified operator | € 1,790.70 | 2028-09-01 |
| `D2` | D2 — 2nd category worker, auxiliary machinery operator | € 1,684.41 | 2028-09-01 |
| `E` | E — 1st category worker, simple and executive tasks | € 1,567.71 | 2028-09-01 |

## Seniority increments

**Cadence:** every 24 months  
**Maximum:** 5 increments

| Level | Increment (monthly) |
|---|---:|
| `Q` | € 15.49 |
| `AS` | € 15.49 |
| `A` | € 15.49 |
| `B1` | € 13.94 |
| `B2S` | € 13.69 |
| `B2` | € 13.69 |
| `C1S` | € 13.43 |
| `C1` | € 13.43 |
| `C2` | € 13.17 |
| `C3` | € 12.91 |
| `D1` | € 12.39 |
| `D2` | € 11.88 |
| `E` | € 11.62 |

## Apprenticeship

**triennale** (type: `percentage`)  
Destination levels: `C3`, `C2`, `C1`, `C1S`, `B2`, `B2S`, `B1`, `A`  
percentage: 0.95

**biennale_categoria_D** (type: `percentage`)  
Destination levels: `D2`, `D1`  
percentage: 0.95

## Known simplifications

Each simplification below is a model limitation of the registry. An open limitation with a monetary impact (`yes` or `unknown`) makes every result it applies to not payable, with an `open_limitation` blocker; the result lists every applicable limitation in `assurance.limitations`.

!!! warning "carta-cartone-assocarta/emc_absorption_unconfirmed · base_salary · impact unknown · open"
    EMC CHECK: aggregators and a payroll firm print 2026 minimi without the EMC (C1 1960.11 = 1835.11 + 125), but none cites a clause removing it; the signed 2026 ipotesi keeps Art. 100 bis and Art. 49. The Assocarta 'nota illustrativa e tabella nuovi minimi' of 24/02/2026 is members-only and was not read: if it shows the EMC absorbed, the 2026-2028 values are EUR 13-33 too high.

    **Applies when:** `base_salary` applies; from 2026-04-01.

    **Remediation:** Read the Assocarta nota illustrativa of 24/02/2026 (or a signed table) and settle whether the EMC is in the 2026-2028 minimi; correct base_salary if absorbed.

!!! warning "carta-cartone-assocarta/apprentice_seniority · seniority · impact unknown · open"
    APPRENTICE SENIORITY: the CCNL text read for this ruleset does not state whether apprentices accrue the level seniority increments or an amount of their own, and no apprentice amount is modelled. The engine pays no increment during the apprenticeship (provisional); the run is affected when the apprentice has matured increments the level pays.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Source the CCNL clause on apprentice seniority and model it as seniority_increments.apprentice_amount (zero when apprentices accrue none), then remove this note.

!!! note "apprentice_seniority_simplified · seniority · impact unknown · resolved"
    Apprentices accrue only the CCNL apprentice-specific seniority increment, paid in full: the apprenticeship percentage no longer reduces it a second time. A CCNL that declares no apprentice amount pays none and carries its own open limitation <ccnl_id>/apprentice_seniority, recorded when the level pays matured increments.

    **Applies when:** `seniority` applies; the run takes the engine code path; contract type in apprentice.

    **Remediation:** Resolved: the remaining CCNLs are tracked by their own apprentice_seniority limitation.

!!! note "sickness_inps_daily_base · sickness · impact unknown · resolved"
    The INPS share of a sick day is computed on the INPS daily base of the episode, on the days INPS pays (the weekdays of an operaio, every day but the national holidays on a Sunday of an impiegato, point 7.3 of INPS circ. 134368/1981): the retribuzione media globale giornaliera of the month before the illness (INPS circ. 134368/1981 point 11; circ. 55/2024 Allegato 1), whole or partial month, impiegato or operaio, or for the lavoratori dello spettacolo the average pay of the last 40 daily contributions, capped for a fixed-term worker (INPS circ. 132/2021 par. 2.4). The base is a fact of the payroll history the episode states (SicknessEpisode.inps_base).

    **Applies when:** `sickness` applies; the run takes the engine code path.

    **Remediation:** Resolved: the INPS share is computed on the base of every regime of the bundle; an episode that states no base the engine can read has the missing_fact issue sickness_inps_base_unknown (fact inps_base), which blocks the run. Tests: tests/integration/ccnl_engine/sickness/base/test_rules.py, tests/unit/ccnl_engine/sickness/base/test_rules.py.

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

!!! warning "maternity_daily_base · maternity_leave · impact unknown · open"
    The INPS maternity indemnity of an operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 23 c. 5 D.Lgs. 151/2001 divides the pay of an operaia by the days worked or paid (or by the hours, when fewer than the contract), and the divisor of her daily rateo of the 13th is not settled by a primary source. The base of another worker over a whole month is computed from MaternityLeaveEvent.maternity_base_pay.

    **Applies when:** `maternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of an operaia (an INPS circular on art. 23 c. 5) and compute her base and that of a month not worked in full, then resolve this limitation.

!!! warning "paternity_daily_base · paternity_leave · impact unknown · open"
    The INPS indemnity of the compulsory paternity leave of an operaio, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 29 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from PaternityLeaveEvent.paternity_base_pay.

    **Applies when:** `paternity_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_daily_base · parental_leave · impact unknown · open"
    The INPS indemnity of the parental leave of an operaio or operaia, or of a leave whose month before was not worked in full, is computed on the pay of the run over 30 with the rateo of the extra months, not on the pay of the month before the leave: art. 34 c. 1 D.Lgs. 151/2001 applies art. 23, whose c. 5 divides the pay of a manual worker by the days worked or paid (or by the hours) with a daily rateo no primary source settles. The base of another worker over a whole month is computed from ParentalLeaveEvent.parental_base_pay.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily rateo of a manual worker under art. 23 c. 5 and compute his base and that of a month not worked in full, then resolve this limitation.

!!! warning "parental_income_condition · parental_leave · impact unknown · open"
    The days of parental leave beyond the indemnified months (three of each parent and three of the couple, nine of a sole parent) are paid nothing: art. 34 c. 3 D.Lgs. 151/2001 pays them 30% when the parent's income is below 2.5 times the trattamento minimo di pensione, an income test and a yearly amount the engine does not model.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the yearly trattamento minimo and the income the test reads, take the income as a fact of the leave and pay the further days at 30% when the condition holds, then resolve this limitation.

!!! warning "parental_month_split · parental_leave · impact unknown · open"
    When a counter of the parental leave (a rate band or the indemnified months) ends inside a calendar month of the leave that is not of thirty days, the engine pays the days of that month in order, one day of counter each and the last day what is left of the thirty: INPS counts the calendar month as one month (FAQ congedo parentale 2024, n. 10) but no source says which of its days fall in which band.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how INPS splits a calendar month between two rates of the parental leave and apply it, then resolve this limitation.

!!! warning "parental_extra_month_share · parental_leave · impact unknown · open"
    The days of parental leave accrue the 13th and the other extra months in full at the employer's charge (art. 34 c. 5 D.Lgs. 151/2001: the leave does not reduce them), while the INPS indemnity is computed on a base that already holds their daily rateo (art. 23 c. 2, INPS circ. 122/2022): no source read settles whether the employer's extra month is reduced by the share INPS pays, so the rateo of a month on leave may be overstated.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source how the extra months of a parental leave are split between INPS and the employer and net the INPS share from the employer's rateo, then resolve this limitation.

!!! warning "parental_hourly_ccnl_rule · parental_leave · impact unknown · open"
    A parental leave by the hour takes half the average daily hours a day and counts two such days as one day of leave, the general criterion of art. 32 c. 1-ter D.Lgs. 151/2001 (INPS circ. 152/2015 par. 2.2); a collective agreement, also of the company, that sets other hours to a day of leave or other rules of cumulation prevails, and the bundle holds none.

    **Applies when:** `parental_leave` applies; the run takes the engine code path.

    **Remediation:** Source the collective rules on the leave by the hour of the CCNL (hours of a day of leave, cumulation) and apply them, then resolve this limitation.

!!! warning "disability_permit_tfr · disability_permits · impact unknown · open"
    The days of permit under L. 104/1992 art. 33 c. 3 keep the TFR base, as payroll practice holds; art. 2120 c. 3 c.c. keeps in the TFR base only the absences of art. 2110 c.c. and the wage integration, and no primary source read says the permits are among them, so the TFR quota of a month with permits may be overstated.

    **Applies when:** `disability_permits` applies; the run takes the engine code path.

    **Remediation:** Source the TFR treatment of the permit days (an INPS or Ministry ruling, or case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "notice_indemnity_partial · termination_notice · impact unknown · open"
    A notice partly worked pays the share of its calendar days left of the indemnity the CCNL band gives in monthly pays; the CCNL clause read (Federmeccanica Sez. Quarta Tit. VIII Art. 1) states the indemnity of the whole notice only, and practice also measures the rest by 30ths or 26ths of the monthly pay.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source how the CCNL or case law measures the indemnity of a notice partly worked and apply it, then resolve this limitation.

!!! warning "notice_indemnity_extra_months · termination_notice · impact yes · open"
    The indemnity is the monthly pays of the CCNL band on the monthly pay of art. 2121 c.c.; the 13th and 14th the notice would have accrued are not added, although art. 2121 counts 'ogni altro compenso di carattere continuativo', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source whether the indemnity carries the rateo of the extra months (CCNL clause or case law) and add it, then resolve this limitation.

!!! note "notice_indemnity_tfr · termination_notice · impact yes · resolved"
    The notice indemnity enters the TFR base only when the CCNL puts it there: the Cassazione holds that it is out of it, being referable to a period not worked after the end of the employment, and art. 2120 c. 2 c.c. leaves a different rule to the collective agreement.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Resolved: the indemnity is out of the TFR base unless the CCNL notice sets tfr_base true.

!!! warning "notice_indemnity_day_measure · termination_notice · impact unknown · open"
    A CCNL that sets the notice in calendar days measures the indemnity on the pay of those days: the engine takes a calendar day as a 30th of the monthly pay; Commercio art. 209 refers the monthly pay to all the days of the calendar month, but its art. 210 sets the daily quota at 1/26 'in tutti i casi', so the indemnity may be understated.

    **Applies when:** `termination_notice` applies; the run takes the engine code path.

    **Remediation:** Source the daily measure of the notice indemnity of the CCNL (an interpretation of the parties or case law) and apply it, then resolve this limitation.

!!! warning "extraordinary_leave_daily_base · extraordinary_leave · impact unknown · open"
    The daily indemnity of the extraordinary leave is the last monthly pay of fixed and continuous items times the monthly payments of a year over 365: art. 42 c. 5-ter D.Lgs. 151/2001 and INPS messaggio 30/2024 set the pay and its rateo of the extra months, and the INPS table of the yearly maximum divides it by 365 (2026: 43,486.00 / 365 = 119.14), but no source read states the divisor of the worker's own pay.

    **Applies when:** `extraordinary_leave` applies; the run takes the engine code path.

    **Remediation:** Source the daily divisor INPS applies to the last pay (circ. INPS 64/2001 or 32/2012) and apply it, then resolve this limitation.

!!! warning "naspi_dismissal_exceptions · naspi_dismissal · impact unknown · open"
    The NASpI contribution of the end of an employment is read from the cause, the just cause and the contract type alone. The request states none of the cases that change it: a resignation in the protected period of maternity and a mutual agreement before the labour office or on a transfer over 50 km owe it (INPS circ. 44/2013 par. 1); a collective dismissal without union agreement owes it three times (L. 92/2012 art. 2 c. 35); the changes of contractor with a social clause and the closures of a construction site of c. 34, and the reductions agreed under artt. 4 and 24 L. 223/1991, leave it out; the service counts the fixed-term periods before the open-ended contract and leaves out the leave of art. 42 c. 5 D.Lgs. 151/2001 only through EmploymentPeriod.started_on.

    **Applies when:** `naspi_dismissal` applies; the run takes the engine code path.

    **Remediation:** Add the facts of these cases to the end of the employment (EmploymentPeriod) and apply them, then resolve this limitation.

!!! warning "personal_withholding_same_kind · personal_withholdings · impact unknown · open"
    Two garnishments of the same kind, or two salary assignments, share the measure of their kind (a fifth, or the tenth or seventh of the agente della riscossione) in the order of notification: art. 545 c. 4 c.p.c. sets 'un quinto per i tributi ... ed in eguale misura per ogni altro credito' and art. 5 DPR 180/1950 a cessione 'fino al quinto', but no text read says how two orders of the same kind split the measure, so the later order may be under- or overstated.

    **Applies when:** `personal_withholdings` applies; the run takes the engine code path.

    **Remediation:** Source how the employer splits the measure between two orders of the same kind (art. 499 c.p.c. on the intervention of creditors, case law of the Cassazione) and apply it, then resolve this limitation.

!!! warning "mid_month_level_change · base_salary · impact unknown · open"
    A promotion on a day other than the first of a month splits the monthly pay of the run between the level before and the new level by the payable days of the CCNL daily quota on each side of the promotion, component by component; the hourly quotas of the month (overtime, permits, absences) read the same split chain whatever the day of the event. The CCNL texts read (Commercio and Terziario art. 118, DMO art. 102) give the new level from the promotion but not how its month is split.

    **Applies when:** `base_salary` applies; the run takes the engine code path.

    **Remediation:** Source how a month is split by a promotion inside it (a CCNL clause or an INPS or Ministry ruling) and price the events of the month at the terms of their day, then resolve this limitation.

## Sources

| Document | Kind | Date | URL |
|---|---|---|---|
| https://www.lexplain.it/tabelle-retributive-ccnl-carta-industria-anno-2024-e-precedenti/ | tabella_retributiva | 2024-07-01 | [↗](https://www.lexplain.it/tabelle-retributive-ccnl-carta-industria-anno-2024-e-precedenti/) |
| https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx | tabella_retributiva | 2026-04-01 | [↗](https://www.kitech.it/Retribuzione-stipendio-ccnl.aspx) |
| https://www.pisacaneboxes.com/wp-content/uploads/2022/02/ccnl-carta-industria2022.pdf | altro | 2021-07-28 | [↗](https://www.pisacaneboxes.com/wp-content/uploads/2022/02/ccnl-carta-industria2022.pdf) |
| https://www.zetaservice.com/wp-content/uploads/2026/02/RINNOVO-CCNL-CARTA-AZIENDE-INDUSTRIALI-G022.pdf | altro | 2026-02-10 | [↗](https://www.zetaservice.com/wp-content/uploads/2026/02/RINNOVO-CCNL-CARTA-AZIENDE-INDUSTRIALI-G022.pdf) |

??? note "Coverage notes"
    SALARY MODEL: base_salary is the stipendio of Art. 49, TEM + EMC (Elemento di Modernizzazione Contrattuale, EUR 20.00 at C1, parametrised). 2024-07-01: column 'Minimi dal 1.7.2024' of the ipotesi of 28/07/2021 (CNEL G022, deposit 138131, p. 46), which already includes the EMC. 2026-04-01 to 2028-09-01: previous minimo + the C1 increments of the ipotesi of 10/02/2026 (CNEL deposit 246200, p. 8: 125, 45, 45, 60) reparametrised by level parameter / 153 (Art. 48 table, p. 3). The 2026 ipotesi neither abolishes nor conglobates the EMC (Art. 100 bis) and keeps Art. 49 in force, so the EMC stays in base_salary; fixed_allowances=[] for all levels.
    
    FUTURE TRANCHES: +45 EUR at C1 from 01.01.2027, +45 from 01.01.2028, +60 from 01.09.2028 confirmed from rinnovo 10.02.2026 (zetaservice PDF). Per-level amounts are parametrically derived: each level increment = C1_increment × (level_2026-04-01 / C1_2026-04-01), rounded to cent. Math-verified all 13 levels × 3 tranches: all within ±0.02 EUR of parametric formula — consistent with the conglobated coefficient scale of the 2026 rinnovo.
    
    HOURLY DIVISOR: 173 (40h/week, Art. Orario di Lavoro CCNL 28/07/2021; confirmed ilccnl.it).
    
    ADDITIONAL MONTHS: 13 (tredicesima only). Source: CCNL 28/07/2021 Art. Tredicesima mensilità. Quattordicesima not provided.
    
    SENIORITY: biennale (24 months), max 5 scatti. Per-level amounts from CCNL 28/07/2021 Art. Aumenti periodici di anzianità (pisacaneboxes.com PDF, verified). Amounts unchanged in rinnovo 10/02/2026.
    
    APPRENTICESHIP professionalizzante, percentage type (CCNL 28/07/2021 Art. Apprendistato professionalizzante, pisacaneboxes.com PDF): track 'triennale' (36 months, 6 semesters 70/75/80/85/90/95%) for destination levels C3, C2, C1, C1S, B2, B2S, B1, A; track 'biennale_categoria_D' (24 months, 6 quadrimestri with the same percentages) for D2 and D1. E, AS and Q are not apprenticeship destinations. The final 95% period is open-ended: after the contractual duration the worker is qualified and paid at 100% as a permanent employee.
    
    INPS: reuses 2026-industria.json (Confindustria/CIGO). Assocarta is a Confindustria federation; CIGO applicable per D.Lgs. 148/2015.
    

## Raw data

The contract file this page is generated from: [`agreement/carta-cartone-assocarta.json`](https://github.com/lucas-puerari/ccnl-engine/blob/main/src/ccnl_engine/knowledge/agreement/carta-cartone-assocarta.json).

## Usage example

```python
--8<-- "docs/examples/agreement/carta-cartone-assocarta/example.py"
```
