"""AFAM allowances by band of seniority (CCNL Istruzione e Ricerca D3-D6).

From 1.1.2025 the RPD of a docente di prima fascia is 231.28 up to 14 years
of service, 283.91 from 15 to 27, 351.92 from 28; the CIA of an assistente
126.98.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.seniority.inputs import SeniorityFact, SenioritySource


def _allowances(level: str, months: int) -> dict[str, Decimal]:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="afam-aran",
            level_code=level,
            seniority=SeniorityFact(months, date(2026, 3, 1), SenioritySource.PAYSLIP),
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    return {
        i.item_id.rsplit("_", 1)[-1]: i.amount
        for i in result.pay_items
        if i.kind == "fixed_allowance_earning"
    } | {
        "total": sum(
            (i.amount for i in result.pay_items if i.kind == "fixed_allowance_earning"),
            Decimal(0),
        )
    }


@pytest.mark.parametrize(
    ("months", "rpd"),
    [(100, "231.28"), (180, "283.91"), (335, "283.91"), (336, "351.92")],
)
def test_rpd_band_of_the_seniority(months: int, rpd: str) -> None:
    """One RPD band applies, the one of the anzianità di servizio."""
    assert _allowances("DOCENTE_PRIMA_FASCIA", months)["total"] == Decimal(rpd)


def test_cia_of_an_assistente() -> None:
    """The CIA is paid whatever the seniority."""
    assert _allowances("ASSISTENTE", 12)["total"] == Decimal("126.98")


def test_university_tecnologo_positions() -> None:
    """Tabella B2, from 1.3.2026: 0-5 years 34,537.80, 6-11 years 38,661.40.

    With 7 years of service the step of the second position is paid:
    38,661.40 / 12 - 34,537.80 / 12 = 3,221.78 - 2,878.15 = 343.63.
    """
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=2026, month=4),
            payment_date=date(2026, 4, 27),
            ccnl_id="universita-tecnologi-aran",
            level_code="TECNOLOGO",
            seniority=SeniorityFact(84, date(2026, 4, 1), SenioritySource.PAYSLIP),
            opening_state=PeriodState.zero(),
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    by_kind = {i.kind: i.amount for i in result.pay_items}
    assert by_kind["base_salary_earning"] == Decimal("2878.15")
    assert by_kind["seniority_earning"] == Decimal("343.63")
