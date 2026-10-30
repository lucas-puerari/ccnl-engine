"""Handlers of a maternity leave and a work injury: deduction, indemnity, top-up.

The run that posts the monthly pay of a month pays the days of the absence
in that month and in the employment (:mod:`.rules`).  It posts the
deduction of the days, the insurer share the employer advances
(``maternity_item``, ``work_injury_item``: outside the INPS and TFR bases)
and the employer pay (``absence_integration_item``: the CCNL top-up and
the waiting period of an injury).  An INAIL indemnity the employer does not
advance is paid by INAIL and not posted; the top-up is still measured on
it.  Every event records one decision of its capability; without the
CCNL treatment the run pays the statutory amounts only and is provisional.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.base.rules import leave_base
from ccnl_engine.absence.insured.inputs import (
    MaternityLeaveEvent,
    PaternityLeaveEvent,
    WorkInjuryEvent,
)
from ccnl_engine.absence.insured.posting.services import post_lines
from ccnl_engine.absence.insured.rules import InsuredPay, injury_pay, maternity_pay
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.event.handlers import (
    EventEffect,
    _EventHandlerCtx,
)
from ccnl_engine.pay_item.services import _ZERO

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.extraordinary.inputs import (
        ExtraordinaryLeaveEvent,
    )
    from ccnl_engine.absence.insured.parental.inputs import ParentalLeaveEvent
    from ccnl_engine.absence.insured.permit.inputs import DisabilityPermitEvent
    from ccnl_engine.absence.insured.services import InsuredTerms

__all__ = [
    "INJURY",
    "MATERNITY",
    "NOT_MODELLED",
    "_handle_maternity_leave",
    "_handle_work_injury",
]

#: Capability of a maternity leave.
MATERNITY = "maternity_leave"
#: Capability of a work injury.
INJURY = "workplace_injury"
#: Issue of an absence whose CCNL treatment the bundle does not hold.
NOT_MODELLED = "insured_absence_ccnl_not_modelled"
#: Maternity paid on the pay of the run: the base of art. 23 is not computed.
MATERNITY_BASE_LIMITATION = "maternity_daily_base"
#: INPS pays a maternity indemnity and the leave states no base.
MATERNITY_BASE_UNKNOWN = "maternity_base_pay_unknown"
_INTEGRATION = "absence_integration_item"


def _span(
    event: MaternityLeaveEvent
    | PaternityLeaveEvent
    | ParentalLeaveEvent
    | DisabilityPermitEvent
    | ExtraordinaryLeaveEvent
    | WorkInjuryEvent,
    terms: InsuredTerms | None,
    feature: str,
) -> tuple[date, date]:
    """Return the days of ``event`` the run pays.

    Returns:
        The days within the employed days of the month.

    Raises:
        InvalidInputError: When the run posts no monthly pay, or the event
            does not touch the employed days of its month.
    """
    employed = None if terms is None else terms.employed
    span = None if employed is None else event.within(*employed)
    if span is None:
        name = type(event).__name__
        msg = (
            f"{name} must be passed to the run that posts the monthly pay of "
            "a month it touches, within the employment"
        )
        raise InvalidInputError(msg, field=name, feature=feature)
    return span


def _decision(
    capability: str,
    terms: InsuredTerms,
    span: tuple[date, date],
    pay: InsuredPay,
    *,
    modelled: bool,
    advanced: bool,
) -> CalculationDecision:
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL if modelled else CalculationStatus.PROVISIONAL,
        reason_code="ccnl_treatment_applied" if modelled else "statutory_only",
        rule=terms.rule,
        rule_version=terms.rule_version,
        inputs={
            "first_day": span[0].isoformat(),
            "last_day": span[1].isoformat(),
            "deduction": pay.deduction,
            "indemnity": pay.indemnity,
            "indemnity_advanced": "yes" if advanced else "no",
            "integration": pay.integration,
            "carenza": pay.carenza,
        },
        source=terms.source,
        amount=(pay.indemnity if advanced else _ZERO) + pay.integration + pay.carenza,
    )


def _not_modelled(capability: str) -> CalculationIssue:
    return CalculationIssue(
        code=NOT_MODELLED,
        message=(
            "the bundle holds no CCNL treatment of this absence: the run pays "
            "the statutory amounts only, without the CCNL top-up"
        ),
        status=CalculationStatus.PROVISIONAL,
        capability=capability,
    )


def _no_quota(capability: str) -> EventEffect:
    return EventEffect(
        issues=[
            CalculationIssue(
                code="insured_absence_without_daily_quota",
                message=(
                    "the CCNL has no daily quota the days of the absence are "
                    "deducted with: nothing is posted"
                ),
                status=CalculationStatus.INCOMPLETE,
                capability=capability,
            )
        ]
    )


def _handle_maternity_leave(
    event: MaternityLeaveEvent, ctx: _EventHandlerCtx
) -> EventEffect:
    """Pay the days of the maternity leave in the month of the run.

    Returns:
        The items, entries, base deltas, decision and issues of the leave.
    """
    terms = ctx.insured
    span = _span(event, terms, MATERNITY)
    if terms is None or terms.pay is None:
        return _no_quota(MATERNITY)
    rules = None if terms.rules is None else terms.rules.maternity
    base = leave_base(
        event.maternity_base_pay,
        terms,
        event.started_on,
        capability=MATERNITY,
        field="MaternityLeaveEvent.maternity_base_pay",
        code=MATERNITY_BASE_UNKNOWN,
        limitation=MATERNITY_BASE_LIMITATION,
    )
    pay = maternity_pay(
        span[0],
        span[1],
        event.started_on,
        terms.pay,
        terms.rates.maternity,
        rules,
        base.rmgg,
    )
    effect = post_lines(
        (
            ("abs", -pay.deduction, _INTEGRATION, pay.units),
            ("inps", pay.indemnity, "maternity_item", Decimal(pay.days)),
            ("intg", pay.integration, _INTEGRATION, Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(
            MATERNITY, terms, span, pay, modelled=rules is not None, advanced=True
        )
    ]
    effect.issues = [] if rules is not None else [_not_modelled(MATERNITY)]
    effect.issues.extend(base.issues)
    effect.limitations = base.limitations
    return effect


def _handle_work_injury(event: WorkInjuryEvent, ctx: _EventHandlerCtx) -> EventEffect:
    """Pay the days of the inability after a work injury in the month of the run.

    Returns:
        The items, entries, base deltas, decision and issues of the injury.
    """
    terms = ctx.insured
    span = _span(event, terms, INJURY)
    if terms is None or terms.pay is None:
        return _no_quota(INJURY)
    rules = None if terms.rules is None else terms.rules.injury
    pay = injury_pay(
        span[0],
        span[1],
        event.injury_on,
        terms.pay,
        terms.hourly_divisor,
        terms.weekly_hours,
        terms.rates.injury,
        rules,
    )
    advanced = (
        rules is not None
        and rules.advanced
        and (terms.permanent or not rules.advanced_permanent_only)
    )
    effect = post_lines(
        (
            ("abs", -pay.deduction, _INTEGRATION, pay.units),
            ("crnz", pay.carenza, _INTEGRATION, pay.carenza_units),
            (
                "inail",
                pay.indemnity if advanced else _ZERO,
                "work_injury_item",
                Decimal(pay.days),
            ),
            ("intg", pay.integration, _INTEGRATION, Decimal(pay.days)),
        ),
        ctx,
    )
    effect.decisions = [
        _decision(
            INJURY, terms, span, pay, modelled=rules is not None, advanced=advanced
        )
    ]
    effect.issues = [] if rules is not None else [_not_modelled(INJURY)]
    return effect
