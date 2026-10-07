"""Capability report of a run against the 2026 registry.

An ordinary month covers every capability that applies to it; the
unsupported ones are not applicable or outside the input.  A run that
closes the employment makes the unsupported residual-leave capability
applicable, and a sickness episode executes a native capability.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import date

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.assurance import BlockerCode, CoverageStatus
from ccnl_engine.payroll.domain.capability_report import (
    CapabilityGapKind,
    CapabilityReport,
    CapabilityScope,
)
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.family import FamilyComposition
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from tests.fixtures.seniority import new_hire
from tests.fixtures.sickness_episode import march_sickness_episode

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026
_RESIDUAL_LEAVE = "termination_residual_leave"


def _req(month: int = 1) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        seniority=new_hire(),
        opening_state=PeriodState.zero(),
    )


def _gap_kinds(request: PeriodCalculationRequest) -> dict[str, CapabilityGapKind]:
    report = calculate_period(request).capability_report
    return {gap.feature: gap.kind for gap in report.gaps}


class TestOrdinaryMonth:
    """An ordinary month leaves no gap: nothing unsupported applies."""

    def test_report_is_complete(self) -> None:
        """With the residence and the family stated: complete, no blocker."""
        stated = replace(
            _req(),
            regione="IT-25",
            comune_belfiore="F205",
            family_composition=FamilyComposition(),
        )
        result = calculate_period(stated)
        assert isinstance(result.capability_report, CapabilityReport)
        assert result.capability_report.catalog_year == _YEAR
        assert result.capability_report.gaps == ()
        assert result.assurance.coverage is CoverageStatus.COMPLETE
        assert not any(
            b.code is BlockerCode.CAPABILITY_NOT_COMPUTED for b in result.blockers
        )

    @pytest.mark.parametrize(
        ("feature", "scope"),
        [
            ("base_salary", CapabilityScope.APPLICABLE),
            ("irpef", CapabilityScope.APPLICABLE),
            ("somma_esente", CapabilityScope.APPLICABLE),
            ("overtime", CapabilityScope.NOT_APPLICABLE),
            ("family_deductions", CapabilityScope.NOT_APPLICABLE),
            (_RESIDUAL_LEAVE, CapabilityScope.NOT_APPLICABLE),
            ("inail", CapabilityScope.OUTSIDE_INPUT),
            ("maternity_leave", CapabilityScope.OUTSIDE_INPUT),
        ],
    )
    def test_scope_of_each_capability(
        self, feature: str, scope: CapabilityScope
    ) -> None:
        """Core stages apply; events, unsupported and absent facts do not."""
        report = calculate_period(_req()).capability_report
        assert report.scope[feature] is scope


class TestClosingRun:
    """A run that closes the employment needs residual leave settled."""

    def test_termination_run_is_incomplete(self) -> None:
        """The unsupported capability applies: a gap and a blocker."""
        request = replace(
            _req(month=3),
            run=PayrollRun(run_kind=RunKind.TERMINATION, month=3, year=2026),
        )
        result = calculate_period(request)
        assert _gap_kinds(request) == {_RESIDUAL_LEAVE: CapabilityGapKind.UNSUPPORTED}
        assert result.assurance.coverage is CoverageStatus.INCOMPLETE
        assert (BlockerCode.CAPABILITY_NOT_COMPUTED, _RESIDUAL_LEAVE) in {
            (b.code, b.feature) for b in result.blockers
        }
        assert not result.is_payable

    def test_employment_ending_in_month_closes_it(self) -> None:
        """A regular run of the month the employment ends in is the last."""
        period = EmploymentPeriod(
            started_on=date(2020, 1, 1), ended_on=date(2026, 3, 15)
        )
        request = replace(_req(month=3), employment_period=period)
        assert _gap_kinds(request) == {_RESIDUAL_LEAVE: CapabilityGapKind.UNSUPPORTED}

    def test_extra_month_run_does_not_close_it(self) -> None:
        """The tredicesima paid in the last month leaves the closing to the payslip."""
        period = EmploymentPeriod(
            started_on=date(2020, 1, 1), ended_on=date(2026, 3, 15)
        )
        run = PayrollRun(run_kind=RunKind.THIRTEENTH, month=3, year=2026)
        request = replace(_req(month=3), employment_period=period, run=run)
        assert _RESIDUAL_LEAVE not in _gap_kinds(request)

    def test_employment_ending_later_does_not(self) -> None:
        """An end date in a later month leaves the run ordinary."""
        period = EmploymentPeriod(
            started_on=date(2020, 1, 1), ended_on=date(2026, 4, 1)
        )
        assert _gap_kinds(replace(_req(month=3), employment_period=period)) == {}


class TestNativeSickness:
    """A sickness episode executes a native capability."""

    def test_sickness_episode_leaves_no_gap(self) -> None:
        """For an operaio INPS cover is known: sickness opens no gap."""
        request = replace(
            _req(month=3),
            events=(march_sickness_episode(),),
            category=WorkerCategory.OPERAIO,
        )
        result = calculate_period(request)
        assert _gap_kinds(request) == {}
        assert result.capability_report.scope["sickness"] is CapabilityScope.APPLICABLE

    def test_unknown_cover_leaves_a_partial_result(self) -> None:
        """Without the category INPS cover is unknown: the result is partial."""
        request = replace(_req(month=3), events=(march_sickness_episode(),))
        result = calculate_period(request)
        assert _gap_kinds(request) == {"sickness": CapabilityGapKind.PARTIAL_RESULT}
        assert not result.is_payable


class TestReportValue:
    """The report is frozen and deterministic."""

    def test_report_is_frozen(self) -> None:
        """Assigning to capability_report raises FrozenInstanceError."""
        result = calculate_period(_req())
        with pytest.raises(FrozenInstanceError):
            result.capability_report = CapabilityReport.empty(_YEAR)  # type: ignore[misc]

    def test_same_request_same_report(self) -> None:
        """capability_report is deterministic for identical requests."""
        req = _req(month=3)
        assert calculate_period(req).capability_report == (
            calculate_period(req).capability_report
        )
