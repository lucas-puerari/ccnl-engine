"""Work-rule events: overtime, absence, sick leave, fringe benefit, welfare, bonus."""

from datetime import date
from decimal import Decimal

from ccnl_engine import EmploymentFacts, PayrollEngine, PayrollRequest, PayrollRun
from ccnl_engine.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
    OvertimeEvent,
    SickLeaveEvent,
    WelfareEvent,
)

engine = PayrollEngine.bundled()

result = engine.calculate(
    PayrollRequest(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        ccnl_slug="metalmeccanico-federmeccanica.json",
        level_code="C3",
        employment_facts=EmploymentFacts(num_employees=100),
        events=(
            OvertimeEvent(
                event_date=date(2026, 3, 5),
                hours=Decimal(4),
                hourly_rate=Decimal("16.50"),
                multiplier=Decimal("1.25"),
            ),
            AbsenceEvent(
                event_date=date(2026, 3, 10),
                hours=Decimal(8),
                hourly_rate=Decimal("16.50"),
            ),
            SickLeaveEvent(
                event_date=date(2026, 3, 12),
                amount=Decimal(0),
                sick_days=3,
                waiting_period_days=3,
            ),
            FringeEvent(
                event_date=date(2026, 3, 1),
                amount=Decimal(200),
            ),
            WelfareEvent(
                event_date=date(2026, 3, 1),
                amount=Decimal(500),
            ),
            BonusEvent(
                event_date=date(2026, 3, 1),
                amount=Decimal(1000),
                kind="productivity_bonus",
                prior_income=Decimal(0),
            ),
        ),
    )
)

print(f"Period gross:           {result.period_gross}")
print(f"Period net:             {result.period_net}")
print(f"Absence deduction:      {result.unpaid_absence_deduction}")

print("\nWork-rule pay items:")
for item in result.pay_items:
    print(f"  {item.kind:40s} {item.amount}")
