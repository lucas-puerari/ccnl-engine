# Work rules (L3)

Variable work data for a payroll run (overtime, absences, sick leave,
supplements, benefits, bonuses) is passed as work events in
`PeriodFacts.events`: on `PeriodInput.facts` for one run, or in
`CompetenceYearPlan.periods` keyed by month or by run id for a year. Events are part
of the run and change the
result according to the treatment in the table below. For example, overtime
raises `period_gross`; an unpaid absence is reported in
`unpaid_absence_deduction`; a bilateral fund contribution changes only
`period_net` and `period_employer_cost`. Each event appears as pay items in
`result.pay_items`.

Import event types from the `ccnl_engine` package, like every other public name.

```python
--8<-- "docs/examples/event/example.py"
```

---

## Event types

All events are frozen dataclasses. Every event carries an `event_date`;
amounts are `Decimal` values in EUR, validated on construction.

| Event | Fields | Treatment |
|---|---|---|
| `OvertimeEvent` | `hours`, `hourly_rate` (default `None`: the CCNL hourly base), `multiplier` (default `None`: from the CCNL band), `kind` (`OvertimeKind`, default `WEEKDAY`) | Pay `hours × hourly_rate × multiplier`; subject to INPS, IRPEF and TFR |
| `NightShiftEvent` | `supplement_amount` or `hours` | Night-work supplement; INPS and IRPEF |
| `HolidayWorkEvent` | `supplement_amount` or `hours`, `kind` (`HolidayWorkKind`, default `HOLIDAY`) | Public holiday, Sunday or weekly rest-day supplement; INPS and IRPEF, no TFR |
| `ShiftWorkEvent` | `supplement_amount` or `hours` and `kind` (`ShiftKind`) | Shift allowance; INPS and IRPEF, no TFR |
| `AbsenceEvent` | `hours`, `hourly_rate` (default `None`: the CCNL quota), `working_days`, `end_date`, `suspends_accrual` | Unpaid absence deducted from pay; reduces the INPS and TFR base |
| `SicknessEpisode` | `episode_id`, `started_on`, `ended_on`, `relapse_of`, `prior_worked_days` (fixed-term), `hospital_stays`, `serious_illness` | Sickness episode; the engine derives the deduction, INPS indemnity, CCNL integration and carenza pay of the days in the run's month; see [Sickness](#sickness) |
| `MaternityLeaveEvent` | `started_on`, `ended_on` | Compulsory maternity leave; the engine derives the deduction, the INPS indemnity it advances and the CCNL top-up of the days in the run's month; see [Maternity leave and work injury](#maternity-leave-and-work-injury) |
| `WorkInjuryEvent` | `injury_on`, `ended_on` | Temporary inability after a work injury; the engine derives the deduction, the waiting period, the INAIL indemnity (advanced or not) and the CCNL top-up; see [Maternity leave and work injury](#maternity-leave-and-work-injury) |
| `SickLeaveEvent` | `amount`, `sick_days`, `waiting_period_days` | Sick pay the caller computed: an override of the engine, never payable; INPS and IRPEF, no TFR |
| `FringeEvent` | `amount` | Fringe benefit (art. 51 c. 3 TUIR); exempt while the year total stays within the threshold, then the whole year total is taxable; see [Fringe benefits](#fringe-benefits) |
| `WelfareEvent` | `amount` | Welfare benefit; exempt from INPS and IRPEF, no TFR |
| `TravelAllowanceEvent` | `days`, `outside_municipality`, `meals_lodging` (required), `daily_amount` or `hours_away`, `tfr_base`, `abroad` | Daily travel allowance (indennità di trasferta), paid in cash; outside the comune exempt from IRPEF and INPS up to 46.48 a day (77.47 abroad), reduced by one third or two thirds when meals or lodging are reimbursed or provided (art. 51 c. 5 TUIR, art. 12 c. 2 L. 153/1969); within the comune income in full. Without `daily_amount` the CCNL `work_rules.travel_allowance` amount of the span of `hours_away` is paid (Logistica travelling staff, art. 62). The TFR base takes nothing, the whole, or the part above the exemption, as `tfr_base` or the CCNL says; a `trasfertista` (art. 51 c. 6) is rejected |
| `StandbyEvent` | `kind` (`StandbyKind`: hours, worked day, rest day, holiday, week, week with holiday, week with holiday and rest day), `quantity`, `calls` | Standby pay (reperibilità) at the CCNL `work_rules.standby_rules` rates of the worker's level band in force on the event date, plus the CCNL fee per call with an intervention; income for IRPEF and INPS; TFR as the CCNL rules say (Federmeccanica: excluded). A CCNL or a date without rates rejects the event (`MissingRuleError`) |
| `BonusEvent` | `amount`, `kind`, `agreement_signed_on` | One-off bonus; `kind` selects ordinary IRPEF, the PdR regime or the renewal regime |
| `BilateralFundEvent` | `employee_amount`, `employer_amount` | Bilateral or health fund contribution; see [Pay components](pay-components.md#bilateral-funds-fondi-bilaterali) |
| `ArrearsEvent` | `amount`, `separate_tax_rate`, `reference_period` | Renewal arrears; see [Renewal arrears](#renewal-arrears) |
| `TerminationTFREvent` | `amount`, `separate_tax_rate` (both optional) | TFR settlement at cessazione (art. 19 TUIR); see [TFR settlement](pay-components.md#settlement-at-the-termination) |
| `LeaveTakenEvent` | `bucket` (`LeaveBucket`: `ferie`, `rol`, `ex_festivita`), `quantity` (days of ferie, hours of a permit) | Paid leave taken: no pay of its own (the monthly pay holds it), it consumes the balance of its bucket; see [Paid leave](#paid-leave-ferie-rol-and-ex-festivita) |

### Overtime multiplier

D.Lgs. 66/2003 art. 5 c. 5 leaves the overtime supplement to the CCNL and
sets no statutory rate, so the engine has no default multiplier.

| `multiplier` | CCNL band of `kind` | Paid with | Decision and status |
|---|---|---|---|
| `None` | present | `1 + band` | `overtime` decision `ccnl_overtime_band_applied`, origin `engine`, citing the band and its source |
| `None` | absent | nothing: `InvalidInputError` | the run is rejected; pass an explicit multiplier |
| explicit | equal to a band | the caller's value | `caller_supplied` decision only |
| explicit | different | the caller's value | `caller_supplied` decision and a `provisional` issue `caller_multiplier_differs_from_ccnl` with both values |
| explicit | absent | the caller's value | `caller_supplied` decision only |

A caller-supplied multiplier, matching a band or not, is a
`caller_supplied_rule` blocker: the result is not payable until the value is
validated outside the engine.

`kind` selects the band: `WEEKDAY` (straordinario diurno), `NIGHT`,
`HOLIDAY`, `REST_DAY` or `NIGHT_HOLIDAY`, matched against the
`applies_to_kinds` of the CCNL `work_rules.time_supplements.overtime_bands`.
`REST_DAY` is overtime on the weekly rest day for the CCNLs that pay it apart
from the public holidays (Logistica travelling staff, art. 13 c. 6: 30% on
Saturday and Sunday, 65% on the festività); a CCNL without a `rest_day` band
pays it with its `HOLIDAY` band. The band used is the
first tier: the percentage band with code `OT_*` that has no hour threshold
and no context condition. When the CCNL also has bands that start beyond a
daily or weekly hour threshold (commercio: 15% up to 48 weekly hours, 20%
beyond; metalmeccanico: 25% for the first two hours, 30% beyond), the event does not carry the hours of the week, so the first tier
is applied to every hour and the run is `provisional` with issue
`overtime_tier_not_applied`: pass an explicit multiplier for the hours
beyond the threshold (a multiplier equal to a higher tier raises no
difference issue). A CCNL whose bands for the kind all start beyond a
threshold, or are not in force on the event date gives no multiplier. A
kind with no percentage band but a band in EUR per hour (`indennita_per_hour`:
the PA tables of fixed hourly amounts, e.g. the scuola ATA Tabella E1.7) is
paid that amount for each hour in place of `hourly_rate`, with multiplier 1.
A band that lists `levels` applies only to those levels. The derived band is a payable rule of `overtime`: its
provenance status is reported in `capability_report.rule_sources`.

```python
from datetime import date
from decimal import Decimal

from ccnl_engine.events import OvertimeEvent, OvertimeKind

# Metalmeccanico OT_NOTTURNO 50%: 2 h x 15.00 EUR x 1.50 = 45.00 EUR.
night = OvertimeEvent(
    date(2026, 3, 10), Decimal(2), Decimal("15.00"), kind=OvertimeKind.NIGHT
)
# Without hourly_rate: 2 h x the CCNL hourly base x 1.50.
derived = OvertimeEvent(date(2026, 3, 10), Decimal(2), kind=OvertimeKind.NIGHT)
```

### Hourly rate, supplements and absence quota from the CCNL

Without `OvertimeEvent.hourly_rate`, the `supplement_amount` of a night,
holiday or shift event or `AbsenceEvent.hourly_rate`, the engine derives
the value from the CCNL, only from a rule whose source is verified:

| Value | Derived as | Rule |
|---|---|---|
| Hourly base | monthly pay elements of `hourly_base_method` / `parameters.hourly_divisor` in force on the event date | `work_rules.time_supplements.hourly_base_method`, read only when `hourly_base_provenance` is `verified` |
| Overtime hourly rate | the hourly base | decision `ccnl_hourly_rate_derived` |
| Night, holiday, Sunday, rest-day, shift supplement | `rate × hours × hourly base` (the band's own `base` when it names one) | the `supplement_bands` band of the event's work, level and role; decision `ccnl_supplement_applied` |
| Absence | `hours × hourly base` (`by_hourly`), `working_days × monthly / 26` (`by_26`; also 22 and 30) | `work_rules.absence_rules`, only when `verified`; decision `ccnl_absence_quota_applied` |

`hourly_base_method` names the elements of the worker's full-time monthly
pay (the CCNL divisor is a full-time divisor; an apprentice's chain is
reduced by the percentage): `minimo_tabellare` (base salary),
`minimo_e_anzianita` (base salary and seniority, chimica art. 15 punto 1)
or `gross_incl_allowances` (base salary, seniority and every fixed
allowance paid in cash). Individual elements (`Employment.individual_elements`: superminimi,
merito, assegni ad personam) are not in the hourly base: every derived
decision reports `individual_elements: not_included`, and a worker whose
CCNL counts them states the rate. A CCNL that sets `hourly_divisor_weekly_hours` (Turismo, Pubblici
Esercizi, Terziario: 40) derives nothing for an employment whose stated
full-time week differs, whose divisor is not modelled.

A supplement band (`SupplementBand`) pays one work (`night`, `holiday`,
`holiday_compensatory_rest`, `sunday`, `rest_day`, `day_shift`,
`night_shift`), may be reserved to levels or to a role of
`Employment.roles` (Turismo `qualifica_notturna`, 12%; Terziario
`impianto_carburante_autostradale`, 10% on Sundays); with role bands the
roles must be stated. The engine posts the maggiorazione only. A band
whose CCNL also pays the hours themselves on top of the monthly pay
(`hours_paid_apart: true`, e.g. Turismo art. 220) or whose text does not
settle it (`null`, chimica and metalmeccanici) makes the run `provisional`
with issue `supplement_hours_not_posted`: those hours are ordinary pay the
engine does not post.

The 8 pilot CCNLs carry the data; each lists in its coverage note "HOURLY
RATE AND SUPPLEMENTS" what is derived and what stays the caller's:

| CCNL | Night | Holiday | Other | Absence |
|---|---|---|---|---|
| chimica-farmaceutica-federchimica | caller (company window) | 50% | day shift 4% | caller (rule derived) |
| turismo-federalberghi | 25% (12% role) | 20% | | 1/26 |
| pubblici-esercizi-fipe-angem | 25% | 20% | Sunday 10% on paga base and contingenza | 1/26 |
| terziario-confesercenti, commercio-confcommercio | 15% | 30% | Sunday 30% (10% role), rest day 30% | 1/26 |
| metalmeccanico-confapi | caller (window, shift column) | 55% | compensatory rest 10% | caller (rule derived) |
| metalmeccanico-federmeccanica | caller (window, shift column) | 50% | compensatory rest 10% | caller (rule derived) |
| studi-professionali-confprofessioni | caller (unconfirmed) | 30% | | 1/26 |

Where the CCNL sets no value the engine applies, the event is rejected
with `InvalidInputError` naming the field and the reason. A value the
caller states is applied as given and reported as a `caller_supplied`
decision listing only the fields the caller stated. The
`separate_tax_rate` of arrears comes from the caller; the TFR settlement is
computed by the engine, its payout and rate are optional overrides.

### Sickness

A `SicknessEpisode` is one illness: a stable `episode_id`, the first and
last day on the certificates and, for a relapse (*ricaduta*), the
`relapse_of` id of the episode it continues. Pass the same episode, same id
and start, to every regular run whose month it touches; a later run may
extend `ended_on`. Only the run that posts the monthly pay of its month
(a regular run, or a termination run when the regular run is not closed)
accepts an episode, so no day is paid twice.

Each calendar day has an index in the episode, counted on from the episode
it continues for a relapse. The index sets:

| Days | INPS (INPS page on the sickness indemnity) | Worker receives |
|---|---|---|
| 1-3 (carenza) | nothing | CCNL `carenza_integration_rate`, only past `carenza_min_days` of sickness when the CCNL sets it |
| 4-20 | 50% | the higher of the CCNL tier rate and the INPS rate |
| 21-180 | 66.66% | the same |
| past the comporto | left out, `incomplete` issue | left out |

A fixed-term contract pays sickness for no more days than those of work in
the 12 months before the episode, every employer counted
(`SicknessEpisode.prior_worked_days`, D.L. 463/1983 art. 5 c. 1); with 30
days or fewer, for at most 30 days in the calendar year, the INPS share
paid by INPS directly (c. 3). The employer advances the INPS share only for
the calendar days of the employment in those 12 months; INPS pays the later
days directly (c. 5), so their share is not on the payslip. The days past
the limit are unpaid sickness (`fixed_term_limit`, deducted). Without
`prior_worked_days` the limit is not applied and the run has a provisional
`sickness_fixed_term_prior_work_unknown` issue. The 30 days of c. 3 and
the source are the `fixed_term` record of `sickness/indemnity/rates.json`,
cited in the rule sources of a fixed-term run.

A CCNL whose workers INPS indemnifies at other rates names the regime in
`work_rules.sickness_rules.inps_regime`; its bands replace the ones above,
while the carenza, the 180-day maximum and the cover stay. The bundle holds
one regime, `pubblici_esercizi`: 80% from day 4 to day 180 for the
employees of pubblici esercizi and laboratori di pasticceria, whose
employers pay the additional sickness contribution of 0.77% (INPS page and
circ. 71/1985). A regime the table lacks is a data error. The employers of
a regime also pay its additional contribution: the INPS table of the year
lists it under `inps.sick_pay_supplements` (0.77% of the INPS taxable pay
for `pubblici_esercizi`, in the terziario tables), and every run adds it to
the employer contributions as the `sick_pay_supplement_employer` component.
A year whose table has no supplement for the regime is a data error.

INPS pays at most 180 days a calendar year, counted over every recorded
episode. INPS covers the worker by the rules of
`knowledge/sickness/indemnity/rates.json`: operai of industry and the
terziario and impiegati of the terziario (secondary source), operai of the
building and artisan sectors, quadri of the terziario and apprentices
(unverified); not impiegati and quadri of industry (secondary source),
dirigenti, public employees or domestic workers (unverified). Each rule
names its source in the file. Without a rule the cover is unknown: the days
are paid at the CCNL rate only and a `provisional` issue
`sickness_inps_cover_unknown` names the fact `category` when the level does
not fix it. For most CCNLs the tier is the one of the month of sickness
(30 days) the day falls in, so a month that crosses a tier threshold pays
each day its own rate, and the comporto ends past `max_duration_days` of
the episode and its relapses. A CCNL that counts several episodes sets a
cumulation instead ([below](#sickness-counted-over-several-episodes)).

The payable days of each class are counted with the CCNL daily quota of an
unpaid absence (`work_rules.absence_rules.daily_divisor_method`), the same
count as a hire or termination month, unless the sickness rules set their
own (`work_rules.sickness_rules.daily_divisor_method`: the CCNL lavoro
domestico pays sickness in thirtieths and absences in twenty-sixths), and
never exceed one monthly pay,
however many episodes the month holds: the episodes of a run are taken by
first day, whatever their order in the facts, and the days past the pay
left by the earlier ones are dropped. Their pay is rounded once on the days
counted so far, not band by band, so the sick days of a month never deduct
more than the monthly pay. The run deducts the daily pay of the sick days (`absence_deduction`) and pays
back the INPS share as `sickness_inps_item` (outside the contribution base,
the days are covered by figurative contributions) and the employer share
and carenza pay as `sickness_item`. TFR keeps the full monthly pay (art.
2120 c. 3 c.c.).

The closing state records each episode up to its last processed day
(`EmploymentAccrualState.sickness_episodes`); `OpeningBalances` takes the
same records for a worker taken over from another provider. Each episode
records one `sickness` decision with the classified days in its inputs.

| Missing | Effect |
|---|---|
| CCNL `work_rules.sickness_rules` | Nothing posted; `incomplete` issue `sickness_rule_missing` |
| CCNL daily quota | Nothing posted; `incomplete` issue `sickness_daily_quota_missing` |

Two engine limitations stay open: the INPS share uses the CCNL daily quota
of the month instead of the INPS daily base of the month before
(`sickness_inps_daily_base`), and, for a CCNL without a cumulation, tiers
and comporto count one relapse chain, not the CCNL window across episodes
(`sickness_cumulation_window`).

#### Sickness counted over several episodes

`work_rules.sickness_rules.cumulation` holds the rules of a CCNL that
counts the sickness of several episodes. Metalmeccanici Federmeccanica
(Sez. Quarta Titolo VI Art. 2) is the first:

| Seniority | Full pay | Then | Comporto breve |
|---|---|---|---|
| up to 3 years | first 122 days of the chain | 80% | 183 days |
| 3 to 6 years | first 153 days | 80% | 274 days |
| over 6 years | first 214 days | 80% | 365 days |

- The chain sums the days of consecutive episodes; it restarts for an
  episode that starts after at least 61 calendar days of work.
- The comporto counts the sick days of the three years that end on the
  day; a day past it is left out with an `incomplete` issue (the comporto
  prolungato and the days added for a certified disability are not
  modelled).
- From the fourth short absence (at most 5 days) of a calendar year, the
  first three days are paid 66%, from the fifth 50%, unless the CCNL
  exempts the absence (`SicknessEpisode.short_absence_exempt`).
- The band is the one of the seniority on the first day of the episode.

A seniority band can count over its own window (`window_months`: Logistica
Confetra art. 63, 24 months up to 5 years of seniority and 30 above) and pay
the days past its full-pay days by steps (`steps`, by day of the count: the
PA comparti pay 90% for 3 months and 50% for the next 6); a day in no step
takes `reduced_integration_rate`.

Without `reset_after_days` there is no chain: the full-pay days are counted
over the same window as the comporto. The CCNL lavoro domestico (Art. 27
cc. 4-7) pays the sickness within the comporto, 50% up to the third day
and 100% from the fourth, for at most 8, 10 or 15 days "complessivi
nell'anno" by seniority, and keeps the job 10, 45 or 180 days in the 365
days from the event.

A fact the engine does not know raises a `provisional` issue, a blocker,
only when it could change a day the run pays:

| Issue | When | Settled by |
|---|---|---|
| `sickness_history_unknown` | days before the recorded history could pass a threshold | `OpeningBalances.sickness_known_from` (the hire date when the imported episodes are complete), or `Employment.employment_period` |
| `sickness_seniority_unknown` | the counts pass the days of the first band | `Employment.seniority` |
| `sickness_short_absence_exemption_unknown` | a short absence could be reduced | `SicknessEpisode.short_absence_exempt` |
| `sickness_fixed_term_prior_work_unknown` | a fixed-term episode without its days of work before it | `SicknessEpisode.prior_worked_days` |
| `sickness_seniority_band_changes` | the band changes within the days paid | not modelled |
| `sickness_hospital_stays_unknown` | a reduced day of a CCNL that pays long hospital stays in full (Federmeccanica: over 10 consecutive days, up to 61 days) | `SicknessEpisode.hospital_stays` |
| `sickness_hospital_stay_not_modelled` | a reduced day of a CCNL whose hospital rule is not in the bundle | not modelled |
| `sickness_serious_illness_unknown` | a reduced day of a CCNL that treats a particularly serious illness apart (Logistica art. 63: 18 months in full, outside the comporto; Concia art. 60 B: comporto 2, 3, 4 months longer) | `SicknessEpisode.serious_illness` |
| `sickness_fixed_term_proportion` | a fixed-term contract (periods scaled to its length) | not modelled |

An import without `sickness_known_from` lists the sickness of its tax year
only, from 1 January; the engine's own chained state lists every sick day
of the employment.

#### A month whose days differ from the divisor

No CCNL text in the bundle says how a month of sickness is deducted when
its payable days differ from the divisor, so the run raises the
`provisional` issue `sickness_month_quota_mismatch` when every payable day
of a fully posted month is sick yet part of the pay is left (24/26 of a
February by 26), or a payable day is worked yet the sick days deduct the
whole pay (sick 1 to 30 of a 31-day month by 30).

`SickLeaveEvent` remains as an explicit override: an amount the caller
computed. It records a caller-supplied `sickness` decision, so the result is
never payable.

### Paid leave: ferie, ROL and ex festività

A CCNL whose leave clauses were read states, in `work_rules.leave_rules`,
each bucket with its provenance: `ferie_accrual` (the twelfths of the
yearly days of `entitlement_tiers` and how a month fraction counts),
`permits` (the yearly hours of `rol` and `ex_festivita` by employer size,
a single `rol` pool with `includes_ex_festivita` when the CCNL pools them,
and a new-hire `ramp`) and `termination` (the basis of the indemnity for
the residual leave). A CCNL without them accrues nothing.

Every regular run credits its competence month: a twelfth of the yearly
entitlement of each bucket, when the month counts under its rule
(`whole_month`, or `more_than_half`: more than fifteen days). The days
served are those of the employment in the month, less the days of the
absences with `suspends_accrual`. The permit hours of a part-time worker are
proportional to the weekly hours; a ramp applies the share in force on the
last day of the month. What the request cannot tell is not guessed
silently: a month fraction under a bucket whose rule the text leaves open
accrues nothing, an unknown seniority takes the default days, an unknown
hire date the first step of the ramp, an absence without `suspends_accrual`
counts as served, and each marks the balance `exact = False`.

A `LeaveTakenEvent` is decided by the `leave` capability: final, amount
zero, when the CCNL accrues its bucket; incomplete
(`leave_bucket_not_modelled`) otherwise. The leave is taken from the oldest
balance with a residual first, then from the balance of the year, which may
go negative (leave granted in advance). An unpaid absence stays an
`AbsenceEvent`.

The run that closes the employment pays every residual as a
`leave_settlement_item` (ordinary IRPEF, INPS and TFR base) and decides
`termination_residual_leave`: final, or provisional when a balance is
inexact; incomplete with nothing paid when the CCNL accrues no leave
(`leave_accrual_not_modelled`), gives no basis
(`termination_basis_not_sourced`, `permit_basis_not_sourced`), a bucket is
overdrawn (`leave_taken_beyond_accrual`: the recovery is not sourced) or
imported balances miss the leave (`missing_fact leave_balances`).

| CCNL | Ferie | Permits | Residual at termination |
|---|---|---|---|
| Commercio, Confesercenti | 26 days, month rule not stated | ex festività 32 h, ROL 56 h (72 above 15 employees; 0% / 50% / 100% at 0 / 24 / 48 months for hires after 1 March 2011), whole months | ferie: monthly pay / 26; permits: monthly pay / hourly divisor |
| Turismo | 26 days, cumulated fractions not modelled | pool of 104 h with the ex festività | not sourced |
| FIPE | 26 days, cumulated fractions not modelled | ex festività 32 h, ROL 72 h (0% / 50% / 100% for hires after 1 January 2018) | not sourced |
| Metalmeccanici (Federmeccanica, Confapi) | 20 / 21 / 25 days, fraction > 15 days | PAR pool of 104 h | divisor not stated |
| Studi professionali | 22 days, month rule not stated | ex festività 32 h; ROL not accrued (weekly schedule not an input) | not sourced |
| Chimica | 20 / 25 days, fraction > 15 days | ROL 68 h (giornalieri, 2x5, 2x6), ex festività 40 h | divisor not stated |

The balances are carried in the state and shown on the result
(`PeriodResult.leave_balances`); see [Payroll state](payroll-state.md#leave-balances).
Not modelled, each a limitation of its CCNL: the payout of the residual
permits at the CCNL deadline (Commercio 30 June, Federmeccanica conto ore
after 24 months), the hours absorbed by a 38- or 39-hour week, sector, shift
and comparto hours, and vertical part time.

### Maternity leave and work injury

A `MaternityLeaveEvent` or a `WorkInjuryEvent` is one absence over its
days, like a sickness episode: pass the same event to every regular run
whose month it touches. The run deducts the days at the CCNL daily quota
(a whole calendar month deducts the whole monthly pay) and posts:

- maternity (D.Lgs. 151/2001 artt. 22-23): the INPS indemnity, 80% of the
  monthly pay over thirty plus the daily rateo of the extra months, for
  every calendar day (`maternity_item`, advanced by the employer, outside
  the INPS and TFR bases), and the CCNL top-up of the days within its limit
  (`absence_integration_item`);
- work injury (D.P.R. 1124/1965 artt. 68, 73, 116-117): the injury day is
  paid in full and never deducted, the three days after it at the CCNL
  waiting-period rate (60% by law), from the fourth day the INAIL
  indemnity, 60% of the daily base to the ninetieth day and 75% after it
  (`work_injury_item` when the CCNL makes the employer advance it), and the
  CCNL top-up.

A top-up on the net pay grosses the insurer share up by the worker's INPS
rate. A month whose employed days are all indemnified (after the injury
day) has no INPS minimum base: the days are credited with figurative
contributions. A month partly indemnified has an undetermined minimum when
its base is below the bound, as for any other absence.

The bundle holds the CCNL treatment of turismo Federalberghi (art. 179:
100% of the net pay for five months; art. 172: INAIL advanced to permanent
workers only) and chimica Federchimica (art. 41: 100% of the gross pay for
five months; art. 40 C: waiting period in full, INAIL advanced and topped
up to the net pay). Elsewhere the run pays the statutory amounts and is
`provisional` with the issue `insured_absence_ccnl_not_modelled`; without a
CCNL daily quota it posts nothing and is `incomplete`
(`insured_absence_without_daily_quota`). The pay of the month before is the
monthly pay of the run: its variable pay is not known.

### Absences are bounded by the pay of the run

Unpaid absences that deduct more than the monthly pay of the run raise
`InvalidInputError` before any amount is computed: check the hours and the
hourly rate. The sick days of `SicknessEpisode` are capped at the monthly
pay by construction ([Sickness](#sickness)). An `AbsenceEvent` on a day of
an episode raises `InvalidInputError`; on another day of the month it is
deducted at the caller's rate beside the sick days at the CCNL quota, with
the `provisional` issue `sickness_with_unpaid_absence`, and when the two
exceed the pay the run raises `OutOfScopeError` with reason
`sickness_with_unpaid_absence`. Absences below the pay can still leave less than the IRPEF and
surtax due on the run (the withholding follows the projected annual income).
The taxes are then withheld up to the pay left and the rest is carried to
the next runs of the tax year
([Fiscal](fiscal.md#pay-that-does-not-cover-the-tax)). A run whose other
deductions (INPS, substitute tax, recovery installments) exceed the pay
left still raises `OutOfScopeError` with reason `withholding_shortfall`.

### Fringe benefits

For tax years 2025 to 2027 goods and services granted to the worker are
exempt from IRPEF and INPS up to 1,000 EUR in the year, or 2,000 EUR when the
worker has children "che si trovano nelle condizioni previste dall'articolo
12, comma 2" TUIR and declares them to the employer with their tax codes
(L. 207/2024 art. 1 cc. 390-391, derogating TUIR art. 51 c. 3). The engine
derives the condition from `PeriodFacts.family_composition`: declare every
child, a minor too, as a `Dependent` once the worker has made the
declaration. A child counts when its dependency interval touches the tax
year and its `own_income` is within the limit of art. 12 c. 2 (2,840.51
EUR, 4,000 EUR for a child who turns at most 24 in the year); the age band
and the residency condition of the art. 12 deduction do not apply. When the
condition is unknown (no family composition, or a child's `own_income` left
`None` and no other child within the limit) the 1,000 EUR threshold is
applied and, if the 2,000 EUR one would tax another amount, the decision is
`provisional` with an `incomplete` issue `fringe_threshold_undetermined`
(`fact="own_income"` when a composition is given), so the run is not
payable.

The threshold is all or nothing (AdE circ. 4/E of 16 May 2025, par. 2.7): an
amount equal to the threshold is still exempt, but once the year total
exceeds it the whole amount of the year is taxable, not only the excess. The
year total comes from `opening_state.cash.fringe`, so chain the closing state
of each run into the next. The benefit that crosses the threshold makes the
earlier exempt amounts of the year taxable in its run. For example, 600 EUR
in February is exempt; another 600 EUR in March brings the year to 1,200 EUR
and makes 1,200 EUR taxable in March; a further 300 EUR in April is taxable
on its own.

Each `FringeEvent` reports:

- on its `FringeBenefitItem`: `threshold_annual`, `ytd_total` (year total
  including the benefit) and `taxable_amount` (which can exceed `amount` on
  the crossing benefit);
- a `fringe_benefit` decision in `result.decisions`, with reason
  `within_threshold`, `above_threshold` or `above_threshold_retroactive`,
  the threshold and the children condition, the year totals, the
  `retroactive_amount` and the taxable amount as `amount`.

### Substitute-tax regimes

The prior-year employment income and the written waivers that decide
eligibility for the substitute-tax regimes are declared once, in
`PriorYearTaxFacts` on the input, not on each event. The sector is declared on
`Employment` and the employer activity on `EmployerProfile`. An unknown fact
means ordinary taxation; for night, holiday and shift supplements and for
renewal increments the result is then provisional. A renewal increment
(`BonusEvent` with `kind="contract_renewal"`) carries the signing date of its
renewal in `agreement_signed_on`. See
[Substitute tax regimes](substitute-tax-regimes.md).

### Renewal arrears

Art. 17 c. 1 lett. b TUIR taxes separately the "emolumenti arretrati per
prestazioni di lavoro dipendente riferibili ad anni precedenti" received
by effect of a collective agreement; art. 21 c. 1 sets the rate on half
the income of the two years before the year of receipt, which the engine
does not know: the caller supplies it as `separate_tax_rate`.
`reference_period` is compared with the tax year of the run (a December
paid by 12 January belongs to its year):

| `reference_period` | Taxation | `contract_renewal_arrears` decision |
|---|---|---|
| An earlier tax year | Separate, `amount x separate_tax_rate` on `separate_tax` (code 1002) | `separate_taxation`, final |
| The tax year of the run | Ordinary IRPEF with the run; the rate is not used | `ordinary_taxation`, final |
| `None` | Separate, as a simulation, with an `arrears_reference_period_unknown` issue and a `missing_fact reference_period` blocker | `reference_period_unknown`, incomplete |
| A later year | `InvalidInputError` | |

The arrears enter the INPS base of the run in every case.

---

## Reading the result

Each event produces pay items and ledger entries on the period result. A
condition that lowers the reliability of the result (for example an unknown
prior-year income) is reported in `result.issues` and blocks
`result.is_payable`. See [Assurance and payability](../api/results.md#assurance-and-payability).
