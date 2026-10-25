# Second-level bargaining

Company or territorial agreements may add allowances on top of the national
CCNL minimum. The bundle carries only the national agreements: a
second-level amount is a caller input, declared on the employer as a
`SecondLevelElement`.

## Second-level elements

Each element names its code, its full-time monthly amount, its kind of
agreement (`company` or `territorial`) and the day it starts; it may end on
a day, apply only to some levels, stay out of the extra months or out of the
TFR base:

```python
from datetime import date
from decimal import Decimal

from ccnl_engine import EmployerProfile, Headcount
from ccnl_engine.inputs import SecondLevelAgreement, SecondLevelElement

employer = EmployerProfile(
    headcount=Headcount(60),
    second_level_elements=(
        SecondLevelElement(
            code="premio_presenza",
            monthly=Decimal("50.00"),
            agreement=SecondLevelAgreement.COMPANY,
            valid_from=date(2026, 1, 1),
            levels=("4", "5"),
        ),
    ),
)
```

On every run whose competence date falls in its validity and whose level it
lists (every level when `levels` is empty), the element is paid as a fixed
allowance of the level: scaled by part time and partial months like an
allowance of the CCNL, in the extra months unless `extra_months=False`, in
the TFR base unless `tfr_relevant=False`. It is part of the INPS and IRPEF
bases like any ordinary earning.

Each element paid adds one decision under `company_supplement` or
`territorial_supplement`, with origin `caller_supplied` and reason
`caller_supplied_amount`: no bundled source backs the amount, and the
capability report lists the element among the caller-supplied values.

A one-off amount (a premio di risultato, an una tantum) is not an element:
declare it as a work event of the run, for example a `BonusEvent`.

See [Domain: Second-level bargaining](../domain/components.md#12-second-level-bargaining-contrattazione-di-secondo-livello)
for the legal background.

## Company agreements and the calendar

A company agreement can change when an extra month is paid, or grant more
than the CCNL. The year calculation accepts such a calendar only as a
`CalendarOverride` with its reason, validated against the CCNL calendar:

```python
--8<-- "docs/examples/calendar/example.py"
```

!!! note
    A *premio di risultato* paid under a second-level agreement is a
    `BonusEvent` with `kind="productivity_bonus"`. Its 1% substitute tax
    needs the prior-year employment income in `PriorYearTaxFacts`; without
    it the bonus is taxed at ordinary rates.

**API reference:** [`CompetenceYearPlan`, `CalendarOverride`](../api/ccnl_engine.md)
