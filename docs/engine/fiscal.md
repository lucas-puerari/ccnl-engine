# Fiscal computation

The engine computes the full gross-to-net chain: INPS, IRPEF, *trattamento
integrativo*, and optionally regional and municipal surcharges.

See [Domain: IRPEF and surcharges](../domain/components.md#10-irpef-and-surcharges)
for the legal background.

The tax year of a run follows its payment date, with the 12 January
extension of TUIR art. 51 c. 1: see
[Tax year and payment date](index.md#tax-year-and-payment-date).

Some pay items take a flat substitute tax instead of IRPEF when the worker
meets the statutory requirements: see
[Substitute-tax regimes](substitute-tax-regimes.md).

## IRPEF flow

1. **Taxable income** = gross − INPS employee contributions
2. **IRPEF gross** = taxable income × progressive brackets (Art. 11 TUIR)
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross. Its income
   ratios are truncated to four decimals (art. 13 c. 6 TUIR).
4. **Ulteriore detrazione lavoro** (Art. 1 c. 6 L. 207/2024): additional credit
   of up to €1,000/year for taxable income between €20,000 and €40,000.
   Flat €1,000 from €20,001 to €32,000; linear taper to zero from €32,001 to €40,000.
   The taper ratio is not truncated: c. 6 has no four-decimal rule and the
   one of art. 13 c. 6 TUIR lists the ratios of art. 13 only.
5. **IRPEF net** = IRPEF gross − work income deduction − ulteriore detrazione
   − family deductions − Art. 15 deductions + clawback sterilisation (floored at 0)
6. **Trattamento integrativo** (Art. 1 D.L. 3/2020): up to €1,200/year.
   Two income bands apply:
   - RC ≤ €15,000: granted when IRPEF gross exceeds the Art. 13 deduction
     minus a €75 corrective (Art. 1 co. 3 L. 207/2024).
   - €15,001–€28,000: granted only when total deductions exceed IRPEF gross;
     amount equals the excess, capped at €1,200.
   - RC > €28,000: zero.

For a part-year employment the work deduction, the ulteriore detrazione and
the trattamento integrativo (with its €75 corrective) are "rapportata al
periodo di lavoro nell'anno": the full-year amount, in cents, times
`days / 365` (730/2026 istruzioni, quadro C: "365 per l'intero anno"). The
day ratio is not
truncated to four decimals, since it is not one of the ratios art. 13 c. 6
TUIR lists: 92 days of the €1,955 deduction give €492.77, not €492.66.

### Withholding of a run

Every run projects the annual taxable income (YTD, this run, and the
recurring pay of the slots still to come) and withholds on that basis:

- income the run pays once (bonus, overtime, ordinary arrears, excess PdR,
  ratei settled at termination) is not in the projection of later slots,
  so the tax it adds to the year is withheld on that run (art. 23 c. 2
  DPR 600/1973: lett. a) on the sums "corrisposti in ciascun periodo di
  paga", lett. b) on the "compensi della stessa natura" of the mensilità
  aggiuntive). It is the net annual IRPEF with the income less the net annual
  IRPEF without it. A €20,000 bonus paid in November to a Metalmeccanico C3
  withholds about €8,399 on the November payslip instead of spreading it
  over November, December and the tredicesima;
- the rest of the balance still owed is spread evenly over the remaining
  slots, the run included;
- the last slot settles the whole balance on the final income, which can
  be a refund (art. 23 c. 3).

The projection of a future tredicesima or quattordicesima uses the rateo
the run will pay on the employment period: a worker hired on 1 July is
projected 6/12 of the tredicesima, not a full month. Absences still to come
are not known and settle at the conguaglio.

A run whose unpaid absences leave less pay than the withholdings due is
still rejected (`withholding_shortfall`): capping the withholding at the pay
left and carrying the rest to the next payslip is not modelled.

## Regional and municipal surcharges

The engine computes *addizionale regionale* and *addizionale comunale* only
for the jurisdictions the request names:

- `regione`: the ISO 3166-2:IT subdivision code of the region, `IT-` and
  two digits, for example `IT-45` for Emilia-Romagna or `IT-25` for
  Lombardia (source: [ISO Online Browsing Platform](https://www.iso.org/obp/ui/#iso:code:3166:IT)).
  The regional surtax is set separately by the autonomous provinces, so use
  `IT-BZ` (Bolzano) or `IT-TN` (Trento); `IT-32` (Trentino-Alto Adige) is
  rejected.  The codes are listed in [`REGION_CODES`](../api/models.md#fiscal).
- `comune_belfiore`: the *codice catastale* (Belfiore code) of the
  municipality, one upper-case letter and three digits, for example `F257`
  for Modena.

A malformed code (`ER`, `Lombardia`, `IT45`, `f257`) is rejected with
`InvalidInputError`.  A well-formed code without a row in the tax year table
is not an input error: see the decisions below.

```python
--8<-- "docs/examples/07_addizionali.py"
```

### Surtax decisions

Each jurisdiction named in the request records one `CalculationDecision` in
`result.decisions`, with capability `addizionale_regionale` or
`addizionale_comunale`.  Its `amount` is the annual surtax projected for the
tax year; the payslip withholds an equal share of it on every withholding
slot.  Its `inputs` hold the code, the table row name, the tax year and the
taxable income, and its `rule` and `rule_version` the bundled ruleset.

| `reason_code` | Status | Amount | Meaning |
|---|---|---|---|
| `table_applied` | `final` | computed | The bundled brackets were applied. |
| `advance_applied` | `final` | computed | Municipal rates are the prior year ones: only the advance (`advance_fraction`, 30%) is computed. |
| `below_exemption_threshold` | `final` | 0 | The municipal exemption threshold covers the taxable income. |
| `no_irpef_due` | `final` | 0 | Net IRPEF (gross less the deductions) on the projected taxable income is zero, so no surtax is withheld. |
| `table_unknown` | `incomplete` | `None` | The code is well formed but the tax year table has no row for it. |

A `table_unknown` decision comes with a `CalculationIssue` coded
`regional_surtax_unknown` or `municipal_surtax_unknown`.  Nothing is
withheld for that surtax (the ledger posts 0), and the period result, hence
the year result, is `incomplete`: **it must not be paid as is**.  Without
`regione` and `comune_belfiore` no surtax decision is taken and nothing is
withheld.

The surtax is due only when the IRPEF net of its deductions is due
(D.Lgs. 446/1997 art. 50 c. 2 for the regional, D.Lgs. 360/1998 art. 1 c. 4
for the municipal): a worker whose deductions absorb the whole gross IRPEF
owes neither. Both articles also net the foreign tax credit (art. 165
TUIR), which the engine does not model.

The annual surtax is split in equal parts over the withholding slots of the
year, not settled on the actual installments (advance in the year, balance
over the following year).

### Tax credit decisions

The ulteriore detrazione (Art. 1 c. 6 L. 207/2024) and the trattamento
integrativo (Art. 1 D.L. 3/2020) each record one `CalculationDecision` per
run in `result.decisions`, with capability `ulteriore_detrazione_lavoro` or
`trattamento_integrativo`, whenever the tax year rules put the credit in
force.  The decision is `final`, its `amount` is the **annual** entitlement
(0 when the credit is not due) and its `reason_code` names the rule branch
that produced the amount:

| Capability | `reason_code` | Amount |
|---|---|---|
| `ulteriore_detrazione_lavoro` | `income_not_above_lower_threshold` | 0 |
| `ulteriore_detrazione_lavoro` | `full_amount` | full, proportioned to the days worked |
| `ulteriore_detrazione_lavoro` | `tapered_amount` | tapered, proportioned to the days worked |
| `ulteriore_detrazione_lavoro` | `income_above_upper_threshold` | 0 |
| `trattamento_integrativo` | `full_amount` | full (income up to 15,000 EUR, IRPEF above the work deduction) |
| `trattamento_integrativo` | `irpef_not_above_work_deduction` | 0 (income up to 15,000 EUR) |
| `trattamento_integrativo` | `deductions_above_irpef` | deductions minus IRPEF, capped (15,000 to 28,000 EUR) |
| `trattamento_integrativo` | `deductions_not_above_irpef` | 0 (15,000 to 28,000 EUR) |
| `trattamento_integrativo` | `income_above_upper_threshold` | 0 |

The trattamento decision also records the signed `period_amount` paid or
recovered on the run and `recovery_in_progress`, `true` while an installment
recovery (D.L. 3/2020 art. 1 c. 3) is running.

The other decisions a run can record are `worker_category` (the category
used and its origin: `declared` on the employment or `fixed_by_level`),
`seniority` (`increments_applied` or `no_increment_due`, only when the
months of service are given), `family_deductions` (`deductions_applied` or
`no_deduction_due`, only with a family composition), `bonus_pdr`
(`substitute_tax_applied` or `annual_limit_reached`, only for a bonus routed
to the PdR substitute tax) and the substitute tax regimes described in
[Substitute tax regimes](substitute-tax-regimes.md).

## Warnings

`PayrollResult.warnings` is a tuple of human-readable strings. The engine emits
a warning (but never fails) for conditions that may indicate a configuration
mistake:

- **IVS ceiling**: when `SeniorityByDate` is supplied with a hire date on or after
  1996-01-01 but `Employee.ivs_ceiling_applies` is `False`, and the contribution
  base exceeds the IVS ceiling. Workers hired from 1996 are generally subject to
  the *massimale IVS*; the flag defaults to `False` to avoid silent over-deduction
  for pre-1996 workers.

**API reference:** [`CalculationDecision`](../api/engine.md#results-and-calculation-status),
[`REGION_CODES`](../api/models.md#fiscal),
[`FamilyComposition`](../api/engine.md), [`Art15Deductions`](../api/engine.md)
