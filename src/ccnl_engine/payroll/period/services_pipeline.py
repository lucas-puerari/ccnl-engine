"""Steps of one run: events, amounts and decisions.

Each step reads the run context and the outputs of the steps before it;
the credits and the postings follow in :mod:`.period._posting`. The steps
only orchestrate: the inputs they gather come from :mod:`._pipeline_inputs`
and the formulas live in the collaborators they call.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.accrual.services_decision import accrual_decisions
from ccnl_engine.payroll.accrual.services_extra_month_settlement import (
    settle_extra_months,
)
from ccnl_engine.payroll.amount.policies_rounding import contribution_base
from ccnl_engine.payroll.amount.services import _compute_amounts
from ccnl_engine.payroll.amount.services_erc import erc_settlement
from ccnl_engine.payroll.amount.services_renewal_minimum import renewal_minimum
from ccnl_engine.payroll.contribution.policies_assistance import assistance_decision
from ccnl_engine.payroll.contribution.services_ivs_ceiling import (
    IvsCeiling,
    ivs_ceiling_decision,
    run_ivs_ceiling,
)
from ccnl_engine.payroll.contribution.services_minimum_base import run_minimum_base
from ccnl_engine.payroll.contribution.services_pension_decision import (
    pension_decision,
    pension_unresolved,
)
from ccnl_engine.payroll.employment.services_seniority import (
    run_seniority,
    seniority_decision,
)
from ccnl_engine.payroll.period.rules_run_decision import contract_decisions
from ccnl_engine.payroll.period.services_base_decision import (
    base_stage_decisions,
)
from ccnl_engine.payroll.period.services_caller_rule import (
    caller_supplied_decisions,
)
from ccnl_engine.payroll.period.services_check import check_absences_within_pay
from ccnl_engine.payroll.period.services_pipeline_input import (
    amounts_input,
    variable_events,
)
from ccnl_engine.payroll.sickness.validators_month import (
    WITH_UNPAID_ABSENCE,
)
from ccnl_engine.payroll.termination.services_public_tfr_reduction import (
    public_tfr_reduction,
)
from ccnl_engine.payroll.termination.services_tfr_revaluation import (
    tfr_revaluation_decisions,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.amount.facade import PayItem
    from ccnl_engine.payroll.amount.types import _PeriodAmounts
    from ccnl_engine.payroll.assurance.models_decision import CalculationDecision
    from ccnl_engine.payroll.contribution.models_minimum_base import MinimumBase
    from ccnl_engine.payroll.contribution.results import ContributionBreakdown
    from ccnl_engine.payroll.event.handlers_totals import _EventTotals
    from ccnl_engine.payroll.ledger.models import LedgerEntry
    from ccnl_engine.payroll.period.services_run_context import RunContext
    from ccnl_engine.payroll.taxation.results import TaxComputation
    from ccnl_engine.payroll.withholding.models_recovery_plan import RecoveryPlan


@dataclass(frozen=True)
class RunEvents:
    """Variable events and extra-month settlements of the run."""

    totals: _EventTotals
    items: tuple[PayItem, ...]
    entries: tuple[LedgerEntry, ...]


@dataclass(frozen=True)
class RunAmounts:
    """Amounts of the run with their INPS and IRPEF computations."""

    amounts: _PeriodAmounts
    contribution_breakdown: ContributionBreakdown
    tax_computation: TaxComputation
    recovery_plan: RecoveryPlan | None
    ivs_ceiling: IvsCeiling | None
    minimum_base: MinimumBase | None
    whole_euro: bool = True

    def inps_base(self, actual: Decimal) -> Decimal:
        """Return the INPS base of the run: ``actual`` raised to the minimum.

        Returns:
            ``actual``, or the minimum base of the run when it is higher,
            rounded to the whole euro (:func:`contribution_base`).
        """
        minimum = self.minimum_base
        raised = actual if minimum is None else minimum.raise_to_minimum(actual)
        return contribution_base(raised, whole_euro=self.whole_euro)


def run_events(ctx: RunContext) -> RunEvents:
    """Post the variable events and the extra-month settlements of the run.

    Unpaid absences that deduct more than the pay of the run are rejected
    before the settlements are merged.

    Returns:
        The event totals with the settled bases added, and the items and
        entries of events and settlements.
    """
    events = RunEvents(*variable_events(ctx))
    settlement = settle_extra_months(
        ctx.settlements,
        ctx.regular_chain,
        ctx.cp,
        ctx.contract.tctx.payment,
        ctx.run_id,
        ctx.resolver,
        ctx.policy_context,
    )
    erc = erc_settlement(ctx)
    reduction = public_tfr_reduction(ctx, events.totals)
    check_absences_within_pay(
        events.entries,
        ctx.monthly_gross,
        with_sickness=any(i.code == WITH_UNPAID_ABSENCE for i in events.totals.issues),
    )
    totals = reduction.added_to(erc.added_to(settlement.added_to(events.totals)))
    return RunEvents(
        totals,
        events.items + settlement.items + erc.items + reduction.items,
        events.entries + settlement.entries + erc.entries + reduction.entries,
    )


def run_amounts(ctx: RunContext, totals: _EventTotals) -> RunAmounts:
    """Compute contributions, taxable income, IRPEF and surtax of the run.

    The surtax and family deduction rules are loaded only when the employer
    is a withholding agent and the request declares a residence or a family
    composition.

    Returns:
        The amounts of the run and their computations.
    """
    request, fiscal_year = ctx.request, ctx.fiscal_year
    withholds = ctx.withholding_agent
    needs_surtax = withholds and (
        request.regione is not None or request.comune_belfiore is not None
    )
    surtax_rules = ctx.repo.load_surtax_rules(fiscal_year) if needs_surtax else None
    family_rules = (
        ctx.repo.load_family_deduction_rules(fiscal_year)
        if withholds and request.family_composition is not None
        else None
    )
    minimum = run_minimum_base(ctx, totals.inps_base)
    actual = ctx.monthly_gross + totals.inps_base
    inps = ctx.contract.year_rules.inps
    whole_euro = inps is None or inps.base_whole_euro
    ivs = run_ivs_ceiling(
        ctx,
        contribution_base(
            actual if minimum is None else minimum.raise_to_minimum(actual),
            whole_euro=whole_euro,
        ),
    )
    computed = _compute_amounts(
        amounts_input(
            ctx,
            totals,
            surtax_rules,
            family_rules,
            ivs_ceiling_applies=ivs is not None and ivs.applies,
            inps_minimum=None if minimum is None else minimum.minimum,
        )
    )
    return RunAmounts(
        *computed, ivs_ceiling=ivs, minimum_base=minimum, whole_euro=whole_euro
    )


def run_decisions(
    ctx: RunContext, totals: _EventTotals, run: RunAmounts
) -> tuple[CalculationDecision, ...]:
    """Return the base stage, contract, event and tax decisions of the run.

    Returns:
        The base stage decisions, the extra-month ratei counted, the
        contract decisions, the pension fund, the assistance contribution,
        the TFR revaluation and the renewal regime on the minimo, then those
        of the
        events and of the amounts, and last the caller-supplied values of
        the events.
    """
    request, contract = ctx.request, ctx.contract
    amounts = run.amounts
    year = contract.tctx.competence.year
    pension = pension_decision(
        contract.ccnl, amounts.pension, year, unknown=pension_unresolved(ctx)
    )
    assistance = assistance_decision(contract.ccnl, amounts.assistance, year)
    ivs = run.ivs_ceiling
    ivs_decision = () if ivs is None else (ivs_ceiling_decision(ctx, ivs),)
    renewal = renewal_minimum(ctx)
    return (
        base_stage_decisions(ctx, totals, run)
        + ivs_decision
        + accrual_decisions(ctx)
        + contract_decisions(
            contract.ccnl,
            contract.level,
            request.category,
            ctx.worker_category,
            seniority_decision(ctx, run_seniority(ctx)),
            contract.tctx.competence.year,
            ctx.apprenticeship,
        )
        + ((pension,) if pension is not None else ())
        + ((assistance,) if assistance is not None else ())
        + tfr_revaluation_decisions(ctx)
        + (() if renewal is None else (renewal.decision,))
        + totals.decisions
        + amounts.decisions
        + caller_supplied_decisions(request.events, contract.ccnl)
    )
