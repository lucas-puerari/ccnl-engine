# Employment types

Italian labor law recognises three categories of subordinate employment that differ
in their legal duration, INPS contribution rules, and salary computation. Each maps
to a concrete type in `ccnl_engine` passed via `ContractPosition.employment`.

See [CCNL Components](components.md#8-fixed-term-tempo-determinato) for the
legal background on fixed-term and
[Apprenticeship](components.md#6-apprenticeship-apprendistato-professionalizzante)
for how the apprendistato professionalizzante contract works under Italian law.

## Permanent (*tempo indeterminato*)

The standard open-ended employment contract under Art. 2094 c.c. No duration
limit; full INPS rates apply. This is the baseline from which all other types
deviate.

```python
--8 < --"docs/examples/01_quickstart.py"
```

## Fixed-term (*tempo determinato*)

Governed by D.Lgs. 81/2015. Duration is capped (36 months, with acausale
extensions). The employer owes the 1.40% NASpI *addizionale* on the INPS side
as a disincentive to systematic precarious use. Gross and net pay are unchanged
relative to a permanent worker at the same level.

```python
--8 < --"docs/examples/03_fixed_term.py"
```

## Apprenticeship (*apprendistato*)

The *apprendistato professionalizzante* (Art. 44 D.Lgs. 81/2015) is a
dual-purpose contract: the employer trains the worker toward a target
qualification (*qualifica*) while benefiting from reduced INPS rates and a
below-minimum starting salary. Duration and pay progression are set by the CCNL,
not by statute.

The `Apprentice` type covers both salary tracks used by Italian CCNLs:

- **Percentage track**: pay = % of destination level minimum, stepped by elapsed
  months. Used by most industrial CCNLs (Metalmeccanico, Chimica, Edilizia).
- **Under-classification track**: the apprentice is placed at a lower level for each
  phase. Used by most tertiary CCNLs (Commercio, Turismo).

The engine automatically detects which track the loaded CCNL uses.

```python
--8 < --"docs/examples/06_apprentice.py"
```

**API reference:** [`Permanent`](../api/models.md), [`FixedTerm`](../api/models.md),
[`Apprentice`](../api/models.md), [`ContractPosition`](../api/engine.md)

---

[Engine: Pay components →](../engine/pay-components.md)
