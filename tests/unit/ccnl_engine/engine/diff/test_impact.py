"""Unit tests for count_affected_scenarios() and _results_differ()."""

from __future__ import annotations

from datetime import date

from ccnl_engine.engine.diff.impact import _results_differ, count_affected_scenarios
from ccnl_engine.engine.payroll.domain.employee import SeniorityByCount
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scenario(
    ccnl_file: str = "metalmeccanico-federmeccanica.json",
    level_code: str = "C2",
    as_of: date = date(2026, 1, 1),
) -> PayrollScenario:
    return PayrollScenario(
        employee=Employee(
            level_code=level_code,
            seniority=SeniorityByCount(0),
        ),
        employment=Employment(
            ccnl=ccnl_file,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            date=as_of,
        ),
    )


# ---------------------------------------------------------------------------
# _results_differ
# ---------------------------------------------------------------------------


class TestResultsDiffer:
    """_results_differ compares two PayrollResult-like objects field by field."""

    def test_identical_results_not_different(self) -> None:
        """Two compute() calls at the same date produce identical results."""
        s = _scenario()
        r1 = compute(s).result
        r2 = compute(s).result
        assert not _results_differ(r1, r2)

    def test_different_results_are_different(self) -> None:
        """Results at two dates straddling a salary change differ."""
        # metalmeccanico has a tranche at 2026-06-01; only 2026 tax data exists
        s_before = _scenario(as_of=date(2026, 1, 1))
        s_after = _scenario(as_of=date(2026, 7, 1))
        r_before = compute(s_before).result
        r_after = compute(s_after).result
        assert _results_differ(r_before, r_after)

    def test_same_tranche_not_different(self) -> None:
        """Results in the same salary tranche are not different."""
        # Both dates fall within 2026-01-01..2026-06-01 (same tranche)
        s1 = _scenario(as_of=date(2026, 1, 1))
        s2 = _scenario(as_of=date(2026, 3, 1))
        r1 = compute(s1).result
        r2 = compute(s2).result
        # Same tranche: no monetary difference
        assert not _results_differ(r1, r2)


# ---------------------------------------------------------------------------
# count_affected_scenarios
# ---------------------------------------------------------------------------


class TestCountAffectedScenarios:
    """count_affected_scenarios returns the number of impacted scenarios."""

    def test_empty_iterable_returns_zero(self) -> None:
        """No scenarios -> count is 0."""
        count = count_affected_scenarios([], date(2022, 1, 1), date(2026, 1, 1))
        assert count == 0

    def test_count_one_affected_scenario(self) -> None:
        """One scenario whose result changes is counted.

        Metalmeccanico has a tranche at 2026-06-01; only 2026 tax data exists.
        """
        scenarios = [_scenario(as_of=date(2026, 1, 1))]
        count = count_affected_scenarios(scenarios, date(2026, 1, 1), date(2026, 7, 1))
        assert count == 1

    def test_unaffected_scenario_not_counted(self) -> None:
        """A scenario whose result is the same both dates is not counted."""
        # Both dates fall in the same salary tranche (2026-01 and 2026-04)
        scenarios = [_scenario(as_of=date(2026, 1, 1))]
        count = count_affected_scenarios(scenarios, date(2026, 1, 1), date(2026, 4, 1))
        assert count == 0

    def test_failing_scenario_is_skipped(self) -> None:
        """A scenario that raises during compute() is silently ignored."""
        # A non-existent CCNL file -> compute() will raise
        scenarios = [_scenario(ccnl_file="nonexistent.json")]
        count = count_affected_scenarios(scenarios, date(2026, 1, 1), date(2026, 7, 1))
        assert count == 0
