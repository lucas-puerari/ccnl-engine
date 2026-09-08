# Employment types

Every `Employee` requires a `ContractPosition` with an `employment` field that
specifies the contract type. The type determines INPS rates, salary computation,
and output flags.

See [Domain: Fixed-term](../domain/components.md#8-fixed-term-tempo-determinato),
[Apprenticeship](../domain/components.md#6-apprenticeship-apprendistato-professionalizzante)
for the legal background.

## Permanent (*tempo indeterminato*)

The default. No additional contributions; full INPS rates apply.

```python
--8<--"docs/examples/01_quickstart.py"
```

## Fixed-term (*tempo determinato*)

`FixedTerm()` adds the 1.40% NASpI *addizionale* to the employer's INPS side.
Gross and net are unchanged.

```python
--8<--"docs/examples/03_fixed_term.py"
```

## Apprenticeship (*apprendistato*)

The `Apprentice` type covers both salary tracks used by Italian CCNLs:

- **Percentage track**: pay = % of destination level minimum, stepped by elapsed
  months. Used by most industrial CCNLs (Metalmeccanico, Chimica, Edilizia).
- **Under-classification track**: the apprentice is placed at a lower level for each
  phase. Used by most tertiary CCNLs (Commercio, Turismo).

The engine automatically detects which track the loaded CCNL uses.

```python
--8<--"docs/examples/06_apprentice.py"
```

**API reference:** [`Permanent`](../api/models.md), [`FixedTerm`](../api/models.md),
[`Apprentice`](../api/models.md), [`ContractPosition`](../api/engine.md)
