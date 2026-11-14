"""Ortofrutticoli seasonal staff, CCNL 2024-2027 art. 72 (p. 81).

The 'personale assunto con contratto a tempo determinato stagionale' is paid
the paga conglobata of the hours worked (monthly over 173) and 'una
indennità pari al 34,45% [...] con esclusione di tutte le ore di lavoro
straordinario'; TFR 'nella misura del 7,40% da computarsi su tutte le
somme'. Level 5, January 2026, 1,653.71 a month, 120 hours: 1,653.71 / 173 x
120 = 1,147.08, indemnity 1,147.08 x 0.3445 = 395.17; TFR 7.40% of 1,542.25
= 114.13 less the 0.50% contribution of L. 297/1982 art. 3 (7.71) = 106.42.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import Employment
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.fixed_term.rules import (
    overtime_hours,
    with_fixed_term_pay,
)
from ccnl_engine.employment.fixed_term.inputs import NaspiExclusion
from ccnl_engine.events import OvertimeEvent
from ccnl_engine.inputs import (
    ContributableHours,
    FixedTerm,
    NoPensionFund,
    WorkerCategory,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import employment_only
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

_CCNL_ID = "ortofrutticoli-agrumari"
_SEASONAL = FixedTerm(naspi_exclusion=NaspiExclusion.SEASONAL)


def _pay(contract: FixedTerm) -> dict[str, Decimal]:
    result = regular_period(
        employment=Employment(
            ccnl_id=_CCNL_ID,
            level_code="5",
            category=WorkerCategory.OPERAIO,
            seniority=new_hire(),
            pension_fund=NoPensionFund(),
            contract_type=contract,
        ),
        current_year=employment_only(),
        ordinary_hours_worked=ContributableHours(Decimal(120)),
    )
    return {
        i.item_id.removesuffix("_2026-01-regular"): i.amount for i in result.pay_items
    }


def test_a_seasonal_worker_is_paid_the_hours_and_the_indemnity() -> None:
    """1,147.08 for the hours, 395.17 of indemnity, TFR 106.42."""
    pay = _pay(_SEASONAL)
    assert pay["base_salary"] == Decimal("1147.08")
    assert pay["indennita_stagionale"] == Decimal("395.17")
    assert pay["tfr"] == Decimal("106.42")


def test_another_fixed_term_keeps_the_monthly_pay() -> None:
    """Art. 72 covers the seasonal fixed terms only."""
    pay = _pay(FixedTerm())
    assert pay["base_salary"] == Decimal("1653.71")
    assert "indennita_stagionale" not in pay


def test_the_indemnity_leaves_out_the_overtime() -> None:
    """'con esclusione di tutte le ore di lavoro straordinario'."""
    ccnl = with_fixed_term_pay(load_ccnl(_CCNL_ID), WorkerCategory.OPERAIO, _SEASONAL)
    events = (OvertimeEvent(date(2026, 1, 15), Decimal(10)),)
    assert overtime_hours(ccnl, events) == 0
