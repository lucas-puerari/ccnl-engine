"""Seniority of a run: whether it is known, required and what it pays.

The recognised seniority is a fact of the employment
(:class:`~ccnl_engine.payroll.domain.employment_facts.SeniorityFact`),
aged to the first day of the competence month.  It is required only when
the level pays seniority increments to the worker's category, or holds an
allowance gated by months of service.  The run always records a
``seniority`` decision whose reason is one of :data:`REASONS`.

Without a required fact the run leaves the increments and the gated
allowances out of its amounts: the decision carries no amount and an
incomplete issue names the missing fact, so the result is not payable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.period._rule_lookup import contract_rules
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.service.chain import service_gated_allowances
from ccnl_engine.payroll.service.seniority import (
    NOT_APPLICABLE_BY_CONTRACT,
    increments_apply,
)

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal

    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.seniority_fact import (
        SeniorityFact,
    )
    from ccnl_engine.provenance.domain.source import SourceLocation

__all__ = [
    "CAPABILITY",
    "FACT",
    "INCREMENTS_APPLIED",
    "NOT_APPLICABLE_BY_CONTRACT",
    "REASONS",
    "REQUIRED_FACT_MISSING",
    "ZERO_CONFIRMED",
    "RunSeniority",
    "run_seniority",
    "seniority_decision",
    "seniority_months_at",
]

CAPABILITY = "seniority"
FACT = "seniority"
ZERO_CONFIRMED = "zero_confirmed"
INCREMENTS_APPLIED = "increments_applied"
REQUIRED_FACT_MISSING = "required_fact_missing"
#: Every reason a seniority decision can carry.
REASONS = frozenset({
    NOT_APPLICABLE_BY_CONTRACT,
    ZERO_CONFIRMED,
    INCREMENTS_APPLIED,
    REQUIRED_FACT_MISSING,
})
_NONE = "none"


def seniority_months_at(fact: SeniorityFact | None, competence: date) -> int | None:
    """Return the months of recognised service a run counts.

    Returns:
        The months completed by ``competence``, the first day of the
        competence month; ``None`` when the seniority is not known.
    """
    return None if fact is None else fact.months_at(competence)


@dataclass(frozen=True)
class RunSeniority:
    """Whether the seniority of a run is known and needed, and what it pays.

    Attributes:
        fact: Recognised seniority of the request, if supplied.
        months: Months of service the run counts, ``None`` when unknown.
        increments: Whether the level pays increments to the worker.
        gated: Codes of the allowances gated by months of service.
        amount: Seniority amount of the run's pay chain.
        source: Location of the seniority rules of the CCNL.
    """

    fact: SeniorityFact | None
    months: int | None
    increments: bool
    gated: tuple[str, ...]
    amount: Decimal
    source: SourceLocation | None

    @property
    def required(self) -> bool:
        """Whether the pay of the run depends on the seniority."""
        return self.increments or bool(self.gated)

    @property
    def missing(self) -> bool:
        """Whether the run needs a seniority it was not given."""
        return self.fact is None and self.required

    @property
    def reason(self) -> str:
        """Reason code of the seniority decision."""
        if self.missing:
            return REQUIRED_FACT_MISSING
        if not self.increments:
            return NOT_APPLICABLE_BY_CONTRACT
        return INCREMENTS_APPLIED if self.amount else ZERO_CONFIRMED

    def issue(self) -> CalculationIssue | None:
        """Return the missing-fact issue of a run without its seniority.

        Returns:
            An incomplete issue naming ``seniority``, or ``None``.
        """
        if not self.missing:
            return None
        gated = ", ".join(self.gated) or _NONE
        return CalculationIssue(
            code="seniority_unknown",
            message=(
                "the level pays seniority increments or allowances gated by "
                f"months of service (gated: {gated}): without the recognised "
                "seniority they are undetermined, the amounts shown leave "
                "them out"
            ),
            status=CalculationStatus.INCOMPLETE,
            source=self.source,
            fact=FACT,
        )


def run_seniority(ctx: RunContext) -> RunSeniority:
    """Return the seniority of the run of ``ctx``.

    Returns:
        The fact, the months counted, what the level pays by seniority and
        the seniority amount of the chain.
    """
    ccnl, level = ctx.contract.ccnl, ctx.contract.level
    rules = ccnl.parameters.seniority_increments
    request = ctx.request
    return RunSeniority(
        fact=request.seniority,
        months=seniority_months_at(request.seniority, ctx.contract.tctx.competence),
        increments=increments_apply(
            rules,
            level.code,
            ctx.worker_category,
            apprentice=isinstance(request.contract_type, Apprentice),
        ),
        gated=tuple(a.code for a in service_gated_allowances(level, request.roles)),
        amount=ctx.chain.seniority,
        source=None if rules.provenance is None else rules.provenance.location,
    )


def seniority_decision(ctx: RunContext, run: RunSeniority) -> CalculationDecision:
    """Return the decision of the seniority of the run.

    A run without its required seniority is provisional, as the amount it
    shows may change once the fact is supplied; the decision carries no
    amount and the issue names the fact.

    Returns:
        A decision with one of the :data:`REASONS` and, unless the fact is
        missing, the seniority amount of the run.
    """
    ((rule, _provenance),) = contract_rules(ctx)[CAPABILITY]
    ruleset = ctx.contract.ccnl.ruleset
    fact = run.fact
    inputs: dict[str, Decimal | str] = {
        "seniority_months": _NONE if fact is None else str(fact.months),
        "as_of": _NONE if fact is None else fact.as_of.isoformat(),
        "source": _NONE if fact is None else fact.source.value,
        "months_at_run": _NONE if run.months is None else str(run.months),
        "increments_apply": str(run.increments).lower(),
        "gated_allowances": ",".join(run.gated) or _NONE,
    }
    return CalculationDecision(
        capability=CAPABILITY,
        status=(
            CalculationStatus.PROVISIONAL if run.missing else CalculationStatus.FINAL
        ),
        reason_code=run.reason,
        rule=rule,
        rule_version=(
            str(ctx.contract.tctx.competence.year)
            if ruleset is None
            else ruleset.version
        ),
        inputs=inputs,
        source=run.source,
        amount=None if run.missing else run.amount,
    )
