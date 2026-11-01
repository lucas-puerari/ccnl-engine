"""The terms a run pays a maternity leave or a work injury with."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.absence.insured.rules import MonthPay
from ccnl_engine.employment.inputs import Permanent
from ccnl_engine.sickness.services import sickness_terms

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.absence.insured.models import (
        InsuredAbsenceRates,
        InsuredAbsenceRules,
    )
    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.models import SourceLocation

__all__ = ["InsuredTerms", "insured_terms"]

#: Full-time weekly hours of an employment that states none.
_DEFAULT_WEEKLY_HOURS = Decimal(40)
_MONTHS = 12


@dataclass(frozen=True)
class InsuredTerms:
    """Rules and facts of the run for the absences an insurer pays.

    Attributes:
        employed: Employed days of the month whose monthly pay the run
            posts; ``None`` when it posts none.
        pay: The pay of the month, ``None`` without a CCNL daily quota.
        rates: The statutory indemnities.
        rules: The CCNL treatment, ``None`` when the CCNL states none.
        hourly_divisor: CCNL monthly hours, for the INAIL daily base.
        weekly_hours: Full-time weekly hours, for the INAIL daily base.
        permanent: Whether the contract is permanent.
        rule: Identifier of the CCNL rule.
        rule_version: Version of the CCNL ruleset.
        source: Location of the CCNL rule, if recorded.
        category: Category of the worker, which selects the maternity base.
        monthly_payments: Monthly payments a year of the CCNL, by date.
        vertical: Whether the employment is a vertical or mixed part time
            (``Employment.work_pattern``).
    """

    employed: tuple[date, date] | None
    pay: MonthPay | None
    rates: InsuredAbsenceRates
    rules: InsuredAbsenceRules | None
    hourly_divisor: Decimal
    weekly_hours: Decimal
    permanent: bool
    rule: str
    rule_version: str
    source: SourceLocation | None = None
    category: WorkerCategory | None = None
    monthly_payments: TimeSeries | None = None
    vertical: bool = False


def insured_terms(ctx: RunContext) -> InsuredTerms:
    """Return the terms of the run for the absences an insurer pays.

    Returns:
        The terms; without a CCNL daily quota their pay is ``None`` and an
        absence posts nothing.
    """
    sick = sickness_terms(ctx)
    ccnl = ctx.contract.ccnl
    competence = ctx.contract.tctx.competence
    work = ccnl.work_rules
    rules = None if work is None else work.insured_absence
    pay = None
    if sick.quota is not None and sick.chain is not None:
        months = ccnl.parameters.additional_months.value_at(competence)
        pay = MonthPay(
            chain=sick.chain,
            quota=sick.quota,
            extra_months=int(months) - _MONTHS,
            employee_rate=sick.employee_rate,
        )
    stated = ctx.request.full_time_weekly_hours
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    record = None
    if rules is not None:
        clause = rules.maternity or rules.injury
        record = None if clause is None else clause.provenance.location
    return InsuredTerms(
        employed=sick.employed,
        pay=pay,
        rates=ctx.repo.load_insured_absence_rates(),
        rules=rules,
        hourly_divisor=ccnl.parameters.hourly_divisor.value_at(competence),
        weekly_hours=_DEFAULT_WEEKLY_HOURS if stated is None else stated.value,
        permanent=isinstance(ctx.request.contract_type, Permanent),
        rule=f"{name}:work_rules.insured_absence",
        rule_version=(
            str(competence.year) if ccnl.ruleset is None else ccnl.ruleset.version
        ),
        source=record,
        category=sick.category,
        monthly_payments=sick.monthly_payments,
        vertical=ctx.request.work_pattern is not None,
    )
