"""Rules and facts of a run that a sickness episode is paid with."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.sickness.models import SicknessHistory

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.models import DailyDivisorMethod
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.compensation.element.types import MonthlyPayChain
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.sickness.base.models import RegimeDailyBase
    from ccnl_engine.sickness.day.models import SickPayRules

__all__ = ["DailyQuota", "SicknessTerms"]


@dataclass(frozen=True)
class DailyQuota:
    """The CCNL daily quota a sick day is deducted and paid with.

    Attributes:
        method: Daily divisor method of the CCNL absence rule.
        divisor: Days (``by_26``, ``by_30``, ``by_month_hours``) or hours
            (``by_hourly``) of one monthly pay.
        daily_hours: Hours of one payable day, ``by_hourly`` only.
    """

    method: DailyDivisorMethod
    divisor: Decimal
    daily_hours: Decimal | None = None


@dataclass(frozen=True)
class SicknessTerms:
    """What a run pays a sickness episode with.

    The defaults describe a run that cannot pay sickness: it posts no
    monthly pay.

    Attributes:
        employed: First and last employed day of the month whose monthly
            pay the run posts; ``None`` when the run posts none.
        history: Episodes recorded by earlier runs.
        counted: Units of the monthly pay deducted by the episodes
            processed earlier in the run.
        rules: INPS and CCNL rules; ``None`` when the CCNL defines no
            sickness rule.
        quota: Daily quota of the CCNL; ``None`` without an absence rule.
        chain: Pay chain of a fully employed month the quota divides.
        rule: Identifier of the CCNL sickness rule.
        rule_version: Version of the CCNL ruleset.
        source: Location of the CCNL sickness rule, if recorded.
        cover_fact: Public fact whose absence leaves INPS cover unknown
            (``category``), ``None`` when cover is known or the bundle has
            no rule for the worker.
        fixed_term: Whether the contract is fixed-term.
        apprentice: Whether the contract is an apprenticeship.
        employee_rate: INPS rate of the worker, which grosses up the INPS
            share of a CCNL integrating the net daily pay.
        category: Category of the worker, which selects the divisor of the
            INPS daily base; ``None`` when unknown.
        monthly_payments: Monthly payments a year of the CCNL, by date
            (``additional_months``), read by the INPS daily base.
        daily_base: The daily base of the INPS regime of the CCNL; ``None``
            for the general one, on the month before the illness.
        paid_by_the_hour: Whether the run pays the worker by the hour
            worked: the sick hours are not among them, so the sick days
            deduct nothing from the pay.
    """

    employed: tuple[date, date] | None = None
    history: SicknessHistory = field(default_factory=SicknessHistory)
    counted: Decimal = Decimal(0)
    rules: SickPayRules | None = None
    quota: DailyQuota | None = None
    chain: MonthlyPayChain | None = None
    rule: str = "work_rules.sickness_rules"
    rule_version: str = "bundle"
    source: SourceLocation | None = None
    cover_fact: str | None = None
    fixed_term: bool = False
    apprentice: bool = False
    employee_rate: Decimal = Decimal(0)
    paid_by_the_hour: bool = False
    category: WorkerCategory | None = None
    monthly_payments: TimeSeries | None = None
    daily_base: RegimeDailyBase | None = None
