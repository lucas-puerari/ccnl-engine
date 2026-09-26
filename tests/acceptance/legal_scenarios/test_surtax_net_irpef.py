"""The IRPEF surtaxes are due only when the net IRPEF is due.

D.Lgs. 446/1997 art. 50 c. 2 (regional) and D.Lgs. 360/1998 art. 1 c. 4
(municipal): the surtax "è dovuta se per lo stesso anno risulta dovuta
l'imposta sul reddito delle persone fisiche, al netto delle detrazioni per
essa riconosciute" and of the foreign tax credit.  A positive gross IRPEF
fully absorbed by the deductions owes no surtax.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import WeeklyHours
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from tests.fixtures.legal_examples.irpef_2026 import gross_irpef, net_irpef

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult

pytestmark = pytest.mark.legal_scenario

_YEAR = 2026
_FULL_TIME = 40


def _run(weekly_hours: int) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(50)),
            period_id=PeriodId(year=_YEAR, month=1),
            payment_date=date(_YEAR, 1, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            opening_state=PeriodState.zero(),
            weekly_hours=WeeklyHours(weekly_hours),
            full_time_weekly_hours=WeeklyHours(_FULL_TIME),
            regione="IT-25",
            comune_belfiore="F205",
        )
    )


def _projected_taxable(result: PeriodResult) -> Decimal:
    (decision,) = (
        d for d in result.decisions if d.capability == "addizionale_regionale"
    )
    taxable = decision.inputs["taxable_income"]
    assert isinstance(taxable, Decimal)
    return taxable


def _surtax_reasons(result: PeriodResult) -> list[str]:
    return [
        d.reason_code
        for d in result.decisions
        if d.capability in {"addizionale_regionale", "addizionale_comunale"}
    ]


def test_deductions_absorbing_the_gross_tax_leave_no_surtax() -> None:
    """A 12-hour part-time C3 owes gross IRPEF but no net IRPEF, so no surtax.

    The oracle confirms the premise on the projected income the run used:
    gross IRPEF above zero, net IRPEF zero (the 1,955 EUR deduction of art. 13
    c. 1 lett. a) TUIR exceeds it).  Before the fix the surtax followed the
    gross IRPEF and was withheld.
    """
    result = _run(12)
    taxable = _projected_taxable(result)

    assert gross_irpef(taxable) > 0
    assert net_irpef(taxable) == 0
    assert _surtax_reasons(result) == ["no_irpef_due", "no_irpef_due"]
    assert result.closing_state.ytd.tax.surtax == 0


def test_net_irpef_due_keeps_the_surtax() -> None:
    """A full-time C3 owes net IRPEF, so both surtaxes are withheld."""
    result = _run(_FULL_TIME)

    assert net_irpef(_projected_taxable(result)) > 0
    assert "no_irpef_due" not in _surtax_reasons(result)
    assert result.closing_state.ytd.tax.surtax > 0
