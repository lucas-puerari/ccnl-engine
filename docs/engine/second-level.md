# Second-level bargaining

Company or territorial agreements may add allowances on top of the national
CCNL minimum. Second-level amounts are not an input of the engine: there is no
model for a caller-supplied second-level allowance, and a CCNL data file
carries only the allowances of the national agreement. An amount agreed at
company level that must be paid can be declared today only through the work
events of the run, for example a `BonusEvent`, with the treatment of that
event.

See [Domain: Second-level bargaining](../domain/components.md#12-second-level-bargaining-contrattazione-di-secondo-livello)
for the legal background.

## Company agreements and the calendar

A company agreement can change when an extra month is paid, or grant more
than the CCNL. The year calculation accepts such a calendar only as a
`CalendarOverride` with its reason, validated against the CCNL calendar:

```python
--8<-- "docs/examples/08_second_level.py"
```

!!! note
    A *premio di risultato* paid under a second-level agreement is a
    `BonusEvent` with `kind="productivity_bonus"`. Its 1% substitute tax
    needs the prior-year employment income in `PriorYearTaxFacts`; without
    it the bonus is taxed at ordinary rates.

**API reference:** [`YearInput`, `CalendarOverride`](../api/engine.md)
