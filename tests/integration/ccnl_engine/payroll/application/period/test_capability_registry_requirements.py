"""Required capabilities of the registry on every kind of run.

A withholding employer, residence and family left unknown: every run of
the competence year (regular, thirteenth, the month the employment ends),
an adjustment and a termination run carry a requirement per unknown fact,
and posting an installment of last year's surtax does not decide this
year's.  A stated residence and family resolve them.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest

from ccnl_engine import PayrollEngine, PayrollRun, PeriodFacts, PeriodResult
from ccnl_engine.inputs import EmploymentPeriod
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.results import UnresolvedRequirement
from tests.fixtures.explicit_facts import CONCIA_D2, competence_year, regular_run
from tests.fixtures.imported_surtax import opening_with_2025_surtax

_ENGINE = PayrollEngine.bundled()
_ALL = (
    UnresolvedRequirement("addizionale_regionale", "facts.regione"),
    UnresolvedRequirement("addizionale_comunale", "facts.comune_belfiore"),
    UnresolvedRequirement("family_deductions", "facts.family_composition"),
)
_ENDS_IN_SEPTEMBER = replace(
    CONCIA_D2, employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 9, 20))
)
_ENDS_IN_MARCH = replace(
    CONCIA_D2, employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 3, 31))
)


def _year(
    *, unknown: bool, ends_in_september: bool = False
) -> tuple[PeriodResult, ...]:
    plan = competence_year(
        employment=_ENDS_IN_SEPTEMBER if ends_in_september else CONCIA_D2
    )
    if unknown:
        plan = replace(plan, default_facts=PeriodFacts())
    return _ENGINE.calculate_competence_year(plan).period_results


@pytest.mark.parametrize("ends_in_september", [False, True])
def test_every_run_requires_the_unknown_facts(ends_in_september: bool) -> None:
    """Regular, thirteenth and closing runs each name the three facts."""
    runs = _year(unknown=True, ends_in_september=ends_in_september)
    kinds = {r.run.run_kind for r in runs if r.run is not None}
    assert len(kinds) == 1 + (not ends_in_september)
    assert all(r.capability_report.unresolved == _ALL for r in runs)


def test_stated_facts_leave_no_requirement() -> None:
    """With residence and an empty family stated, nothing is unresolved."""
    assert all(r.capability_report.unresolved == () for r in _year(unknown=False))


def test_an_installment_does_not_decide_the_surtax_of_the_year() -> None:
    """January posts the 2025 surtax installments; residence is still unknown."""
    request = regular_run(
        month=1, facts=PeriodFacts(), opening_state=opening_with_2025_surtax()
    )
    result = _ENGINE.calculate_period(request)
    posted = {d.capability for d in result.decisions if d.amount}
    assert {"addizionale_regionale", "addizionale_comunale"} <= posted
    assert result.capability_report.unresolved == _ALL


@pytest.mark.parametrize("kind", [RunKind.ADJUSTMENT, RunKind.TERMINATION])
def test_off_cycle_runs_require_the_unknown_facts(kind: RunKind) -> None:
    """An adjustment or a termination run after March names the three facts."""
    march = _ENGINE.calculate_period(regular_run(month=3, facts=PeriodFacts()))
    employment = _ENDS_IN_MARCH if kind is RunKind.TERMINATION else CONCIA_D2
    request = replace(
        regular_run(
            month=3,
            employment=employment,
            facts=PeriodFacts(),
            opening_state=march.closing_state,
        ),
        run=PayrollRun(run_kind=kind, month=3, year=2026),
        payment_date=date(2026, 3, 31),
    )
    assert _ENGINE.calculate_period(request).capability_report.unresolved == _ALL
