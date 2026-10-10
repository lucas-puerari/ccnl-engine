"""The agricultural zone of the employer, through the period calculation.

INPS circ. 43/2026 par. 7 cuts the employer contributions of agriculture by
68% in a zona svantaggiata and 75% in a zona particolarmente svantaggiata;
an agricultural employer that does not state its zone is charged the full
rates with a ``missing_fact`` blocker.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.assurance.models import BlockerCode
from ccnl_engine.payroll.employment.inputs_employer import (
    AgriculturalZone,
    EmployerProfile,
    Headcount,
)
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_AGRICOLTURA = ("operai-agricoli-florovivaisti.json", "Area1")
_INDUSTRIA = ("metalmeccanico-federmeccanica.json", "C3")


def _run(contract: tuple[str, str], zone: AgriculturalZone | None) -> PeriodResult:
    ccnl, level = contract
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=ccnl,
            level_code=level,
            category=WorkerCategory.OPERAIO,
            employer=EmployerProfile(headcount=Headcount(10), agricultural_zone=zone),
            opening_state=PeriodState.zero(),
            tfr_treasury_fund=False,
        )
    )


def _zone_blocked(result: PeriodResult) -> bool:
    return (BlockerCode.MISSING_FACT, "agricultural_zone") in {
        (b.code, b.detail) for b in result.blockers
    }


def test_unknown_zone_charges_the_full_rates_and_blocks() -> None:
    """The full rates of an ordinary zone, with a missing fact."""
    unknown = _run(_AGRICOLTURA, None)
    ordinary = _run(_AGRICOLTURA, AgriculturalZone.ORDINARY)
    assert "agricultural_zone_unknown" in {i.code for i in unknown.issues}
    assert _zone_blocked(unknown)
    assert not _zone_blocked(ordinary)
    assert (
        unknown.contribution_breakdown.employer
        == ordinary.contribution_breakdown.employer
    )


def test_mountain_zone_cuts_the_employer_contributions() -> None:
    """75% less of every employer contribution but the 0.30%."""
    ordinary = _run(_AGRICOLTURA, AgriculturalZone.ORDINARY)
    mountain = _run(_AGRICOLTURA, AgriculturalZone.MOUNTAIN)
    assert mountain.contribution_breakdown.employer < (
        ordinary.contribution_breakdown.employer
    )
    assert (
        mountain.contribution_breakdown.employee
        == ordinary.contribution_breakdown.employee
    )


def test_other_sectors_do_not_read_the_zone() -> None:
    """Industria has no zone cut: no issue without the fact."""
    result = _run(_INDUSTRIA, None)
    assert not _zone_blocked(result)
