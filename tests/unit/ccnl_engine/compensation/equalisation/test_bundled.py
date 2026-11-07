"""The elemento perequativo of the metalworking CCNLs, end to end.

Federmeccanica, CCNL 5 February 2021, Sez. Quarta Tit. IV Art. 13, printed
pp. 177-178 (sha256
ff182dd8aeb42b15b236c48775030a12720b9affabba460d38e426ec7be5c151);
Unionmeccanica-Confapi, CCNL 3 July 2017, Art. 48, p. 122 (sha256
c3e694dc561879c0b5ef510d0e931a16e3562f073a88e8a06a210fbf00451fad): 485 euro
a year with the June pay to the worker in service on 1 January of a firm
without second-level bargaining, by the months of the year before,
"onnicomprensiva e non incidente sul Tfr".
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
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import EmploymentPeriod, Permanent
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_ENGINE = PayrollEngine.bundled()
_CCNLS = [("metalmeccanico-federmeccanica", "C3"), ("metalmeccanico-confapi", "5")]


def _run(ccnl_id: str, level: str, premium: bool | None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id=ccnl_id,
                level_code=level,
                seniority=new_hire(),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(date(2025, 3, 10)),
            ),
            employer=EmployerProfile(
                headcount=Headcount(20), second_level_premium=premium
            ),
            facts=PeriodFacts(regione="IT-25", comune_belfiore="A005"),
        )
    )


def _bonus(result: PeriodResult) -> list[Decimal]:
    return [i.amount for i in result.pay_items if i.kind == "bonus_earning"]


def _tfr(result: PeriodResult) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account.value == "tfr_accrual"),
        Decimal(0),
    )


@pytest.mark.parametrize(("ccnl_id", "level"), _CCNLS)
def test_the_data_pays_485_a_year_in_june(ccnl_id: str, level: str) -> None:
    """The element of the CCNL data: 485 a year, June, a month past 15 days."""
    element = load_ccnl(ccnl_id).parameters.equalisation_element
    assert element is not None
    assert (element.yearly, element.paid_in_month, element.month_min_days) == (
        Decimal(485),
        6,
        16,
    )


@pytest.mark.parametrize(("ccnl_id", "level"), _CCNLS)
def test_june_pays_the_months_of_the_year_before(ccnl_id: str, level: str) -> None:
    """Hired 10 March 2025: ten months of 2025, 404.17, out of the TFR base.

    The TFR quota falls only by the 0.50% contribution (L. 297/1982 art. 3)
    on the bonus, which enters the INPS base: 2.02.
    """
    without = _run(ccnl_id, level, premium=True)
    result = _run(ccnl_id, level, premium=False)

    assert _bonus(result) == [Decimal("404.17")]
    assert result.period_gross - without.period_gross == Decimal("404.17")
    assert _tfr(without) - _tfr(result) == Decimal("2.02")


@pytest.mark.parametrize(("ccnl_id", "level"), _CCNLS)
def test_an_unstated_firm_leaves_it_out_and_says_so(ccnl_id: str, level: str) -> None:
    """The run names the missing fact second_level_premium."""
    result = _run(ccnl_id, level, premium=None)

    assert _bonus(result) == []
    assert "second_level_premium_unknown" in {i.code for i in result.issues}
