# Fiscal computation

The engine computes the full gross-to-net chain: INPS, IRPEF, *trattamento
integrativo*, and optionally regional and municipal surcharges.

See [Domain: IRPEF and surcharges](../domain/components.md#10-irpef-and-surcharges)
for the legal background.

## IRPEF flow

1. **Taxable income** = gross − INPS employee contributions
2. **IRPEF gross** = taxable income × progressive brackets
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross
4. **Ulteriore detrazione lavoro** (Art. 1 c. 6 L. 207/2024): additional credit
   of up to €910/year for taxable income between €8,500 and €15,000, tapering to
   zero at €28,000
5. **IRPEF net** = IRPEF gross − work income deduction − ulteriore detrazione
6. **Trattamento integrativo** (Art. 1 D.L. 3/2020): if taxable income is between
   €8,500 and €28,000, the engine adds €1,200/year as a negative tax (credit).

## Regional and municipal surcharges

By default the engine skips *addizionale regionale* and *addizionale comunale*,
recording both as [`FiscalSimplification`](../api/models.md) entries in
`payroll.fiscal_simplifications`.

To include them, pass:
- a `TaxProfile` on the `Employee` with `regione` and `comune_belfiore`, and
- a `SurtaxRules` object loaded from `load_surtax_rules()` as the `surtax` argument
  of `compute()`.

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
  1996-01-01 but `Employee.ivs_ceiling_applies` is `False`. Workers hired from
  1996 are generally subject to the *massimale IVS*; the flag defaults to `False`
  to avoid silent over-deduction for pre-1996 workers.

**API reference:** [`TaxProfile`](../api/engine.md),
[`FiscalSimplification`](../api/models.md),
[`load_surtax_rules`](../api/loaders.md), [`SurtaxRules`](../api/models.md)
