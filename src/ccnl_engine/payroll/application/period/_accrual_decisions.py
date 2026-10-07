"""Decisions and rule sources of the extra-month ratei a run counted.

An extra-month run pays the rateo of its window; a run of the termination
month may also liquidate the ratei of the extra months not yet paid.  Each
of these accruals records one ``base_salary`` decision with reason
``extra_month_ratei_counted``: the window, the qualifying months, and the
month-qualification rule they were counted with (threshold, comparison and
whether it is the CCNL clause or the engine default).

The rule is a payable rule of ``base_salary`` only when it decided the
amount: when a month of the window accrued for part of its days.  A window
of whole months counts the same under any threshold.

An absence whose suspension of accrual is not stated counts as accruing.
When counting it as suspending would change the months, the rateo is
undetermined: its decision is provisional, with the reason
``required_fact_missing``, and an issue names ``suspends_accrual``.  The
engine does not decide which absences suspend accrual under the CCNL.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._run_decisions import _ccnl_rule
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.provenance.domain.chain import ProvenanceStatus

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.application.period._rule_lookup import Rule
    from ccnl_engine.payroll.domain.accrual import ExtraMonthAccrual, MonthAccrualRule

__all__ = ["accrual_decisions", "accrual_issue", "accrual_rules", "run_accruals"]

REASON_CODE = "extra_month_ratei_counted"
UNDETERMINED_CODE = "required_fact_missing"
FACT = "suspends_accrual"


def run_accruals(ctx: RunContext) -> tuple[ExtraMonthAccrual, ...]:
    """Return the accruals the run pays: its own rateo, then the settlements.

    Returns:
        The rateo of an extra-month run, if any, and the ratei liquidated
        on the run.
    """
    own = () if ctx.accrual is None else (ctx.accrual,)
    return own + ctx.settlements


def _origin(rule: MonthAccrualRule) -> str:
    """Return where the threshold of ``rule`` comes from.

    Returns:
        ``ccnl`` for a sourced CCNL clause, ``engine_default`` for the
        default applied without one, ``request`` for a rule the caller
        built.
    """
    if rule.provenance is None:
        return "request"
    if rule.provenance.status is ProvenanceStatus.MISSING:
        return "engine_default"
    return "ccnl"


def accrual_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return one decision per accrual the run pays.

    Returns:
        The decisions, in :func:`run_accruals` order; provisional with the
        reason ``required_fact_missing`` for an undetermined accrual.
    """
    contract = ctx.contract
    version = _ccnl_rule(contract.ccnl, contract.tctx.competence.year)[1]
    return tuple(
        CalculationDecision(
            capability="base_salary",
            status=(
                CalculationStatus.PROVISIONAL
                if accrual.undetermined
                else CalculationStatus.FINAL
            ),
            reason_code=UNDETERMINED_CODE if accrual.undetermined else REASON_CODE,
            rule=accrual.rule.rule,
            rule_version=version,
            inputs={
                "kind": accrual.kind.value,
                "window_start": accrual.window.start.isoformat(),
                "window_end": accrual.window.end.isoformat(),
                "months": str(accrual.months),
                "partial_months": str(accrual.partial_months),
                "fraction": accrual.fraction,
                "min_days": str(accrual.rule.min_days),
                "comparison": accrual.rule.comparison.value,
                "rule_origin": _origin(accrual.rule),
            },
            source=(
                None
                if accrual.rule.provenance is None
                else accrual.rule.provenance.location
            ),
        )
        for accrual in run_accruals(ctx)
    )


def accrual_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the missing-fact issue of a rateo an unknown absence changes.

    Returns:
        An incomplete issue naming ``suspends_accrual`` when an accrual the
        run pays is undetermined, else ``None``.
    """
    kinds = [a.kind.value for a in run_accruals(ctx) if a.undetermined]
    if not kinds:
        return None
    return CalculationIssue(
        code="accrual_suspension_unknown",
        message=(
            f"the ratei of {', '.join(kinds)} depend on absences whose "
            "suspension of accrual is not stated: the amounts shown count "
            "them as accruing; state AbsenceEvent.suspends_accrual"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=FACT,
    )


def accrual_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the accrual rules whose threshold decided a rateo of the run.

    Returns:
        One entry per distinct rule with a provenance record that counted
        a window with a partly accrued month.
    """
    rules: dict[str, Rule] = {}
    for accrual in run_accruals(ctx):
        rule = accrual.rule
        if accrual.partial_months and rule.provenance is not None:
            rules.setdefault(rule.rule, (rule.rule, rule.provenance))
    return tuple(rules.values())
