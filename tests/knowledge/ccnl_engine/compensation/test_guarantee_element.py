"""The elements of guarantee owed without a company premium, by employer fact.

Circular of the renewal of 28 May 2025, p. 8 (sha256
85fbb0242738a0d34e7549a302c9c4002b5ff257146b3c3aeee10b8a945b7ba6): the
firms that pay no premio per obiettivi pay, level 4, 26.46 a month from 1
November 2023 and 37.04 from 1 January 2027, on 12 monthly payments.
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
    PeriodResult,
)
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()


def _run(premium: bool | None, run: PayrollRun, paid_on: date) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=paid_on,
            employment=Employment(
                ccnl_id="alimentari-pmi-unionalimentari",
                level_code="4",
                seniority=new_hire(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2025, 1, 1)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(20), second_level_premium=premium
            ),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )


def _egr(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if "EGR" in i.item_id]


@pytest.mark.parametrize(("year", "amount"), [(2026, "26.46"), (2027, "37.04")])
def test_a_firm_without_the_premium_pays_the_element(year: int, amount: str) -> None:
    """The amount of the column in force, in a regular month."""
    assert _egr(_run(False, PayrollRun.regular(year, 1), date(year, 1, 27))) == [
        Decimal(amount)
    ]


def test_a_firm_that_pays_the_premium_owes_nothing() -> None:
    """The premium replaces the element."""
    assert _egr(_run(True, PayrollRun.regular(2027, 1), date(2027, 1, 27))) == []


def test_an_unstated_premium_leaves_the_element_out_and_says_so() -> None:
    """The run names the missing fact second_level_premium."""
    result = _run(None, PayrollRun.regular(2027, 1), date(2027, 1, 27))

    assert _egr(result) == []
    assert "second_level_premium_unknown" in {i.code for i in result.issues}


def test_the_element_is_not_paid_on_the_extra_months() -> None:
    """'erogati per 12 mensilità': nothing on the tredicesima."""
    assert _egr(_run(False, PayrollRun.thirteenth(2026, 12), date(2026, 12, 15))) == []


def _alimentari(premium: bool | None, year: int) -> list[Decimal]:
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, 1),
            payment_date=date(year, 1, 27),
            employment=Employment(
                ccnl_id="alimentari-federalimentare",
                level_code="4",
                seniority=new_hire(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2025, 1, 1)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(20), second_level_premium=premium
            ),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )
    return [i.amount for i in result.pay_items if "MANCATA_CONTRATTAZIONE" in i.item_id]


@pytest.mark.parametrize(
    ("premium", "year", "amount"),
    [(False, 2027, "39.42"), (True, 2027, None), (False, 2026, None)],
    ids=["no-premium-2027", "premium", "before-2027"],
)
def test_alimentari_pays_art_51_bis_from_2027(
    premium: bool, year: int, amount: str | None
) -> None:
    """Level 4: 39.42 from January 2027 to a firm without the premium."""
    expected = [] if amount is None else [Decimal(amount)]
    assert _alimentari(premium, year) == expected
