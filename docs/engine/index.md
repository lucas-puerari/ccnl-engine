# Engine

The engine takes a payroll scenario (the employment, the employer, the facts
of the run and the applicable rules) and returns a fully itemised
`PeriodResult`. It is a pure
function: given the same inputs and the same knowledge base version, it always
produces the same output.

## Entry point: `PayrollEngine`

Construct the engine with `PayrollEngine.bundled()` and call
`calculate_period()` for a single pay run or `calculate_year()` for a full
year:

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

engine = PayrollEngine.bundled()
employment = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
)
employer = EmployerProfile(headcount=Headcount(50))

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
    )
)
print(result.status)
print(result.period_gross)
print(result.period_net)
```

To add period-specific events (overtime, absences, benefits), pass them in
the `PeriodFacts` of the run:

```python
from ccnl_engine import PeriodFacts
from ccnl_engine.events import OvertimeEvent

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        employment=employment,
        employer=employer,
        facts=PeriodFacts(
            events=(
                OvertimeEvent(
                    event_date=date(2026, 1, 10),
                    hours=8,
                    hourly_rate=...,
                    multiplier=...,
                ),
            ),
        ),
    )
)
```

`calculate_period()` returns a `PeriodResult` with status, issues, decisions,
gross, net, pay items, the closing state and a full ledger of every
accounting entry. See [API: Engine](../api/engine.md).

## Tax year and payment date

`payment_date` is required on every `PeriodInput`. It selects the tax year
of the run (TUIR art. 51 c. 1, `TaxYearPolicy`), while the run year and month
keep selecting the contractual values (salary table, seniority, allowances):

| Payment of a December 2026 run | Tax year | Rule |
|---|---|---|
| any day of December 2026 | 2026 | cash |
| 1 to 12 January 2027 | 2026 | *cassa allargata* |
| 13 January 2027 or later in 2027 | 2027 | cash |
| June 2028 | 2028 | cash |

- The 12 January extension covers only runs of the previous year: December
  2025 paid on 10 January 2027 belongs to 2027.
- A payment before the first day of the run month raises `InvalidInputError`.
- There is no upper bound on the payment date. Separate taxation of arrears
  (TUIR art. 17) is not modelled.
- The tax tables, INPS rates, surtax tables and year-to-date state are those
  of the attributed tax year. A year the bundle does not ship (2027 today)
  raises `UnsupportedTaxYearError` with the year, instead of computing the
  run with the rules of another year.
- `opening_state.tax_year`, when set, must match the attributed tax year: a
  December 2026 run paid on 13 January 2027 does not close into the 2026
  state and raises `InvalidInputError`. Open the new year with
  `PayrollEngine.close_tax_year()` on the closing state of the last run of
  the previous year: it resets the year-to-date state and carries the
  obligations, such as an installment recovery. See
  [Payroll state and the year change](payroll-state.md).

## Full year: `calculate_year()`

`calculate_year()` runs every payslip of the year. The calendar is derived
from the CCNL `additional_months`: tredicesima in December and, when granted,
quattordicesima in June. The run sequence and the IRPEF withholding schedule
are both built from that calendar.

```python
from ccnl_engine import YearInput

commercio = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
year = engine.calculate_year(
    YearInput(year=2026, employment=commercio, employer=employer)
)
print(len(year.period_results))  # 14: 12 regular runs, tredicesima, quattordicesima
```

Each run takes its `PeriodFacts` from `YearInput.periods`, keyed by month
(1-12, the regular run of that month) or by run id (for example
`"2026-12-thirteenth"`), and otherwise from `default_facts`. An entry replaces
`default_facts` for its run, so repeat the region and the family in it, for
example with `dataclasses.replace(default_facts, events=...)`.
`default_facts` must carry no event. Naming a run twice (by month and by run
id) raises `InvalidInputError`. `year.closing_state` is the state after the
last run: pass it to `engine.close_tax_year()` to open the next year.

A different calendar is accepted only as a `CalendarOverride` with a
`CalendarOverrideReason` and a non-blank note. The override is checked
against the CCNL calendar and raises `InvalidInputError` when a rule fails:

| Reason | Allowed | Rejected |
|---|---|---|
| `PAYMENT_MONTH` | another payment month, e.g. quattordicesima in July | any change of the extra months or their fractions |
| `MORE_FAVOURABLE_TREATMENT` (art. 2077 c.c.) | adding an extra month or raising a fraction | an override that grants nothing more |

No reason allows dropping or lowering an extra month the CCNL grants. Every
extra month must accrue over the 12 months ending in its payment month
(`accrual_window_start_month == payment_month % 12 + 1`, which
`PayrollCalendar.from_additional_months` sets): any other window pays a
full-year worker less than the fraction, so a tredicesima stays in December. Paying
the ratei monthly (mensilizzazione) is not supported: the engine does not
pay ratei inside regular runs. The effective calendar and the override are
returned on the year result as `calendar` and `calendar_override`.

Every run is paid on `payment_day` of its own month, 28 by default. Any day
from 1 to 28 is accepted, so every payment falls in the requested year and
every run belongs to that tax year; another day raises `InvalidInputError`.

```python
tenth = engine.calculate_year(
    YearInput(year=2026, employment=commercio, employer=employer, payment_day=10)
)
print(tenth.period_results[0].payment_date)  # 2026-01-10
```

### Employment period

`Employment.employment_period` selects the runs of the year:

- a regular run for every month with at least one employed day;
- an extra-month run only when its payment month is such a month, so a
  worker employed from July to September has no tredicesima or
  quattordicesima run;
- one IRPEF withholding slot per selected run, so the conguaglio settles on
  the last run of the employment;
- an employment with no day in the year raises `InvalidInputError`.

A month the employment covers only in part (hire on the 15th, end before the
last day) keeps its run and the full monthly pay: the bundled CCNL data
define no daily divisor, so the engine does not choose between calendar-day
and 26ths proration. The run carries a `partial_month_not_prorated` issue and
its status is `PROVISIONAL`.

Extra months accrue per qualifying month of their window, counted from the
employment dates and never from the runs already closed:

- the 12-month window ends in the payment month and starts at the hire date
  when the worker was hired inside it (hire on 15 March: the June
  quattordicesima accrues March to June, 4/12);
- a month qualifies when it has at least 15 accruing calendar days. This is
  an engine default, not read from the CCNL files, which carry no accrual
  threshold and no clause text to check it against. CCNLs word it
  differently: Metalmeccanico industria (Federmeccanica-Assistal), art. 7
  "Tredicesima mensilità", reads "La frazione di mese superiore a 15 giorni
  va considerata a questi effetti come mese intero" (text as published by
  contrattometalmeccanici.it, not the signed agreement), so a month of
  exactly 15 days does not accrue there and the engine counts it. The
  default is kept until the threshold is carried per CCNL in the data, with
  the signed text as source; a caller building the `ExtraMonthAccrual` of a
  `calculate_period` request can pass `MonthAccrualRule(min_days=16)` for
  the stricter reading;
- an `AbsenceEvent` with `suspends_accrual=True` (for example aspettativa non
  retribuita) removes its calendar days from every window. The caller says
  which absences suspend accrual; an ordinary unpaid absence reduces pay,
  not the ratei. Absences of the previous year are not known, and a single
  `calculate_period()` call on an extra-month run counts from the employment dates
  only;
- when the employment ends before an extra month's payment month, the ratei
  accrued up to the termination are paid on the last regular run as
  `extra_month_earning` items (ordinary IRPEF, INPS and TFR base). A
  quattordicesima whose June run was already paid restarts in July, so an
  end in September liquidates 3/12 of the next one.

The work deduction (art. 13 TUIR), the ulteriore detrazione (L. 207/2024
art. 1 c. 6) and the trattamento integrativo are proportioned to the days of
employment in the tax year, at most 365.

CCNL and level validity does not drop runs: a month the salary table does not
cover fails in the salary lookup.

```python
from datetime import date

from ccnl_engine import EmploymentPeriod

short = engine.calculate_year(
    YearInput(
        year=2026,
        employment=Employment(
            ccnl_slug="commercio-confcommercio.json",
            level_code="4",
            employment_period=EmploymentPeriod(date(2026, 7, 1), date(2026, 9, 30)),
        ),
        employer=employer,
    )
)
print(len(short.period_results))  # 3: July, August, September
print(short.annual_gross)  # 6243.15: three months plus 3/12 of each extra month
```

```python
from ccnl_engine import CalendarOverride, CalendarOverrideReason, PayrollCalendar

july = CalendarOverride(
    calendar=PayrollCalendar.from_additional_months(
        2026, 14, fourteenth_payment_month=7
    ),
    reason=CalendarOverrideReason.PAYMENT_MONTH,
    note="quattordicesima paid with the July salary",
)
```

## Computation chain

The engine applies rules in a fixed sequence:

```
1. Resolve time-series values (base salary, seniority amounts, hourly divisor)
   ↓
2. Apply part-time coefficient and apprenticeship percentage
   ↓
3. Add fixed allowances
   ↓
4. Compute INPS contributions (employee + employer, NASpI addizionale if fixed-term)
   ↓
5. Compute TFR accrual (Art. 2120 c.c.)
   ↓
6. Compute employer contractual funds
   ↓
7. Compute IRPEF: bracket tax → work-income deduction → trattamento integrativo
   ↓
8. Apply regional + municipal surtax (when jurisdiction is provided)
   ↓
9. Apply Art. 12 family deductions and Art. 15 mortgage interest deduction
   (reduce irpef_net / net_annual; only when inputs are provided)
   ↓
10. Compute L3 work-rules supplements (informational — do not mutate gross/net):
    overtime pay, absence deduction, leave accrual, sick-pay integration,
    fringe benefits, welfare, PdR bonus
    ↓
11. Assemble PeriodResult: gross, net, employer cost, status, issues,
    decisions, capability report
```

Steps 7–9 are fiscal and can be parameterised heavily. See
[Fiscal](fiscal.md) for the full reference. Step 10 is optional — see
[Work rules](work-rules.md).

## Input types

| Type | What it describes |
|---|---|
| `PeriodInput` | One run: `PayrollRun`, payment date, employment, employer, facts of the run, prior-year facts, opening state |
| `YearInput` | Every run of a tax year: employment, employer, prior-year facts, `periods` and `default_facts`, calendar override, payment day, opening state |
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, `WeeklyHours`, `SeniorityMonths`, roles, IVS ceiling status and sector; impossible values are rejected on construction |
| `EmployerProfile` | The employer: its `Headcount` (required, at least 1) selects the INPS rate tier; `activity` feeds the L. 199/2025 c. 18 exclusion |
| `PriorYearTaxFacts` | Prior-year employment income and written waivers, declared once and read by every substitute-tax regime |
| `PeriodFacts` | Events, contributable hours, region and Belfiore code, family composition of one run |
| `PayrollRun` | The pay run: year, month, and run kind (regular / thirteenth / fourteenth) |
| `FamilyComposition` | Dependent spouse and children (Art. 12 TUIR) |
| `OvertimeEvent` | Overtime hours for a specific date |
| `AbsenceEvent` | Unpaid absence in the period; `suspends_accrual` also stops the extra-month ratei |
| `SickLeaveEvent` | Sick-leave calendar days |
| `FringeEvent` | Fringe-benefit value and threshold flag |
| `WelfareEvent` | Welfare benefit annual amount |
| `BonusEvent` | Bonus amount and kind (ordinary, PdR, contract renewal with its signing date) |

Full type reference: [API: Engine](../api/engine.md).

## Output: `PeriodResult`

The result contains every gross, net, and cost component. Key fields:

```python
result.status               # final, provisional, incomplete or rejected
result.issues               # conditions that lowered the status
result.decisions            # what each capability decided, with its inputs
result.period_gross         # gross entitlement for the period (before absence deductions)
result.period_net           # net pay for this period
result.period_employer_cost # total employer cost (gross + contributions + TFR accrual)
result.unpaid_absence_deduction  # wages withheld for unpaid absences
result.closing_state        # tax year state and obligations: opening_state of the next run
result.pay_items            # all pay items produced
result.ledger_entries       # full accounting ledger
result.capability_report    # what the run executed against the capability catalog
```

`YearResult` sums the runs (`annual_gross`, `annual_net`,
`annual_employer_cost`), keeps every `PeriodResult` in `period_results` and
exposes the worst `status`, the `issues` and `decisions` of its runs and the
`closing_state` of the last run. See [Trust: Confidence](../trust/confidence.md)
for how the status is derived.

## Guides

| Page | Contents |
|---|---|
| [Pay components](pay-components.md) | Part-time, seniority, RAL overrides |
| [Second level](second-level.md) | Second-level agreements: what the engine does not take as input |
| [Fiscal](fiscal.md) | IRPEF, surtax, family and Art. 15 deductions |
| [Domestic work](domestic-work.md) | Flat per-hour contributions, non-withholding employer |
| [Work rules](work-rules.md) | L3: overtime, absence, leave, sickness, bonus, welfare |
