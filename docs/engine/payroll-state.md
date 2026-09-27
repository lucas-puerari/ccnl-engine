# Payroll state and the year change

Every run opens with a `PeriodState` and returns the next one as
`result.closing_state`. The state has two parts with different lifetimes:

| Part | Type | Lifetime | Holds |
|---|---|---|---|
| `state.ytd` | `TaxYearState` | one tax year | run counters, withholding slots, closed run ids, YTD earnings, fringe, tax withheld, trattamento integrativo, somma esente, night/holiday/shift cap, IRPEF and surtax not yet withheld (`shortfall`) |
| `state.obligations` | `EmploymentObligations` | the employment | installment recoveries still running (trattamento integrativo, D.L. 3/2020 art. 1 c. 3; somma esente and ulteriore detrazione, L. 207/2024 art. 1 c. 7) |

`state.tax_year` is a shortcut for `state.ytd.tax_year`.

## Within a tax year

Pass the `closing_state` of a run as the `opening_state` of the next run of
the same tax year. `PeriodState.zero()` opens the first run of a new
employment. A run attributed to another tax year
(see [tax year attribution](index.md)) is rejected with `InvalidInputError`.

## Closed runs

`state.ytd.closed_run_ids` is a tuple of `PayrollRunId` in closing order.
A `PayrollRunId` holds the year and month of the run and its `RunKind`; its
text form is the `run_id` of `PayrollRun` (`"2026-12-thirteenth"`), and
`PayrollRunId.parse()` reads it back. A period computed without a `run`
closes the regular run of its month.

A run is rejected with `InvalidInputError` (feature `payroll_run`) when:

- it was already closed in the tax year;
- its year is after the tax year of the state;
- it is a run of the tax year that comes before one already closed. Runs
  close in payment order: by month, and within a month the regular payslip
  before the tredicesima or quattordicesima, before a termination run.

Two runs are not ordered: an adjustment run, which corrects a run already
closed, and a run of an earlier year paid late, which belongs to the tax
year of its payment (TUIR art. 51 c. 1). A `TaxYearState` built by hand
follows the same rules, needs a `tax_year` when it lists closed runs, and
cannot list more regular or slot-consuming runs than its counters.

## Year-to-date totals and credit accounts

Every YTD total (`earnings`, `tax`, `fringe`) is non-negative: a run can post
a negative adjustment, but no total of the year falls below zero. A state
that would break this is rejected; a run that produces one fails with
`DataIntegrityError`. No relation between totals is enforced beyond
`fringe.taxed <= fringe.value`: taxable income can exceed gross (a fringe
benefit above the threshold is taxable without cash gross).

The trattamento integrativo, the somma esente and the ulteriore detrazione
share one account schema, `CreditAccount` (`TrattamentoAccount`,
`SommaEsenteAccount`, `UlterioreDetrazioneAccount`; for the deduction,
`recognized` is the part the withholding applied, see
[Fiscal](fiscal.md#ulteriore-detrazione-recognized-and-recovered)):

| Field | Meaning |
|---|---|
| `recognized` | credit paid this tax year |
| `recovered` | credit taken back this tax year, never above `recognized` |
| `due` | updated annual entitlement computed by the last run |
| `reason` | reason code of the last decision on the credit |
| `net` | `recognized - recovered` |
| `residual` | over-payment still to recover, `max(net - due, 0)` |

The recovery plan is not in the account: it can outlast the tax year, so
it lives in `state.obligations`, one per credit and origin year
(`obligations.recovery_of(tax_year, kind)`).

## Somma esente

The somma esente (L. 207/2024 art. 1 c. 4) is paid on every run as its share
of the annual amount on the projected income, capped at what is still due.
The annual amount is a percentage of the employment income of the year; the
percentage is chosen on that income "rapportato all'intero anno" (c. 5),
`income * 365 / days`, as in circolare AdE 4/E of 16 May 2025, esempio 1
(€2,000 in 62 days: 5.3%, €106). The 20,000 EUR limit applies to the
reddito complessivo, which is not an input: the engine takes the employment
income for it. Other income can only raise the reddito complessivo, so a
run with an amount due carries the `provisional` issue
`somma_esente_income_assumed`.
Its entitlement is verified at the conguaglio, the last withholding slot
(art. 1 c. 7):

- the balance still due is paid, so the credits of the year add up to the
  annual amount;
- an amount paid and not due is recovered: in full up to 60 EUR, otherwise
  in ten equal installments from the conguaglio payslip. The installments
  after the last run of the year are carried into N+1.

A run before the conguaglio that finds the due below what was paid pays
nothing and recovers nothing (`overpayment_pending_conguaglio`); the excess
waits for the conguaglio. Every run records a `CalculationDecision` with
capability `somma_esente`, the signed amount of the run and one of the
reasons `share_paid`, `not_due`, `overpayment_pending_conguaglio`,
`settled_at_conguaglio`, `overpayment_recovered`,
`overpayment_recovery_opened`, `overpayment_recovered_at_termination`,
`installment_posted`, `last_installment_posted`,
`installment_posted_adjustment_run`, `settled_at_termination`. A recovery
posts the line `somma_esente_recovery_{run_id}` on account `CREDITS`.

The trattamento integrativo follows its own rule: an over-payment is
recovered as soon as a run finds it, in eight installments above 60 EUR
(D.L. 3/2020 art. 1 c. 3). Every recovery of the trattamento records a
`CalculationDecision` with capability `trattamento_integrativo_recovery`,
the negative amount of the run and the residual left after it.

## Recovery at the end of the employment

No installment outlives the employment. AdE circ. 29/E/2020 par. 6
(trattamento integrativo) and circ. 4/E/2025 par. 1.2 (somma esente and
ulteriore detrazione) state that at the conguaglio di fine rapporto the
withholding agent recovers the credits not due "in un'unica soluzione,
indipendentemente dall'importo, in mancanza di ulteriori retribuzioni sulle
quali operare il recupero in maniera dilazionata". The laws themselves
(D.L. 3/2020 art. 1 c. 3, L. 207/2024 art. 1 c. 7) are silent on the
cessation.

A run is the last one of the employment when it is a `termination` run, or
when the employment period ends in the tax year and the run takes its last
withholding slot. For an employment ending on 31 December the last run is
the tredicesima, not the regular December payslip. On that run the three
credits follow one rule (`RecoveryPlan.post`):

- an excess found by the conguaglio is recovered in full, above 60 EUR too
  (`overpayment_recovered_at_termination`);
- a plan of the current year or carried from an earlier year posts its
  whole residual (`settled_at_termination`) and closes.

What the pay cannot cover is not lost: the circolari refer to art. 23 c. 3
DPR 600/1973, the amount is communicated to the worker. The withholding cap
takes the credit recoveries first, then IRPEF and surtax; the part of a
recovery the pay leaves uncovered is given back by one
`credit_recovery_shortfall_{run_id}` line on `CREDITS`, tracked as
`shortfall.credit_recovery` apart from the IRPEF, and reported by the
provisional issue `withholding_shortfall_unrecovered`.

Example: a 2025 somma esente plan of 200 EUR in ten installments of 20,
three posted, with an employment from 1 January to 31 March 2026. January
and February post 20 EUR each; March posts 200 - 5 x 20 = 100 EUR and the
closing state carries no recovery.

## Adjustment runs after the conguaglio

An adjustment run paid after the conguaglio of year N is a payslip "alla
quale si applicano gli effetti del conguaglio", so it posts the next
installment of every plan the conguaglio opened, with reason
`installment_posted_adjustment_run`:

- trattamento integrativo and somma esente post the installment as a
  negative `CREDITS` line;
- the ulteriore detrazione plan lives inside the IRPEF of N. The adjustment
  run settles the cumulative balance again, so it withholds the balance
  less what is still deferred after its installment. When the balance falls
  below that, e.g. an adjustment that restores the deduction, the plan is
  closed and the cumulative balance settles the year
  (`recovery_absorbed_by_conguaglio`). An excess found again while the plan
  runs is recovered in full on the run, not merged into the plan.

## Opening the next tax year

`PayrollEngine.close_tax_year(closing_state)` takes the closing state of the
last run of year N and returns the opening state of N+1:

- `ytd` restarts: no run closed, every YTD account at zero, bound to N+1.
  This includes the night, holiday and shift cap account, which is annual.
- `obligations` is carried unchanged. A recovery keeps the tax year that
  opened it; its remaining installments are due from the first run of N+1,
  one per run, until the last one, or at once on the last run of the
  employment.

The input must be a year-end state: bound to a tax year, with every
withholding slot of the year closed. The state after December but before the
tredicesima is rejected, and so is a hand-built state that never ran.

Single runs computed with `PayrollEngine.calculate_period()` use the standard
withholding schedule of the CCNL. For an employment that did not cover the
whole year that schedule is never completed, so `close_tax_year` rejects the
state: compute the year with `calculate_year`, whose schedule follows the
employment, or build the N+1 state with `OpeningBalances`.

`PeriodState.zero()` is the state of a new employment: used at the year
change it drops every obligation, which cannot be told apart from a new
employment.

```python
from ccnl_engine import EmployerProfile, Employment, Headcount, PayrollEngine, YearInput

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
)
employer = EmployerProfile(headcount=Headcount(50))
year_2026 = engine.calculate_year(
    YearInput(year=2026, employment=employment, employer=employer)
)
opening_2027 = engine.close_tax_year(year_2026.closing_state)
# engine.calculate_year(YearInput(year=2027, ..., opening_state=opening_2027))
```

`calculate_year` accepts `opening_state` only when it closes no run of the
year: `PeriodState.zero()` or the result of `close_tax_year`.

## Recovery carried into the next year

The conguaglio of year N can find that trattamento integrativo, somma
esente or ulteriore detrazione was not due. Above 60 EUR the recovery runs
in equal installments from the payslip of the conguaglio (eight for the
trattamento integrativo, D.L. 3/2020 art. 1 c. 3; ten for the somma esente
and the ulteriore detrazione, L. 207/2024 art. 1 c. 7), so it often
continues into N+1. The adjustment runs of N post installments too; an
employment that ends recovers the residual in full on its last run.

- Installments posted in N enter `recovered` of the N credit account.
- Installments posted in N+1 are a negative tax credit line on the payslip
  (`{kind}_recovery_{N}_{run_id}`, account `CREDITS`). They do not enter the
  N+1 credit account, and the N+1 credit is computed as for any other year.
- The invariant `carried_recovery_advance` checks that each carried
  recovery posts its next installment and closes one installment further
  along, or posts its whole residual and closes on the last run of the
  employment.
- Each carried installment records a `CalculationDecision` with capability
  `trattamento_integrativo_recovery` (rule `dl3-2020-art1-c3`) or
  `somma_esente_recovery` (rule `l207-2024-art1-c7`), reason
  `installment_posted`, `last_installment_posted`,
  `installment_posted_adjustment_run` or `settled_at_termination`, the
  origin tax year, the installment number and the residual before it, and
  the negative amount posted.

At most one recovery per credit and origin year is held. The recovery opened
by the conguaglio of the current year runs inside the conguaglio, as before.

## Balances from a previous provider

`OpeningBalances` takes the progressive totals of a previous payroll
provider for one tax year, with the recoveries still running, and validates
them with the rules of the state the engine produces: every amount
non-negative with at most two decimals, credit recovered not above
recognized (`trattamento_*`, `somma_esente_*`), taxed fringe not above fringe
value, closed runs (`closed_run_ids`, a tuple of `PayrollRunId`) of the tax
year and in order, no recovery opened after the tax year. A violation raises
`InvalidInputError` with feature `opening_balances`. `to_state()` returns the `PeriodState`
for the first run the engine computes.

```python
from decimal import Decimal

from ccnl_engine import OpeningBalances, RecoveryObligation, RecoveryPlan

opening = OpeningBalances(
    tax_year=2027,
    recoveries=(
        RecoveryObligation(
            tax_year=2026,
            plan=RecoveryPlan(
                kind="trattamento_integrativo",
                original_amount=Decimal(160),
                installment_amount=Decimal(20),
                installments_total=8,
                installments_posted=4,
            ),
        ),
    ),
).to_state()
```
