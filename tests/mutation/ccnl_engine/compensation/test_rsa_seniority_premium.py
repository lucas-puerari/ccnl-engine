"""The ratified RSA bridge agreement, signed 3 October 2023 (AIOP PDF pp. 7-12).

PDF SHA-256 8c4bc6f957e9c122714cd1ebe77300d97ec31d4da25d62be241d0bb22db73214:
page 11 awards EUR 40 on thirteen payments, TFR-relevant, to levels A-E3
with ten years of service at the same company or group at signing.
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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import EmploymentPeriod, Permanent, WorkerCategory
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _premium(level: str, hired: date | None, run: PayrollRun) -> list[Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(run.year, run.month, 27),
            employment=Employment(
                ccnl_id="rsa-aiop",
                level_code=level,
                category=WorkerCategory.IMPIEGATO,
                seniority=new_hire(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired)
                if hired is not None
                else None,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    return [
        item.amount
        for item in result.pay_items
        if "PREMIO_ANZIANITA_2023" in item.item_id
    ]


@pytest.mark.parametrize("level", ["A", "B", "C", "D1", "D2", "D3", "E1", "E2", "E3"])
def test_ten_year_cohort_receives_the_premium(level: str) -> None:
    """From October 2023: EUR 40; before then EUR 0; EUR 40 in 2026."""
    allowance = next(
        a
        for lv in load_ccnl("rsa-aiop").levels
        if lv.code == level
        for a in lv.fixed_allowances
        if a.code == "PREMIO_ANZIANITA_2023"
    )
    assert not allowance.monthly.applies_on(date(2023, 9, 1))
    assert allowance.monthly.value_at(date(2023, 10, 1)) == Decimal("40.00")
    assert _premium(level, date(2013, 10, 1), PayrollRun.regular(2026, 10)) == [
        Decimal("40.00")
    ]


@pytest.mark.parametrize("hired", [date(2013, 10, 4), date(2013, 11, 1), None])
def test_late_or_unknown_group_service_is_not_eligible(hired: date | None) -> None:
    """EUR 0, rather than EUR 40, for later or unknown group-service start."""
    assert _premium("D2", hired, PayrollRun.regular(2026, 10)) == []
    assert _premium("D2", hired, PayrollRun.thirteenth(2026, 12)) == []


def test_signing_date_boundary_qualifies() -> None:
    """Ten years exactly by 3 October 2023: EUR 40 in an ordinary month."""
    assert _premium("D2", date(2013, 10, 3), PayrollRun.regular(2026, 10)) == [
        Decimal("40.00")
    ]


def test_thirteenth_payment_and_tfr_relevance() -> None:
    """D2 base 1463.33 + premium 40 = 1503.33; 12 + 1 payments = 520/year."""
    premium = _premium("D2", date(2013, 10, 1), PayrollRun.thirteenth(2026, 12))
    assert premium == [Decimal("40.00")]
    level = next(lv for lv in load_ccnl("rsa-aiop").levels if lv.code == "D2")
    assert level.base_salary.value_at(date(2026, 12, 1)) + premium[0] == Decimal(
        "1503.33"
    )
    allowance = next(
        a
        for lv in load_ccnl("rsa-aiop").levels
        if lv.code == "D2"
        for a in lv.fixed_allowances
        if a.code == "PREMIO_ANZIANITA_2023"
    )
    assert allowance.tfr_relevant is True
    assert allowance.months_per_year == 13
    assert allowance.in_service_on == date(2013, 10, 3)


def test_level_f_has_no_premium() -> None:
    """Level F has EUR 0 premium even with more than ten years' service."""
    assert _premium("F", date(2013, 10, 1), PayrollRun.regular(2026, 10)) == []
    assert _premium("F", date(2013, 10, 1), PayrollRun.thirteenth(2026, 12)) == []
