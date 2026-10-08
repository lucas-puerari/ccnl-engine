# Domestic work (*lavoro domestico*)

Domestic employment (*lavoro domestico*) follows a contribution system entirely
different from the general regime. Understanding the differences is essential before
computing payrolls for this sector.

See [Domain: Social contributions](../domain/components.md#9-social-contributions-inps)
for the background on the general and flat-rate systems.

## Key differences

| Feature | General regime | Domestic work |
|---|---|---|
| INPS contributions | % of gross salary | Flat rate per hour worked (INPS quarterly tables) |
| INPS base | Proportional | Depends on wage bracket |
| Employer as *sostituto d'imposta* | Yes, withholds IRPEF at source | **No**, the worker files directly |
| `weekly_hours` required | No | **Yes**, needed to compute flat INPS |
| IRPEF and surcharges withheld | Yes | No |
| Trattamento integrativo, somma esente, ulteriore detrazione | Paid on the payslip | No |
| Substitute taxes (PdR, renewal, night and shift regimes) | When eligible | No, the amount is ordinary income |

## Convivente vs. non-convivente

The library includes three separate JSON files:

- `lavoro-domestico-convivente.json`: live-in domestic worker, Tabella A
  (art. 14 c. 1 lett. a, up to 54 weekly hours)
- `lavoro-domestico-convivente-orario-ridotto.json`: live-in worker of
  levels B, B super and C hired under art. 14 c. 2, up to 30 weekly hours,
  Tabella B
- `lavoro-domestico-non-convivente.json`: non-live-in domestic worker

Each file carries the correct INPS rate table and level structure for that variant.

The monthly minimum of a non convivente is the Tabella C hourly rate times
40 × 52 / 12 (CCNL of 28 October 2025, art. 14 c. 1 lett. b and chiarimento a
verbale 1): level CS, €8.30 an hour, is €1,438.67 a month.  The hourly divisor
of the file is 173.33, so the hourly rate the INPS bracket reads is the table
rate to the cent.

A convivente under art. 14 c. 2 is paid the Tabella B minimum "qualunque sia
l'orario di lavoro osservato nel limite massimo delle 30 ore settimanali",
board and lodging in full: level B super is €737.39 a month at 20 or at 30
weekly hours. The file sets `flat_pay_max_weekly_hours` to 30, so the pay is
not proportioned, no full time is needed and more than 30 weekly hours raise
`InvalidInputError`. Seniority is 4% of the Tabella B minimum (art. 37).

A convivente under art. 14 c. 1 may agree fewer than 54 weekly hours, but
Tabella A gives monthly values and the CCNL no rule to proportion them. The
engine scales the pay on the stated full time (C super at 40 of 54 hours:
€884.33) and reports the open limitation
`lavoro-domestico-convivente/part_time_scaling`, so the run is not payable.

## Cas.Sa.Colf contribution

The CCNL charges contributi di assistenza contrattuale for the Cas.Sa.Colf and
its other joint bodies: €0.06 per paid hour, of which €0.02 withheld from the
worker and €0.04 paid by the employer (art. 54 c. 2, due at this rate from 1
January 2021, chiarimento a verbale 6).  The engine charges them on the
`contributable_hours` of the run, posts the worker share to the
`bilateral_fund_employee` account (it reduces the net) and the employer share
to `bilateral_fund_employer` (it adds to the employer cost), and records an
`assistance_contribution` decision with the hours, rates and the clause as its
source.  A run is charged on the hours it states, INPS and Cas.Sa.Colf alike:
a tredicesima stated with 0 hours charges nothing, but a competence year gives
every run, the tredicesima included, the hours of its `default_facts` (see
the `extra_month_hours` limitation below).

## Board and lodging of a convivente

A convivente receives board and lodging in kind.  Their valore convenzionale
is set by Tabella F (art. 36 c. 3): in 2026 €2.33 for pranzo e/o colazione,
€2.33 for cena and €2.00 for alloggio a day, a month being 30 days, so
€199.80 a month.  Every level of `lavoro-domestico-convivente.json` carries it
as the allowance `vitto_alloggio`, flagged `in_kind`:

| Run | Effect of board and lodging | Source |
|---|---|---|
| Regular | Not paid in cash; counted in the TFR base: (1,193.84 + 199.80) / 13.5 = €103.23 for level CS | art. 41 c. 1 |
| Tredicesima | Paid in cash: 1,193.84 + 199.80 = €1,393.64 for a full year | art. 39 c. 1, chiarimento a verbale 5 |
| Ratei at termination | Included in the tredicesima ratei | art. 39 c. 2 |
| Reduced hours | Not reduced | art. 14 c. 2 |

Three cases are open limitations.  The first two are recorded on every
regular and termination run of the CCNL, because the request has no fact for
them; the third on every tredicesima run of both files:

- `lavoro-domestico-convivente/board_lodging_substitute`: the cash indennità
  sostitutiva for the days a convivente does not take board and lodging
  (ferie art. 17 c. 7, sospensioni art. 18 c. 1, matrimonio art. 24 c. 2,
  malattia and infortunio outside hospital art. 27 c. 9 and art. 29 c. 7);
- `lavoro-domestico-non-convivente/meal_indennity`: the meal, or its
  valore convenzionale, owed to a non convivente on six or more hours a day
  with continuous presence (art. 14 c. 8);
- `<ccnl>/extra_month_hours`: no source in the bundle says whether a
  tredicesima carries contributable hours; the engine charges INPS and
  Cas.Sa.Colf on the hours the run states, and a competence year states the
  hours of a regular month.

## Usage

Pass `weekly_hours` on `Employment` and the `contributable_hours` of the run
on `PeriodFacts`. The engine uses them together with the flat-rate INPS table
to compute contributions. Pass `full_time_weekly_hours` too: the monthly
minimum of the bundle is the pay of a full-time week (54 hours for
conviventi, 40 for non conviventi, the weeks of its hourly divisors), and
weekly hours without it leave the part-time fraction unknown, with a
`missing_fact` blocker.

Both facts are value objects validated when they are built: `WeeklyHours` must
be positive (and not above `full_time_weekly_hours` when that is given), and
`ContributableHours` must be a non-negative `Decimal`. Impossible values raise
`InvalidInputError` instead of producing negative
contributions.

```python
--8<-- "docs/examples/10_domestic.py"
```

## No withholding on the payslip

A household employer (*datore di lavoro domestico*) is not a withholding agent.
The withholding agents are listed by art. 23 c. 1 DPR 600/1973 (in force until
31 December 2026) and, from 1 January 2027, by art. 33 c. 1 of the testo unico
of D.Lgs. 33/2025 (art. 243, as amended by D.L. 200/2025 art. 4): entities and
companies, partnerships, individuals running a business or a profession, the
condominium. A private household is not among them. The payroll taxes and
credits of an ordinary payslip all go through the withholding agent:

| Item | Source | Domestic payslip |
|---|---|---|
| IRPEF withholding and conguaglio | art. 23 c. 1-3 DPR 600/1973 | none |
| Addizionale regionale | D.Lgs. 446/1997 art. 50 c. 4 | none |
| Addizionale comunale | D.Lgs. 360/1998 art. 1 c. 5 | none |
| Trattamento integrativo | D.L. 3/2020 art. 1 c. 3 | none |
| Somma esente, ulteriore detrazione | L. 207/2024 art. 1 c. 7 | none |

The net pay is therefore the gross less the employee INPS contributions and the
worker share of the Cas.Sa.Colf contribution (and any other non-tax deduction,
such as unpaid absences). Convivente level A, September 2026, 40 weekly hours
and 173 contributable hours: gross €908.10, employee INPS 173 × €0.31 = €53.63,
Cas.Sa.Colf 173 × €0.02 = €3.46, net €851.01.

The engine takes this from the CCNL: `CCNLMeta.withholding_agent` is false for
the `lavoro-domestico` tax sector. For such a run:

- `tax_computation` is empty (no components, no withholding, no credit) and
  the ledger has no `ordinary_tax`, `surtax`, `substitute_tax` or `credits`
  entry;
- each skipped capability (`irpef`, `family_deductions`,
  `ulteriore_detrazione_lavoro`, `trattamento_integrativo`, `somma_esente`,
  `addizionale_regionale`, `addizionale_comunale`) records a final
  `CalculationDecision` with reason `not_withholding_agent`, amount 0 and the
  article as its source, and its capability trace is `not_applicable`;
- a PdR or a pay item under a substitute regime is ordinary income: its
  decision has reason `not_withholding_agent` and no substitute tax;
- the reconciliation invariant `non_agent_untaxed` checks that no tax or
  credit is posted and that the net does not exceed the gross;
- an opening state carrying a credit recovery, a withholding shortfall or
  IRPEF or surtax withheld is rejected with `InvalidInputError`: a household
  employer cannot have produced it.

The taxable income is still accumulated in `state.cash.earnings.taxable`, since
the worker declares it.

**API reference:** [`Employment`, `PeriodFacts`](../api/engine.md),
[`PeriodResult`](../api/engine.md)
