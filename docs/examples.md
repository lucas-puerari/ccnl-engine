# Examples

Runnable scripts covering every major `Scenario` field.
Each file in `docs/examples/` is executed in CI via `tests/doc/test_docs_examples.py` —
if an API change breaks an example, the build fails.

## Basics

### Quickstart

Minimal call: load a CCNL, build a `Scenario`, call `compute()`.

```python
--8<-- "docs/examples/01_quickstart.py"
```

### Reading the Payslip

`compute()` returns a frozen dataclass with every gross-to-net and employer-cost component.

```python
--8<-- "docs/examples/02_payslip_fields.py"
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

### Part-time

`part_time_pct` scales base pay, seniority, and allowances. `ad_personam_monthly` is NOT scaled.

```python
--8<-- "docs/examples/04_part_time.py"
```

### Seniority increments (scatti di anzianità)

Two equivalent ways to express seniority: explicit count or total service months.

```python
--8<-- "docs/examples/05_seniority.py"
```

### Negotiated RAL

When the worker's gross is individually agreed above the CCNL minimum, pass `negotiated_ral` to bypass the table.

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

Pass `regione` + `comune_belfiore` and a `SurtaxRules` object to include addizionale regionale and comunale.

```python
--8<-- "docs/examples/07_addizionali.py"
```

### Domestic work (lavoro domestico)

Flat per-hour INPS contributions; the employer does not withhold IRPEF. `weekly_hours` is required.

```python
--8<-- "docs/examples/10_domestic.py"
```
