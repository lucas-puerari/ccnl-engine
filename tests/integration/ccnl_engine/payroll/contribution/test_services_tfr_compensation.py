"""Compensations of the TFR conferred, through the period calculation.

D.Lgs. 252/2005 art. 10 and D.L. 203/2005 art. 8: the employer of a worker
whose TFR goes to a pension fund or to the Fondo Tesoreria is exempted from
the Fondo di garanzia contribution and from 0.28 points of the social
contributions (INPS circ. 70/2007 par. 6, circ. 4/2008).  An apprentice
takes the relief only and the run records the
``tfr_compensation_apprentice_guarantee_fund`` limitation.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.employment.models_category import WorkerCategory
from ccnl_engine.payroll.contribution.inputs_pension_fund import PensionFundEnrolment
from ccnl_engine.payroll.contribution.services_tfr_compensation import (
    APPRENTICE_GUARANTEE_FUND,
    GUARANTEE_FUND_COMPONENT,
    RELIEF_COMPONENT,
)
from ccnl_engine.payroll.employment.inputs import Apprentice
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.state.models import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.period.results import PeriodResult

_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_APPRENTICE = Apprentice(months_elapsed=6, track="professionalizzante_36")


def _run(
    ccnl: str = _METALMECCANICO, level: str = "C3", **kwargs: object
) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_slug=ccnl,
            level_code=level,
            employer=EmployerProfile(headcount=Headcount(50)),
            opening_state=PeriodState.zero(),
            **kwargs,  # type: ignore[arg-type]
        )
    )


def _credits(result: PeriodResult) -> dict[str, Decimal]:
    return {
        c.name: c.amount
        for c in result.contribution_breakdown.components
        if c.name in {GUARANTEE_FUND_COMPONENT, RELIEF_COMPONENT}
    }


def _limitations(result: PeriodResult) -> set[str]:
    return {lim.id for lim in result.limitations}


def test_tfr_to_the_treasury_fund_takes_both_compensations() -> None:
    """A worker of industria: Fondo di garanzia 0.20% and 0.28 points."""
    result = _run(tfr_treasury_fund=True)
    found = _credits(result)
    assert set(found) == {GUARANTEE_FUND_COMPONENT, RELIEF_COMPONENT}
    assert all(amount < 0 for amount in found.values())
    assert APPRENTICE_GUARANTEE_FUND not in _limitations(result)


def test_dirigente_industriale_is_exempted_from_its_0_40_rate() -> None:
    """The Fondo di garanzia of a dirigente industriale is 0.40%."""
    result = _run(tfr_treasury_fund=True, category=WorkerCategory.DIRIGENTE)
    base = next(
        c.base
        for c in result.contribution_breakdown.components
        if c.name == GUARANTEE_FUND_COMPONENT
    )
    fund = _credits(result)[GUARANTEE_FUND_COMPONENT]
    assert fund == -(base * Decimal("0.0040")).quantize(Decimal("0.01"))


def test_apprentice_takes_the_relief_and_records_the_limitation() -> None:
    """The Fondo di garanzia share of the apprentice rate is not sourced."""
    result = _run(contract_type=_APPRENTICE, tfr_treasury_fund=True)
    assert set(_credits(result)) == {RELIEF_COMPONENT}
    assert APPRENTICE_GUARANTEE_FUND in _limitations(result)


def test_apprentice_in_a_pension_fund_records_the_limitation() -> None:
    """The TFR paid to the pension fund is conferred as well."""
    enrolment = PensionFundEnrolment("COMETA", Decimal("0.012"), tfr_to_fund=True)
    result = _run(contract_type=_APPRENTICE, pension_fund=enrolment)
    assert APPRENTICE_GUARANTEE_FUND in _limitations(result)


def test_apprentice_keeping_the_tfr_takes_no_compensation() -> None:
    """TFR in the company: no exemption, no limitation."""
    result = _run(contract_type=_APPRENTICE, tfr_treasury_fund=False)
    assert _credits(result) == {}
    assert APPRENTICE_GUARANTEE_FUND not in _limitations(result)


def test_agricoltura_has_no_compensation_rule() -> None:
    """Its rates by contract are not modelled: no exemption, no limitation."""
    result = _run(
        "operai-agricoli-florovivaisti.json",
        "Area1",
        contract_type=Apprentice(months_elapsed=6),
        tfr_treasury_fund=True,
    )
    assert _credits(result) == {}
    assert APPRENTICE_GUARANTEE_FUND not in _limitations(result)
