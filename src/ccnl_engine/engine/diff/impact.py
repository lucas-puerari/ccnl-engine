"""Scenario impact counting for a RulesDiff.

This module is intentionally decoupled from the test directory.  The caller
assembles a list of :class:`~ccnl_engine.engine.payroll.domain.scenario.\
PayrollScenario` objects (e.g. by loading the reference JSON cases) and
passes them to :func:`count_affected_scenarios`.  The function runs each
scenario twice -- once at *from_date*, once at *to_date* -- by substituting
``Employment.date``, and returns the count of scenarios whose
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.PayrollResult`
differs in any field.
"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.orchestrator import compute

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario


def count_affected_scenarios(
    scenarios: Iterable[PayrollScenario],
    from_date: date,
    to_date: date,
) -> int:
    """Count scenarios whose payroll result changes between two dates.

    Each scenario is run twice: once with ``Employment.date`` set to
    *from_date* and once with *to_date*.  A scenario is *affected* when
    any :class:`~ccnl_engine.engine.payroll.domain.payroll_result.\
PayrollResult` field (other than ``as_of``) differs between the two runs.

    Computation errors for a given scenario are silently skipped (e.g. the
    scenario references a CCNL that pre-dates *from_date*).

    Args:
        scenarios: Iterable of scenarios to test.  May be empty.
        from_date: Reference date for the *before* state.
        to_date: Reference date for the *after* state.

    Returns:
        Number of affected scenarios.
    """
    count = 0
    for scenario in scenarios:
        pair = _compute_pair(scenario, from_date, to_date)
        if pair is not None and _results_differ(*pair):
            count += 1
    return count


def _compute_pair(
    scenario: PayrollScenario,
    from_date: date,
    to_date: date,
) -> tuple[PayrollResult, PayrollResult] | None:
    """Run *scenario* at both dates.

    Returns:
        A ``(before, after)`` result pair, or ``None`` if either run fails.
    """
    before_employment = dataclasses.replace(scenario.employment, date=from_date)
    after_employment = dataclasses.replace(scenario.employment, date=to_date)
    before_scenario = dataclasses.replace(scenario, employment=before_employment)
    after_scenario = dataclasses.replace(scenario, employment=after_employment)
    try:
        before_result = compute(before_scenario).result
        after_result = compute(after_scenario).result
    except Exception:  # noqa: BLE001
        return None
    return before_result, after_result


def _results_differ(before: PayrollResult, after: PayrollResult) -> bool:
    """Return True if any field other than ``as_of`` differs.

    Returns:
        ``True`` when the results differ in at least one monetary field.
    """
    before_dict = {k: v for k, v in dataclasses.asdict(before).items() if k != "as_of"}
    after_dict = {k: v for k, v in dataclasses.asdict(after).items() if k != "as_of"}
    return before_dict != after_dict
