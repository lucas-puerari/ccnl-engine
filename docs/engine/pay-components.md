# Pay components

This page covers the employment facts that adjust gross pay beyond the CCNL
table minimum: part-time scaling, seniority and worker category. It also
covers bilateral fund contributions, which change net pay and employer cost.

See [Domain: Components](../domain/components.md) for the legal background.

## Part-time

Pass the contracted `weekly_hours` together with the CCNL
`full_time_weekly_hours` on `Employment`, as `WeeklyHours`. The engine derives the
part-time fraction from the two and scales the contractual pay by it.
`weekly_hours` must not exceed `full_time_weekly_hours`.

```python
from datetime import date

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import WeeklyHours

engine = PayrollEngine.bundled()


def gross(weekly_hours: WeeklyHours | None = None) -> str:
    employment = Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        weekly_hours=weekly_hours,
        full_time_weekly_hours=WeeklyHours(40),
    )
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            employment=employment,
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    return str(result.period_gross)


print("Full time:", gross())
print("Half time:", gross(WeeklyHours(20)))
```

## Seniority increments (*scatti di anzianità*)

Pass the recognised seniority as `Employment.seniority`, a `SeniorityFact`:
the completed months of service on a date (`as_of`) and where they were read
from (`SenioritySource`). `SeniorityFact.since(date, source)` states the date
the recognised service starts instead. The engine ages the fact to each run:
a run counts the months completed by the first day of its competence month,
so an increment matured during a month is paid from the next one; service
that starts within the month (a hire on the 15th recognised from that day)
counts zero months, and a run of a month before the recognised service
raises `InvalidInputError`. It derives
the number of matured increments from the CCNL cadence and adds the amount
the level earns.

Every run records a `seniority` decision with one of four reasons:

| Reason | When | Amount |
|---|---|---|
| `not_applicable_by_contract` | The level pays no increment to the worker: no amount for the level, a zero maximum or an excluded category (e.g. operai edili, paid through the Cassa Edile) | `0` |
| `zero_confirmed` | The seniority is known and no increment has matured | `0` |
| `increments_applied` | The seniority is known and increments are paid | the increments |
| `required_fact_missing` | `seniority=None` on a level that pays increments, or an allowance gated by months of service | `None` |

The fact is required only when the level pays increments to the worker's
category (an unknown category counts when any category is paid) or holds an
allowance gated by months of service for the worker's roles. Without it the
decision is `provisional`, the `seniority_unknown` issue names the fact, the
result has a `missing_fact` blocker for `seniority` and is not payable. The
amounts of such a run leave the increments and the gated allowances out:
they are what a worker without seniority would earn, not the answer.

```python
--8<-- "docs/examples/05_seniority.py"
```

### Worker category

Some CCNLs price seniority by legal category (art. 2095 c.c.): in Servizi
Postali in Appalto FISE an *operaio* and an *impiegato* on the same level earn
different increments. Pass the category as `Employment.category`, a
`WorkerCategory` (`operaio`, `impiegato`, `quadro`, `dirigente`). The same
value selects category-specific INPS employer rates (e.g. *impiegati* in
artigianato).

- A level reserved to one category (e.g. a `quadro` level) supplies it when
  you omit it; declaring a different category raises `InvalidInputError`.
- When increments for the level exist only per category and you pass
  `seniority` without a category, the calculation raises
  `InvalidInputError` instead of silently dropping the increment.

## Bilateral funds (*fondi bilaterali*)

Many CCNLs require contributions to sector bilateral bodies (health funds,
training funds). The engine does not derive them from the CCNL: pass the
amounts due in the period as a `BilateralFundEvent`. The employee portion
reduces net pay; the employer portion increases employer cost. For the
pension fund of the CCNL use the enrolment described in
[Pension funds](#pension-funds-previdenza-complementare) instead.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import BilateralFundEvent

engine = PayrollEngine.bundled()

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
        facts=PeriodFacts(
            events=(
                BilateralFundEvent(
                    event_date=date(2026, 3, 1),
                    employee_amount=Decimal("2.00"),
                    employer_amount=Decimal("13.00"),
                ),
            ),
        ),
    )
)
print(result.period_net, result.period_employer_cost)
```

## Pension funds (*previdenza complementare*)

Enrolment in a complementary pension fund is voluntary (D.Lgs. 252/2005
art. 1 c. 2), so the engine never assumes it. Declare it on the employment
as `Employment.pension_fund`, a `PensionFundEnrolment`:

- `fund_code`: a fund of the CCNL, e.g. `"ALIFOND"` for Tabacco or
  `"FONCHIM"` for Vetro meccanizzato. A code the CCNL does not declare
  raises `InvalidInputError`.
- `employee_rate`: the contribution the worker chose. It cannot be below
  the CCNL minimum when the bundle records one (ALIFOND: 1%).
- `tfr_to_fund`: whether the TFR accrued is paid to the fund. Required,
  with no default.

`pension_fund=None` means not enrolled: no fund line is posted. On a CCNL
that has a fund, the `pension_fund_contribution` decision records the
reason `not_enrolled` and the capability is not applicable.

When enrolled, each run posts:

| Line | Account | Amount | Effect |
|---|---|---|---|
| Employer contribution | `pension_fund_employer` | CCNL rate x INPS base of the run | employer cost |
| Solidarity contribution | `employer_contributions` | 10% of the employer contribution | employer cost |
| Employee contribution | `pension_fund_employee` | chosen rate x INPS base | withheld from net |
| TFR to the fund | `pension_fund_tfr` instead of `tfr_accrual` | TFR of the run | none: the cost does not change |

The rules behind it:

- **Base.** The bundle stores each fund rate as a fraction of the INPS
  contribution base of the run, events included
  (`CCNL.parameters.employer_funds`). A fund whose statute uses another
  base (e.g. the TFR base) must be converted to it in the data.
- **Deduction.** Employee and employer contributions are deductible from
  the taxable income up to 5 300.00 EUR a year from tax year 2026
  (D.Lgs. 252/2005 art. 8 c. 4 as amended by L. 199/2025; TUIR art. 10
  c. 1 lett. e-bis and art. 51 c. 2 lett. h). Within the cap the taxable
  falls by the employee part; beyond it the employer part is taxable
  income. The TFR paid to the fund does not count. The amount already
  deducted is tracked in `closing_state.cash.earnings.pension_deducted`
  (`OpeningBalances.pension_deducted` when importing a year in progress).
- **Solidarity.** The employer contributions, the TFR excluded, stay
  outside the INPS base and bear the 10% solidarity contribution to INPS
  (D.Lgs. 252/2005 art. 16 c. 1; art. 9-bis D.L. 103/1991, conv. L.
  166/1991). It is posted to `employer_contributions` in the ledger but
  is not a component of `contribution_breakdown`, which holds the INPS
  contributions on the pay only.

Not modelled: the compensatory measures for employers whose TFR goes to a
fund (D.Lgs. 252/2005 art. 10), the extra deduction of workers first
employed from 2007 (art. 8 c. 6), a partial TFR conferment, and the eligibility
conditions some CCNLs set (e.g. ALIFOND excludes fixed-term contracts up
to six months).

```python
--8<-- "docs/examples/13_pension_fund.py"
```

**API reference:** [`Employment`](../api/engine.md),
[`WorkerCategory`](../api/engine.md)
