"""Individual pay elements as fixed allowances of the level of a run.

Each :class:`~ccnl_engine.compensation.individual.inputs.IndividualElement`
of the employment joins the fixed allowances of the level, so the pay chain
treats it like a CCNL allowance: part time, a partial month and the ratei
of an extra month scale it, and its flags decide the extra months and the
TFR base.  An apprentice is paid the agreed amount whole: the
apprenticeship percentage reduces the CCNL elements only.

An absorbable element (superminimo assorbibile) is reduced by the
increases of the minimo tabellare of the level from the day its amount is
stated to the competence date of the run, never below zero: the increases
of a renewal replace the individual amount instead of adding to it.  A
cut of the minimo does not raise it.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.compensation.individual.inputs import FEATURE
from ccnl_engine.compensation.models import Allowance
from ccnl_engine.decision.models import CalculationDecision, CalculationStatus
from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.individual.inputs import IndividualElement
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.period.context.services import RunContext

__all__ = [
    "individual_element_decisions",
    "monthly_on",
    "with_individual_elements",
]

_ZERO = Decimal(0)
_MONTHS = 12


def monthly_on(element: IndividualElement, level: Level, day: date) -> Decimal:
    """Return the full-time monthly amount of ``element`` on ``day``.

    Returns:
        The stated amount, less the increase of the minimo of ``level``
        since :attr:`~IndividualElement.as_of` when the element is
        absorbable, never below zero.

    Raises:
        InvalidInputError: When the level has no minimo on the ``as_of``
            day of an absorbable element.
    """
    if not element.absorbable or element.as_of is None:
        return element.monthly
    then = level.base_salary.period_at(element.as_of)
    if then is None or then.value is None:
        msg = (
            f"IndividualElement {element.code!r} is stated on {element.as_of}, "
            f"a day the level {level.code} has no minimo to absorb from"
        )
        raise InvalidInputError(msg, field="IndividualElement.as_of", feature=FEATURE)
    increase = max(_ZERO, level.base_salary.value_at(day) - then.value)
    return max(_ZERO, element.monthly - increase)


def with_individual_elements(
    ccnl: CCNL,
    level_code: str,
    elements: tuple[IndividualElement, ...],
    day: date,
) -> CCNL:
    """Return the CCNL with the elements among the allowances of the level.

    Returns:
        ``ccnl`` unchanged without elements or without the level (the run
        reports the unknown level); else a copy whose level ``level_code``
        pays each element, at its amount on ``day``, as a fixed allowance.
    """
    if not elements:
        return ccnl
    levels = tuple(
        _with(level, elements, day) if level.code == level_code else level
        for level in ccnl.levels
    )
    return ccnl.model_copy(update={"levels": levels})


def _with(level: Level, elements: tuple[IndividualElement, ...], day: date) -> Level:
    added = tuple(
        Allowance(
            code=e.code,
            description=f"individual element {e.code}",
            monthly=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date.min,
                        valid_until=None,
                        value=monthly_on(e, level, day),
                    ),
                )
            ),
            months_per_year=None if e.extra_months else _MONTHS,
            tfr_relevant=e.tfr_relevant,
            apprenticeship_pct_relevant=False,
        )
        for e in elements
    )
    return level.model_copy(
        update={"fixed_allowances": (*level.fixed_allowances, *added)}
    )


def individual_element_decisions(ctx: RunContext) -> tuple[CalculationDecision, ...]:
    """Return one decision per individual element of the run.

    Returns:
        ``individual_element_absorbed`` for an absorbable element the
        increases of the minimo reduced, with the stated amount and the
        amount on the run, else ``individual_element_paid``; the amounts
        are full-time monthly.
    """
    elements = ctx.request.individual_elements
    if not elements:
        return ()
    contract = ctx.contract
    day = contract.tctx.competence
    ccnl = contract.ccnl
    ruleset = ccnl.ruleset
    decisions = []
    for element in elements:
        paid = monthly_on(element, contract.level, day)
        absorbed = paid < element.monthly
        inputs: dict[str, Decimal | str] = {
            "element": element.code,
            "stated": element.monthly,
        }
        if element.as_of is not None:
            inputs["as_of"] = element.as_of.isoformat()
        decisions.append(
            CalculationDecision(
                capability=FEATURE,
                status=CalculationStatus.FINAL,
                reason_code="individual_element_absorbed"
                if absorbed
                else "individual_element_paid",
                rule=f"ccnl/{ccnl.meta.ccnl_id}" if ruleset is None else ruleset.id,
                rule_version=str(day.year) if ruleset is None else ruleset.version,
                inputs=inputs,
                amount=paid,
            )
        )
    return tuple(decisions)
