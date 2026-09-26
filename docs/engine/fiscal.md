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

By default the engine skips *addizionale regionale* and *addizionale comunale*,
recording both as [`FiscalSimplification`](../api/models.md) entries in
`payroll.fiscal_simplifications`.

To include them, set `jurisdiction` on the `Employee` with `regione` and/or
`comune_belfiore`. The engine loads the relevant surtax rules automatically.

```python
--8 < --"docs/examples/07_addizionali.py"
```

## FiscalSimplification flags

Always check `payroll.fiscal_simplifications` before presenting results to end
users. The frozenset contains every item the engine did **not** compute (or
intentionally omitted), so callers know where to apply manual adjustments.

| Flag | Meaning |
|---|---|
| `NO_ADDIZIONALE_REGIONALE` | Regional surtax not computed; no `Jurisdiction.regione` was passed |
| `NO_ADDIZIONALE_COMUNALE` | Municipal surtax not computed |
| `NO_DETRAZIONI_FAMILIARI` | Family-dependent deductions (Art. 12 TUIR) not computed; no `FamilyComposition` was passed |
| `NO_DETRAZIONI_ART15_MORTGAGE` | Mortgage-interest deduction (Art. 15 TUIR) not computed |
| `PARTIAL_DETRAZIONI_ART15` | Always present; the engine only models mortgage interest — the other 14 Art. 15 categories (medical, insurance, etc.) are not modelled |
| `NO_BILATERAL_FUNDS` | Always present when `bilateral_funds` is empty; bilateral fund contributions are not computed |
| `NO_ASSEGNO_UNICO` | Always present; the *Assegno Unico e Universale* (D.Lgs. 230/2021) for children under 21 is paid directly by INPS and is not modelled by the engine |

## Warnings

`PayrollResult.warnings` is a tuple of human-readable strings. The engine emits
a warning (but never fails) for conditions that may indicate a configuration
mistake:

- **IVS ceiling**: when `SeniorityByDate` is supplied with a hire date on or after
  1996-01-01 but `Employee.ivs_ceiling_applies` is `False`, and the contribution
  base exceeds the IVS ceiling. Workers hired from 1996 are generally subject to
  the *massimale IVS*; the flag defaults to `False` to avoid silent over-deduction
  for pre-1996 workers.

**API reference:** [`Jurisdiction`](../api/engine.md),
[`FiscalSimplification`](../api/models.md),
[`FamilyComposition`](../api/engine.md), [`Art15Deductions`](../api/engine.md)
