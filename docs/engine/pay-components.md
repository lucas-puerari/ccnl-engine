# Pay components

This page covers the employment facts that adjust gross pay beyond the CCNL
table minimum: part-time scaling, seniority and worker category. It also
covers bilateral fund contributions, which change net pay and employer cost.

See [Domain: Components](../domain/components.md) for the legal background.

## Part-time

Pass the contracted `weekly_hours` together with the CCNL
`full_time_weekly_hours` on `Employment`, as `WeeklyHours`. The engine derives the
part-time fraction from the two and scales the contractual pay by it.
`weekly_hours` must not exceed `full_time_weekly_hours`. The contracted hours
alone never count as full time: without `full_time_weekly_hours` the run
computes the full-time pay and carries a `missing_fact` blocker for it, on
a domestic CCNL too, where `weekly_hours` also selects the INPS bracket.

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
from ccnl_engine.inputs import Permanent, WeeklyHours

engine = PayrollEngine.bundled()


def gross(weekly_hours: WeeklyHours | None = None) -> str:
    employment = Employment(
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        contract_type=Permanent(),
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

## Role allowances

Some allowances of a level are paid only to a worker holding a role, e.g.
`IND_FUNZIONE_QUADRO` of Alimentari 1S for the role `quadro`. State the roles
on `Employment.roles`, a `frozenset` of role codes; `frozenset()` states that
the worker holds none. `roles=None`, the default, means not known: on a level
with an allowance restricted to a role in force, the run leaves the
allowance out and has a `missing_fact` blocker for `roles`. A worker
category, `QUADRO` included, does not unlock a role allowance.

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

## TFR

Each run accrues the TFR quota of art. 2120 c.c. (the TFR base over 13.5),
less the 0.50% additional IVS of L. 297/1982 art. 3 c. 16 where the sector
deducts it (an apprentice owes none: INPS circ. 70/2007, note 5). Two facts
of `Employment` decide where it goes and how the fund grows.

### Fondo Tesoreria

`tfr_treasury_fund` says whether the TFR not paid to a pension fund goes to
the Fondo Tesoreria INPS (L. 296/2006 art. 1 cc. 755-756). The obligation
does not follow the headcount of the run: it is the yearly average of 2006,
or of the year the activity started (DM 30 gennaio 2007 art. 1 c. 6), and
from 2026 also the average of the year before for an employer that grows
past 50, with at least 60 employees in 2026 and 2027 (c. 756 as in force
from 12 August 2026). Some workers are excluded whatever the size (DM art. 1
c. 8: fixed-term contracts under three months, home workers, agricultural
white collars insured with ENPAIA). State the outcome:

| `tfr_treasury_fund` | Account of the TFR | Blocker |
|---|---|---|
| `True` | `tfr_treasury_fund` | none |
| `False` | `tfr_accrual` | none |
| `None` | `tfr_accrual` | `missing_fact` `tfr_treasury_fund` on a run with a non-zero TFR outside a pension fund |

The amount and the employer cost are the same on both accounts. Domestic
employers and public administrations are outside the Fondo: `None` and
`False` keep the TFR in the company, `True` raises `InvalidInputError`. The
TFR a worker pays to a pension fund goes to `pension_fund_tfr` whatever the
fact says.

### Revaluation at 31 December

`tfr_fund` is a `TfrFundBalance(year, amount)`: the TFR the worker has with
the employer at 31 December of `year`, after that day's revaluation and
substitute tax and less the advances paid, including the part at the Fondo
Tesoreria and excluding the part at a pension fund. The December regular
run revalues it (art. 2120 c. 4 c.c.): the quota accrued in the year is
excluded, the rate is 1.5% plus 75% of the increase of the ISTAT FOI index
without tobacco from December to December (L. 81/1992 art. 4 c. 1; across a
change of index base the ratio is multiplied by ISTAT's link coefficient,
1.214 from base 2015 to base 2025). The revaluation bears a 17% substitute
tax charged to the fund (D.Lgs. 47/2000 art. 11 cc. 3-4).

The run records a `tfr_revaluation` decision:

| Reason | When | Amount |
|---|---|---|
| `revalued` | Fund of the year before stated, December index bundled | Revaluation; `substitute_tax` and `net_revaluation` in the inputs |
| `no_opening_fund` | A zero fund, or `tfr_fund=None` on an employment that starts in the year | `0` |
| `required_fact_missing` | `tfr_fund=None` on an employment that started before the year or is not tracked | `None`, `missing_fact` `tfr_fund` |
| `fund_of_another_year` | `tfr_fund.year` is not the year before the run | `None`, `missing_fact` `tfr_fund` |
| `price_index_not_published` | The bundle has no December index of the year | `None` |
| `termination_not_computed` | The run ends the employment before 31 December (art. 2120 c. 5: a fraction of the year) | `None` |
| `negative_rate` | The index fell enough to make the rate negative: no source says how it applies | `None` |

Every reason but the first two leaves the decision `incomplete` and the run
not payable. ISTAT publishes the December 2026 index in mid-January 2027:
until the bundle carries it, every December 2026 run with a fund to revalue
is blocked. The decision is not posted to the ledger: the revaluation
changes the fund, not the pay, the net or the employer cost of the run.

An employment that starts in the year is taken to have no fund. When it
carries a TFR over (a transfer of undertaking under art. 2112 c.c., or a
rehire whose TFR moved with the worker), state `tfr_fund` anyway.

The engine never outputs the fund. Carry it to the next year yourself:
`tfr_fund` of the next year = `tfr_fund` + `net_revaluation` + the
`tfr_accrual` and `tfr_treasury_fund` postings of the year - the advances
paid.

Not computed: the revaluation for a fraction of the year at termination,
the acconto of the substitute tax (90% by 16 December) and its saldo (16
February), the share of the revaluation the Fondo Tesoreria bears and the
employer recovers, and the TFR of public employees, which INPS manages:
`tfr_fund` is still required on their December runs.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent, TfrFundBalance

engine = PayrollEngine.bundled()
result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=12),
        payment_date=date(2026, 12, 23),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            contract_type=Permanent(),
            employment_period=EmploymentPeriod(date(2020, 1, 1)),
            tfr_fund=TfrFundBalance(2025, Decimal("15000.00")),
            tfr_treasury_fund=True,
        ),
        employer=EmployerProfile(headcount=Headcount(60)),
    )
)
(revaluation,) = (d for d in result.decisions if d.capability == "tfr_revaluation")
print(revaluation.reason_code)  # price_index_not_published until January 2027
```

## Bilateral funds (*fondi bilaterali*)

Many CCNLs require contributions to sector bilateral bodies (health funds,
training funds). The engine does not derive them from the CCNL: pass the
amounts due in the period as a `BilateralFundEvent`. The employee portion
reduces net pay; the employer portion increases employer cost. For the
pension fund of the CCNL use the enrolment described in
[Pension funds](#pension-funds-previdenza-complementare) instead.  A CCNL that
fixes its contribution per paid hour in the bundle (the Cas.Sa.Colf of the
CCNL lavoro domestico, see [Domestic work](domestic-work.md)) is charged by the
engine itself, on the same accounts, under the `assistance_contribution`
capability.

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
from ccnl_engine.inputs import Permanent

engine = PayrollEngine.bundled()

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            contract_type=Permanent(),
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

- `fund_code`: a fund of the CCNL, e.g. `"ALIFOND"` for Tabacco,
  `"FONCHIM"` for Vetro meccanizzato or `"FONTE"` for Commercio. A code the CCNL does not declare
  raises `InvalidInputError`.
- `employee_rate`: the contribution the worker chose. It cannot be below
  the CCNL minimum when the bundle records one (ALIFOND: 1%, Fon.Te.:
  0.55%).
- `tfr_to_fund`: whether the TFR accrued is paid to the fund. Required,
  with no default.

`pension_fund=NoPensionFund()` states that the worker is not enrolled: no
fund line is posted. On a CCNL that has a fund, the
`pension_fund_contribution` decision records the reason `not_enrolled` and
the capability is not applicable. `pension_fund=None`, the default, means
not known: on every CCNL but domestic work, whether or not the bundle holds
its negotiated fund, the decision is `incomplete` with the reason
`required_fact_missing`, no fund line is posted and the run has a
`missing_fact` blocker for `pension_fund`. The bundle holds the fund data of
thirteen CCNLs (Cometa for metalmeccanico Federmeccanica, Alifond for
tabacco and alimentari Federalimentare, Fondapi
for alimentari PMI, Fonchim for chimica farmaceutica and vetro
meccanizzato, Prevedi for edilizia industria and artigianato, and Fon.Te. for
commercio, turismo Confcommercio and Federalberghi, pubblici esercizi FIPE
and agenzie di viaggio FIAVET): an enrolment in the
fund of another CCNL raises `InvalidInputError`, since its rates are not in
the bundle. Whether the TFR of a worker who
expressed no choice goes to the fund (silent consent, D.Lgs. 252/2005 art.
8 c. 7) is for the caller to establish: the engine does not infer it.

When enrolled, each run posts:

| Line | Account | Amount | Effect |
|---|---|---|---|
| Employer contribution | `pension_fund_employer` | CCNL rate x fund base of the run | employer cost |
| Solidarity contribution | `employer_contributions` | 10% of the employer contribution | employer cost |
| Employee contribution | `pension_fund_employee` | chosen rate x fund base | withheld from net |
| TFR to the fund | `pension_fund_tfr` instead of `tfr_accrual` or `tfr_treasury_fund` | TFR of the run, net of the 0.50% additional IVS (L. 297/1982 art. 3 c. 16) | none: the cost does not change |

The rules behind it:

- **Base.** Each fund of `CCNL.parameters.employer_funds` names the base
  its rates apply to in `contribution_base`: `inps_base`, the default, is
  the INPS contribution base of the run, events included; `tfr_base` is
  the pay that enters the TFR of the run (the monthly pay, the benefits in
  kind and the events the TFR includes), the base of every fund in the
  bundle (Fon.Te., Alifond, Fondapi on the food PMI, Fonchim).
  Fonchim's employer rate includes the 0.25% the employer pays to the
  fund for the insurance of premorienza and invalidity.
  Overtime and bonuses enter the INPS base and not the TFR base.
- **Rates by contract.** A fund can charge apprentices another employer
  rate (`apprentice_rate`, used when `contract_type` is an `Apprentice`).
  Fon.Te. takes the rates of each CCNL from Allegato 1 of its nota
  informativa: 1.55% employer on Commercio (1.05% for apprentices), 0.55%
  on Turismo, Pubblici esercizi and Agenzie di viaggio; the worker pays at
  least 0.55% everywhere.
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

A CCNL can also owe its fund a fixed contribution a month for every
worker, enrolled or not (`CCNL.parameters.contractual_fund_contribution`,
an amount per level). The Materiali da costruzione CCNL (lapidei) owes
Fondapi 5 EUR "riparametrati su base 100": 6.80 EUR for level 5. It is an
employer contribution to the fund: posted to `pension_fund_employer` with
its 10% solidarity, within the deduction cap, on every run that pays the
month and on no extra-month run. A worker not enrolled has the decision
reason `contractual_only`; an enrolled one has it in the `contractual`
input, on top of the ordinary rates. The sources give no rule for a partial
month or part time: the run pays the full amount and has the open
limitation `contractual_fund_partial`.

The clause can carry the rules of its fund. Prevedi, on Edilizia industria
and artigianato, pays the impiegati and quadri 10 to 20.50 EUR a month by
level (apprentices 10), only for a month of at least 15 calendar days worked
(sickness and days without pay left out), in proportion to part time, on
the tredicesima and quattordicesima in proportion to their ratei, and not
for a fixed term of three months or less unless the worker pays voluntary
contributions (CNCE vademecum; accordo of 4 July 2025). The operai pay the
hourly amount of their level (0.0685 to 0.1027 EUR, apprentices 0.0700)
times `PeriodFacts.ordinary_hours_worked`, the ordinary hours actually
worked in the month, rounded to the euro, and nothing on an extra month:
an operaio qualificato of the industria with 160 hours owes 0.0801 x 160 =
12.82, 13 EUR. Without the hours the run has the issue
`contractual_fund_hours_unknown`; a level the table has no row for,
`contractual_fund_not_computed`; a level that leaves the category open,
`contractual_fund_category_unknown`.

Not modelled: the compensatory measures for employers whose TFR goes to a
fund (D.Lgs. 252/2005 art. 10), the extra deduction of workers first
employed from 2007 (art. 8 c. 6), a partial TFR conferment, and the eligibility
conditions some CCNLs set (e.g. ALIFOND excludes fixed-term contracts up
to six months). Fondapi on tessile PMI and metalmeccanico PMI computes on the contractual
minimum too; its base also counts the EDR (and, for the metalmeccanico, the
indennita di funzione of the quadri and the elemento of the 8th and 9th
categories), which the bundle pay lacks: an enrolled run has the open
limitation `fondapi_base_elements` and is not payable.

A fund can raise the employer rate with the rate the worker chooses
(`EmployerFund.employer_rate_tiers`): Fondapi on the chemical PMI pays
1.66% on the TFR base, 2.00% once the worker contributes at least 1.60%
(minimum 1.06%).

A fund due on the twelve monthly payments alone has
`EmployerFund.extra_months` false: an extra-month run of an enrolled worker
has a zero base. Byblos on the CCNL Esercizi cinematografici (art. 43: 1%
employer and 1% employee "per 12 mensilità annue") is one.

Byblos on the CCNL grafici editoriali pays the employer 1.9% of the TFR base
(the retribuzione contrattuale annua), 1.4% for a holder of the Elemento di
Raccordo Contrattuale (`EmployerFund.erc_holder_rate`), whose employer rate
the renewal of 19 January 2021 did not raise. State the annual ERC in
`Employment.erc_amount`, zero when the worker has none. Left `None`, an
enrolled run uses 1.9% and has the issue `pension_fund_erc_unknown`. The
same amount is paid with the tredicesima (see the extra months in the
engine overview).

Cometa computes on the contractual minimum of the level
(`contribution_base` `contractual_minimum`, the base salary of the pay
chain): employer 2%, employee at least 1.2%. A higher employee rate goes on
the TFR base (`employee_base_above_minimum`). A member enrolled after 5
February 2021 before turning 35 has an employer rate of 2.2%: state it in
`PensionFundEnrolment.young_member`. Left `None`, the run uses 2% and has
the issue `pension_fund_young_member_unknown`. The 40% TFR quota of a worker
employed before 28 April 1993 is not modelled.

```python
--8<-- "docs/examples/13_pension_fund.py"
```

**API reference:** [`Employment`](../api/engine.md),
[`WorkerCategory`](../api/engine.md)
