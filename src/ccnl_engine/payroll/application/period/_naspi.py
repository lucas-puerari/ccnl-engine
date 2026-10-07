"""NASpI surcharge of the run of a context, and its issue.

The rule is in :mod:`~ccnl_engine.payroll.service.naspi_surcharge`.  A run
whose surcharge depends on a fact the request leaves unknown computes the
employer contributions without exclusion and renewals, and its
``inps_employer`` decision and an incomplete issue naming the fact say that
they are undetermined.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.service.naspi_surcharge import (
    SurchargeReason,
    naspi_surcharge,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._context import RunContext
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.service.naspi_surcharge import NaspiSurcharge

__all__ = ["ISSUE_CODE", "naspi_issue", "run_naspi_surcharge", "with_naspi"]

#: Code of the issue of a run whose NASpI surcharge is undetermined.
ISSUE_CODE = "naspi_surcharge_undetermined"


def run_naspi_surcharge(ctx: RunContext) -> NaspiSurcharge:
    """Return the NASpI surcharge of the run of ``ctx``.

    Returns:
        The surcharge of the contract, category and sector of the run.
    """
    rules = ctx.contract.year_rules
    return naspi_surcharge(
        rules,
        ctx.request.contract_type,
        ctx.worker_category,
        domestic=rules.inps is None,
    )


def naspi_issue(ctx: RunContext) -> CalculationIssue | None:
    """Return the incomplete issue of an undetermined NASpI surcharge.

    Returns:
        An incomplete issue naming the unknown fact, ``None`` when the
        surcharge is determined.
    """
    fact = run_naspi_surcharge(ctx).missing_fact
    if fact is None:
        return None
    provenance = ctx.contract.year_rules.fixed_term_additional_rate_provenance
    return CalculationIssue(
        code=ISSUE_CODE,
        message=(
            "inps_employer: the NASpI surcharge of a fixed-term contract "
            "(L. 92/2012 art. 2 c. 28-29) depends on a fact the request does "
            f"not state ({fact}); the amounts shown charge it as for a "
            "contract with no exclusion and no renewal"
        ),
        status=CalculationStatus.INCOMPLETE,
        source=None if provenance is None else provenance.location,
        fact=fact,
    )


def with_naspi(ctx: RunContext, employer: CalculationDecision) -> CalculationDecision:
    """Return the ``inps_employer`` decision with the NASpI surcharge.

    Returns:
        The decision unchanged for a contract that is not fixed-term, else
        with the surcharge rate and reason in its inputs; incomplete and
        without an amount when the surcharge is undetermined.
    """
    surcharge = run_naspi_surcharge(ctx)
    if surcharge.reason is SurchargeReason.NOT_FIXED_TERM:
        return employer
    inputs = {
        **employer.inputs,
        "naspi_surcharge": surcharge.reason.value,
        "naspi_surcharge_rate": surcharge.rate,
        "naspi_renewals": Decimal(surcharge.renewals),
    }
    if surcharge.missing_fact is None:
        return replace(employer, inputs=inputs)
    return replace(
        employer,
        inputs=inputs,
        status=CalculationStatus.worst((employer.status, CalculationStatus.INCOMPLETE)),
        amount=None,
    )
