"""Apply a preferential tax regime to the pay item of one event."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.events import (
    BonusEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    ShiftWorkEvent,
)
from ccnl_engine.payroll.domain.ledger import AccountKind, PostingIntent
from ccnl_engine.payroll.service.regime_eligibility import (
    RegimeFacts,
    assess_regime,
    sector_of_tax_sector,
)
from ccnl_engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.preferential_regime import (
        PreferentialTaxRegime,
    )
    from ccnl_engine.payroll.application.handlers._context import _EventHandlerCtx
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount

_ZERO = Decimal(0)

_RegimeEvent = BonusEvent | NightShiftEvent | HolidayWorkEvent | ShiftWorkEvent
_WORK_TIME_EVENTS = (NightShiftEvent, HolidayWorkEvent, ShiftWorkEvent)


@dataclass(frozen=True, slots=True)
class RegimeOutcome:
    """Postings and records of a regime applied to one pay item.

    Attributes:
        intents: Substitute-tax posting, empty when nothing is eligible.
        ordinary_amount: Part of the pay item left to ordinary IRPEF.
        cap_used: Part of the annual cap this pay item consumed; zero for an
            uncapped regime.
        decision: The eligibility decision taken.
        issue: Provisional issue when the eligibility is unknown.
    """

    intents: tuple[PostingIntent, ...]
    ordinary_amount: Decimal
    cap_used: Decimal
    decision: CalculationDecision
    issue: CalculationIssue | None


@dataclass(frozen=True, slots=True)
class _Coverage:
    """The regime covering an event and the cap account it draws on."""

    event: _RegimeEvent
    regime: PreferentialTaxRegime
    cap_account: RegimeCapAccount | None


def _coverage(
    event: object, kind: str, substitute: bool, ctx: _EventHandlerCtx
) -> _Coverage | None:
    """Return the regime covering ``event``, if any.

    A contract-renewal increment is covered when its accounting policy
    routes it to a substitute tax.  A night, holiday or shift supplement is
    covered by the work-time regime whatever the ordinary policy of the
    supplement kind, and draws on the work-time cap account.

    Returns:
        The coverage, or ``None`` when no regime covers the event.
    """
    coverage: _Coverage | None = None
    if isinstance(event, BonusEvent) and substitute and ctx.rinnovo_regime is not None:
        coverage = _Coverage(event, ctx.rinnovo_regime, None)
    elif isinstance(event, _WORK_TIME_EVENTS) and ctx.work_time_regime is not None:
        coverage = _Coverage(event, ctx.work_time_regime, ctx.work_time_cap)
    if coverage is None or kind not in coverage.regime.eligible_kinds:
        return None
    return coverage


def regime_facts(event: _RegimeEvent, ctx: _EventHandlerCtx) -> RegimeFacts:
    """Return the worker facts a regime is checked against.

    Every regime reads the same inputs: the prior-year employment income and
    the written renunciation from the event, the sector from the CCNL tax
    sector of the policy context.

    Returns:
        The facts of ``event``.
    """
    return RegimeFacts(
        prior_income=event.prior_income,
        sector=sector_of_tax_sector(ctx.context.sector),
        waived=event.substitute_tax_waived,
    )


def apply_preferential_regime(
    event: object,
    kind: str,
    substitute: bool,
    ctx: _EventHandlerCtx,
    gross: Decimal,
    policy_id: str,
) -> RegimeOutcome | None:
    """Assess the pay item of ``event`` and post its substitute tax.

    A capped regime only takes the substitute rate on the part of its annual
    cap not yet used this tax year; the excess is ordinary income.

    Args:
        event: The event being handled.
        kind: Pay item kind resolved for the event.
        substitute: Whether the accounting policy routes the kind to a
            substitute tax.
        ctx: Handler context carrying the regimes and the cap account.
        gross: Amount of the pay item.
        policy_id: Accounting policy of the pay item, cited by the posting.

    Returns:
        The outcome, or ``None`` when no regime covers the event.
    """
    coverage = _coverage(event, kind, substitute, ctx)
    if coverage is None:
        return None
    regime, account = coverage.regime, coverage.cap_account
    cap_available = None
    if account is not None and regime.annual_cap is not None:
        cap_available = account.available(regime.annual_cap)
    assessment = assess_regime(
        regime,
        regime_facts(coverage.event, ctx),
        gross,
        ctx.context.year,
        cap_available,
    )
    tax = money(assessment.eligible_amount * regime.flat_tax_rate)
    intents: tuple[PostingIntent, ...] = ()
    if tax > _ZERO:
        intents = (
            PostingIntent(
                entry_id=f"{regime.regime_id}_tax_{ctx.evt_id}",
                source_item_id=ctx.evt_id,
                pay_item_kind=kind,
                account=AccountKind.SUBSTITUTE_TAX,
                amount=tax,
                policy_decision_id=policy_id,
            ),
        )
    return RegimeOutcome(
        intents=intents,
        ordinary_amount=assessment.ordinary_amount,
        cap_used=_ZERO if account is None else assessment.eligible_amount,
        decision=assessment.decision(tax),
        issue=assessment.issue(),
    )
