"""Rules and facts of a run that a sickness episode is paid with."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.sickness import SicknessHistory

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.absence import DailyDivisorMethod
    from ccnl_engine.payroll.domain.sick_days import SickPayRules
    from ccnl_engine.payroll.service.types import MonthlyPayChain
    from ccnl_engine.provenance.domain.source import SourceLocation

__all__ = ["DailyQuota", "SicknessTerms"]


@dataclass(frozen=True)
class DailyQuota:
    """The CCNL daily quota a sick day is deducted and paid with.

    Attributes:
        method: Daily divisor method of the CCNL absence rule.
        divisor: Days (``by_26``, ``by_30``) or hours (``by_hourly``) of
            one monthly pay.
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
