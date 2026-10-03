"""Eligibility of a run for the IVS massimale, derived from the history.

L. 335/1995 art. 2 c. 18 caps the IVS contribution base at an annual
massimale for workers first enrolled from 1 January 1996 and for those who
opted for the contributory system (art. 1 c. 23).  The massimale itself is
data of the INPS rules of the year, with their provenance.

The engine derives the eligibility from the
:class:`~ccnl_engine.payroll.domain.eligibility.ContributionHistory` of the
request.  Without one, the eligibility only matters when the INPS base of
the year crosses the massimale in this run: below it both branches give the
same contributions.  When it matters, the run computes the uncapped branch
as a simulation, its INPS decisions carry no amount, and an incomplete issue
names the missing fact, so the result is not payable.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._rule_lookup import contract_rules
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.eligibility import CONTRIBUTORY_COHORT_START
from ccnl_engine.payroll.service.contributions import resolve_contributions

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.eligibility import ContributionHistory
    from ccnl_engine.provenance.domain.source import SourceLocation
    from ccnl_engine.tax.domain.ruleset import YearRules

__all__ = [
    "CAPABILITY",
    "FACT",
    "IvsCeiling",
    "ivs_ceiling_decision",
    "resolve_ivs_ceiling",
    "run_ivs_ceiling",
]

CAPABILITY = "ivs_ceiling_eligibility"
FACT = "contribution_history"
_LEGAL_BASIS = "L. 335/1995 art. 2 c. 18; art. 1 c. 23"
CEILING_NOT_REACHED = "ceiling_not_reached"
REQUIRED_FACT_MISSING = "required_fact_missing"


@dataclass(frozen=True)
class IvsCeiling:
    """Whether the massimale of the INPS rules caps the run, and why.

    Attributes:
        ceiling: Massimale of the year from the INPS rules.
        ytd_base: INPS base of the tax year before the run.
        period_base: INPS base of the run.
        history: Contribution history of the request, if supplied.
        source: Location of the INPS rules the massimale is read from.
    """

    ceiling: Decimal
    ytd_base: Decimal
    period_base: Decimal
    history: ContributionHistory | None
    source: SourceLocation | None

    @property
    def reached(self) -> bool:
        """Whether the yearly INPS base exceeds the massimale in this run."""
        return self.ytd_base + self.period_base > self.ceiling

    @property
    def undetermined(self) -> bool:
        """Whether the contributions of the run depend on a missing history."""
        return self.history is None and self.reached

    @property
    def applies(self) -> bool:
        """Whether the run caps the IVS base: never without a history."""
        return self.history is not None and self.history.ivs_ceiling_applies

    @property
    def reason(self) -> str:
        """Reason code of the eligibility decision."""
        if self.history is not None:
            return self.history.ivs_ceiling_basis.value
        return REQUIRED_FACT_MISSING if self.reached else CEILING_NOT_REACHED

    @property
    def status(self) -> CalculationStatus:
        """Provisional while the run simulates the uncapped branch.

        The decision read the massimale and found the history missing: the
        branch it simulates may change once the history is supplied.  The
        undetermined amounts are on the INPS decisions, which are
        incomplete, and on the issue, which names the fact.
        """
        return (
            CalculationStatus.PROVISIONAL
            if self.undetermined
            else CalculationStatus.FINAL
        )

    def issue(self) -> CalculationIssue | None:
        """Return the missing-fact issue of an undetermined eligibility.

        Returns:
            An incomplete issue naming ``contribution_history``, or ``None``.
        """
        if not self.undetermined:
            return None
        return CalculationIssue(
            code="ivs_ceiling_eligibility_unknown",
            message=(
                f"the INPS base of the year crosses the IVS massimale of "
                f"{self.ceiling}: whether it caps the contributions depends on "
                "the first enrolment date and contributory option "
                f"({_LEGAL_BASIS}); the contributions are undetermined, the "
                "amounts shown are the uncapped simulation"
            ),
            status=CalculationStatus.INCOMPLETE,
            source=self.source,
            fact=FACT,
        )


def resolve_ivs_ceiling(
    rules: YearRules,
    history: ContributionHistory | None,
    *,
    ytd_base: Decimal,
    period_base: Decimal,
) -> IvsCeiling | None:
    """Return the IVS massimale eligibility of a run.

    Returns:
        ``None`` when the INPS rules of the year carry no massimale (domestic
        work, or a sector without one in the data).
    """
    inps = rules.inps
    if inps is None or inps.ceiling is None:
        return None
    return IvsCeiling(
        ceiling=inps.ceiling,
        ytd_base=ytd_base,
        period_base=period_base,
        history=history,
        source=None if inps.provenance is None else inps.provenance.location,
    )


def run_ivs_ceiling(ctx: RunContext, event_inps_base: Decimal) -> IvsCeiling | None:
    """Return the IVS massimale eligibility of the run of ``ctx``.

    Returns:
        The eligibility on the YTD and period INPS bases of the run, or
        ``None`` when its INPS rules carry no massimale.
    """
    return resolve_ivs_ceiling(
        ctx.contract.year_rules,
        ctx.request.contribution_history,
        ytd_base=ctx.opening.ytd.earnings.inps_base,
        period_base=ctx.monthly_gross + event_inps_base,
    )


def _flag(value: bool) -> str:
    return str(value).lower()


def _branches(ctx: RunContext, ivs: IvsCeiling) -> dict[str, Decimal | str]:
    """Return the contributions of the run with and without the massimale.

    Returns:
        Employee and employer totals of the capped and uncapped branches.
    """
    branches: dict[str, Decimal | str] = {}
    for name, applies in (("capped", True), ("uncapped", False)):
        breakdown = resolve_contributions(
            ivs.period_base,
            ctx.contract.year_rules,
            ctx.request.contract_type,
            ctx.worker_category,
            ytd_inps_base=ivs.ytd_base,
            ivs_ceiling_applies=applies,
        )
        branches[f"employee_{name}"] = breakdown.employee
        branches[f"employer_{name}"] = breakdown.employer
    return branches


def ivs_ceiling_decision(ctx: RunContext, ivs: IvsCeiling) -> CalculationDecision:
    """Return the decision of the IVS massimale eligibility of the run.

    The rule is the INPS rules block of the year that holds the massimale;
    its source is the provenance of that block.  An undetermined decision
    lists the contributions of both branches.

    Returns:
        A decision without amount, whose reason is the basis of the
        eligibility, ``ceiling_not_reached`` or ``required_fact_missing``.
    """
    rules = ctx.contract.year_rules
    ruleset = rules.inps_ruleset
    ((rule, _provenance),) = contract_rules(ctx)[CAPABILITY]
    history = ivs.history
    inputs: dict[str, Decimal | str] = {
        "first_enrolled_on": (
            "none" if history is None else history.first_enrolled_on.isoformat()
        ),
        "contributory_option": (
            "none" if history is None else _flag(history.contributory_option)
        ),
        "cohort_start": CONTRIBUTORY_COHORT_START.isoformat(),
        "legal_basis": _LEGAL_BASIS,
        "ceiling": ivs.ceiling,
        "ytd_base": ivs.ytd_base,
        "period_base": ivs.period_base,
        "ceiling_applies": "undetermined" if ivs.undetermined else _flag(ivs.applies),
    }
    if ivs.undetermined:
        inputs |= _branches(ctx, ivs)
    return CalculationDecision(
        capability=CAPABILITY,
        status=ivs.status,
        reason_code=ivs.reason,
        rule=rule,
        rule_version=str(rules.year) if ruleset is None else ruleset.version,
        inputs=inputs,
        source=ivs.source,
    )
