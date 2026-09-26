# Examples

Runnable scripts covering every major feature of the engine.
Each file in `docs/examples/` is executed in CI via `tests/unit/docs/test_docs_examples.py`:
if an API change breaks an example, the build fails.

## Trust — Why this number?

The most important question a payroll engine must answer is not "what is the
net salary?" but "why is it that number?" This example walks through all three
verifiability layers: provenance, versioning, and the capability report.

```python
--8<-- "docs/examples/11_why_this_number.py"
```

## Basics

### Quickstart

Minimal call: build a `PeriodInput` and pass it to `PayrollEngine.calculate_period()`.

```python
--8<-- "docs/examples/01_quickstart.py"
```

### Reading the result

`PayrollEngine.calculate_period()` returns a `PeriodResult` for one run: its status, period
gross, net and employer cost, the INPS contribution breakdown, the IRPEF
computation and the pay items.

```python
--8<-- "docs/examples/02_payroll_fields.py"
```

## Contract types

### Fixed-term (tempo determinato)

`FixedTerm()` adds the 1.40% NASpI *addizionale* to the employer's INPS contribution; gross and net are unchanged.

```python
--8<-- "docs/examples/03_fixed_term.py"
```

### Apprenticeship (apprendistato)

Percentage track: the apprentice's pay is a % of the destination level, increasing with `months_elapsed`.

```python
--8<-- "docs/examples/06_apprentice.py"
```

## Pay components

### Family deductions

A `FamilyComposition` with dependants raises the Art. 12 TUIR deductions and the net pay.

```python
--8<-- "docs/examples/04_part_time.py"
```

### Seniority increments (scatti di anzianità)

Pass the months of service as `Employment.seniority_months`; the category selects category-specific increments.

```python
--8<-- "docs/examples/05_seniority.py"
```

### Year-to-date chaining

Pass the `closing_state` of one run as the `opening_state` of the next, so progressive IRPEF and the year-to-date totals carry forward.

```python
--8<-- "docs/examples/09_negotiated_ral.py"
```

### Second-level bargaining (contrattazione di secondo livello)

Territorial or company allowances on top of the CCNL minimums, with per-item contribution/TFR/apprenticeship control.

```python
--8<-- "docs/examples/08_second_level.py"
```

## Fiscal

### Regional and municipal surcharges (addizionali)

Pass `regione` (ISO 3166-2:IT region code, e.g. `IT-45`) and `comune_belfiore` (Belfiore code, e.g. `F257`) to include addizionale regionale and comunale. Check `result.status` and `result.decisions`: an unknown table makes the result `incomplete`.

```python
--8<-- "docs/examples/07_addizionali.py"
```

### Domestic work (lavoro domestico)

Flat per-hour INPS contributions; the employer does not withhold IRPEF. `weekly_hours` is required.

```python
--8<-- "docs/examples/10_domestic.py"
```
