"""Work-rule events: overtime, absence, sickness, fringe benefit, welfare, bonus."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import (
    AbsenceEvent,
    BonusEvent,
    FringeEvent,
    OvertimeEvent,
    SicknessEpisode,
    WelfareEvent,
)
from ccnl_engine.inputs import PriorYearTaxFacts

engine = PayrollEngine.bundled()

events = (
    # No multiplier: the CCNL weekday band gives it (metalmeccanico
    # OT_DIURNO 25% for the first two hours, so 4 h x 16.50 EUR x 1.25 =
    # 82.50 EUR; the run is provisional because the 30% tier beyond two
    # hours needs an explicit multiplier).
    OvertimeEvent(
        event_date=date(2026, 3, 5),
        hours=Decimal(4),
        hourly_rate=Decimal("16.50"),
    ),
    AbsenceEvent(
        event_date=date(2026, 3, 10),
        hours=Decimal(8),
        hourly_rate=Decimal("16.50"),
    ),
    # The engine pays the sick days from the CCNL and INPS rules: three
    # days of carenza, here integrated at 100% by the CCNL.  An episode
    # that continues into April is passed again, same id, to the April run.
    SicknessEpisode(
        episode_id="cert-2026-0316",
        started_on=date(2026, 3, 16),
        ended_on=date(2026, 3, 18),
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
    ),
)

result = engine.calculate_period(
    PeriodInput(
        run=PayrollRun.regular(year=2026, month=3),
        payment_date=date(2026, 3, 27),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json", level_code="C3"
        ),
        employer=EmployerProfile(headcount=Headcount(100)),
        facts=PeriodFacts(events=events),
        # The PdR substitute tax needs the prior-year employment income.
        prior_year=PriorYearTaxFacts(employment_income=Decimal(0)),
    )
)

print(f"Period gross:           {result.period_gross}")
print(f"Period net:             {result.period_net}")
print(f"Absence deduction:      {result.unpaid_absence_deduction}")

print("\nWork-rule pay items:")
for item in result.pay_items:
    print(f"  {item.kind:40s} {item.amount}")
