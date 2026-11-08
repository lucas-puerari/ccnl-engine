"""Take the pay a CCNL sets apart for a fixed-term worker."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.employment.inputs import FixedTerm

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.facade import CCNL
    from ccnl_engine.employment.category.models import WorkerCategory
    from ccnl_engine.sector.models import YearRules

__all__ = ["covers", "with_fixed_term_pay", "with_fixed_term_tfr"]


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
