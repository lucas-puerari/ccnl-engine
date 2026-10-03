# Payroll state and the year change

Every run opens with a `PeriodState` and returns the next one as
`result.closing_state`. Competence and cash are two clocks, so the state
has two parts with different lifetimes:

| Part | Type | Lifetime | Holds |
|---|---|---|---|
| `state.accrual` | `EmploymentAccrualState` | the employment | competence runs closed (`competence_runs`, a tuple of `PayrollRunId` in closing order): the months and extra months of each competence year already paid |
| `state.cash` | `TaxCashState` | one tax year | payments of the tax year (`payments`, a tuple of `PaymentId`), withholding payments closed and slots of the schedule, YTD earnings, fringe, tax withheld (with the municipal acconto withheld), trattamento integrativo, somma esente, night/holiday/shift cap, IRPEF and surtax not yet withheld (`shortfall`) |
| `state.cash.obligations` | `EmploymentObligations` | carried from year to year | installment recoveries still running (trattamento integrativo, D.L. 3/2020 art. 1 c. 3; somma esente and ulteriore detrazione, L. 207/2024 art. 1 c. 7) surtax a conguaglio determined, still to withhold (`surtax`), and IRPEF of a conguaglio deferred on the worker's written request (`deferred_shortfall`, art. 23 c. 3 DPR 600/1973) |

`state.tax_year` is a shortcut for `state.cash.tax_year`.

## Within a tax year

Pass the `closing_state` of a run as the `opening_state` of the next run.
`PeriodState.zero()` opens the first run of a new employment. A run whose
payment is attributed to another tax year than the state
(see [tax year attribution](index.md)) is rejected with
`InvalidInputError`.

## Competence runs and payments

A run is the competence of a month or an extra month; a payment is the cash
event that settles it. December 2026 paid on 13 January 2027 is a 2026
competence run and a payment of tax year 2027 (TUIR art. 51 c. 1).

- `state.accrual.competence_runs` lists the runs closed over the whole
  employment. `accrual.regular_months(year)` counts the regular months of a
  competence year, at most 12 because a run closes once;
  `accrual.extra_months_paid(year)` lists its tredicesima and
  quattordicesima runs.
- `state.cash.payments` lists the payments of the tax year as `PaymentId`
  (`run_id` and `payment_date`; text form `"2026-12-regular@2027-01-13"`,
  read back with `PaymentId.parse()`). Their number has no maximum: a tax
  year with a late December holds fifteen payments on a CCNL with
  tredicesima and quattordicesima.
  `cash.prior_competence_payments` are the payments of an earlier
  competence year.
- `state.cash.withholding_payments_closed` counts the payments that took an
  IRPEF withholding slot (every run kind but adjustment), with no maximum.

A `PayrollRunId` holds the year and month of the run and its `RunKind`; its
text form is the `run_id` of `PayrollRun` (`"2026-12-thirteenth"`), and
`PayrollRunId.parse()` reads it back. A period computed without a `run`
closes the regular run of its month.

A run is rejected with `InvalidInputError` before any amount is computed
when:

- its competence run is already closed, in this tax year or an earlier
  one: the accrual state is carried across the year change (feature
  `accrual_state`);
- it is a regular month of a competence year that comes before a regular
  month of the same year already closed, or any run but an adjustment of a
  competence year whose termination run is already closed (feature
  `accrual_state`). The tredicesima and the quattordicesima are not ordered
  against the regular months: their ratei are counted from the employment
  dates, so an employer that pays in arrears may pay the December
  tredicesima before the December salary, or the quattordicesima before a
  July salary paid in August. An adjustment run, which corrects a run
  already closed, is not ordered; runs of different competence years are
  not ordered against each other;
- its payment belongs to another tax year than the state (feature
  `tax_cash_state` or `tax_year`).

Closing is idempotent by payment: the same request on the same opening
state yields the same closing state, and a state that already closed the
payment rejects it, so a retry never counts competence, gross or
withholdings twice. A state built by hand follows the same rules: a
`TaxCashState` needs a `tax_year` when it lists payments, each of that tax
year and of a different run, and cannot list more slot-consuming payments
than `withholding_payments_closed`; a `PeriodState` rejects a payment whose
run the accrual state has not closed.

## Withholding schedule of the tax year

The IRPEF projection and the conguaglio run on a `WithholdingSchedule`: one
slot per payment of the tax year, the last of which settles the year. A
standalone run builds it from the standard calendar of the CCNL, preceded
by the payments of an earlier competence year in the state and by the run
itself when it is one. `calculate_year` builds it from the runs of the
year, preceded by the late payments already closed in its opening state.
With December 2026 paid on 13 January 2027, every run of 2027 sees fifteen
slots and the conguaglio falls on the last payment of 2027.

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
it lives in `state.cash.obligations`, one per credit and origin year
(`obligations.recovery_of(tax_year, kind)`), carried across the year
change.

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
posts the line `somma_esente_recovery_{run_id}` on account
`CREDIT_RECOVERIES`, coded 1704 like the amount paid (see
[Ledger accounts and F24 remittance](#ledger-accounts-and-f24-remittance)).

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
`credit_recovery_shortfall_{run_id}` line on `CREDIT_RECOVERY_SHORTFALL`
(a part carried in and withheld later posts the same line on
`CREDIT_RECOVERIES`), tracked as
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

- trattamento integrativo and somma esente post the installment on
  `CREDIT_RECOVERIES`;
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

- `cash` restarts: no payment closed, every YTD account at zero, bound to
  N+1. This includes the night, holiday and shift cap account, which is
  annual.
- `accrual` is carried unchanged: a competence run closed in N cannot be
  paid again in N+1.
- `cash.obligations` is carried unchanged. A recovery keeps the tax year that
  opened it; its remaining installments are due from the first run of N+1,
  one per run, until the last one, or at once on the last run of the
  employment. The surtax the conguaglio of N determined (regional surtax
  and municipal saldo of N, municipal acconto of N+1) is withheld on the
  regular payslips of N+1, see
  [Surtax carried into the next year](#surtax-carried-into-the-next-year).
  The IRPEF the conguaglio of N deferred on the worker's written request
  is withheld from March of N+1, see
  [Deferred shortfall carried into the next year](#deferred-shortfall-carried-into-the-next-year).

The input must be a year-end state: bound to a tax year, with every
withholding slot of the year closed. The state after December but before the
tredicesima is rejected, and so is a hand-built state that never ran.

Single runs computed with `PayrollEngine.calculate_period()` use the standard
withholding schedule of the CCNL, with the late payments of an earlier
competence year in front. For an employment that did not cover the
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
- Installments posted in N+1 are a `CREDIT_RECOVERIES` line on the payslip
  (`{kind}_recovery_{N}_{run_id}`). They do not enter the
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

## Surtax carried into the next year

The conguaglio of N determines the surtax of N and the municipal acconto
of N+1 and stores them in `cash.obligations.surtax`, one `SurtaxObligation` per
component (`SurtaxComponent.REGIONAL_BALANCE`, `MUNICIPAL_BALANCE`,
`MUNICIPAL_ADVANCE`), with the tax year of the conguaglio, the region or
municipality it is due to and a `RecoveryPlan` of its installments:

- regional surtax and municipal saldo: eleven installments, January to
  November of N+1 (D.Lgs. 446/1997 art. 50 c. 4, D.Lgs. 360/1998 art. 1
  c. 5);
- municipal acconto of N+1: nine installments, March to November
  (art. 1 c. 5).

Each regular payslip of the window withholds one installment, the November
one the residual; extra-month, December and adjustment payslips withhold
none; the last run of the employment withholds every residual. The payslip
lines are `surtax_{component}_{reference year}_{run_id}` on `SURTAX`, coded
3802, 3848 or 3847. `TaxYtd.municipal_advance` counts the acconto withheld
in the year, which the conguaglio deducts from the municipal surtax; an
acconto above the surtax due is refunded on `SURTAX_REFUNDS`
(`surtax_refund_{run_id}`). A termination run after the last withholding
slot is a second conguaglio of the year: it drops the obligations the
first one deferred and withholds the surtax of the year less what an
earlier conguaglio of the year already withheld (`TaxYtd.regional_settled`,
`TaxYtd.municipal_settled`). At most one obligation per component and
conguaglio year is held. See
[Fiscal: when the surtax is withheld](fiscal.md#when-the-surtax-is-withheld)
for the rules and the decisions.

## Deferred shortfall carried into the next year

When `PriorYearTaxFacts.shortfall_deferral` holds the worker's written
request, the conguaglio of N moves the IRPEF its pay cannot cover from
`cash.shortfall.irpef` to `cash.obligations.deferred_shortfall`: one
`DeferredShortfall(tax_year=N, signed_on, deferred_from, irpef)` per
conguaglio, `deferred_from` being the first day of the pay period of the
conguaglio (`obligations.deferred_of(N)`). Without the request the
shortfall stays in `cash.shortfall` and ends with the year, as before.

`close_tax_year` carries it. From the March pay period of N+1 every run
other than an adjustment withholds from its net pay, after every other
line, the largest principal whose interest (0.50% a month since
`deferred_from`) still fits, on `deferred_irpef_{N}_{run_id}` and
`deferred_irpef_{N}_interest_{run_id}` (`ORDINARY_TAX`, code 1066), and
keeps the rest. The conguaglio of N+1 and the last run of the employment
drop what is left with a provisional `deferred_shortfall_unrecovered`
issue. These lines do not enter `cash.tax.irpef` of N+1: the invariant
`irpef_withheld_continuity` leaves out the entries coded 1066, and
`irpef_annual_reconciliation` of N counts the deferred IRPEF with the
withheld one. See
[Fiscal: written deferral](fiscal.md#written-deferral-of-the-year-end-shortfall).

## Ledger accounts and F24 remittance

The withholding agent remits the tax it withholds and offsets the credits
it paid on the F24, one line per codice tributo. The ledger keeps each flow
on its own account, every entry non-negative, so that the F24 lines of a
run can be read from it:

| Account | What it holds | Codice tributo |
|---|---|---|
| `ORDINARY_TAX` | IRPEF withheld, before any credit is offset | 1001 |
| `ORDINARY_TAX` | IRPEF of an earlier conguaglio deferred on written request, and its interest (`deferred_irpef_{year}_{run}`, `deferred_irpef_{year}_interest_{run}`) | 1066 |
| `TAX_REFUNDS` | IRPEF refunded by the conguaglio | none |
| `SURTAX` | regional surtax (`surtax_regional_balance_{year}_{run}`) | 3802 |
| `SURTAX` | municipal saldo (`surtax_municipal_balance_{year}_{run}`) | 3848 |
| `SURTAX` | municipal acconto (`surtax_municipal_advance_{year}_{run}`) | 3847 |
| `SURTAX` | surtax carried from an earlier run for lack of pay (`surtax_{run}`) | none |
| `SURTAX_REFUNDS` | municipal acconto refunded by the conguaglio | none |
| `SUBSTITUTE_TAX` | PdR, rinnovo, notte, festivi e turni | 1053, 1075, 1076 |
| `SEPARATE_TAX` | arrears, TFR | 1002, 1012 |
| `CREDITS` | trattamento integrativo, somma esente paid | 1701, 1704 (credit column) |
| `CREDIT_RECOVERIES` | somma esente recovered | 1704 (debit column) |
| `CREDIT_RECOVERIES` | trattamento integrativo recovered, ulteriore detrazione of an earlier year | none |
| `CREDIT_RECOVERY_SHORTFALL` | recovery the pay could not cover, given back and carried | none |

Sources: Allegato 1 to the AdE provvedimento of 31 January 2025 (1001,
1002, 1012, 1053, 1701, 1704, 3802, 3847 and 3848, the last two instituted
by ris. 368/E/2007), ris. 35/E/2020 (1701), ris. 6/E/2021 (1066), ris. 9/E/2025
(1704, "importi a credito compensati" for the amount paid and "importi a
debito versati" for the amount "già erogata e poi recuperata"), ris.
3/E/2026 (1075) and 2/E/2026 (1076). The codes live in
`ccnl_engine.payroll.domain.remittance`; each entry carries its code in
`LedgerEntry.remittance_code`.

A code that cannot be verified is left out rather than guessed:

- surtax carried from an earlier run for lack of pay is not tracked by
  component;
- ris. 35/E/2020 gives 1701 for the credit column only, so a trattamento
  integrativo recovered from the worker has no code;
- the ulteriore detrazione recovered in the next tax year is IRPEF of the
  earlier year after its conguaglio;
- the national codes are used: the variants for Sicily, Sardinia and Valle
  d'Aosta are not selected.

When the pay does not cover the surtax due, the run withholds the surtax
carried in from an earlier run first (uncoded `surtax_{run}` line), then
the components in order (regional, municipal saldo, municipal acconto);
the rest is carried to the next run. The recovery shortfall is not tracked by credit, so a
somma esente recovery under 1704 can be partly given back on the uncoded
shortfall line of the same run.

`PeriodResult.remittance_summary()` returns one `RemittanceLine` per
account and code (account, code, F24 column, amount) for a run, and
`YearResult.remittance_summary()` the same totals for the year. The F24 is
filed by month of payment, so use the run summaries to fill it.

The net identity reads the accounts with their direction:

```text
period_net = CASH_EARNINGS + TFR_SETTLEMENT + CREDITS + TAX_REFUNDS
           + SURTAX_REFUNDS + CREDIT_RECOVERY_SHORTFALL - CREDIT_RECOVERIES
           - EMPLOYEE_CONTRIBUTIONS - BILATERAL_FUND_EMPLOYEE
           - PENSION_FUND_EMPLOYEE - EMPLOYEE_DEDUCTIONS
           - ORDINARY_TAX - SURTAX - SUBSTITUTE_TAX - SEPARATE_TAX
```

The invariant `credit_non_negative` rejects a negative entry on the credit
accounts, and `remittance_code_consistent` requires a code on every
`ORDINARY_TAX`, `SEPARATE_TAX` and `CREDITS` entry and rejects a code the
account does not admit.

## Balances from a previous provider

`OpeningBalances` takes the progressive totals of a previous payroll
provider for one tax year, with the recoveries still running, and validates
them with the rules of the state the engine produces: every amount
non-negative with at most two decimals, credit recovered not above
recognized (`trattamento_*`, `somma_esente_*`), taxed fringe not above fringe
value, payments (`payments`, a tuple of `PaymentId`) of the tax year, each
of a different run and in order within its competence year, with
`withholding_payments_closed` at least the slot-consuming ones, no recovery opened after the tax year, surtax
obligations (`surtax_obligations`) determined by the conguaglio of an
earlier year, an acconto withheld (`municipal_advance_withheld`) not
above the surtax withheld, and IRPEF deferred on written request
(`deferred_shortfall`) by the conguaglio of `tax_year - 1` only. A violation raises
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
