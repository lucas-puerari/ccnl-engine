# Second-level bargaining

Company or territorial agreements may add allowances on top of the national CCNL
minimum. These are modelled by passing an `Employer` object to `compute()`.

See [Domain: Second-level bargaining](../domain/components.md#12-second-level-bargaining-contrattazione-di-secondo-livello)
for the legal background.

## SupplementaryAllowance flags

Each `SupplementaryAllowance` entry has three boolean flags:

| Flag | Default | Effect when `True` |
|---|:---:|---|
| `contribution_relevant` | `True` | Amount is included in the INPS base |
| `tfr_relevant` | `True` | Amount is included in the TFR accrual base |
| `apprenticeship_relevant` | `True` | Amount enters the apprentice's percentage or under-classification computation |

Set a flag to `False` to exclude the allowance from that base (e.g. a productivity
bonus that is INPS-exempt under Art. 1 c. 182 L. 208/2015).

```python
--8<-- "docs/examples/08_second_level.py"
```

!!! note
    The preferential 5% IRPEF rate on *premi di risultato* is not computed by the
    engine — tax is always applied at ordinary rates.

**API reference:** [`Employer`](../api/engine.md),
[`SupplementaryAllowance`](../api/engine.md)
