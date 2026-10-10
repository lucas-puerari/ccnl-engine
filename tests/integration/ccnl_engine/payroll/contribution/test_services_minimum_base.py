"""Minimum INPS base of a run by qualifica, through the period calculation.

INPS circ. 6/2026 allegato 1, Tabella A: the daily minimum of a qualifica
when above the 58.13 of D.L. 463/1983 art. 7 c. 1 (Agricoltura: impiegato
67.84, dirigente 128.65).  Art. 7 c. 5 keeps the operai agricoli out of the
minimum, and Tabella A still lists 51.70 for them: their runs record the
``inps_minimum_base_exempt_category`` limitation.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.contribution.services_minimum_base import (
    EXEMPT_CATEGORY_FLOOR,
)
from ccnl_engine.payroll.employment.inputs import Apprentice
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.employment.inputs_fact import ContributableHours, WeeklyHours
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_OPERAI = "operai-agricoli-florovivaisti.json"


def _run(ccnl: str, level: str, **kwargs: object) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=ccnl,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(10)),
            opening_state=PeriodState.zero(),
            tfr_treasury_fund=False,
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _limitations(result: PeriodResult) -> set[str]:
    return {lim.id for lim in result.limitations}


def test_operaio_agricolo_records_the_open_floor() -> None:
    """Excluded from the minimum, with the 51.70 of Tabella A unsettled."""
    result = _run(_OPERAI, "Area1", category=WorkerCategory.OPERAIO)
    assert EXEMPT_CATEGORY_FLOOR in _limitations(result)


def test_apprentice_operaio_has_no_open_floor() -> None:
    """Art. 7 c. 5 excludes apprentices as such, whatever the category."""
    result = _run(
        _OPERAI,
        "Area1",
        category=WorkerCategory.OPERAIO,
        contract_type=Apprentice(months_elapsed=6),
    )
    assert EXEMPT_CATEGORY_FLOOR not in _limitations(result)


def test_impiegato_agricolo_keeps_the_minimum() -> None:
    """An impiegato is not excluded: no open floor."""
    result = _run(
        "impiegati-tecnici-agricoli.json", "1", category=WorkerCategory.IMPIEGATO
    )
    assert EXEMPT_CATEGORY_FLOOR not in _limitations(result)


def test_sector_without_minimum_has_no_open_floor() -> None:
    """Domestic work has no ordinary INPS rules and no minimum."""
    result = _run(
        "lavoro-domestico-convivente.json",
        "A",
        weekly_hours=WeeklyHours(40),
        contributable_hours=ContributableHours(Decimal(173)),
    )
    assert EXEMPT_CATEGORY_FLOOR not in _limitations(result)
