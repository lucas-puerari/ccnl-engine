# Changelog

All notable changes to `ccnl-engine` are documented here.

## Unreleased

### Breaking changes

- **`Scenario.num_employees` is now a required field.**  
  `Scenario` must be constructed with an explicit `num_employees: int` (>= 1)
  representing the employer's total headcount. This value drives INPS
  contribution-tier selection, which was previously an implicit argument to
  `load_year_rules()`. Existing code that builds `Scenario` without
  `num_employees` will raise a `TypeError` at construction time.

  **Migration:** add `num_employees=<headcount>` to every `Scenario(...)` call.
  Pass the same value to `load_year_rules(year, sector, num_employees)` as
  before.

  ```python
  # Before
  rules = load_year_rules(2026, ccnl.meta.tax_sector, 50)
  scenario = Scenario(level_code="C2", as_of=date(2026, 1, 1), employment=Permanent())

  # After
  scenario = Scenario(
      level_code="C2",
      as_of=date(2026, 1, 1),
      employment=Permanent(),
      num_employees=50,
  )
  rules = load_year_rules(2026, ccnl.meta.tax_sector, scenario.num_employees)
  ```
