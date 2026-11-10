"""Art. 34 role-gated pay in the bundled live-in domestic agreements.

The 2026 signed CCNL (PDF pp. 44-45, 59) pays BS full-time
1053.39 + 138.54 = 1191.93 with an eligible under-six sitter role;
CS full-time 1193.84 + 119.66 = 1313.50 when assisting more than
one non-self-sufficient person; B full-time certified pays 983.16 + 30.27
= 1013.43; reduced-hours BS pays 737.39 + 97.06 = 834.45.
Without the attested roles the additions are zero.
"""

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
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire


@pytest.mark.parametrize(
    ("agreement", "level", "hours", "role", "base", "with_role"),
    [
        (
            "lavoro-domestico-convivente",
            "BS",
            54,
            "baby_sitter_under_6",
            "1053.39",
            "1191.93",
        ),
        (
            "lavoro-domestico-convivente",
            "CS",
            54,
            "assistenza_piu_non_autosufficienti",
            "1193.84",
            "1313.50",
        ),
        (
            "lavoro-domestico-convivente",
            "B",
            54,
            "certificazione_uni_11766",
            "983.16",
            "1013.43",
        ),
        (
            "lavoro-domestico-convivente-orario-ridotto",
            "BS",
            30,
            "baby_sitter_under_6",
            "737.39",
            "834.45",
        ),
    ],
)
def test_art34_monthly_role_allowance(
    agreement: str, level: str, hours: int, role: str, base: str, with_role: str
) -> None:
    """Eligible role adds 138.54, 119.66, 30.27 or 97.06; otherwise zero."""
    for roles, expected in ((frozenset(), base), (frozenset({role}), with_role)):
        result = PayrollEngine.bundled().calculate_period(
            PeriodInput(
                run=PayrollRun.regular(year=2026, month=3),
                payment_date=date(2026, 3, 20),
                employment=Employment(
                    ccnl_id=agreement,
                    level_code=level,
                    seniority=new_hire(),
                    weekly_hours=WeeklyHours(Decimal(hours)),
                    roles=roles,
                    contract_type=Permanent(),
                ),
                employer=EmployerProfile(headcount=Headcount(1)),
                facts=PeriodFacts(
                    contributable_hours=ContributableHours(Decimal(hours * 52) / 12)
                ),
            )
        )
        assert result.period_gross == Decimal(expected)
