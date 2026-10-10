"""Split the runs of a competence year into those the bundle can compute."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.contract.identity.rules_validity import rule_scope
from ccnl_engine.errors import MissingRuleError, UnknownLevelError
from ccnl_engine.payroll.year.models_uncovered_run import UncoveredRun

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.year.services_payment import PlannedPayment

__all__ = ["split_covered"]

_FEATURE = "base_salary"


def split_covered(
    ccnl: CCNL,
    level_code: str,
    payments: tuple[PlannedPayment, ...],
    *,
    seniority_stated: bool = False,
) -> tuple[tuple[PlannedPayment, ...], tuple[UncoveredRun, ...]]:
    """Return the payments whose pay tables are in force, and the others.

    The base salary of the level is the first rule every run reads (see
    :func:`~ccnl_engine.payroll.period.services_contract.load_contract`),
    and the seniority amount of the level the next one when the employment
    states a seniority: a run whose competence date has no value of either
    cannot be computed.  Such a run is set aside, so that the year computes
    its other runs on a withholding schedule without it.  When no payment
    is in force, the :class:`~ccnl_engine.errors\
.MissingRuleError` of the first one is raised.

    Returns:
        The payments to compute, in their order, and the runs set aside.

    Raises:
        UnknownLevelError: When the CCNL has no level ``level_code``.
    """
    try:
        level = ccnl.level_by_code(level_code)
    except ValueError:
        raise UnknownLevelError(level_code, ccnl.meta.ccnl_id) from None
    series = [(_FEATURE, level.base_salary)]
    seniority = ccnl.parameters.seniority_increments.amount_by_level.get(level_code)
    if seniority_stated and seniority is not None:
        series.append(("seniority", seniority))
    covered: list[PlannedPayment] = []
    uncovered: list[UncoveredRun] = []
    for planned in payments:
        try:
            for feature, values in series:
                with rule_scope(ruleset=ccnl.meta.ccnl_id, feature=feature):
                    values.value_at(planned.payment.competence)
        except MissingRuleError as error:
            uncovered.append(UncoveredRun.of(planned.payment, error))
        else:
            covered.append(planned)
    if not covered:
        raise uncovered[0].error
    return tuple(covered), tuple(uncovered)
