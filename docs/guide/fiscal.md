# Fiscal computation

The engine computes the full gross-to-net chain: INPS, IRPEF, *trattamento
integrativo*, and optionally regional and municipal surcharges.

See [Domain: IRPEF and surcharges](../domain/components.md#10-irpef-and-surcharges)
for the legal background.

## IRPEF flow

1. **Taxable income** = gross − INPS employee contributions
2. **IRPEF gross** = taxable income × progressive brackets
3. **Work income deduction** (Art. 13 TUIR) reduces IRPEF gross
4. **IRPEF net** = IRPEF gross − work income deduction
5. **Trattamento integrativo** (Art. 1 D.L. 3/2020): if taxable income is between
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
--8<--"docs/examples/07_addizionali.py"
```

## FiscalSimplification flags

Always check `payroll.fiscal_simplifications` before presenting results to end
users. The frozenset contains every item the engine did **not** compute, so
callers know where to apply manual adjustments.

**API reference:** [`TaxProfile`](../api/engine.md),
[`FiscalSimplification`](../api/models.md),
[`load_surtax_rules`](../api/loaders.md), [`SurtaxRules`](../api/models.md)
