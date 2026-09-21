"""Gross, work-rules, and extra-month pay-item builders."""

from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.item_producer_policy import _resolve
from ccnl_engine.engine.payroll.domain.pay_items import (
    AbsenceDeduction,
    BaseSalaryEarning,
    BonusEarning,
    CompetencePeriod,
    ExtraMonthEarning,
    FixedAllowanceEarning,
    FringeBenefitItem,
    NightHolidayShiftEarning,
    OvertimeEarning,
    SeniorityEarning,
    SicknessItem,
    WelfareItem,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.engine.payroll.service.gross import GrossPay
    from ccnl_engine.engine.payroll.service.work_rules import WorkRulesPay

_ZERO = Decimal(0)


def _last_day(as_of: date) -> date:
    last = calendar.monthrange(as_of.year, as_of.month)[1]
    return date(as_of.year, as_of.month, last)


def _period(as_of: date) -> CompetencePeriod:
    return CompetencePeriod(year=as_of.year, month=as_of.month)


def _build_gross_items(
    gross: GrossPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce items from contractual gross-pay chain components.

    Returns:
        List of typed PayItem objects for base salary, seniority, and allowances.
    """
    items: list[PayItem] = []
    if gross.chain.base != _ZERO:
        items.append(
            BaseSalaryEarning(
                item_id=f"base_salary_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=gross.chain.base,
                policy_decision=_resolve("base_salary_earning", as_of),
            )
        )
    if gross.chain.seniority != _ZERO:
        items.append(
            SeniorityEarning(
                item_id=f"seniority_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(gross.count),
                amount=gross.chain.seniority,
                seniority_count=gross.count,
                policy_decision=_resolve("seniority_earning", as_of),
            )
        )
    for allowance, amount in gross.chain.allowances:
        if amount == _ZERO:
            continue
        items.append(
            FixedAllowanceEarning(
                item_id=f"allowance_{allowance.code}_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=amount,
                allowance_code=allowance.code,
                policy_decision=_resolve("fixed_allowance_earning", as_of),
            )
        )
    return items


def _build_work_items(
    work: WorkRulesPay,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce items from work-rules supplements and variable pay.

    Returns:
        List of typed PayItem objects for supplements, absence, and variable pay.
    """
    items: list[PayItem] = []
    if work.overtime_supp != _ZERO:
        items.append(
            OvertimeEarning(
                item_id=f"overtime_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.overtime_supp,
                hours=work.overtime_hours,
                policy_decision=_resolve("overtime_earning", as_of),
            )
        )
    if work.night_supp != _ZERO:
        items.append(
            NightHolidayShiftEarning(
                item_id=f"night_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.night_supp,
                hours=work.night_hours,
                policy_decision=_resolve("night_holiday_shift_earning", as_of),
            )
        )
    if work.holiday_supp != _ZERO:
        items.append(
            NightHolidayShiftEarning(
                item_id=f"holiday_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.holiday_supp,
                hours=work.holiday_hours,
                policy_decision=_resolve("night_holiday_shift_earning", as_of),
            )
        )
    if work.absence_deduction_monthly != _ZERO:
        items.append(
            AbsenceDeduction(
                item_id=f"absence_deduction_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=-work.absence_deduction_monthly,
                absence_days=Decimal(1),
                policy_decision=_resolve("absence_deduction", as_of),
            )
        )
    if work.bonus_annual != _ZERO:
        items.append(
            BonusEarning(
                item_id=f"bonus_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.bonus_annual,
                policy_decision=_resolve("bonus_earning", as_of),
            )
        )
    if work.fringe_benefit_annual != _ZERO:
        items.append(
            FringeBenefitItem(
                item_id=f"fringe_benefit_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.fringe_benefit_annual,
                threshold_annual=work.fringe_benefit_threshold_annual,
                taxable_amount=work.fringe_benefit_taxable_annual,
                policy_decision=_resolve("fringe_benefit_item", as_of),
            )
        )
    if work.welfare_annual != _ZERO:
        items.append(
            WelfareItem(
                item_id=f"welfare_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=work.welfare_annual,
                policy_decision=_resolve("welfare_item", as_of),
            )
        )
    sickness_total = (
        work.sick_inps_indemnity_monthly + work.sick_company_integration_monthly
    )
    if sickness_total != _ZERO:
        items.append(
            SicknessItem(
                item_id=f"sickness_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=sickness_total,
                sick_days=work.sick_days_monthly,
                policy_decision=_resolve("sickness_item", as_of),
            )
        )
    return items


def _build_extra_month_items(
    gross: GrossPay,
    extra_monthly_payments: int,
    period: CompetencePeriod,
    payment: date,
    yymm: str,
    as_of: date,
) -> list[PayItem]:
    """Produce ExtraMonthEarning items for tredicesima and quattordicesima.

    Returns:
        List of ExtraMonthEarning items (0, 1, or 2 entries).
    """
    items: list[PayItem] = []
    amount = gross.gross_monthly
    if amount == _ZERO:
        return items
    for i in range(extra_monthly_payments):
        month_number = 13 + i
        items.append(
            ExtraMonthEarning(
                item_id=f"extra_month_{month_number}_{yymm}",
                competence_period=period,
                payment_date=payment,
                quantity=Decimal(1),
                amount=amount,
                month_number=month_number,
                policy_decision=_resolve("extra_month_earning", as_of),
            )
        )
    return items
