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
- carries what it could not withhold in `state.ytd.shortfall` (`irpef`,
  `surtax`) and withholds it in full on the next run, before the share of
  the rest of the balance;
- records a `withholding_shortfall` decision (`withholding_capped` when it
  carries an amount out, `shortfall_withheld` when it withholds a carried
  amount), with the pay available and the amounts due in its inputs;
- on the last withholding slot, reports what is still not withheld as a
  provisional `withholding_shortfall_unrecovered` issue.

The cumulative conguaglio settles the tax on the whole year (art. 33 c. 4
D.Lgs. 33/2025, which replaces art. 23 c. 3 DPR 600/1973 from 1 January
2026, art. 243). For what is left at year end the same comma says: "L'importo
che al termine del periodo d'imposta non è stato trattenuto per cessazione del
rapporto di lavoro o per incapienza delle retribuzioni deve essere comunicato
all'interessato che deve provvedere al versamento entro il 15 gennaio
dell'anno successivo". The written request of the worker to have it
withheld on later pay periods, with interest at 0.50% a month, is not
modelled; the shortfall does not survive the year change. The statute does
not state how a shortfall found before the conguaglio is spread: taking it
on the next run is the engine's choice. Art. 33 c. 1, which makes the worker
pay the withholding that finds no cash, is written for values in kind and
is not used here.

Metalmeccanico C3, 160 absence hours at 12.50 EUR in January 2026: the pay
left after INPS is 143.25 EUR, the IRPEF share is 162.33 EUR; January
withholds 143.25 EUR and nets 0.00, February withholds the 19.08 EUR
carried on top of its share.

A run whose other deductions (INPS, substitute tax, recovery installments)
exceed the pay left by unpaid absences is still rejected
(`OutOfScopeError`, reason `withholding_shortfall`).

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

### Surtax decisions

Each jurisdiction named in the request records one `CalculationDecision` in
`result.decisions`, with capability `addizionale_regionale` or
`addizionale_comunale`.  Its `amount` is the annual surtax projected for the
tax year; the payslip withholds an equal share of it on every withholding
slot.  Its `inputs` hold the code, the table row name, the tax year and the
taxable income, and its `rule` and `rule_version` the bundled ruleset.

| `reason_code` | Status | Amount | Meaning |
|---|---|---|---|
| `table_applied` | `final` | computed | The bundled brackets were applied. |
| `advance_applied` | `final` | computed | Municipal rates are the prior year ones: only the advance (`advance_fraction`, 30%) is computed; `inputs["balance"]` is `not_modelled`. |
| `below_exemption_threshold` | `final` | 0 | The municipal exemption threshold covers the taxable income. |
| `no_irpef_due` | `final` | 0 | Net IRPEF (gross less the deductions) on the projected taxable income is zero, so no surtax is withheld. |
| `table_unknown` | `incomplete` | `None` | The code is well formed but the tax year table has no row for it. |

A `table_unknown` decision comes with a `CalculationIssue` coded
`regional_surtax_unknown` or `municipal_surtax_unknown`.  Nothing is
withheld for that surtax (the ledger posts 0), and the period result, hence
the year result, is `incomplete`: **it must not be paid as is**.  Without
`regione` and `comune_belfiore` no surtax decision is taken and nothing is
withheld.

The surtax is due only when the IRPEF net of its deductions is due
(D.Lgs. 446/1997 art. 50 c. 2 for the regional, D.Lgs. 360/1998 art. 1 c. 4
for the municipal): a worker whose deductions absorb the whole gross IRPEF
owes neither.

#### Foreign tax credit

Both articles take the IRPEF net of the deductions **and of the credit for
taxes paid abroad** (art. 165 TUIR); art. 33 c. 4 D.Lgs. 33/2025 also lets
the employer deduct at the conguaglio the foreign taxes paid on employment
income produced abroad. The engine has no input for foreign income or
foreign taxes: the net IRPEF it withholds, and the one that decides whether
the surtax is due, never subtract that credit. For a worker with income
taxed abroad the IRPEF withheld can be too high and a surtax can be
withheld where the credit would bring the net IRPEF to zero; compute such
cases outside the engine.

#### Advance and balance

For the municipal surtax, D.Lgs. 360/1998 art. 1 c. 4 sets an acconto of
30% of the surtax "ottenuta applicando le aliquote ... al reddito
imponibile dell'anno precedente", where "l'aliquota di cui al comma 3 e
la soglia di esenzione di cui al comma 3-bis sono assunte nella misura
vigente nell'anno precedente", withheld "in un numero massimo di nove rate
mensili, effettuate
a partire dal mese di marzo". The saldo is determined at the conguaglio
and withheld "in un numero massimo di undici rate" from the next pay
period, within the December remittance.

The bundled 2026 municipal table holds the rates deliberated for 2025,
the ones the 2026 acconto uses, so the engine computes the acconto only
(`advance_applied`). The decision stays `final`: the rates and the 30% are
the statutory ones, and the status of a surtax decision grades the table
applied, as for the regional surtax, whose timing is simplified the same
way. What the engine does not model is recorded instead of hidden:

- the saldo of the year (withheld in the next year) and the saldo of the
  year before (withheld in this one) are not computed; `inputs["balance"]`
  of the decision is `not_modelled`;
- the acconto is computed on the projected taxable income of the current
  year, not on the taxable income of the year before; the two differ for a
  new hire or a change of pay;
- the annual surtax, regional and municipal, is split in equal parts over
  the withholding slots of the year, not over the statutory installments
  (nine from March for the municipal acconto, eleven in the next year for
  the balances).

`provisional` was considered for the acconto: it would flag every
municipal result as not final without telling the reader what is missing,
and would leave the regional surtax, simplified in the same way, `final`.

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
recovery (D.L. 3/2020 art. 1 c. 3) is running.

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
`state.ytd.ulteriore_detrazione` (a `CreditAccount`). A run that takes part
of it back before the conguaglio (a bonus above the band) records it as
recovered by the withholding: that part is not found at the conguaglio and
is not spread again. On the last withholding slot:

- the account settles on the annual due;
- an excess up to 60 EUR stays in the conguaglio IRPEF;
- above 60 EUR the conguaglio IRPEF keeps the first of ten equal
  installments and the other nine are deferred: they open a recovery
  obligation of kind `ulteriore_detrazione_lavoro`, posted from the first
  run of the next tax year as a negative tax credit line
  (`ulteriore_detrazione_lavoro_recovery_{N}_{run_id}`, account `CREDITS`),
  like the other c. 7 recoveries. The ledger does not tell the IRPEF they
  recover apart from an offset credit.

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
a shortfall left to the worker (art. 33 c. 4 D.Lgs. 33/2025, see
[Pay that does not cover the tax](#pay-that-does-not-cover-the-tax)).
Runs of year N after the conguaglio (adjustments) do not post the
installments.

The other decisions a run can record are `worker_category` (the category
used and its origin: `declared` on the employment or `fixed_by_level`),
`seniority` (`increments_applied` or `no_increment_due`, only when the
months of service are given), `family_deductions` (`deductions_applied` or
`no_deduction_due`, only with a family composition), `bonus_pdr`
(`substitute_tax_applied` or `annual_limit_reached`, only for a bonus routed
to the PdR substitute tax) and the substitute tax regimes described in
[Substitute tax regimes](substitute-tax-regimes.md).

## Warnings

`PayrollResult.warnings` is a tuple of human-readable strings. The engine emits
a warning (but never fails) for conditions that may indicate a configuration
mistake:

- **IVS ceiling**: when `SeniorityByDate` is supplied with a hire date on or after
  1996-01-01 but `Employee.ivs_ceiling_applies` is `False`, and the contribution
  base exceeds the IVS ceiling. Workers hired from 1996 are generally subject to
  the *massimale IVS*; the flag defaults to `False` to avoid silent over-deduction
  for pre-1996 workers.

**API reference:** [`CalculationDecision`](../api/engine.md#results-and-calculation-status),
[`REGION_CODES`](../api/models.md#fiscal),
[`FamilyComposition`](../api/engine.md), [`Art15Deductions`](../api/engine.md)
