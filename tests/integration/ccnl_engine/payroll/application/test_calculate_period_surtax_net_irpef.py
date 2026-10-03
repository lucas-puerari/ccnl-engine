"""The IRPEF surtaxes are due only when the net IRPEF is due.

D.Lgs. 446/1997 art. 50 c. 2 (regional) and D.Lgs. 360/1998 art. 1 c. 4
(municipal): the surtax "è dovuta se per lo stesso anno risulta dovuta
l'imposta sul reddito delle persone fisiche, al netto delle detrazioni per
essa riconosciute" and of the foreign tax credit.  A positive gross IRPEF
fully absorbed by the deductions owes no surtax.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    WeeklyHours,
)
from tests.fixtures.legal_examples.irpef_2026 import gross_irpef, net_irpef

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_YEAR = 2026
_FULL_TIME = 40
_ENGINE = PayrollEngine.bundled()


def _run(weekly_hours: int) -> PeriodResult:
    """Return the conguaglio of 2026, the run that determines the surtax.

    Returns:
        The last run of the year, the tredicesima of Metalmeccanico C3.
    """
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=_YEAR,
            employment=Employment(
                ccnl_slug="metalmeccanico-federmeccanica.json",
                level_code="C3",
                weekly_hours=WeeklyHours(weekly_hours),
                full_time_weekly_hours=WeeklyHours(_FULL_TIME),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
            default_facts=PeriodFacts(regione="IT-25", comune_belfiore="F205"),
        )
    )
    return year.period_results[-1]


def _projected_taxable(result: PeriodResult) -> Decimal:
    (decision,) = (
        d
        for d in result.decisions
        if d.capability == "addizionale_regionale" and "component" not in d.inputs
    )
    taxable = decision.inputs["taxable_income"]
    assert isinstance(taxable, Decimal)
    return taxable


def _surtax_reasons(result: PeriodResult) -> list[str]:
    return [
        d.reason_code
        for d in result.decisions
        if d.capability in {"addizionale_regionale", "addizionale_comunale"}
        and "component" not in d.inputs
    ]


def _deferred(result: PeriodResult) -> Decimal:
    return sum(
        (o.plan.original_amount for o in result.closing_state.cash.obligations.surtax),
        Decimal(0),
    )


def test_deductions_absorbing_the_gross_tax_leave_no_surtax() -> None:
    """A 12-hour part-time C3 owes gross IRPEF but no net IRPEF, so no surtax.

    The oracle confirms the premise on the annual income of the conguaglio:
    gross IRPEF above zero, net IRPEF zero (the 1,955 EUR deduction of art. 13
    c. 1 lett. a) TUIR exceeds it).  Before the fix the surtax followed the
    gross IRPEF and was withheld.  Nothing is deferred to 2027 either.
    """
    result = _run(12)
    taxable = _projected_taxable(result)

    assert gross_irpef(taxable) > 0
    assert net_irpef(taxable) == 0
    assert _surtax_reasons(result) == ["no_irpef_due", "no_irpef_due"]
    assert _deferred(result) == 0


def test_net_irpef_due_keeps_the_surtax() -> None:
    """A full-time C3 owes net IRPEF, so both surtaxes are deferred to 2027."""
    result = _run(_FULL_TIME)

    assert net_irpef(_projected_taxable(result)) > 0
    assert "no_irpef_due" not in _surtax_reasons(result)
    assert _deferred(result) > 0
