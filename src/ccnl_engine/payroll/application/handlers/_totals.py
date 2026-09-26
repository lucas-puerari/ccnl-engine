"""Totals of the events of a run: bases, decisions, issues and features."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application._period_utils import _ZERO
from ccnl_engine.payroll.domain.events import (
    AbsenceEvent,
    ArrearsEvent,
    BilateralFundEvent,
    FringeEvent,
    HolidayWorkEvent,
    NightShiftEvent,
    OvertimeEvent,
    ShiftWorkEvent,
    SickLeaveEvent,
    SicknessCaseEvent,
    TerminationTFREvent,
    WelfareEvent,
)
from ccnl_engine.payroll.domain.ytd_accounts import RegimeCapAccount

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.application.handlers._context import EventEffect
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.ledger import PostingIntent
    from ccnl_engine.payroll.domain.pay_items import PayItem

#: Catalog feature each event type executes.  A bonus has none of its own:
#: its PdR substitute tax is the ``bonus_pdr`` decision of the run.
EVENT_FEATURES: dict[type, str] = {
    OvertimeEvent: "overtime",
    NightShiftEvent: "night_work",
    HolidayWorkEvent: "holiday_work",
    ShiftWorkEvent: "shift_work",
    AbsenceEvent: "absence",
    SickLeaveEvent: "leave",
    SicknessCaseEvent: "sickness",
    FringeEvent: "fringe_benefit",
    WelfareEvent: "welfare",
    ArrearsEvent: "contract_renewal_arrears",
    BilateralFundEvent: "bilateral_funds",
    TerminationTFREvent: "termination_tfr",
}


def _has_effect(effect: EventEffect) -> bool:
    """Return whether a handler posted a non-zero amount or took a decision.

    Returns:
        ``True`` when ``effect`` changes the payslip or records a decision.
    """
    return bool(effect.decisions) or any(i.amount for i in effect.intents)


@dataclass(frozen=True)
class _EventTotals:
    """Aggregated INPS/TFR/IRPEF bases, decisions and issues of the events.

    ``executed_features`` are the catalog features of the events whose
    handler had an effect (see :func:`_has_effect`).
    """

    inps_base: Decimal
    tfr_base: Decimal
    irpef_base: Decimal
    fringe_value: Decimal
    fringe_inps: Decimal
    fringe_irpef: Decimal
    substitute_base: Decimal
    work_time_cap_used: Decimal = _ZERO
    decisions: tuple[CalculationDecision, ...] = ()
    issues: tuple[CalculationIssue, ...] = ()
    executed_features: frozenset[str] = frozenset()


@dataclass
class _EventAccumulator:
    """Running totals of the events of a run, updated after each handler.

    The fringe accumulators and the work-time regime cap feed the context of
    the next event; the rest is summed into :class:`_EventTotals`.
    """

    cumulative_fringe: Decimal
    cumulative_taxed: Decimal
    opening_cap: RegimeCapAccount
    work_time_cap: RegimeCapAccount
    inps: Decimal = _ZERO
    tfr: Decimal = _ZERO
    irpef: Decimal = _ZERO
    substitute: Decimal = _ZERO
    fringe_value: Decimal = _ZERO
    fringe_inps: Decimal = _ZERO
    fringe_irpef: Decimal = _ZERO
    items: list[PayItem] = field(default_factory=list)
    intents: list[PostingIntent] = field(default_factory=list)
    decisions: list[CalculationDecision] = field(default_factory=list)
    issues: list[CalculationIssue] = field(default_factory=list)
    executed: set[str] = field(default_factory=set)

    def add(self, event: WorkEvent, result: EventEffect) -> None:
        """Add the effect of one event handler to the running totals."""
        self.items.extend(result.items)
        self.intents.extend(result.intents)
        self.decisions.extend(result.decisions)
        self.issues.extend(result.issues)
        feature = EVENT_FEATURES.get(type(event))
        if feature is not None and _has_effect(result):
            self.executed.add(feature)
        self.inps += result.inps_delta
        self.tfr += result.tfr_delta
        self.irpef += result.irpef_delta
        self.substitute += result.substitute_delta
        self.fringe_value += result.fringe_value
        self.fringe_inps += result.fringe_inps
        self.fringe_irpef += result.fringe_irpef
        self.work_time_cap = RegimeCapAccount(
            self.work_time_cap.used + result.regime_cap_used
        )
        if result.new_cumulative_fringe is not None:
            self.cumulative_fringe = result.new_cumulative_fringe
        if result.new_cumulative_taxed is not None:
            self.cumulative_taxed = result.new_cumulative_taxed

    def totals(self) -> _EventTotals:
        """Return the aggregated bases, decisions and issues of the events.

        Returns:
            The :class:`_EventTotals` of every event added so far.
        """
        return _EventTotals(
            inps_base=self.inps,
            tfr_base=self.tfr,
            irpef_base=self.irpef,
            fringe_value=self.fringe_value,
            fringe_inps=self.fringe_inps,
            fringe_irpef=self.fringe_irpef,
            substitute_base=self.substitute,
            work_time_cap_used=self.work_time_cap.used - self.opening_cap.used,
            decisions=tuple(self.decisions),
            issues=tuple(self.issues),
            executed_features=frozenset(self.executed),
        )
