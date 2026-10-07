# Engine

The engine takes a payroll scenario (the employment, the employer, the facts
of the run and the applicable rules) and returns a fully itemised
`PeriodResult`. It is a pure
function: given the same inputs and the same knowledge base version, it always
produces the same output.

## Entry point: `PayrollEngine`

Construct the engine with `PayrollEngine.bundled()` and call
`calculate_period()` for a single pay run or `calculate_competence_year()` for a full
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
print(result.is_payable, [blocker.code.value for blocker in result.blockers])
print(result.period_gross)
print(result.period_net)
```

To add period-specific events (overtime, absences, benefits), pass them in
the `PeriodFacts` of the run:

```python
from decimal import Decimal

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
                    hours=Decimal(8),
                    hourly_rate=...,
                    # multiplier omitted: 1 + the CCNL weekday band
                ),
            ),
        ),
    )
)
```

`calculate_period()` returns a `PeriodResult` with its assurance, issues, decisions,
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
- A CCNL rule the run needs with no value on the competence date (the date
  precedes the first tranche of the bundle, or falls in a gap the data
  declares, such as the seniority amounts of `grafica-editoria-aieg` before
  July 2026) raises `MissingRuleError` with the CCNL (`ruleset`), the
  `feature`, the date (`as_of`), the declared `gap_kind` and a
  `remediation`. A rule is read only when it pays something: a worker with
  no seniority increment due is computed even where the increment amounts
  are missing.
- `opening_state.tax_year`, when set, must match the attributed tax year: a
  December 2026 run paid on 13 January 2027 does not close into the 2026
  state and raises `InvalidInputError`. Open the new year with
  `PayrollEngine.close_tax_year()` on the closing state of the last run of
  the previous year: it resets the tax cash state and carries the
  obligations, such as an installment recovery, and the competence runs
  already closed. See
  [Payroll state and the year change](payroll-state.md).
- `opening_state` holds the history of the employment: the zero state is
  the fact only for the first run of an employment whose start is stated,
  and the INPS base of the worker's other employments is a fact too; a run
  without them is not payable. See
  [Opening state and imported balances](opening-state.md).

## Full year: `calculate_competence_year()`

`calculate_competence_year()` runs every payslip of a competence year. The
calendar is derived from the CCNL `additional_months`: tredicesima in
December and, when granted, quattordicesima in June. The runs follow from
that calendar; the IRPEF withholding schedule follows from the payments
actually made in each tax year, so a December paid after 12 January settles
the conguaglio of the year on its tredicesima and opens the next tax year
(see [Payroll state](payroll-state.md#competence-and-tax-year-plans)).
`calculate_tax_year(TaxYearPlan(...))` computes every payment of one tax
year instead, late payments of an earlier competence year included.

```python
from ccnl_engine import CompetenceYearPlan

commercio = Employment(ccnl_slug="commercio-confcommercio.json", level_code="4")
year = engine.calculate_competence_year(
    CompetenceYearPlan(year=2026, employment=commercio, employer=employer)
)
print(len(year.period_results))  # 14: 12 regular runs, tredicesima, quattordicesima
```

Each run takes its `PeriodFacts` from `CompetenceYearPlan.periods`, keyed by month
(1-12, the regular run of that month) or by run id (for example
`"2026-12-thirteenth"`), and otherwise from `default_facts`. An entry replaces
`default_facts` for its run, so repeat the region and the family in it, for
example with `dataclasses.replace(default_facts, events=...)`.
`default_facts` must carry no event. Naming a run twice (by month and by run
id) raises `InvalidInputError`. `year.closing_state` is the state after the
last run; `year.next_opening_state` opens the next competence year.

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
`WorkCalendar.from_additional_months` sets): any other window pays a
full-year worker less than the fraction, so a tredicesima stays in December. Paying
the ratei monthly (mensilizzazione) is not supported: the engine does not
pay ratei inside regular runs. The effective calendar and the override are
returned on the year result as `calendar` and `calendar_override`.

Every run is paid on `payment_day` of its own month, 28 by default; any day
from 1 to 28 is accepted, another raises `InvalidInputError`.
`payment_dates` names the date of a run, keyed like `periods`: an employer
that pays in arrears pays each month on the 10th of the next one and may pay
the extra months before the salary of their month. A date before the first
day of its run month, or of a run the year does not compute, is rejected.

```python
tenth = engine.calculate_competence_year(
    CompetenceYearPlan(year=2026, employment=commercio, employer=employer, payment_day=10)
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
last day) keeps its run and pays the daily quotas of its employed days, in
`calculate_period` and in the year plans alike. The quota is the one the CCNL
sets for unpaid absences, `work_rules.absence_rules.daily_divisor_method`,
with its provenance:

- `by_26`: one twenty-sixth per employed Monday to Saturday (Sundays are not
  paid days, a public holiday on a weekday is);
- `by_30`: one thirtieth per day of a 30-day commercial month (a span to the
  month end runs to day 30, day 31 counts as day 30);
- `by_hourly`: `daily_hours / hourly_divisor` per employed Monday to Friday.

Each pay component is prorated and rounded on its own, after the part-time
ratio, and never above one monthly pay (2 March 2026, a Monday after a
Sunday 1st, pays the whole of March). The `base_salary` decision has reason
`pay_chain_prorated` and records `employed_from`, `employed_until`,
`divisor_method`, `payable_days` and `divisor`; the absence rule and, for
`by_hourly`, the hourly divisor join the rules of `base_salary`.

The monthly pay of a competence month is posted once, by the run that
closes the month first. The regular run posts it. A termination run posts
it, prorated the same way, only when the regular run of its month is not
closed in the opening state (a termination closes the competence year, so
no regular run of the month can follow it); after the regular run it posts
no monthly pay, only its own items (events, TFR, the second conguaglio). An
adjustment run corrects a run already closed and never posts the monthly
pay. A run that posts none has a `base_salary` decision with reason
`monthly_pay_posted_by_another_run`, amount 0.00 and input
`monthly_pay_posted_by` (the regular run id, or `corrected_run`).
Extra-month runs follow the accrual rule below.

A CCNL whose data define no daily quota (no `absence_rules`, or `by_hourly`
without `daily_hours` or an hourly divisor in force) never pays the month in
full: the run posts no pay, the `base_salary` decision is `provisional` with
reason `partial_month_rule_missing` and no amount, and the
`partial_month_rule_missing` issue (`incomplete`) makes it not payable.

Extra months accrue per qualifying month of their window, counted from the
employment dates and never from the runs already closed:

- the 12-month window ends in the payment month and starts at the hire date
  when the worker was hired inside it (hire on 15 March: the June
  quattordicesima accrues March to June, 4/12);
- a month qualifies when its accruing calendar days pass the CCNL accrual
  rule, `parameters.accrual_rule`: a threshold (`min_days`) and a
  comparison, `more_than` ("la frazione di mese superiore a 15 giorni va
  considerata come mese intero", Metalmeccanico Federmeccanica, sez.
  quarta, titolo IV, art. 7) or `at_least` ("superiori o uguali a 15
  giorni", Terziario Confcommercio, art. 204). The rule is stored only for
  the 40 CCNLs whose signed text was read, with the article and the quote
  (status `assumed` until a named reviewer checks it). The other CCNLs use
  the engine default, at least 15 days, recorded as a `missing` rule: a run
  whose window has a partly accrued month then adds `rule_source_missing`
  and is `incomplete`; a window of whole months does not read the rule.
  Each rateo paid records a `base_salary` decision `extra_month_ratei_counted`
  with the months, the partly accrued months, the threshold, the comparison
  and whether the rule is the CCNL clause (`ccnl`), the default
  (`engine_default`) or one the caller built (`request`). A caller building
  the `ExtraMonthAccrual` of a `calculate_period` request can pass its own
  `MonthAccrualRule(min_days=15, comparison=AccrualComparison.MORE_THAN)`
  (from `ccnl_engine.payroll.domain.accrual` and
  `ccnl_engine.contract.domain.compensation`);
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

from ccnl_engine.inputs import EmploymentPeriod

short = engine.calculate_competence_year(
    CompetenceYearPlan(
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
from ccnl_engine.inputs import CalendarOverride, CalendarOverrideReason, WorkCalendar

july = CalendarOverride(
    calendar=WorkCalendar.from_additional_months(
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
2. Apply apprenticeship percentage (base and allowances flagged
   apprenticeship_pct_relevant; the apprentice seniority amount is paid in
   full), then part-time coefficient
   ↓
3. Add fixed allowances
   ↓
4. Compute INPS contributions (employee + employer, NASpI addizionale if fixed-term)
   ↓
5. Compute TFR accrual (Art. 2120 c.c.), less the 0.50% additional IVS
   (L. 297/1982 art. 3 c. 16), to the company, the Fondo Tesoreria or
   the pension fund; on the December run, decide the revaluation of the
   fund at 31 December (art. 2120 c. 4 c.c.)
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
10. Compute L3 work-rules supplements (informational, do not mutate gross/net):
    overtime pay, absence deduction, leave accrual, sick-pay integration,
    fringe benefits, welfare, PdR bonus
    ↓
11. Assemble PeriodResult: gross, net, employer cost, issues, decisions,
    capability report, rulesets; the assurance is derived from them
```

Steps 7–9 are fiscal and can be parameterised heavily. See
[Fiscal](fiscal.md) for the full reference. Step 10 is optional; see
[Work rules](work-rules.md).

## Input types

| Type | What it describes |
|---|---|
| `PeriodInput` | One run: `PayrollRun`, payment date, employment, employer, facts of the run, prior-year facts, opening state |
| `CompetenceYearPlan` | Every run of a competence year: employment, employer, prior-year facts, `periods` and `default_facts`, calendar override, payment day and `payment_dates`, opening state |
| `TaxYearPlan` | Every payment of a tax year: the competence years whose runs are paid in it and the opening state |
| `OpeningBalances` | Totals, payments, competence runs and INPS bases of another provider, imported with `engine.import_opening_balances()` |
| `Employment` | CCNL slug, level, contract type, category, `EmploymentPeriod`, `WeeklyHours`, `SeniorityFact`, roles, `ContributionHistory` and sector; impossible values are rejected on construction |
| `EmployerProfile` | The employer: its `Headcount` (required, at least 1) selects the INPS rate tier; `activity` feeds the L. 199/2025 c. 18 exclusion |
| `PriorYearTaxFacts` | Prior-year employment income and written waivers, declared once and read by every substitute-tax regime |
| `CurrentYearTaxFacts` | Income of the tax year beyond this employment (other employers, other income, main dwelling excluded), its date and quality; read by the Art. 12 family deductions on `PeriodInput.current_year`, `CompetenceYearPlan.current_year` or `TaxYearPlan.current_year` |
| `PeriodFacts` | Events, contributable hours, region and Belfiore code, family composition of one run |
| `PayrollRun` | The pay run: year, month, and run kind (regular / thirteenth / fourteenth) |
| `FamilyComposition` | Dependent spouse, children and ascendants (Art. 12 TUIR), each with its dependency interval and its conditions (`None` unknown, never met); `sole_parent` for the first-child rule |
| `OvertimeEvent` | Overtime hours for a specific date |
| `AbsenceEvent` | Unpaid absence in the period; `suspends_accrual` also stops the extra-month ratei |
| `SicknessEpisode` | Sickness episode; the engine pays its days in each month it touches |
| `SickLeaveEvent` | Sick pay computed by the caller: an override, never payable |
| `FringeEvent` | Fringe-benefit value; the annual threshold follows the children of `PeriodFacts.family_composition` |
| `WelfareEvent` | Welfare benefit annual amount |
| `BonusEvent` | Bonus amount and kind (ordinary, PdR, contract renewal with its signing date) |

Full type reference: [API: Engine](../api/engine.md).

## Output: `PeriodResult`

The result contains every gross, net, and cost component. Key fields:

```python
result.is_payable           # whether the amounts can be paid as computed
result.blockers             # every reason they cannot: code, feature, detail
result.assurance            # calculation, coverage, evidence, rulesets, mode, payability
result.rulesets             # rulesets read, with id, hash, kind and readiness
result.mode                 # simulation (default) or operational
result.issues               # conditions that lowered the calculation axis
result.decisions            # what each capability decided, with its inputs
result.period_gross         # gross entitlement for the period (before absence deductions)
result.period_net           # net pay for this period
result.period_employer_cost # total employer cost (gross + contributions + TFR accrual)
result.unpaid_absence_deduction  # wages withheld for unpaid absences
result.closing_state        # accrual and tax cash state: opening_state of the next run
result.pay_items            # all pay items produced
result.ledger_entries       # full accounting ledger
result.capability_report    # what the run executed against the capability registry
```

`CompetenceYearResult` and `TaxYearResult` sum the runs (`annual_gross`,
`annual_net`, `annual_employer_cost`), keep every `PeriodResult` in
`period_results` and expose the combined `assurance` (and `is_payable`,
`blockers`, `rulesets`), the `issues` and `decisions` of their runs, the
`closing_state` of the last run, the payments that settled a conguaglio
(`conguagli`) and the `next_opening_state`. `TaxYearResult` also lists the
`payments` of the tax year and its `conguaglio`. See [Trust: Assurance](../trust/confidence.md) for how the assurance is
derived.

## Guides

| Page | Contents |
|---|---|
| [Pay components](pay-components.md) | Part-time, seniority, RAL overrides |
| [Second level](second-level.md) | Second-level agreements: what the engine does not take as input |
| [Fiscal](fiscal.md) | IRPEF, family and Art. 15 deductions |
| [Surtax](surtax.md) | Regional and municipal surcharges, their tables and decisions |
| [Tax credits](tax-credits.md) | Ulteriore detrazione and trattamento integrativo decisions |
| [Domestic work](domestic-work.md) | Flat per-hour contributions, non-withholding employer |
| [Work rules](work-rules.md) | L3: overtime, absence, leave, sickness, bonus, welfare |
