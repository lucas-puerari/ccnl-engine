"""Scenario impact counting for a RulesDiff.

This module is intentionally decoupled from the test directory.  The caller
assembles a list of :class:`~ccnl_engine.engine.payroll.domain.scenario.\
AnnualEstimateInput` objects (e.g. by loading the reference JSON cases) and
passes them to :func:`count_affected_scenarios`.  The function runs each
scenario twice -- once at *from_date*, once at *to_date* -- by substituting
``Employment.as_of``, and returns an :class:`ImpactResult` with
structured counts so callers can distinguish "no change", "not evaluated",
and "evaluation failed".
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.orchestrator import estimate_annual

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.engine.payroll.domain.payroll_result import AnnualEstimate
    from ccnl_engine.engine.payroll.domain.scenario import AnnualEstimateInput


@dataclass(frozen=True)
class ImpactResult:
    """Structured result of :func:`count_affected_scenarios`.

    Attributes:
        affected: Scenarios whose result differed between the two dates.
        evaluated: Scenarios where both runs completed without error.
        failed: Scenarios where at least one run raised an exception.
    """

    affected: int
    evaluated: int
    failed: int


def count_affected_scenarios(
    scenarios: Iterable[AnnualEstimateInput],
    from_date: date,
    to_date: date,
) -> ImpactResult:
    """Count scenarios whose payroll result changes between two dates.

    Each scenario is run twice: once with ``Employment.as_of`` set to
    *from_date* and once with *to_date*.  A scenario is *affected* when
    any :class:`~ccnl_engine.engine.payroll.domain.payroll_result.\
AnnualEstimate` field (other than ``as_of``) differs between the two runs.

    Computation errors are tracked in ``ImpactResult.failed`` so callers can
    distinguish "no change" from "all scenarios errored".

    Args:
        scenarios: Iterable of scenarios to test.  May be empty.
        from_date: Reference date for the *before* state.
        to_date: Reference date for the *after* state.

    Returns:
        Structured counts: affected, evaluated, and failed scenario counts.
    """
    affected = 0
    evaluated = 0
    failed = 0
    for scenario in scenarios:
        pair = _compute_pair(scenario, from_date, to_date)
        if pair is None:
            failed += 1
        else:
            evaluated += 1
            if _results_differ(*pair):
                affected += 1
    return ImpactResult(affected=affected, evaluated=evaluated, failed=failed)


def _compute_pair(
    scenario: AnnualEstimateInput,
    from_date: date,
    to_date: date,
) -> tuple[AnnualEstimate, AnnualEstimate] | None:
    """Run *scenario* at both dates.

    Returns:
        A ``(before, after)`` result pair, or ``None`` if either run fails.
    """
    before_employment = scenario.employment.model_copy(update={"as_of": from_date})
    after_employment = scenario.employment.model_copy(update={"as_of": to_date})
    before_scenario = scenario.model_copy(update={"employment": before_employment})
    after_scenario = scenario.model_copy(update={"employment": after_employment})
    try:
        before_result = estimate_annual(before_scenario).result
        after_result = estimate_annual(after_scenario).result
    except Exception:  # noqa: BLE001
        return None
    return before_result, after_result


def _results_differ(before: AnnualEstimate, after: AnnualEstimate) -> bool:
    """Return True if any field other than ``as_of`` differs.

    Returns:
        ``True`` when the results differ in at least one monetary field.
    """
    date_keys = {"as_of", "contract_effective_date"}
    before_dict = {
        k: v for k, v in dataclasses.asdict(before).items() if k not in date_keys
    }
    after_dict = {
        k: v for k, v in dataclasses.asdict(after).items() if k not in date_keys
    }
    return before_dict != after_dict
