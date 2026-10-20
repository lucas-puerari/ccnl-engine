"""The payslip voce of a pay item: code, unit, quantity, rate and column."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.pay_item.models import (
    AbsenceDeduction,
    BaseSalaryEarning,
    EmployeeWithholdingItem,
    EmployerContributionItem,
    ExtraMonthEarning,
    FixedAllowanceEarning,
    NightHolidayShiftEarning,
    OvertimeEarning,
    PayItem,
    TaxCreditItem,
)
from ccnl_engine.pay_item.selection.policies import CompetencePeriod
from ccnl_engine.pay_item.voce.rules import VoceSide, VoceUnit

_COMMON: dict[str, Any] = {
    "item_id": "x",
    "competence_period": CompetencePeriod(year=2026, month=3),
    "payment_date": date(2026, 3, 27),
}


@pytest.mark.parametrize(
    ("item", "code", "unit", "quantity", "rate", "side"),
    [
        (
            BaseSalaryEarning(
                **_COMMON, quantity=Decimal(1), amount=Decimal("1257.46")
            ),
            "base_salary_earning",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("1257.46000"),
            VoceSide.EARNING,
        ),
        (
            FixedAllowanceEarning(
                **_COMMON,
                quantity=Decimal(1),
                amount=Decimal("524.22"),
                allowance_code="CONTINGENZA_EDR",
            ),
            "fixed_allowance_earning:CONTINGENZA_EDR",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("524.22000"),
            VoceSide.EARNING,
        ),
        (
            ExtraMonthEarning(
                **_COMMON, quantity=Decimal(1), amount=Decimal(100), month_number=13
            ),
            "extra_month_earning:13",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("100.00000"),
            VoceSide.EARNING,
        ),
        (
            OvertimeEarning(
                **_COMMON,
                quantity=Decimal(4),
                amount=Decimal("62.50"),
                hours=Decimal(4),
            ),
            "overtime_earning",
            VoceUnit.HOURS,
            Decimal(4),
            Decimal("15.62500"),
            VoceSide.EARNING,
        ),
        (
            NightHolidayShiftEarning(
                **_COMMON, quantity=Decimal(1), amount=Decimal(30)
            ),
            "night_holiday_shift_earning",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("30.00000"),
            VoceSide.EARNING,
        ),
        (
            AbsenceDeduction(
                **_COMMON,
                quantity=Decimal(16),
                amount=Decimal(-150),
                absence_days=Decimal(2),
            ),
            "absence_deduction",
            VoceUnit.DAYS,
            Decimal(2),
            Decimal("-75.00000"),
            VoceSide.DEDUCTION,
        ),
        (
            EmployeeWithholdingItem(**_COMMON, quantity=Decimal(0), amount=Decimal(9)),
            "employee_withholding_item",
            VoceUnit.UNITS,
            Decimal(0),
            None,
            VoceSide.DEDUCTION,
        ),
        (
            EmployerContributionItem(**_COMMON, quantity=Decimal(1), amount=Decimal(7)),
            "employer_contribution_item",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("7.00000"),
            VoceSide.EMPLOYER,
        ),
        (
            TaxCreditItem(**_COMMON, quantity=Decimal(1), amount=Decimal(80)),
            "tax_credit_item",
            VoceUnit.UNITS,
            Decimal(1),
            Decimal("80.00000"),
            VoceSide.FIGURATIVE,
        ),
    ],
)
def test_the_voce_of_an_item(
    item: PayItem,
    code: str,
    unit: VoceUnit,
    quantity: Decimal,
    rate: Decimal | None,
    side: VoceSide,
) -> None:
    """Code with its qualifier, the unit it is counted in, rate and column."""
    assert (item.voce_code, item.unit, item.voce_quantity, item.rate, item.side) == (
        code,
        unit,
        quantity,
        rate,
        side,
    )
