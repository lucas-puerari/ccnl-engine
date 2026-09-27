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
training funds). The engine does not derive them from the CCNL: pass the
amounts due in the period as a `BilateralFundEvent`. The employee portion
reduces net pay; the employer portion increases employer cost. For the
pension fund of the CCNL use the enrolment described in
[Pension funds](#pension-funds-previdenza-complementare) instead.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    BilateralFundEvent,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)

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
  deducted is tracked in `closing_state.ytd.earnings.pension_deducted`
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
