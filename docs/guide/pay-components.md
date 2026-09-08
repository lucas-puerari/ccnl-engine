# Pay components

This page covers the runtime knobs that adjust gross pay beyond the CCNL table
minimum: part-time scaling, seniority, and individually negotiated salary.

See [Domain: Components](../domain/components.md) for the legal background.

## Part-time

Pass `part_time_pct` (a `Decimal` between 0 and 1 exclusive) to
`WorkArrangement`. Base salary, seniority, and contractual allowances all scale
proportionally. Individually frozen *ad personam* amounts do not scale.

```python
--8 < --"docs/examples/04_part_time.py"
```

## Seniority increments (*scatti di anzianità*)

Two equivalent ways to specify seniority:

- `SeniorityByCount(n)` — you already know how many increments have matured.
- `SeniorityByMonths(m)` — total service months; the engine derives the count from
  the CCNL cadence.

```python
--8 < --"docs/examples/05_seniority.py"
```

## Individually negotiated salary (*RAL concordata*)

When a worker's annual gross is negotiated above the CCNL minimum, pass a
`SalaryOverrides` with a `RalOverride`. The engine uses this figure directly and
derives monthly and hourly rates from it, instead of building pay from the level
table.

This is mutually exclusive with `Employer.second_level_allowances`.

```python
--8 < --"docs/examples/09_negotiated_ral.py"
```

**API reference:** [`WorkArrangement`](../api/engine.md),
[`SeniorityByCount`, `SeniorityByMonths`](../api/engine.md),
[`SalaryOverrides`, `RalOverride`](../api/engine.md)
