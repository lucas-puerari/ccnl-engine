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

The library includes two separate JSON files:

- `lavoro-domestico-convivente.json`: live-in domestic worker
- `lavoro-domestico-non-convivente.json`: non-live-in domestic worker

Each file carries the correct INPS rate table and level structure for that variant.

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

The net pay is therefore the gross less the employee INPS contributions (and
any other non-tax deduction, such as unpaid absences). Convivente level A,
September 2026, 40 weekly hours and 173 contributable hours: gross €908.10,
employee INPS 173 × €0.31 = €53.63, net €854.47.

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
