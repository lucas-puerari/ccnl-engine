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
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross
4. **Ulteriore detrazione lavoro** (Art. 1 c. 6 L. 207/2024): additional credit
   of up to €1,000/year for taxable income between €20,000 and €40,000.
   Flat €1,000 from €20,001 to €32,000; linear taper to zero from €32,001 to €40,000.
5. **IRPEF net** = IRPEF gross − work income deduction − ulteriore detrazione
   − family deductions − Art. 15 deductions + clawback sterilisation (floored at 0)
6. **Trattamento integrativo** (Art. 1 D.L. 3/2020): up to €1,200/year.
   Two income bands apply:
   - RC ≤ €15,000: granted when IRPEF gross exceeds the Art. 13 deduction
     minus a €75 corrective (Art. 1 co. 3 L. 207/2024).
   - €15,001–€28,000: granted only when total deductions exceed IRPEF gross;
     amount equals the excess, capped at €1,200.
   - RC > €28,000: zero.

## Regional and municipal surcharges

The engine computes *addizionale regionale* and *addizionale comunale* only
for the jurisdictions the request names:

- `regione`: a two-letter upper-case region code of this engine, for
  example `ER` for Emilia-Romagna.  The codes are listed in
  [`REGION_CODES`](../api/models.md#fiscal); they are not ISO 3166-2 codes.
- `comune_belfiore`: the *codice catastale* (Belfiore code) of the
  municipality, one upper-case letter and three digits, for example `F257`
  for Modena.

A malformed code (`LOM`, `Lombardia`, `f257`) is rejected with
`InvalidInputError`.  A well-formed code without a row in the tax year table
is not an input error: see the decisions below.

```python
--8 < --"docs/examples/07_addizionali.py"
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
| `no_irpef_due` | `final` | 0 | Gross IRPEF on the projected taxable income is zero, so no surtax is withheld. |
| `table_unknown` | `incomplete` | `None` | The code is well formed but the tax year table has no row for it. |

A `table_unknown` decision comes with a `CalculationIssue` coded
`regional_surtax_unknown` or `municipal_surtax_unknown`.  Nothing is
withheld for that surtax (the ledger posts 0), and the period result, hence
the year result, is `incomplete`: **it must not be paid as is**.  Without
`regione` and `comune_belfiore` no surtax decision is taken and nothing is
withheld.

The annual surtax is split in equal parts over the withholding slots of the
year, not settled on the actual installments (advance in the year, balance
over the following year).

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
