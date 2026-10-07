# Tax credit decisions

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

## Ulteriore detrazione recognized and recovered

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
[Pay that does not cover the tax](fiscal.md#pay-that-does-not-cover-the-tax)). AdE
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
percentage apprenticeship track), `family_deductions` (`deductions_applied`,
`no_deduction_due`, `required_fact_missing` when the reddito complessivo or
a condition of a dependant is unknown, or
`estimated_income_at_conguaglio`, only with a family composition, see
[Family deductions](fiscal.md#family-deductions-art-12-tuir)), `bonus_pdr`
(`substitute_tax_applied` or `annual_limit_reached`, only for a bonus routed
to the PdR substitute tax), `fringe_benefit` (`within_threshold`,
`above_threshold` or `above_threshold_retroactive`, one per `FringeEvent`,
see [Fringe benefits](work-rules.md#fringe-benefits)) and the substitute tax
regimes described in [Substitute tax regimes](substitute-tax-regimes.md).
