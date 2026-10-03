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

## IRPEF flow

1. **Taxable income** = gross − INPS employee contributions
2. **IRPEF gross** = taxable income × progressive brackets (Art. 11 TUIR)
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross. Its income
   ratios are truncated to four decimals (art. 13 c. 6 TUIR).
4. **Ulteriore detrazione lavoro** (Art. 1 c. 6 L. 207/2024): additional credit
   of up to €1,000/year for taxable income between €20,000 and €40,000.
   Flat €1,000 from €20,001 to €32,000; linear taper to zero from €32,001 to €40,000.
   The taper ratio is not truncated: c. 6 has no four-decimal rule and the
   one of art. 13 c. 6 TUIR lists the ratios of art. 13 only.
5. **IRPEF net** = IRPEF gross − work income deduction − ulteriore detrazione
   − family deductions − Art. 15 deductions + clawback sterilisation (floored at 0)
6. **Trattamento integrativo** (Art. 1 D.L. 3/2020): up to €1,200/year.
   Two income bands apply:
   - RC ≤ €15,000: granted when IRPEF gross exceeds the Art. 13 deduction
     minus a €75 corrective (Art. 1 co. 3 L. 207/2024).
   - €15,001–€28,000: granted only when total deductions exceed IRPEF gross;
     amount equals the excess, capped at €1,200.
   - RC > €28,000: zero.

For a part-year employment the work deduction, the ulteriore detrazione and
the trattamento integrativo (with its €75 corrective) are "rapportata al
periodo di lavoro nell'anno": the full-year amount, in cents, times
`days / 365` (730/2026 istruzioni, quadro C: "365 per l'intero anno"). The
day ratio is not
truncated to four decimals, since it is not one of the ratios art. 13 c. 6
TUIR lists: 92 days of the €1,955 deduction give €492.77, not €492.66.

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
- the rest of the balance still owed is spread evenly over the remaining
  slots, the run included;
- the last slot settles the whole balance on the final income, which can
  be a refund (art. 23 c. 3).

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

## Regional and municipal surcharges

The engine computes *addizionale regionale* and *addizionale comunale* only
for the jurisdictions the request names:

- `regione`: the ISO 3166-2:IT subdivision code of the region, `IT-` and
  two digits, for example `IT-45` for Emilia-Romagna or `IT-25` for
  Lombardia (source: [ISO Online Browsing Platform](https://www.iso.org/obp/ui/#iso:code:3166:IT)).
  The regional surtax is set separately by the autonomous provinces, so use
  `IT-BZ` (Bolzano) or `IT-TN` (Trento); `IT-32` (Trentino-Alto Adige) is
  rejected.  The codes are listed in [`REGION_CODES`](../api/models.md#fiscal).
- `comune_belfiore`: the *codice catastale* (Belfiore code) of the
  municipality, one upper-case letter and three digits, for example `F257`
  for Modena.

A malformed code (`ER`, `Lombardia`, `IT45`, `f257`) is rejected with
`InvalidInputError`.  A well-formed code without a row in the tax year table
is not an input error: see the decisions below.

```python
--8<-- "docs/examples/07_addizionali.py"
```

### When the surtax is withheld

The surtax of tax year N is **determined by the conguaglio of N** and
**withheld on the payslips of N+1**:

| Component | Determined by | Withheld | Codice tributo | Source |
|---|---|---|---|---|
| Regional surtax of N | conguaglio of N | up to 11 installments, January to November of N+1 | 3802 | D.Lgs. 446/1997 art. 50 c. 4 |
| Municipal saldo of N | conguaglio of N: municipal surtax of N less the acconto withheld in N | up to 11 installments, January to November of N+1 | 3848 | D.Lgs. 360/1998 art. 1 c. 5 |
| Municipal acconto of N+1 | conguaglio of N: 30% of the municipal surtax on the income of N, rate and threshold of N | up to 9 installments, March to November of N+1 | 3847 | D.Lgs. 360/1998 art. 1 cc. 4-5 |

Art. 50 c. 4 reads "trattenuto in un numero massimo di undici rate, a
partire dal periodo di paga successivo a quello in cui le stesse sono
effettuate e non oltre quello relativamente al quale le ritenute sono
versate nel mese di dicembre"; art. 1 c. 5 applies the same words to the
municipal saldo and sets the acconto "in un numero massimo di nove rate
mensili, effettuate a partire dal mese di marzo". The withholding remitted
in December is the one of the November pay period, so the engine, whose
conguaglio is the last payslip of the year, withholds:

- one installment on each **regular** payslip of the window, the maximum
  number of equal installments rounded to the cent, the last one taking
  the residual; the November payslip takes whatever is left;
- nothing on the extra-month payslips (tredicesima, quattordicesima), the
  December payslip or an adjustment run;
- on the **last run of the employment**, every residual at once ("in caso
  di cessazione del rapporto l'importo è trattenuto in unica soluzione",
  art. 50 c. 4; "l'addizionale residua dovuta è prelevata in unica
  soluzione", art. 1 c. 5). That run is also the conguaglio of its year:
  the regional surtax and the municipal saldo of the year are withheld on
  it, and no acconto of the next year is determined (CU 2026 instructions,
  point 29 "non dovrà essere compilato" at the cessazione).

When the acconto withheld in the year exceeds the municipal surtax due, the
conguaglio gives the excess back on a `SURTAX_REFUNDS` line (CU 2026
instructions, point 26: the acconto "effettivamente trattenuto, al netto,
quindi, di quanto eventualmente restituito"). The CU text covers the
cessazione; the engine applies the same refund at the ordinary conguaglio,
where the saldo "determinato all'atto delle operazioni di conguaglio"
(art. 1 c. 5) is negative.

A termination run after the last withholding slot is a second conguaglio
of the year: it determines the surtax of the year again on the final
income, drops what the first conguaglio deferred, and withholds the
difference from what an earlier conguaglio of the year already withheld.

A debt keeps the region or municipality of the year that determined it:
the installments of N+1 do not read the `regione` and `comune_belfiore` of
the N+1 runs.

#### First year computed by the engine

The engine withholds in year N only the surtax an earlier conguaglio
determined. For an employment it computes from January 2026 the 2025
saldi and the 2026 acconto come from the conguaglio of 2025, run by the
previous provider or by the employer before the engine: import them with
`OpeningBalances.surtax_obligations` and `municipal_advance_withheld`.
Without them **no surtax is withheld in 2026** and the whole 2026 surtax
is deferred to 2027. The law still requires the 2025 amounts to be
withheld in 2026 by the employer that certified them.

For a worker hired during N with no earlier employment at the same
employer, no acconto of N is withheld (the acconto is determined by the
conguaglio of the year before), the conguaglio of N determines the whole
municipal surtax as saldo, and the acconto of N+1 is computed on the income
this employer paid in N.

### Surtax decisions

Each jurisdiction named in the request records a `CalculationDecision` in
`result.decisions`, with capability `addizionale_regionale` or
`addizionale_comunale`. On the conguaglio its `amount` is the annual surtax
of the tax year on the annual taxable income; on any other run the surtax
is not determined. Its `inputs` hold the code, the table row name, the tax
year and the taxable income, and its `rule` and `rule_version` the bundled
ruleset.

| `reason_code` | Status | Amount | Meaning |
|---|---|---|---|
| `determined_at_conguaglio` | `final` | 0 | A run before the conguaglio: the table exists, nothing of the year is determined yet. |
| `table_applied` | `final` | computed | The bundled row of the tax year was applied: brackets, and for a regional row its whole-income rate and income-only deductions. |
| `dependent_provisions_not_applied` | `provisional` | computed | The regional row has provisions for dependents or disability that are not applied, and the request declares a child or a disabled dependent; issue `regional_surtax_dependent_provisions_not_applied` quotes them. |
| `prior_year_rates_applied` | `provisional` | computed | The municipal row holds the rates of an earlier year (`inputs["rates_year"]`): no delibera of the tax year was published when the table was built; issue `municipal_surtax_prior_year_rates`. |
| `specific_exemptions_not_applied` | `provisional` | computed | The municipal row exempts only a category of income (for example lavoro dipendente up to a limit); issue `municipal_surtax_specific_exemptions_not_applied` quotes the exemptions. |
| `below_exemption_threshold` | `final` | 0 | The regional or municipal exemption threshold covers the taxable income. |
| `no_irpef_due` | `final` | 0 | Net IRPEF (gross less the deductions) of the year is zero, so no surtax is due. |
| `table_unknown` | `incomplete` | `None` | The code is well formed but the tax year table has no row for it. |

A `table_unknown` decision comes with a `CalculationIssue` coded
`regional_surtax_unknown` or `municipal_surtax_unknown`, on every run, not
only on the conguaglio. Nothing is determined for that surtax and the
period result, hence the year result, is `incomplete`: **it must not be
paid as is**. Without `regione` and `comune_belfiore` no surtax decision is
taken and nothing is determined; the installments carried in are withheld
all the same.

The conguaglio and each installment record one more decision per
component, with the same capability and `inputs["component"]`
(`regional_balance`, `municipal_balance` or `municipal_advance`),
`inputs["reference_year"]` and `inputs["jurisdiction"]`:

| `reason_code` | Amount | Meaning |
|---|---|---|
| `deferred_to_installments` | deferred | The conguaglio opened the obligation; `inputs["installments_total"]`, and `inputs["advance_withheld"]` for the saldo. |
| `withheld_at_termination` | withheld | The last run of the employment withheld the surtax of its year at once. |
| `surtax_refunded` | negative | The surtax withheld in the year (usually the acconto) exceeded what is due; the difference is refunded. |
| `installment_posted`, `last_installment_posted` | withheld | An installment of a carried obligation; `inputs["installment_number"]`, `installments_total`, `residual_before`. |
| `settled_at_termination` | withheld | The residual of a carried obligation, on the last run of the employment. |

The surtax is due only when the IRPEF net of its deductions is due
(D.Lgs. 446/1997 art. 50 c. 2 for the regional, D.Lgs. 360/1998 art. 1 c. 4
for the municipal): a worker whose deductions absorb the whole gross IRPEF
owes neither.

#### Foreign tax credit

Both articles take the IRPEF net of the deductions **and of the credit for
taxes paid abroad**: art. 50 c. 2 D.Lgs. 446/1997 names the "crediti di cui
agli articoli 14 e 15" of the TUIR in its former numbering (art. 15 is now
art. 165), art. 1 c. 4 D.Lgs. 360/1998 the "credito di cui all'articolo 165".
See [Foreign tax credit at the conguaglio](#foreign-tax-credit-at-the-conguaglio):
when the credit brings the net IRPEF to zero, both surtax decisions are
`no_irpef_due`.

#### Regional rates of 2026

`regionale-2026.json` is taken from the MEF Dipartimento delle Finanze
pages of the addizionale regionale, one per region or autonomous province
(`addregirpef.php?reg=NN&anno=2026`, retrieved on 27 September 2026). Each
row records the URL of its page, the MEF publication date and a
`derived` provenance; no row has been checked by a named reviewer yet.
Where MEF lists two delibere for 2026 (Molise, Puglia) the later one, which
raises the rates under art. 1 c. 174 L. 311/2004, is bundled.

The provisions that depend on income only are computed:

| Row | Provision |
|---|---|
| Valle d'Aosta | Exempt up to 15,000 euro, then 1.23% on the whole income. |
| Trento | A 30,000 euro deduction for income up to 30,000 euro, stored as an exemption threshold. |
| Friuli-Venezia Giulia | 0.70% on the whole income up to 15,000 euro, otherwise 1.23% on the whole income. |
| Lazio | 1.73% on the whole income up to 28,000 euro; a 60 euro detrazione above 28,000 and up to 30,000 euro. |
| Umbria | 1.23% on the whole income up to 28,000 euro; a 150 euro detrazione above 28,000 and up to 50,000 euro. |
| Bolzano | A 430.50 euro detrazione up to 90,000 euro, and up to 125 euro above 50,000 euro (125 x (income - 50,000) / 25,000). |

Regional deductions never create a credit: the surtax is floored at zero.
Income limits are checked on the IRPEF taxable income of the employment,
also where the regional law refers to *reddito complessivo* (Valle
d'Aosta) or adds income taxed separately (Bolzano).

Provisions for dependents or disability are **not** computed: per-child
detrazioni (Bolzano, Campania, Piemonte, Puglia, Sardegna, Trento) and
reduced rates for a disabled taxpayer or family member (Marche, Veneto).
The row states them in `dependent_provisions`. When the request declares a
child or a disabled dependent in `family_composition`, the regional
decision is `provisional` with the issue
`regional_surtax_dependent_provisions_not_applied`; the surtax withheld
may be too high. The engine has no input for the disability of the worker,
so the Veneto rate for a disabled taxpayer without dependents is not
flagged.

#### Municipal rates of the tax year

The acconto of N+1 uses the rate and threshold "nella misura vigente
nell'anno precedente" (art. 1 c. 4), which at the conguaglio of N are those
of N; the saldo of N uses them too. `comunale-2026.json` is generated by
`scripts/data/build_comunale_surtax.py` from the MEF *elenco generale*
CSV of 2026 and of 2025, downloaded on 27 September 2026 (their sha256 is in
the file notes). A municipality that published a 2026 delibera has its 2026
rates (`final`). One that has not yet (`0*` in the list, 4,558 of 7,897 at
download, Milano, Roma and Torino included) keeps its 2025 rates, which
stay in force without a new delibera (art. 1 c. 169 L. 296/2006): the row
has `rates_year: 2025` and an `assumed` record, and its decision is
`provisional` with the issue `municipal_surtax_prior_year_rates` until the
table is rebuilt from a later list. A delibera can still be published until
20 December 2026. Municipalities without a surtax have a zero rate row.

Exemptions for a category of income only (`FLAG_NUOVA` 5 and 6 of the
list, for example lavoro dipendente up to 12,000 euro) are kept as text in
`specific_exemptions` and not computed; a row with them is `provisional`
with the issue `municipal_surtax_specific_exemptions_not_applied`. To
refresh the table, download both lists and run the script as its docstring
shows; a row it cannot read stops the build.

### Tax credit decisions

The ulteriore detrazione (Art. 1 c. 6 L. 207/2024) and the trattamento
integrativo (Art. 1 D.L. 3/2020) each record one `CalculationDecision` per
run in `result.decisions`, with capability `ulteriore_detrazione_lavoro` or
`trattamento_integrativo`, whenever the tax year rules put the credit in
force.  The decision is `final`, its `amount` is the **annual** entitlement
(0 when the credit is not due) and its `reason_code` names the rule branch
that produced the amount:

| Capability | `reason_code` | Amount |
|---|---|---|
| `ulteriore_detrazione_lavoro` | `income_not_above_lower_threshold` | 0 |
| `ulteriore_detrazione_lavoro` | `full_amount` | full, proportioned to the days worked |
| `ulteriore_detrazione_lavoro` | `tapered_amount` | tapered, proportioned to the days worked |
| `ulteriore_detrazione_lavoro` | `income_above_upper_threshold` | 0 |
| `trattamento_integrativo` | `full_amount` | full (income up to 15,000 EUR, IRPEF above the work deduction) |
| `trattamento_integrativo` | `irpef_not_above_work_deduction` | 0 (income up to 15,000 EUR) |
| `trattamento_integrativo` | `deductions_above_irpef` | deductions minus IRPEF, capped (15,000 to 28,000 EUR) |
| `trattamento_integrativo` | `deductions_not_above_irpef` | 0 (15,000 to 28,000 EUR) |
| `trattamento_integrativo` | `income_above_upper_threshold` | 0 |

The trattamento decision also records the signed `period_amount` paid or
recovered on the run and `recovery_in_progress`, `true` while an installment
recovery (D.L. 3/2020 art. 1 c. 3) is running.  A run that recovers part of it also
records a decision with capability `trattamento_integrativo_recovery`
(`overpayment_recovered`, `overpayment_recovery_opened`,
`overpayment_recovered_at_termination`, `installment_posted`,
`last_installment_posted`, `installment_posted_adjustment_run` or
`settled_at_termination`), amount the negative amount of the run.

#### Ulteriore detrazione recognized and recovered

L. 207/2024 art. 1 c. 7: the employer recognizes the deduction of c. 6 "in
via automatica ... all'atto dell'erogazione delle retribuzioni e
verificano in sede di conguaglio la spettanza"; an amount not due is
recovered, and "Nel caso in cui il predetto importo sia superiore a 60
euro, il recupero dello stesso è effettuato in dieci rate di pari ammontare
a partire dalla prima retribuzione alla quale si applicano gli effetti del
conguaglio".

The deduction lowers the IRPEF withheld, so what a run recognizes is how
much lower its withholding is than the withholding without the deduction,
on the same projection. It accumulates in
`state.cash.ulteriore_detrazione` (a `CreditAccount`). A run that takes part
of it back before the conguaglio (a bonus above the band) records it as
recovered by the withholding: that part is not found at the conguaglio and
is not spread again. On the last withholding slot:

- the account settles on the annual due;
- an excess up to 60 EUR stays in the conguaglio IRPEF;
- above 60 EUR the conguaglio IRPEF keeps the first of ten equal
  installments and the other nine are deferred: they open a recovery
  obligation of kind `ulteriore_detrazione_lavoro`, posted by the
  adjustment runs of the year and from the first run of the next tax year
  as a credit recovery line
  (`ulteriore_detrazione_lavoro_recovery_{N}_{run_id}`, account
  `CREDIT_RECOVERIES`), like the other c. 7 recoveries. The line is
  uncoded: it recovers IRPEF of year N after its conguaglio, and no
  codice tributo for it is verified.

The run records a decision with capability
`ulteriore_detrazione_lavoro_recovery` (`overpayment_recovered`,
`overpayment_recovery_opened` or `overpayment_recovered_at_termination`,
amount the negative excess, `inputs["deferred"]`
the part left to the installments), and the invariant
`irpef_annual_reconciliation` counts the deferred installments with the
IRPEF withheld.

Metalmeccanico C3 at 33 of 40 hours in 2026 is projected at about 20,950 EUR
of taxable income, so the runs recognize 12/13 of the 1,000 EUR deduction
(923.07 EUR) before the conguaglio. 144 absence hours on the tredicesima
bring the final income to 19,639.09 EUR: the deduction is not due, 92.31 EUR
are recovered on the conguaglio and nine installments (830.76 EUR) are
deferred to 2027.

When the employment ends in the tax year no payslip follows the
conguaglio at the cessation: the whole excess stays in its IRPEF
(`overpayment_recovered_at_termination`), and what the pay cannot cover is
a shortfall left to the worker (see
[Pay that does not cover the tax](#pay-that-does-not-cover-the-tax)). AdE
circ. 4/E/2025 par. 1.2: "In caso di cessazione del rapporto di lavoro, si
precisa che il sostituto d'imposta, in sede di conguaglio di fine rapporto,
è tenuto a recuperare i benefici fiscali non spettanti in un'unica
soluzione, indipendentemente dall'importo". The same rule settles the
somma esente and the trattamento integrativo (circ. 29/E/2020 par. 6) and
any plan still running, of this or an earlier year
(see [Payroll state](payroll-state.md#recovery-at-the-end-of-the-employment)).

An adjustment run of year N after the conguaglio posts the next
installment: it settles the cumulative balance again and withholds it less
what is still deferred after the installment (decision reason
`installment_posted_adjustment_run`). If the balance falls below that, the
plan closes and the balance settles the year
(`recovery_absorbed_by_conguaglio`).

The other decisions a run can record are `worker_category` (the category
used and its origin: `declared` on the employment or `fixed_by_level`),
`seniority` (on every run: `not_applicable_by_contract`, `zero_confirmed`,
`increments_applied`, or `required_fact_missing` when the level needs the
recognised seniority and none is given, see
[Pay components](pay-components.md)), `apprenticeship_scaling` (`percentage_applied`
with the percentage and the scaled and unscaled components, only for a
percentage apprenticeship track), `family_deductions` (`deductions_applied` or
`no_deduction_due`, only with a family composition), `bonus_pdr`
(`substitute_tax_applied` or `annual_limit_reached`, only for a bonus routed
to the PdR substitute tax), `fringe_benefit` (`within_threshold`,
`above_threshold` or `above_threshold_retroactive`, one per `FringeEvent`,
see [Fringe benefits](work-rules.md#fringe-benefits)) and the substitute tax
regimes described in [Substitute tax regimes](substitute-tax-regimes.md).

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
employers of the year: the opening INPS base YTD must include them.
Conditions that lower the reliability of a result are reported in
`result.issues`, never as free text.

**API reference:** [`CalculationDecision`](../api/engine.md#results-and-calculation-status),
[`REGION_CODES`](../api/models.md#fiscal),
[`FamilyComposition`](../api/engine.md), [`Art15Deductions`](../api/engine.md)
