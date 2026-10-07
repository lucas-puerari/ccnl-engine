"""Split the runs of a competence year into those the bundle can compute."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.validity import rule_scope
from ccnl_engine.payroll.domain.uncovered_run import UncoveredRun
from ccnl_engine.shared.domain.errors import MissingRuleError, UnknownLevelError

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.application.year._payments import PlannedPayment

__all__ = ["split_covered"]

_FEATURE = "base_salary"


def split_covered(
    ccnl: CCNL, level_code: str, payments: tuple[PlannedPayment, ...]
) -> tuple[tuple[PlannedPayment, ...], tuple[UncoveredRun, ...]]:
    """Return the payments whose base salary is in force, and the others.

    The base salary of the level is the first rule every run reads (see
    :func:`~ccnl_engine.payroll.application.period._contract.load_contract`):
    a run whose competence date has no base salary cannot be computed.
    Such a run is set aside, so that the year computes its other runs on a
    withholding schedule without it.  When no payment has a base salary,
    the :class:`~ccnl_engine.shared.domain.errors.MissingRuleError` of the
    first one is raised.

    Returns:
        The payments to compute, in their order, and the runs set aside.

    Raises:
        UnknownLevelError: When the CCNL has no level ``level_code``.
    """
    try:
        series = ccnl.level_by_code(level_code).base_salary
    except ValueError:
        raise UnknownLevelError(level_code, ccnl.meta.ccnl_id) from None
    covered: list[PlannedPayment] = []
    uncovered: list[UncoveredRun] = []
    for planned in payments:
        try:
            with rule_scope(ruleset=ccnl.meta.ccnl_id, feature=_FEATURE):
                series.value_at(planned.payment.competence)
        except MissingRuleError as error:
            uncovered.append(UncoveredRun(planned.payment, error))
        else:
            covered.append(planned)
    if not covered:
        raise uncovered[0].error
    return tuple(covered), tuple(uncovered)
