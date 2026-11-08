"""Take the pay a CCNL sets apart for a fixed-term worker."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import FixedTerm
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.working_time.inputs import OvertimeEvent

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.compensation.models import Level
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.sector.models import YearRules

__all__ = [
    "covers",
    "overtime_hours",
    "overtime_tfr",
    "with_fixed_term_pay",
    "with_fixed_term_tfr",
]


def covers(ccnl: CCNL, category: WorkerCategory | None, contract_type: object) -> bool:
    """Whether the CCNL pays this worker by its fixed-term pay.

    Returns:
        ``True`` for a fixed-term worker of a category of
        ``parameters.fixed_term_pay``.
    """
    rule = ccnl.parameters.fixed_term_pay
    return (
        rule is not None
        and isinstance(contract_type, FixedTerm)
        and category in rule.categories
    )


def with_fixed_term_pay(
    ccnl: CCNL, category: WorkerCategory | None, contract_type: object
) -> CCNL:
    """Return ``ccnl`` with the pay of a fixed-term worker it sets apart.

    A fixed-term worker of a category of ``parameters.fixed_term_pay`` is
    paid by its hourly pay, with its monthly payments, and accrues no leave
    (the percentages on the hours stand for the ferie).

    Returns:
        ``ccnl`` unchanged, or a copy with the hourly pay, the monthly
        payments and no leave rules of the fixed-term worker.
    """
    rule = ccnl.parameters.fixed_term_pay
    if rule is None or not covers(ccnl, category, contract_type):
        return ccnl
    parameters = ccnl.parameters.model_copy(
        update={
            "hourly_pay": rule.hourly_pay,
            "additional_months": rule.additional_months,
        }
    )
    work = ccnl.work_rules
    return ccnl.model_copy(
        update={
            "parameters": parameters,
            "work_rules": None
            if work is None
            else work.model_copy(update={"leave_rules": None}),
        }
    )


def with_fixed_term_tfr(
    year_rules: YearRules,
    ccnl: CCNL,
    category: WorkerCategory | None,
    contract_type: object,
    day: date,
) -> YearRules:
    """Return ``year_rules`` with the TFR rate of a fixed-term worker.

    The quota of a worker covered by a ``tfr_rate`` is that share of the
    TFR pay: the divisor becomes its inverse.

    Returns:
        ``year_rules`` unchanged, or a copy whose TFR accrual divisor is
        one over the rate in force on ``day``.
    """
    rule = ccnl.parameters.fixed_term_pay
    if (
        rule is None
        or rule.tfr_rate is None
        or not covers(ccnl, category, contract_type)
    ):
        return year_rules
    rate = rule.tfr_rate.value_at(day)
    tfr = year_rules.tfr.model_copy(update={"accrual_divisor": 1 / rate})
    return year_rules.model_copy(update={"tfr": tfr})


def overtime_hours(ccnl: CCNL, events: Iterable[object]) -> Decimal:
    """Return the overtime hours the percentages of a fixed-term worker add.

    Operai agricoli art. 44: the terzo elemento "viene corrisposto anche per
    le ore straordinarie, festive e notturne, ma nella misura in atto per le
    ore ordinarie".  The ordinary night and holiday hours are already in
    the hours worked; the overtime hours of the run are not.

    Returns:
        The hours of the overtime events when ``ccnl`` pays the run's worker
        by its fixed-term pay (``with_fixed_term_pay`` applied), else 0.
    """
    rule = ccnl.parameters.fixed_term_pay
    if rule is None or ccnl.parameters.hourly_pay != rule.hourly_pay:
        return Decimal(0)
    return sum((e.hours for e in events if isinstance(e, OvertimeEvent)), Decimal(0))


def overtime_tfr(
    ccnl: CCNL, level: Level, events: Iterable[object], day: date
) -> Decimal:
    """Return the TFR of the non-occasional overtime of a fixed-term worker.

    Operai agricoli, art. 58: "per le ore di lavoro non ordinario, svolto
    a titolo non occasionale, tale misura è elevata al 10 per cento del
    salario contrattuale, limitatamente alle anzidette ore".

    Returns:
        ``overtime_tfr_rate`` of the salario of those hours (the base salary
        of ``level`` over the hourly divisor), 0 for a worker the pay does not
        cover or without such overtime.
    """
    rule = ccnl.parameters.fixed_term_pay
    if rule is None or rule.overtime_tfr_rate is None:
        return Decimal(0)
    if ccnl.parameters.hourly_pay != rule.hourly_pay:
        return Decimal(0)
    hours = sum(
        (e.hours for e in events if isinstance(e, OvertimeEvent) and e.non_occasional),
        Decimal(0),
    )
    divisor = ccnl.parameters.hourly_divisor.value_at(day)
    hourly = level.base_salary.value_at(day) / divisor
    return money(hourly * hours * rule.overtime_tfr_rate.value_at(day))
