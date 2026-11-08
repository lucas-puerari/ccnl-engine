"""Edilizia PMI Confapi ANIEM: 13 payments for the operai, 14 for the impiegati.

Art. 64 (text of 15 April 2025, p. 95): "Per l'anzianità di servizio
maturata dal 1º luglio al 30 giugno dell'anno successivo è dovuto
all'impiegato non in prova un premio annuo nella misura di una mensilità".
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.category_months.rules import with_category_months
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)

if TYPE_CHECKING:
    from decimal import Decimal

_ID = "edilizia-pmi-confapi-aniem"
_JUNE = date(2026, 6, 1)


def _months(category: WorkerCategory | None) -> Decimal:
    ccnl = with_category_months(load_ccnl(_ID), category)
    return ccnl.parameters.additional_months.value_at(_JUNE)


def test_the_impiegati_and_quadri_have_fourteen_payments() -> None:
    """Tredicesima and premio annuo."""
    assert _months(WorkerCategory.IMPIEGATO) == 14
    assert _months(WorkerCategory.QUADRO) == 14


def test_the_operai_keep_thirteen() -> None:
    """No category rule for the operai, nor for an unstated category."""
    assert _months(WorkerCategory.OPERAIO) == 13
    assert _months(None) == 13


def test_the_premio_annuo_of_a_full_year_is_a_monthly_pay() -> None:
    """Hired in 2024: the June 2026 fourteenth pays the whole month."""
    hired = date(2024, 1, 1)
    employment = Employment(
        ccnl_id=_ID,
        level_code="3",
        category=WorkerCategory.IMPIEGATO,
        contract_type=Permanent(),
        employment_period=EmploymentPeriod(hired, None),
        seniority=SeniorityFact.since(hired, SenioritySource.EMPLOYER_RECORDS),
        pension_fund=NoPensionFund(),
    )
    engine = PayrollEngine.bundled()
    employer = EmployerProfile(headcount=Headcount(10))

    def _base(run: PayrollRun) -> Decimal:
        result = engine.calculate_period(
            PeriodInput(
                run=run,
                payment_date=date(2026, 6, 27),
                employment=employment,
                employer=employer,
            )
        )
        return next(i.amount for i in result.pay_items if i.item_id.startswith("base"))

    assert _base(PayrollRun.fourteenth(2026, 6)) == _base(PayrollRun.regular(2026, 6))
