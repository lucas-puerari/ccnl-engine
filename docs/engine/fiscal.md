# Fiscal computation

The engine computes the full gross-to-net chain: INPS, IRPEF, *trattamento
integrativo*, and optionally regional and municipal surcharges.

See [Domain: IRPEF and surcharges](../domain/components.md#10-irpef-and-surcharges)
for the legal background.

The tax year of a run follows its payment date, with the 12 January
extension of TUIR art. 51 c. 1: see
[Tax year and payment date](index.md#tax-year-and-payment-date).

Some pay items take a flat substitute tax instead of IRPEF when the worker
meets the statutory requirements: see
[Substitute-tax regimes](substitute-tax-regimes.md).

The regional and municipal surcharges are described in
[Surtax](surtax.md); the decisions of the ulteriore detrazione and the
trattamento integrativo in [Tax credits](tax-credits.md).

## IRPEF flow

1. **Taxable income** = gross − INPS employee contributions
2. **IRPEF gross** = taxable income × progressive brackets (Art. 11 TUIR)
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross. Its income
   ratios are truncated to four decimals (art. 13 c. 6 TUIR). Up to €15,000
   it is at least €690, or €1,380 for a fixed-term employment (c. 1
   lett. a); apprenticeship is open-ended (D.Lgs. 81/2015 art. 41 c. 1).
4. **Ulteriore detrazione lavoro** (Art. 1 c. 6 L. 207/2024): additional credit
   of up to €1,000/year for taxable income between €20,000 and €40,000.
   Flat €1,000 from €20,001 to €32,000; linear taper to zero from €32,001 to €40,000.
   The taper ratio is not truncated: c. 6 has no four-decimal rule and the
   one of art. 13 c. 6 TUIR lists the ratios of art. 13 only.
5. **IRPEF net** = IRPEF gross − work income deduction − ulteriore detrazione
   − family deductions + clawback sterilisation (floored at 0). Art. 15
   TUIR deductions are not applied in payroll (capability
   `art15_deductions`, outside the input): the worker claims them in the
   tax return.
6. **Trattamento integrativo** (Art. 1 D.L. 3/2020): up to €1,200/year.
   Two income bands apply:
   - RC ≤ €15,000 (c. 1, first period): granted when IRPEF gross exceeds
     the Art. 13 deduction minus a €75 corrective for the days of work
     (words inserted by L. 207/2024).
   - €15,001–€28,000 (c. 1, second and third periods): granted only when
     the sum of the Art. 12 and Art. 13 c. 1 deductions exceeds IRPEF gross;
     the amount equals the excess, capped at €1,200. The ulteriore
     detrazione is not in the list. The law also counts Art. 15 deductions
     for loans taken out up to 31 December 2021 and the instalments of
     expenses incurred up to that date; payroll does not know them, so the
     credit of the run can only be lower than the one of the tax return.
   - RC > €28,000: zero.

For a part-year employment the work deduction, the ulteriore detrazione and
the trattamento integrativo (with its €75 corrective) are "rapportata al
periodo di lavoro nell'anno": the full-year amount, in cents, times
`days / 365` (730/2026 istruzioni, quadro C: "365 per l'intero anno"). The
day ratio is not
truncated to four decimals, since it is not one of the ratios art. 13 c. 6
TUIR lists: 200 days of the €1,955 deduction give €1,071.23, not €1,071.14.

The minimum of art. 13 c. 1 lett. a) is not proportioned: the deduction due
is the larger of the amount for the days and the minimum (Allegato C to the
730/2026 instructions, par. 19.9.1: the minimum "non deve essere rapportata
ai giorni di lavoro dipendente"). 92 days give €492.77, so €690 is due, or
€1,380 for a fixed term. It applies to every withholding of the year, the
conguaglio of a termination included, and the trattamento integrativo test
up to €15,000 compares the gross tax with that deduction less the €75
corrective for the days: a fixed-term worker whose gross tax does not exceed
€1,380 less the corrective gets no trattamento and owes no IRPEF. The
minimum is €1,380 when any employment the withholding counts in the year is
fixed-term, as the 730 takes it when "in almeno un rigo" of C1 to C3 holds
code 2 (same paragraph).

The days are those of every employment whose income the withholding
projects. A rehire by the same employer in the same tax year, whose first
run opens with the state the earlier employment closed, projects the income
of both, so it counts the days of both: one Certificazione Unica holds
"più rapporti di lavoro ... per il medesimo periodo d'imposta" (punto 11
code 1 for an employment "interrotto e successivamente ripreso"), and
punto 721 counts the days of "tutti i rapporti di lavoro conguagliati",
"i giorni compresi in periodi contemporanei" once (istruzioni CU 2026,
updated 24 February 2026). The tax cash state records each employment as an
`EmploymentSpell` of the tax year (`TaxCashState.employment_spells`): its
first day, its last day (31 December while the end is not stated) and
whether it is fixed-term; a later run of the same employment, keyed by its
first day, replaces it. Metalmeccanico C3 from 1 January to 31 March 2026,
rehired on 1 June, counts 90 + 214 = 304 days from June.

A termination run closes the employment: no run but an adjustment closes
after it in its competence year, and a rehire after it is refused with an
`InvalidInputError` that names the termination run. Open the rehire with
`PeriodState.zero()`: its withholding then counts its own income and days
only. Art. 23 c. 4 DPR 600/1973 (text in force in 2026) lets the worker ask
the year-end conguaglio to count the income "percepiti nel corso di
precedenti rapporti intrattenuti"; the engine does not take that income as
an input.

### Withholding of a run

Every run projects the annual taxable income (YTD, this run, and the
recurring pay of the slots still to come) and withholds on that basis:

- income the run pays once (bonus, overtime, ordinary arrears, excess PdR,
  ratei settled at termination) is not in the projection of later slots,
  so the tax it adds to the year is withheld on that run (art. 23 c. 2
  DPR 600/1973: lett. a) on the sums "corrisposti in ciascun periodo di
  paga", lett. b) on the "compensi della stessa natura" of the mensilità
  aggiuntive). It is the net annual IRPEF with the income less the net annual
  IRPEF without it. A €20,000 bonus paid in November to a Metalmeccanico C3
  withholds about €8,399 on the November payslip instead of spreading it
  over November, December and the tredicesima;
- the rest of the balance still owed is spread evenly over the slots of
  the tax year not yet paid, the run included;
- the payment that leaves no slot unpaid (the conguaglio) settles the whole
  balance on the final income, which can be a refund (art. 23 c. 3). The
  slots are the payments actually made in the tax year, so with December
  paid on 13 January the conguaglio of the year falls on the tredicesima,
  and a payment made after the conguaglio settles the year again (see
  [Payroll state](payroll-state.md#withholding-schedule-of-the-tax-year)).

The projection of a future tredicesima or quattordicesima uses the rateo
the run will pay on the employment period: a worker hired on 1 July is
projected 6/12 of the tredicesima, not a full month. Absences still to come
are not known and settle at the conguaglio.

### Pay that does not cover the tax

A run can owe more IRPEF and surtax than the pay it leaves after the
contributions and the other deductions, for example when unpaid absences
take most of the month. The engine then:

- withholds IRPEF first, up to the pay left, and the surtax from what
  remains, so the net pay is never negative because of the taxes; a
  conguaglio refund is never capped;
- carries what it could not withhold in `state.cash.shortfall` (`irpef`,
  `surtax`) and withholds it in full on the next run, before the share of
  the rest of the balance;
- records a `withholding_shortfall` decision (`withholding_capped` when it
  carries an amount out, `shortfall_withheld` when it withholds a carried
  amount), with the pay available and the amounts due in its inputs;
- on the last withholding slot, reports what is still not withheld as a
  provisional `withholding_shortfall_unrecovered` issue.

The cumulative conguaglio settles the tax on the whole year (art. 23 c. 3
DPR 600/1973, in force for 2026: Normattiva gives it "in vigore dal
21-5-2022 al 31-12-2026"; the same text is art. 33 c. 4 D.Lgs. 33/2025, in
force from 1 January 2027 by art. 243 as amended by D.L. 200/2025 art. 4).
For what is left at year end the same comma says: "L'importo
che al termine del periodo d'imposta non è stato trattenuto per cessazione del
rapporto di lavoro o per incapienza delle retribuzioni deve essere comunicato
all'interessato che deve provvedere al versamento entro il 15 gennaio
dell'anno successivo". The worker can instead ask in writing to have it
withheld on the next pay periods (see
[Written deferral of the year-end shortfall](#written-deferral-of-the-year-end-shortfall)).
The statute does
not state how a shortfall found before the conguaglio is spread: taking it
on the next run is the engine's choice. Art. 23 c. 1, second sentence
(art. 33 c. 1 D.Lgs. 33/2025 from 2027), which makes the worker pay the
withholding that finds no cash, is written for values in kind and is not
used here.

Metalmeccanico C3, 160 absence hours at 12.50 EUR in January 2026: the pay
left after INPS is 143.25 EUR, the IRPEF share is 162.33 EUR; January
withholds 143.25 EUR and nets 0.00, February withholds the 19.08 EUR
carried on top of its share.

Credit recoveries (trattamento integrativo, somma esente, installments of an
earlier year) are capped in the same way and taken before the IRPEF: the
part the pay does not cover is given back by a
`credit_recovery_shortfall_{run_id}` line and carried as
`shortfall.credit_recovery`, apart from the IRPEF. On the last run of the
employment it is reported by the same provisional issue; AdE circ.
29/E/2020 par. 6 and 4/E/2025 par. 1.2 apply art. 23 c. 3 DPR 600/1973 to
a recovery the conguaglio di fine rapporto cannot make "per incapienza
della retribuzione".

A run whose other deductions (INPS, substitute tax) exceed the pay left by
unpaid absences is still rejected (`OutOfScopeError`, reason
`withholding_shortfall`).

### Written deferral of the year-end shortfall

Art. 23 c. 3 DPR 600/1973, second and third sentences (identical in art. 33
c. 4 D.Lgs. 33/2025 from 2027):

> In caso di incapienza delle retribuzioni a subire il prelievo delle
> imposte dovute in sede di conguaglio di fine anno entro il 28 febbraio
> dell'anno successivo, il sostituito può dichiarare per iscritto al
> sostituto di volergli versare l'importo corrispondente alle ritenute
> ancora dovute, ovvero, di autorizzarlo a effettuare il prelievo sulle
> retribuzioni dei periodi di paga successivi al secondo dello stesso
> periodo di imposta. Sugli importi di cui è differito il pagamento si
> applica l'interesse in ragione dello 0,50 per cento mensile, che è
> trattenuto e versato nei termini e con le modalità previste per le somme
> cui si riferisce.

The request is `PriorYearTaxFacts.shortfall_deferral`, a
`ShortfallDeferralRequest(signed_on=...)` signed between 1 January of the
tax year and the end of February of the next one (the deadline of the
conguaglio); another date raises `InvalidInputError`. Without it nothing
changes: the shortfall is communicated to the worker with the provisional
issue above. With it, on the conguaglio of year N:

- the IRPEF the pay cannot cover becomes a `DeferredShortfall` in
  `state.cash.obligations.deferred_shortfall`, with the date of the request and
  the pay period of the conguaglio; `state.cash.shortfall.irpef` is zero and
  a `shortfall_deferral` decision `shortfall_deferred` records the amount.
  `close_tax_year` carries it into N+1;
- only the IRPEF is deferred, the tax the norm names; surtax and credit
  recoveries the pay cannot cover keep the provisional issue;
- when the conguaglio is the last run of the employment no payslip follows:
  the decision is `deferral_not_possible` and the issue stays.

On the payslips of N+1 the engine reads "successivi al secondo" as from the
March pay period (January and February are the two pay periods on which
the conguaglio of N can still be made), and "dello stesso periodo di
imposta" as within N+1. The norm fixes no installments: every run from
March, adjustment runs excepted, withholds from its net pay, after every
other line, the largest principal whose interest still fits, until the
amount is exhausted. The interest is simple: 0.50% for each whole month
from the pay period of the conguaglio to the pay period of the run, on the
principal the run withholds. The norm does not say when the count starts;
this is the engine's reading, and each `deferred_shortfall_withheld`
decision records the principal, the interest, the months and the rate.

Both amounts are posted to `ORDINARY_TAX` on the lines
`deferred_irpef_{N}_{run_id}` and `deferred_irpef_{N}_interest_{run_id}`,
coded **1066** "Ritenute [...] operate dopo il relativo conguaglio di fine
anno", instituted by ris. AdE 6/E/2021 for the withholding of art. 23 c. 3
second sentence, with N as the reference year. The interest takes the code
of the IRPEF it refers to because the norm remits it "con le modalità
previste per le somme cui si riferisce"; no act gives it a code of its own.
Neither amount enters the IRPEF withheld of N+1 (`state.cash.tax.irpef`).

What the conguaglio of N+1 or the last run of the employment still leaves
is dropped with a provisional `deferred_shortfall_unrecovered` issue and
decision: it is communicated to the worker as any other shortfall.

A later run of N that settles the balance again (an adjustment run) counts
the deferred IRPEF as withheld, so it withholds only the tax of its own
pay. Such a run cannot refund IRPEF while the deferral is open: lowering
the deferral by the refund is not modelled and raises `OutOfScopeError`
(reason `shortfall_deferral_refund`). A termination run of N after the
conguaglio drops the deferral with the same provisional issue, since no
payslip of N+1 follows.

A 300.00 EUR deferral of the December 2025 conguaglio, withheld on the
March 2026 payslip: 3 months, interest 300.00 × 0.50% × 3 = 4.50 EUR, net
pay 304.50 EUR lower, F24 code 1066 for 304.50 EUR. When March absences
leave no pay, April withholds it with 4 months: 6.00 EUR.

### Foreign tax credit at the conguaglio

Art. 23 c. 3 DPR 600/1973, last sentences (art. 33 c. 4 D.Lgs. 33/2025 from
2027): "Se alla formazione del reddito di lavoro dipendente concorrono somme
o valori prodotti all'estero le imposte ivi pagate a titolo definitivo sono
ammesse in detrazione fino a concorrenza dell'imposta relativa ai predetti
redditi prodotti all'estero. [...] Se concorrono redditi prodotti in più
Stati esteri la detrazione si applica separatamente per ciascuno Stato." The
withholding agent applies the credit of art. 165 TUIR itself, at the
conguaglio.

The input is `PriorYearTaxFacts.foreign_taxes`: one `ForeignTaxPaid(country,
income, tax)` per State, with the foreign-source employment income as it
entered the Italian taxable income of the year (the conventional pay when
art. 51 c. 8-bis TUIR applies) and the foreign tax paid "a titolo
definitivo", within the treaty rate. When the income entered the taxable
income only in part (the conventional pay), pass the tax already reduced
as art. 165 c. 10 TUIR requires (circ. AdE 9/E/2015 par. 5). Two entries
of one State are rejected.

On the conguaglio only (the last withholding slot or the last run of the
employment; the runs before it withhold on the art. 12 and 13 deductions
alone, art. 23 c. 2), per State:

    quota  = imposta lorda × min(1, income / taxable income)   (to the cent)
    credit = min(foreign tax, quota)

and the credits of all States together at most the imposta netta (art. 165
c. 1 TUIR; circ. AdE 9/E/2015 par. 3.1, LIMITE 1 and LIMITE 2). The quota
is on the imposta lorda as in the Redditi PF 2026 instructions (fascicolo
3, quadro CE, sezione I-A): the credit "spetta fino a concorrenza della
quota d'imposta lorda italiana corrispondente al rapporto tra il reddito
prodotto all'estero ed il reddito complessivo [...] e sempre comunque nel
limite dell'imposta netta italiana", with the ratio brought back to 1. The withholding agent
knows only the income it pays, so the reddito complessivo is the annual
taxable income of the conguaglio. The credit is a `foreign_tax_credit`
component of the tax computation, deducted from the net IRPEF of the year,
and a `foreign_tax_credit` decision (`credit_applied`, or
`limited_to_net_tax` when the imposta netta caps it) with the income, tax,
quota and credit of each State in its inputs.

Metalmeccanico C3 2026, 10,000 EUR earned in France and 500 EUR of French
tax: taxable income 25,779.81 EUR, imposta lorda 23% of it, quota
5,929.36 × 10,000 / 25,779.81 = 2,300.00 EUR, credit 500 EUR; the IRPEF of
the year is 2,751.23 − 500 = 2,251.23 EUR. With the whole income taxed in
France at 20,000 EUR the quota is the whole imposta lorda, the credit the
imposta netta: no IRPEF and no surtax is due, and the conguaglio refunds
what was withheld.

Not modelled, left to the tax return: foreign income taxed in Italy in an
earlier year (art. 165 c. 7 TUIR, which the art. 23 rule also allows at the
conguaglio), the carry-over of the excess foreign tax (art. 165 c. 6) and a
credit above the imposta netta (art. 11 c. 4 TUIR).

## Employers that are not withholding agents

Everything above is done by the employer as *sostituto d'imposta*. A
household employer is not one (art. 23 c. 1 DPR 600/1973; art. 33 c. 1
D.Lgs. 33/2025 from 2027), so for the domestic CCNLs the engine withholds no
IRPEF or surcharge, runs no conguaglio, pays no trattamento integrativo, somma
esente or ulteriore detrazione and applies no substitute tax. Each of these
capabilities records a `not_withholding_agent` decision. See
[Domestic work](domestic-work.md#no-withholding-on-the-payslip).

## Family deductions (Art. 12 TUIR)

The deductions of art. 12 TUIR (text in force read on
[Normattiva](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art12!vig=)
on 3 October 2026) are computed on the **reddito complessivo** of the year:
the employment income the run projects for the year plus the income of
`CurrentYearTaxFacts` (other employers, other income), less the income of the
main dwelling (c. 4-bis). Amounts and limits are data of
`tax/data/family-deductions-<year>.json`, each block with its provenance:

| Dependent | Full-year amount, with R the reddito complessivo |
|---|---|
| Spouse (lett. a) | `800 − 110 × R/15,000` up to 15,000; 690 up to 40,000; `690 × (80,000 − R)/40,000` up to 80,000 |
| Spouse increase (lett. b) | +10 above 29,000 up to 29,200; +20 up to 34,700; +30 up to 35,000; +20 up to 35,100; +10 up to 35,200 |
| Child (lett. c) | `950 × (C − R)/C`, C = 95,000 + 15,000 for each entitled child after the first; from 21 to 29, from 30 only with a disability (art. 3 L. 104/1992) |
| Ascendant (lett. d) | `750 × (80,000 − R)/80,000`, only if living with the worker |

- **Truncation (c. 4).** Each ratio is taken to four decimals, the rest
  discarded, before it multiplies the amount; a ratio of zero or less, or
  of one (no income) for children and ascendants, gives no deduction.
- **Months (c. 3).** A deduction is due from the month its conditions start
  to the month they end, both included: `Dependent.dependent_from` and
  `dependent_until` date the dependency (marriage, separation,
  cohabitation), and a child counts from the month it turns 21 to the
  month it turns 30. The full-year amount is multiplied by the months over
  twelve and by `allocation_pct`, then rounded to the cent once.
- **Own income (c. 2).** 2,840.51, or 4,000 for a child who turns at most
  24 in the year (the whole year, as the Agenzia delle Entrate 730
  instructions read "non superiore a ventiquattro anni").
- **Sole parent (lett. c, last period).** With `FamilyComposition.sole_parent`
  the eldest entitled child takes the spouse deduction when it is higher.
- **Conditions are stated, never assumed.** The engine cannot verify the
  conditions of a dependant; the caller states them on `Dependent`, and a
  condition left `None` is unknown, not met:

  | Field | Read for | Rule |
  |---|---|---|
  | `own_income` | every dependant | c. 2: "Le detrazioni di cui al comma 1 spettano a condizione che le persone alle quali si riferiscono possiedano un reddito complessivo [...] non superiore a 2.840,51 euro" (4,000 for a child up to 24) |
  | `residency_eligibility` | every dependant | c. 2-bis: "Le detrazioni di cui al comma 1 non spettano ai contribuenti che non sono cittadini italiani o di uno Stato membro dell'Unione europea o di uno Stato aderente all'Accordo sullo Spazio economico europeo in relazione ai familiari residenti all'estero"; `True` when the worker is such a citizen or the dependant does not reside abroad |
  | `cohabiting` | ascendant | lett. d: "per ciascun ascendente che conviva con il contribuente" |
  | `allocation_pct` | child, ascendant | lett. c: "La detrazione è ripartita nella misura del 50 per cento tra i genitori non legalmente ed effettivamente separati ovvero, previo accordo tra gli stessi, spetta al genitore che possiede un reddito complessivo di ammontare più elevato", with the rules for separated parents and "In caso di coniuge fiscalmente a carico dell'altro, la detrazione compete a quest'ultimo per l'intero importo"; lett. d: "da ripartire pro quota tra coloro che hanno diritto alla detrazione". The share depends on facts the engine does not know (marriage, separation, agreement, the other parent's income), so no share is assumed. The spouse deduction of lett. a is not shared: only `None` or `100` is accepted for a spouse |

  A dependant that may qualify in some month (no stated condition excludes
  it, a child within its age band) with an unknown condition takes no
  deduction: the decision is `required_fact_missing` with
  `inputs["missing_facts"]`, and an `incomplete` issue
  `dependent_condition_unknown` per field (`fact` the field name) gives a
  `missing_fact` blocker. An unknown condition of a dependant that cannot
  qualify (a child under 21 all year, an ascendant stated not cohabiting)
  blocks nothing. The dependency interval has no default:
  `dependent_from=None` and `dependent_until=None` state an open end and
  must be passed.

The decision `family_deductions` records the income, the months of each
dependent and the amount per relationship. Its reason:

| Reason | Status | When |
|---|---|---|
| `deductions_applied` / `no_deduction_due` | `final` | The reddito complessivo is known; or no income is needed: no dependent gives right to a deduction in any month, or this employment alone takes every deduction past its phase-out (zero whatever the other income) |
| `required_fact_missing` | `provisional` | A dependant may qualify and leaves a condition unknown (see above), or a dependent gives right to a deduction and `current_year` is missing or of another tax year. The decision has no amount; `inputs["simulated_amount"]` holds the deductions on this employment alone, which the IRPEF of the run uses (as for the IVS massimale and the seniority); issue `family_income_unknown` (`incomplete`, `fact="current_year"`), blocker `missing_fact`: the result is `incomplete` and not payable |
| `estimated_income_at_conguaglio` | `provisional` | The conguaglio rests on a `current_year` of quality `estimated`: state `declared` or `certified` figures to settle the year |

Missing income is never taken as zero: a worker whose only income is this
employment states it with `CurrentYearTaxFacts.employment_only(tax_year,
estimated_on)`. A `TaxYearPlan.current_year` replaces the facts of its
competence years, so a December paid in January reads the facts of the year
it is paid in.

## IVS ceiling

The *massimale IVS* caps the IVS contribution base (and the 1% addizionale)
of workers without contributions before 1 January 1996 and of those who
opted for the contributory system (L. 335/1995 art. 2 c. 18 and art. 1
c. 23). Its value is data of the INPS rules of the year with their provenance
(EUR 122,295 for 2026, INPS Circ. 6/2026). The engine derives the
eligibility from `Employment.contribution_history`
(`ContributionHistory`): the date of the first contribution credited to a
mandatory pension scheme and the contributory option. The history is the one
in force for the run: pre-1996 periods credited on request lift the
massimale only from the month after the request (L. 208/2015 art. 1 c. 280)
and the option from when it is exercised, so for earlier runs supply the
history as it stood then. The engine models no effective date of a change.

Every run whose INPS rules carry a massimale records an
`ivs_ceiling_eligibility` decision:

| Reason | When | Massimale |
|---|---|---|
| `first_enrolment_after_1995` | first contribution on or after 1 January 1996 | applied |
| `contributory_option` | the worker opted for the contributory system | applied |
| `enrolled_before_1996` | earlier contributions, no option | not applied |
| `ceiling_not_reached` | no history, and the YTD INPS base plus the run stays within the massimale: both branches give the same contributions | irrelevant |
| `required_fact_missing` | no history, and the run crosses the massimale | undetermined |

With `required_fact_missing` the decision is `provisional` and lists the
employee and employer contributions of both branches in its inputs; the
`inps_employee` and `inps_employer` decisions are `incomplete` with no
amount; an `ivs_ceiling_eligibility_unknown` issue names the fact
`contribution_history`, so the result has a `missing_fact` blocker and is not
payable. The breakdown, the ledger and the net carry the uncapped branch as
a simulation, never as a payable amount. The massimale runs across all the
employers of the year (INPS circ. 237/2016 par. 3.1): import the base of
the others as `InpsBaseYtd.other_employers` with
`engine.import_opening_balances`. The base and the massimale are those of
the competence year of the run: a December paid in January counts toward
the massimale of its own year (see
[INPS base by competence](payroll-state.md#inps-base-by-competence)).
Conditions that lower the reliability of a result are reported in
`result.issues`, never as free text.

## Additional 1% IVS

D.L. 384/1992 art. 3-ter charges the worker 1% on the pay above the first
pensionable band of the year (EUR 56,224 for 2026), within the massimale
when it applies. INPS applies it by the *mensilizzazione* (INPS circ.
6/2026 par. 5, circ. 7/2010 par. 3, msg. 5327/2015 par. 2.1): each month
the 1% is charged on the INPS base of the month above the band "rapportato
a dodici mesi" (EUR 4,685 for 2026), whatever the base of the year. The
runs of one competence month share its threshold; the state keeps the base
of the latest month only, so an adjustment run of an earlier month and a
later run of the current one each count from zero, a difference the
settlement corrects. The rule, with both
thresholds as INPS publishes them, is the `employee_additional` block of
the INPS rules of the year.

The runs of competence December, of the month the employment ends and the
termination run settle the year (msg. 5327/2015 par. 2.3; circ. 156/2025
par. 5): 1% of the base of the year within the massimale above the annual
band, less the 1% already withheld on the year. A December run that follows
another one of the same month settles only what the first left. The
settlement can be a credit to the worker: the component
`addizionale_1pct_conguaglio` then carries a negative amount, and the
employee contributions of the run may be negative by as much. The monthly
component is `addizionale_1pct`.

The 1% withheld is kept per competence year on `InpsBaseYtd.additional_ivs`.
The bases of other employers count toward the band; import them with what
those employers withheld, `InpsBaseYtd.other_employers_additional_ivs`, from
their CU. Left `None` with a base of other employers, a settling run cannot
deduct it: it reports the issue `other_employers_additional_ivs_unknown`
(`incomplete`, `fact="other_employers_additional_ivs"`), so the result has a
`missing_fact` blocker and is not payable.

## Minimum INPS base

The base INPS contributions are computed on has two floors (INPS circ.
6/2026 par. 1):

- the pay of the collective agreement (D.L. 338/1989 art. 1 c. 1), read in
  the comparatively most representative CCNL of the category (L. 549/1995
  art. 2 c. 25). The engine computes the pay of the CCNL of the request
  from its tables, so this floor is the pay chain itself. Whether that
  CCNL is the most representative of the category is not a fact the engine
  holds: a run on a CCNL that is not has to be checked outside the engine;
- the minimum daily pay of D.L. 463/1983 art. 7 c. 1, 9.5% of the minimum
  FPLD pension: EUR 58.13 a day for 2026. A fully paid month of a
  full-time, monthly-paid worker counts 26 days (six days of the normal
  week over 52 weeks and 12 months; the 26 days INPS counts in a full
  month in the Uniemens technical document), EUR 1,511.38. A part-time
  worker has the hourly minimum of D.Lgs. 81/2015 art. 11 c. 1, EUR 8.72
  for a 40-hour week (circ. 6/2026 par. 4, "58,13 euro x 6/40"), times the
  contracted weekly hours over the same 26 days.

The run that posts the monthly pay of a fully employed month without an
unpaid absence or a sick leave raises its INPS base to that minimum
(`minimum_base_reason` `raised_to_minimum`); the pay itself, the gross and
the TFR quota are unchanged, while the contributions, the 0.50% IVS taken
from the TFR, the IRPEF taxable and the year-to-date base follow the raised
base. Art. 7 c. 5 excludes apprentices and the operai agricoli
(`apprentice_excluded`, `category_excluded`); domestic work has its own
hourly contributions.

The bundle cannot fix the minimum of a partly employed month, of a month
with an absence or a sick leave (whose reduced pay circ. 6/2026 par. 1 and
the Uniemens element `RispettoMinimale` exempt), of a run that adds pay to
a month another run posted (an extra month, an adjustment, a termination
after the regular run) or settles the extra-month ratei at termination, of a part-time week whose hourly minimum is not
published (only 40 and, for the Gestione pubblica, 36 hours are), of the
Gestione pubblica (no sourced day count of a month), or of an agricultural
level whose category is open. When the base of such a run is below the
highest minimum its month can have (26 days, or 27 where the day count is
not sourced, fewer days of a six-day week in a partly employed span,
scaled to the part-time hours), its `inps_employee` and
`inps_employer` decisions are `incomplete` with reason
`minimum_base_undetermined` and no amount, an issue
`inps_minimum_base_undetermined` explains it (with `fact="category"` for
the open category), and the result is not payable. A base above that bound
needs no day count and is final. The rule is the `minimum_base` block of
the INPS rules of the year.

**API reference:** [`CalculationDecision`](../api/engine.md#results-and-calculation-status),
[`REGION_CODES`](../api/models.md#fiscal),
[`FamilyComposition`](../api/engine.md), [`Art15Deductions`](../api/engine.md)
