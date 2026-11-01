"""The hourly divisor of the normal week: 168, 182 or 195.

Commercio Confcommercio (Testo Unico 30 July 2019, Art. 211, p. 197) and
Terziario Confesercenti (Art. 211, p. 156): "La quota oraria della
retribuzione, sia normale che di fatto, si ottiene dividendo l'importo
mensile per i seguenti divisori convenzionali: a) 168, per il personale la
cui durata normale di lavoro è di 40 ore settimanali; b) 182, [...] di 42
ore settimanali; c) 195, [...] di 45 ore settimanali."

Two weekday overtime hours on 10 March 2026, level 4 (IV), normale
retribuzione 1,781.68, 15% (art. 149): 2 x 1.15 x 1,781.68 / divisor,
24.39 on 168, 22.52 on 182, 21.01 on 195.  A week of 38 hours has no
divisor of its own: the rate is not derived.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.errors import MissingRuleError
from ccnl_engine.events import OvertimeEvent, OvertimeKind
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WeeklyHours,
)
from ccnl_engine.pay_item.facade import OvertimeEarning

_HIRED = date(2025, 1, 1)
_OVERTIME = OvertimeEvent(date(2026, 3, 10), Decimal(2), kind=OvertimeKind.WEEKDAY)
_LEVELS = [("commercio-confcommercio", "4"), ("terziario-confesercenti", "IV")]


def _overtime(ccnl_id: str, level: str, week: int) -> Decimal:
    hours = WeeklyHours(Decimal(week))
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
                weekly_hours=hours,
                full_time_weekly_hours=hours,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=(_OVERTIME,)),
        )
    )
    return sum(
        (i.amount for i in result.pay_items if isinstance(i, OvertimeEarning)),
        Decimal(0),
    )


@pytest.mark.parametrize(("ccnl_id", "level"), _LEVELS)
@pytest.mark.parametrize(
    ("week", "amount"), [(40, "24.39"), (42, "22.52"), (45, "21.01")]
)
def test_the_overtime_hour_is_divided_by_the_divisor_of_the_week(
    ccnl_id: str, level: str, week: int, amount: str
) -> None:
    """168, 182 and 195 for the weeks of 40, 42 and 45 hours."""
    assert _overtime(ccnl_id, level, week) == Decimal(amount)


@pytest.mark.parametrize(("ccnl_id", "level"), _LEVELS)
def test_a_week_without_a_divisor_is_not_derived(ccnl_id: str, level: str) -> None:
    """38 hours: the CCNL sets no divisor, the caller states the rate."""
    with pytest.raises(MissingRuleError, match="38 hours"):
        _overtime(ccnl_id, level, 38)
