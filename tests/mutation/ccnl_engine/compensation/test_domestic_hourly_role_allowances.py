"""Domestic non-live-in 2026 hourly role allowances.

80 hours x 0.84 = 67.20 for BS; 80 x 0.70 = 56.00 for CS/DS;
certification stays 30.27 a month.
Tabella C gives BS 1291.33 and CS 1438.67 as monthly-equivalent bases.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.allowance.hourly import pay_hourly_allowances
from ccnl_engine.compensation.allowance.models import Allowance
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.inputs import ContributableHours, Permanent, WeeklyHours
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _run(
    level: str, roles: frozenset[str], hours: str = "80", weekly: str = "40"
) -> Decimal:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=3),
            payment_date=date(2026, 3, 20),
            employment=Employment(
                ccnl_id="lavoro-domestico-non-convivente",
                level_code=level,
                seniority=new_hire(),
                weekly_hours=WeeklyHours(Decimal(weekly)),
                full_time_weekly_hours=WeeklyHours(Decimal(40)),
                roles=roles,
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(hours))),
        )
    )
    return result.period_gross


@pytest.mark.parametrize(
    ("level", "roles", "expected"),
    [
        ("BS", frozenset(), "1291.33"),
        ("BS", frozenset({"baby_sitter_under_6"}), "1358.53"),
        (
            "BS",
            frozenset({"baby_sitter_under_6", "certificazione_uni_11766"}),
            "1388.80",
        ),
        ("B", frozenset({"certificazione_uni_11766"}), "1245.34"),
        ("CS", frozenset(), "1438.67"),
        ("CS", frozenset({"assistenza_piu_non_autosufficienti"}), "1494.67"),
        (
            "CS",
            frozenset({
                "assistenza_piu_non_autosufficienti",
                "certificazione_uni_11766",
            }),
            "1524.94",
        ),
        ("DS", frozenset({"assistenza_piu_non_autosufficienti"}), "1784.13"),
        ("DS", frozenset({"baby_sitter_under_6"}), "1728.13"),
    ],
)
def test_eighty_paid_hours(level: str, roles: frozenset[str], expected: str) -> None:
    """BS: 1291.33 + 67.20 + 30.27; CS: 1438.67 + 56 + 30.27."""
    assert _run(level, roles) == Decimal(expected)


def test_monthly_certification_not_converted_to_hourly() -> None:
    """40 x 0.84 = 33.60; the certificate remains 30.27, not prorated."""
    assert _run(
        "BS", frozenset({"baby_sitter_under_6", "certificazione_uni_11766"}), "40"
    ) == Decimal("1355.20")


def test_hourly_rate_cannot_double_count_monthly_pay() -> None:
    """Hourly 0.84 must not also create a nonzero monthly allowance."""
    source = load_ccnl("lavoro-domestico-non-convivente")
    allowance = source.level_by_code("BS").fixed_allowances[0]
    invalid = allowance.model_dump()
    invalid["monthly"]["periods"][0]["value"] = Decimal(1)
    with pytest.raises(ValidationError, match="zero monthly placeholder"):
        Allowance.model_validate(invalid)


def test_active_hourly_role_requires_paid_hours() -> None:
    """An active 0.84/hour role cannot silently earn zero without paid hours."""
    source = load_ccnl("lavoro-domestico-non-convivente")
    allowance = source.level_by_code("BS").fixed_allowances[0]
    chain = MonthlyPayChain(
        base=Decimal("1291.33"),
        seniority=Decimal(0),
        allowances=((allowance, Decimal(0)),),
    )
    with pytest.raises(MissingRequiredFactError, match="paid hours"):
        pay_hourly_allowances(chain, None, date(2026, 3, 1))


def test_part_time_certification_remains_monthly() -> None:
    """1291.33 / 2 = 645.67; 80 x 0.84 = 67.20; plus 30.27 = 743.14."""
    assert _run(
        "BS",
        frozenset({"baby_sitter_under_6", "certificazione_uni_11766"}),
        weekly="20",
    ) == Decimal("743.14")
