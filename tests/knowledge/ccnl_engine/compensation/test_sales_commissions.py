"""Operatori di vendita of the Commercio CCNL paid also by commission.

Protocollo aggiuntivo art. 15: the fixed table, and for the extra months
"la media mensile dei guadagni globali percepiti nei dodici mesi
precedenti"; art. 16: the commissions of the month.  OV1 in 2026: paga base
1257.80, contingenza 530.04.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

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
from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.event.facade import BonusEvent
from ccnl_engine.inputs import Permanent

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

_ENGINE = PayrollEngine.bundled()


def _run(
    run: PayrollRun, *events: BonusEvent, average: Decimal | None = None
) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=run,
            payment_date=date(run.year, run.month, 20),
            employment=Employment(
                ccnl_id="commercio-confcommercio",
                level_code="OV1",
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(events=events, commission_average=average),
        )
    )


def _earning(result: PeriodResult, kind: str) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == kind),
        Decimal(0),
    )


def test_a_commission_is_pay_of_the_period_in_the_tfr_base() -> None:
    """300 of commissions: a commission earning, and more TFR."""
    month = PayrollRun.regular(year=2026, month=3)
    paid = _run(month, BonusEvent(date(2026, 3, 10), Decimal(300), kind="commission"))
    base = _run(month)
    assert _earning(paid, "commission_earning") == Decimal(300)
    assert _earning(paid, "tfr_accrual_item") > _earning(base, "tfr_accrual_item")


def test_the_tredicesima_holds_the_commission_average() -> None:
    """A full year: the tredicesima grows by the whole 400 of average."""
    december = PayrollRun.thirteenth(2026, 12)
    with_average = _run(december, average=Decimal(400)).period_gross
    fixed_only = _run(december, average=Decimal(0)).period_gross
    assert with_average - fixed_only == Decimal(400)


def test_the_commission_average_is_a_fact_of_the_extra_month() -> None:
    """Unstated on a tredicesima of OV1, the run stops: no silent zero."""
    with pytest.raises(MissingRequiredFactError, match="commission_average"):
        _run(PayrollRun.thirteenth(2026, 12))


def test_a_regular_month_needs_no_average() -> None:
    """The average belongs to the extra months only."""
    assert _run(PayrollRun.regular(year=2026, month=3)).period_gross > 0


@pytest.mark.parametrize("code", ["OV1", "OV2"])
def test_the_table_meets_the_guarantee_of_art_217(code: str) -> None:
    """The fixed part with the contingenza is above 105% of the paga base."""
    level = load_ccnl("commercio-confcommercio").level_by_code(code)
    contingenza = next(a for a in level.fixed_allowances if a.code == "CONTINGENZA_EDR")
    for period in level.base_salary.periods:
        if period.value is None:
            continue
        day = period.valid_from
        assert period.value + contingenza.monthly.value_at(
            day
        ) >= period.value * Decimal("1.05")
