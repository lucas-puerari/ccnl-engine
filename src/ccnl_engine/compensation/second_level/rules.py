"""Pay the second-level elements of the employer as allowances of the level."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.compensation.second_level.inputs import SecondLevelAgreement
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationStatus,
    DecisionOrigin,
)

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.second_level.inputs import SecondLevelElement
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "CAPABILITY",
    "second_level_decisions",
    "with_second_level_elements",
]

#: Capability of each kind of agreement, as the registry names it.
CAPABILITY = {
    SecondLevelAgreement.COMPANY: "company_supplement",
    SecondLevelAgreement.TERRITORIAL: "territorial_supplement",
}
_MONTHS = 12


def with_second_level_elements(
    ccnl: CCNL,
    level_code: str,
    elements: tuple[SecondLevelElement, ...],
    day: date,
) -> CCNL:
    """Return the CCNL with the elements in force among the allowances of the level.

    Returns:
        ``ccnl`` unchanged when no element applies on ``day``; else a copy
        whose level ``level_code`` pays each applicable element as a fixed
        allowance, scaled by part time, partial months and extra months
        like an allowance of the CCNL.
    """
    paid = tuple(e for e in elements if e.applies_to(level_code, day))
    if not paid:
        return ccnl
    added = tuple(
        Allowance(
            code=e.code,
            description=f"{e.agreement.value} agreement element {e.code}",
            monthly=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date.min, valid_until=None, value=e.monthly
                    ),
                )
            ),
            months_per_year=None if e.extra_months else _MONTHS,
            tfr_relevant=e.tfr_relevant,
            apprenticeship_pct_relevant=False,
        )
        for e in paid
    )
    levels = tuple(
        level.model_copy(update={"fixed_allowances": (*level.fixed_allowances, *added)})
        if level.code == level_code
        else level
        for level in ccnl.levels
    )
    return ccnl.model_copy(update={"levels": levels})


def second_level_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return one decision per element of the employer in force on the run.

    Returns:
        ``caller_supplied_amount`` with the full-time monthly amount, under
        the capability of its kind of agreement and with a caller-supplied
        origin: no bundled source backs the amount.  Nothing for an element
        that does not apply to the level on the competence date.
    """
    return tuple(
        CalculationDecision(
            capability=CAPABILITY[e.agreement],
            status=CalculationStatus.FINAL,
            reason_code="caller_supplied_amount",
            rule=f"request:employer.second_level_elements.{e.code}",
            rule_version="request",
            inputs={
                "fields": "monthly",
                "monthly": str(e.monthly),
                "element": e.code,
                "valid_from": e.valid_from.isoformat(),
                "levels": ",".join(e.levels) or "all",
            },
            amount=Decimal(e.monthly),
            origin=DecisionOrigin.CALLER_SUPPLIED,
        )
        for e in ctx.request.employer.second_level_elements
        if e.applies_to(ctx.request.level_code, ctx.contract.tctx.competence)
    )
