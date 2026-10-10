"""The NASpI surcharge in the ``inps_employer`` decision and the issues of a run."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.contribution.services_naspi import ISSUE_CODE
from ccnl_engine.payroll.employment.inputs import FixedTerm, Permanent
from ccnl_engine.payroll.employment.inputs_fixed_term import NaspiExclusion
from ccnl_engine.payroll.period.services import calculate_period
from tests.fixtures.period_requests import period_request

if TYPE_CHECKING:
    from ccnl_engine.payroll.assurance.models_decision import CalculationDecision
    from ccnl_engine.payroll.period.results import PeriodResult


def _run(contract: Permanent | FixedTerm) -> PeriodResult:
    return calculate_period(period_request(contract_type=contract))


def _employer(result: PeriodResult) -> CalculationDecision:
    (decision,) = (d for d in result.decisions if d.capability == "inps_employer")
    return decision


def _naspi_issues(result: PeriodResult) -> list[str | None]:
    return [i.fact for i in result.issues if i.code == ISSUE_CODE]


def test_permanent_decision_says_nothing_of_the_surcharge() -> None:
    """A permanent contract has no surcharge input and no issue."""
    result = _run(Permanent())

    assert "naspi_surcharge" not in _employer(result).inputs
    assert _naspi_issues(result) == []


def test_charged_surcharge_is_recorded() -> None:
    """Metalmeccanico C3, fixed term renewed twice: 1.4% + 2 x 0.5% (c. 28)."""
    contract = FixedTerm(renewals=2, naspi_exclusion=NaspiExclusion.NONE)
    result = _run(contract)
    decision = _employer(result)

    assert decision.inputs["naspi_surcharge"] == "charged"
    assert decision.inputs["naspi_surcharge_rate"] == Decimal("0.024")
    assert decision.inputs["naspi_renewals"] == Decimal(2)
    assert decision.amount is not None
    assert _naspi_issues(result) == []


def test_excluded_surcharge_is_recorded() -> None:
    """A seasonal fixed term (c. 29 lett. b) is charged no surcharge."""
    result = _run(FixedTerm(naspi_exclusion=NaspiExclusion.SEASONAL))
    decision = _employer(result)

    assert decision.inputs["naspi_surcharge"] == "excluded"
    assert decision.inputs["naspi_surcharge_rate"] == Decimal(0)


def test_unknown_exclusion_leaves_the_employer_amount_undetermined() -> None:
    """The decision has no amount, and an incomplete issue names the fact."""
    result = _run(FixedTerm(renewals=0))
    decision = _employer(result)
    (issue,) = (i for i in result.issues if i.code == ISSUE_CODE)

    assert decision.amount is None
    assert decision.status is CalculationStatus.INCOMPLETE
    assert issue.fact == "naspi_exclusion"
    assert issue.status is CalculationStatus.INCOMPLETE
    assert issue.source is not None
