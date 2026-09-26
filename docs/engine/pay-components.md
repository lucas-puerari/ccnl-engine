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
    WeeklyHours,
)

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

Pass the months of continuous service as `Employment.seniority_months`, a
`SeniorityMonths`.
The engine derives the number of matured increments from the CCNL cadence and
adds the amount the level earns.

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
  `seniority_months` without a category, the calculation raises
  `InvalidInputError` instead of silently dropping the increment.

## Bilateral funds (*fondi bilaterali*)

Many CCNLs require contributions to sector bilateral bodies (health funds,
training funds, supplementary pension). The engine does not derive them from
the CCNL: pass the amounts due in the period as a `BilateralFundEvent`. The
employee portion reduces net pay; the employer portion increases employer
cost.

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

**API reference:** [`Employment`](../api/engine.md),
[`WorkerCategory`](../api/engine.md)
