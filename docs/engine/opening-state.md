# Opening state and imported balances

A run computes the progressive IRPEF of the tax year (art. 23 c. 1 and c. 3
DPR 600/1973) and the INPS base of the competence year toward the IVS
massimale (L. 335/1995 art. 2 c. 18) from the state it opens with, and the
first run of a tax year withholds what the conguaglio of the year before
carried (surtax, installment recoveries, a deferred shortfall). The opening
state and the bases of the worker's other employments are therefore facts
of the run: a run without them is computed as a simulation and is not
payable. The state itself is described in
[Payroll state and the year change](payroll-state.md).

## History of the employment

The engine checks the content of the opening state, not whether the field
was passed. It reports a `missing_fact opening_state` blocker (issue
`opening_state_unknown`, status `incomplete`) when:

- a regular month of the competence year of the run, from January or from
  the start of the employment, before the month of the run, is not closed
  in the state: `PeriodState.zero()` on a June run of an employment begun
  in January drops January to May, whether passed explicitly or left to
  the default of `PeriodInput.opening_state`;
- the employment began before the competence year of the run, or
  `Employment.employment_period` is not stated, and the state carries
  nothing of an earlier tax year (no run closed, no tax year bound, no
  obligation): January from zero would drop the 2025 surtax and
  recoveries;
- the state descends from a run that opened without its history.
  `PeriodState.history_known` is `False` on the closing state of such a
  run and on the state `close_tax_year()` opens from it, so every later run
  of the chain blocks too.

A run that a year calculation leaves out because the bundle holds no pay
rules on its date (`uncovered_runs`, a `run_not_computed` blocker of the
year) is not counted as missing history: the year reports it once, and the
runs after it do not report it again.

`PeriodState.zero()` is the fact only for the first run of an employment
whose start is stated and falls in the month of the run. The same rule
applies to the first payment of a `CompetenceYearPlan` or a `TaxYearPlan`
whose `opening_state` is `None`: a plan of an employment begun in an
earlier year opens with `close_tax_year()` of the previous year or with
imported balances. A state built by hand (`PeriodState(...)`) states its
history as the caller built it.

## INPS base of other employments

The massimale is per worker (INPS circ. 237/2016 par. 3.1): the base of
earlier or simultaneous employments of the competence year counts toward it,
and toward the band of the additional 1% IVS (D.L. 384/1992 art. 3-ter;
INPS circ. 6/2026 note 10). `InpsBaseYtd.other_employers` is tri-state:
`None` is not known, `Decimal(0)` states that there is no other employment,
an amount is the certified (CU) or declared base. It is stated in one of two
places:

- `CurrentYearTaxFacts.other_employment_inps_base`, required next to the
  other income of the year (`CurrentYearTaxFacts.employment_only()` states
  zero). When the tax year of the facts is the competence year of the run,
  it replaces the base the opening state carries for that year, so the
  latest declaration wins, and the closing state carries it to the next
  runs;
- `OpeningBalances.inps_bases`, with the base of this employment.

An unknown base has no upper bound, so some value of it moves any run with
a positive INPS base across the massimale or the 1% threshold. The engine
encodes no estimate: the run computes on this employment alone and, when
its INPS rules carry a massimale the worker may be subject to (the
contribution history is unknown or within the contributory cohort) or a 1%
threshold, reports a `missing_fact other_employers` blocker (issue
`other_employment_inps_base_unknown`). Domestic work, contributed per hour
without either, reads no base of other employments.

## Balances from a previous provider

`OpeningBalances` takes the progressive totals of a previous payroll
provider for one tax year, with the recoveries still running, and
`PayrollEngine.import_opening_balances(balances)` turns them into the
`PeriodState` of the first run the engine computes: the one entry point for
totals the engine did not compute. `inps_bases`, `recoveries` and
`surtax_obligations` have no default: what the previous provider
determined is stated, `()` when there is nothing, and every competence year
of `payments` and `competence_runs` needs its `InpsBaseYtd`. They are
validated with the rules of the state the engine produces: every amount non-negative with at most two
decimals, credit recovered not above recognized (`trattamento_*`,
`somma_esente_*`), taxed fringe not above fringe value, payments
(`payments`, a tuple of `PaymentId`) of the tax year in payment order, each
of a different run, YTD totals only with the payments that produced them,
competence runs closed in earlier tax years (`competence_runs`, e.g. the
2026 runs paid in 2026 before a December paid in 2027), the INPS base per
competence year with the base of other employers (`inps_bases`), the surtax
already settled at an earlier termination (`regional_settled`,
`municipal_settled`), the shortfalls not yet withheld (`irpef_shortfall`,
`surtax_shortfall`, `credit_recovery_shortfall`), no recovery opened after
the tax year, surtax
obligations (`surtax_obligations`) determined by the conguaglio of an
earlier year, an acconto withheld (`municipal_advance_withheld`) not
above the surtax withheld, and IRPEF deferred on written request
(`deferred_shortfall`) by the conguaglio of `tax_year - 1` only. A violation raises
`InvalidInputError` with feature `opening_balances`.

```python
from decimal import Decimal

from ccnl_engine.inputs import (
    InpsBaseYtd,
    OpeningBalances,
    RecoveryObligation,
    RecoveryPlan,
)

opening = engine.import_opening_balances(OpeningBalances(
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
    # No payment of 2027 yet and no other employment of the worker in 2027.
    inps_bases=(InpsBaseYtd(2027, Decimal(0), Decimal(0)),),
    surtax_obligations=(),
))
```
