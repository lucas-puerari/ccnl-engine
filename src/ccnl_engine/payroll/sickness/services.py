"""The rules and facts a run pays a sickness episode with.

Only the run that posts the monthly pay of its month pays sick days: a
regular run, or a termination run when the regular run of its month is not
closed (:mod:`~ccnl_engine.payroll.amount.services_proration`).  An
adjustment or extra-month run posts no monthly pay, so an episode passed
to it is rejected and no day is counted twice.

The sick days are deducted and paid with the daily quota of the CCNL
absence rule, the one a partial month is prorated with, on the pay chain of
a fully employed month.  INPS cover follows the INPS rules of the bundle
for the tax sector of the CCNL, the category of the worker and the
contract type.
"""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.absence.models import DailyDivisorMethod
from ccnl_engine.payroll.contribution.rules_rate import resolve_rates
from ccnl_engine.payroll.employment.inputs import Apprentice
from ccnl_engine.payroll.period.models_run import RunKind
from ccnl_engine.payroll.sickness.models import SicknessHistory
from ccnl_engine.payroll.sickness.models_pay_rule import SickPayRules
from ccnl_engine.payroll.sickness.rules_cumulation import SicknessWorker
from ccnl_engine.payroll.sickness.rules_terms import (
    DailyQuota,
    SicknessTerms,
)

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.capability.services_rule_lookup import Rule
    from ccnl_engine.payroll.period.services_run_context import RunContext

__all__ = ["sickness_rules", "sickness_terms"]

_CATEGORY = "category"
_PAYING_KINDS = frozenset({RunKind.REGULAR, RunKind.TERMINATION})
_FIXED_DIVISORS = {
    DailyDivisorMethod.BY_26: Decimal(26),
    DailyDivisorMethod.BY_30: Decimal(30),
}


def _name(ccnl: CCNL) -> str:
    return f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id


def _quota(ccnl: CCNL, day: date) -> DailyQuota | None:
    """Return the daily quota of the CCNL absence rule in force on ``day``.

    Returns:
        The quota, ``None`` without an absence rule, for ``by_25``, whose
        payable days are not defined, or for ``by_hourly`` without the
        hourly divisor or the daily hours.
    """
    rules = None if ccnl.work_rules is None else ccnl.work_rules.absence_rules
    if rules is None or rules.daily_divisor_method is DailyDivisorMethod.BY_25:
        return None
    method = rules.daily_divisor_method
    fixed = _FIXED_DIVISORS.get(method)
    if fixed is not None:
        return DailyQuota(method, fixed)
    period = ccnl.parameters.hourly_divisor.period_at(day)
    divisor = None if period is None else period.value
    if divisor is None or rules.daily_hours is None:
        return None
    return DailyQuota(method, divisor, rules.daily_hours)


def _employed(ctx: RunContext) -> tuple[date, date] | None:
    """Return the employed days of the month whose monthly pay the run posts.

    Returns:
        The employed span of a partial month or the whole month; ``None``
        for a run that posts no monthly pay.
    """
    if ctx.run_kind not in _PAYING_KINDS or ctx.proration.posted_by is not None:
        return None
    if ctx.proration.span is not None:
        return ctx.proration.span
    year, month = ctx.cp.year, ctx.cp.month
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def _worker(ctx: RunContext) -> SicknessWorker:
    """Return the facts of the worker a cumulated treatment is counted with.

    Returns:
        The seniority, the first day of the employment and the first day of
        the known sickness history of the opening state.
    """
    request = ctx.request
    period = request.employment_period
    return SicknessWorker(
        seniority=request.seniority,
        hired_on=None if period is None else period.started_on,
        known_from=ctx.opening.accrual.sickness_known_from,
    )


def sickness_terms(ctx: RunContext) -> SicknessTerms:
    """Return the rules and facts the run pays sickness episodes with.

    Returns:
        The terms of the run; without a CCNL sickness rule their rules are
        ``None`` and an episode posts nothing.
    """
    ccnl = ctx.contract.ccnl
    competence = ctx.contract.tctx.competence
    ccnl_rules = None if ccnl.work_rules is None else ccnl.work_rules.sickness_rules
    rules = None
    cover_fact = None
    if ccnl_rules is not None:
        inps = ctx.repo.load_sick_pay_rates()
        category = ctx.worker_category
        cover = inps.covers(
            str(ccnl.meta.tax_sector),
            None if category is None else str(category),
            ctx.request.contract_type.type,
        )
        rules = SickPayRules(
            inps=inps, inps_cover=cover, ccnl=ccnl_rules, worker=_worker(ctx)
        )
        cover_fact = _CATEGORY if cover is None and category is None else None
    provenance = None if ccnl_rules is None else ccnl_rules.provenance
    return SicknessTerms(
        employed=_employed(ctx),
        history=SicknessHistory(ctx.opening.accrual.sickness_episodes),
        rules=rules,
        quota=_quota(ccnl, competence),
        chain=ctx.regular_chain,
        rule=f"{_name(ccnl)}:work_rules.sickness_rules",
        rule_version=(
            str(competence.year) if ccnl.ruleset is None else ccnl.ruleset.version
        ),
        source=None if provenance is None else provenance.location,
        cover_fact=cover_fact,
        fixed_term=ctx.request.contract_type.type == "fixed_term",
        apprentice=isinstance(ctx.request.contract_type, Apprentice),
        employee_rate=_employee_rate(ctx),
    )


def _employee_rate(ctx: RunContext) -> Decimal:
    """Return the INPS rate of the worker of the run, zero without one.

    Returns:
        The employee rate of the contract and category; zero for domestic
        work, which has no ordinary INPS rates.
    """
    rules = ctx.contract.year_rules
    if rules.inps is None:
        return Decimal(0)
    return resolve_rates(
        rules, ctx.request.contract_type, ctx.worker_category
    ).employee_rate


def sickness_rules(ctx: RunContext) -> tuple[Rule, ...]:
    """Return the rules a sickness episode reads, with their provenance.

    Returns:
        The CCNL sickness and absence rules and the INPS indemnity rules.
    """
    ccnl = ctx.contract.ccnl
    name = _name(ccnl)
    work = ccnl.work_rules
    sickness = None if work is None else work.sickness_rules
    absence = None if work is None else work.absence_rules
    return (
        (
            f"{name}:work_rules.sickness_rules",
            None if sickness is None else sickness.provenance,
        ),
        (
            f"{name}:work_rules.absence_rules",
            None if absence is None else absence.provenance,
        ),
        ("inps/sick-pay-rates:bands", ctx.repo.load_sick_pay_rates().bands_provenance),
    )
