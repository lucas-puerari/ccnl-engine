"""Inputs of the run steps: the variable events and the amounts input.

The steps of :mod:`._pipeline` call these helpers, which gather the run
context into the arguments of the event processing and of the amounts
computation.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _int_value
from ccnl_engine.payroll.application.allocate_events import (
    _process_events,
    worker_facts_of,
)
from ccnl_engine.payroll.application.amounts._domestic import _domestic_hourly_rate
from ccnl_engine.payroll.application.amounts._types import _AmountsInput
from ccnl_engine.payroll.application.handlers._overtime_rate import CCNLOvertimeBands
from ccnl_engine.payroll.application.handlers.benefits import fringe_threshold_of
from ccnl_engine.payroll.application.period._additional_ivs import (
    additional_ivs_position,
)
from ccnl_engine.payroll.application.period._pension_decision import pension_terms
from ccnl_engine.payroll.application.period._sickness import sickness_terms
from ccnl_engine.payroll.application.period._tfr_destination import (
    tfr_treasury_fund,
)
from ccnl_engine.payroll.domain.family import DependentRelationship
from ccnl_engine.payroll.domain.obligations import (
    TRATTAMENTO_RECOVERY,
    ULTERIORE_RECOVERY,
)
from ccnl_engine.payroll.domain.run import RunKind
from ccnl_engine.payroll.service.family.children import (
    children_within_income_limit,
)
from ccnl_engine.payroll.service.irpef import DAYS_IN_YEAR

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.handlers._totals import _EventTotals
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
    from ccnl_engine.tax.domain.family import FamilyDeductionRules
    from ccnl_engine.tax.domain.surtax_rules import SurtaxRules

__all__ = ["amounts_input", "variable_events"]

#: Fact that leaves the children condition of the fringe threshold unknown.
OWN_INCOME = "own_income"


def variable_events(
    ctx: RunContext,
) -> tuple[_EventTotals, tuple[PayItem, ...], tuple[LedgerEntry, ...]]:
    """Post the variable events of the run.

    Returns:
        The event totals, and the items and entries of the events.
    """
    request, opening = ctx.request, ctx.opening
    var_pay = ctx.var_pay_rules
    return _process_events(
        request.events,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.contract.date_ctx,
        ctx.resolver,
        ctx.policy_context,
        fringe_threshold_of(
            var_pay.fringe_benefit,
            var_pay.year,
            with_children=_children_within_limit(ctx),
            missing_fact=None if request.family_composition is None else OWN_INCOME,
        ),
        opening_fringe_ytd=opening.cash.fringe.value,
        opening_fringe_taxed=opening.cash.fringe.taxed,
        pdr_income_ceiling=ctx.var_pay_rules.pdr.income_ceiling,
        rinnovo_regime=ctx.var_pay_rules.rinnovo,
        work_time_regime=ctx.var_pay_rules.notte_festivi_turni,
        opening_work_time_cap=opening.cash.work_time_regime,
        worker_facts=worker_facts_of(request, withholding_agent=ctx.withholding_agent),
        overtime_bands=CCNLOvertimeBands.of(
            ctx.contract.ccnl, ctx.contract.tctx.competence.year
        ),
        sickness=sickness_terms(ctx),
    )


def _children_within_limit(ctx: RunContext) -> bool | None:
    """Return whether a child of the family is within the limit of art. 12 c. 2.

    Returns:
        ``None`` without a family composition or with a child whose own
        income is unknown and none within the limit; ``False`` without a
        child.
    """
    family = ctx.request.family_composition
    if family is None:
        return None
    children = [
        d for d in family.dependents if d.relationship is DependentRelationship.CHILD
    ]
    if not children:
        return False
    year = ctx.fiscal_year
    rules = ctx.repo.load_family_deduction_rules(year)
    return children_within_income_limit(children, rules.children, year)


def amounts_input(
    ctx: RunContext,
    totals: _EventTotals,
    surtax_rules: SurtaxRules | None,
    family_rules: FamilyDeductionRules | None,
    *,
    ivs_ceiling_applies: bool,
) -> _AmountsInput:
    """Gather what the amounts of the run are computed from.

    Returns:
        The input of the amounts computation.
    """
    request, contract = ctx.request, ctx.contract
    fiscal_year = ctx.fiscal_year
    return _AmountsInput(
        monthly_gross=ctx.monthly_gross,
        event_inps_base=totals.inps_base,
        event_tfr_base=totals.tfr_base,
        event_irpef_base=totals.irpef_base,
        event_substitute_base=totals.substitute_base,
        opening=ctx.opening.cash,
        ytd_inps_base=ctx.ytd_inps_base,
        withholding=ctx.withholding,
        upcoming_gross=ctx.upcoming_gross,
        rules=contract.year_rules,
        contract_type=request.contract_type,
        category=ctx.worker_category,
        surtax_rules=surtax_rules,
        regione=request.regione,
        comune_belfiore=request.comune_belfiore,
        family_composition=request.family_composition,
        family_deduction_rules=family_rules,
        current_year=request.current_year,
        ivs_ceiling_applies=ivs_ceiling_applies,
        pdr_rules=ctx.var_pay_rules.pdr,
        weekly_hours=_int_value(request.weekly_hours),
        contributable_hours=_contributable_hours(request),
        domestic_hourly_rate=_domestic_hourly_rate(
            contract.ccnl,
            contract.year_rules,
            ctx.regular_gross,
            contract.tctx.competence,
        ),
        eligible_work_days=_eligible_work_days(ctx),
        recovery_plan=ctx.opening.cash.obligations.recovery_of(
            fiscal_year, TRATTAMENTO_RECOVERY
        ),
        ulteriore_plan=ctx.opening.cash.obligations.recovery_of(
            fiscal_year, ULTERIORE_RECOVERY
        ),
        installment_run=ctx.installment_run,
        withholding_agent=ctx.withholding_agent,
        pension=pension_terms(ctx),
        conguaglio=ctx.conguaglio,
        surtax_obligations=ctx.opening.cash.obligations.surtax,
        run_month=request.period_id.month,
        regular_run=ctx.run_kind is RunKind.REGULAR,
        foreign_taxes=request.prior_year.foreign_taxes,
        deferred_irpef=_deferred_irpef(ctx),
        additional_ivs=additional_ivs_position(ctx),
        tfr_treasury_fund=tfr_treasury_fund(ctx),
    )


def _contributable_hours(request: PeriodCalculationRequest) -> Decimal | None:
    """Return the contributable hours of a domestic run, if stated.

    Returns:
        The value of the request's contributable hours, or ``None``.
    """
    hours = request.contributable_hours
    return None if hours is None else hours.value


def _eligible_work_days(ctx: RunContext) -> int:
    """Return the days of employment in the tax year of the run.

    Returns:
        The days of the employment period in the year, or the whole year
        when the period is not tracked.
    """
    period = ctx.request.employment_period
    return DAYS_IN_YEAR if period is None else period.days_in_year(ctx.fiscal_year)


def _deferred_irpef(ctx: RunContext) -> Decimal:
    """Return the IRPEF a conguaglio of the run's tax year deferred.

    Returns:
        Zero without a deferral of the tax year.
    """
    deferred = ctx.opening.cash.obligations.deferred_of(ctx.fiscal_year)
    return Decimal(0) if deferred is None else deferred.irpef
