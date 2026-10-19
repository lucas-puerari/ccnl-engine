"""Operai edili paid by the hour, with the riposi annui and the Cassa Edile.

CCNL edilizia industria of 19 April 2010: the operai are paid the monthly
elements over 173 for the hours worked (Allegato A); Art. 5 B pays the 4.95%
riposi annui with the pay; Art. 18 accrues the 18.5% for ferie and
gratifica natalizia with the Cassa Edile "al netto delle ritenute" by the
criterion of Allegato D: contributions and taxes on the whole gross, 14.2%
of the base withheld from the net.  Both percentages are on the paga base
and the ex contingenza (Art. 24 point 3-4), and in the TFR base (Art. 33).

Operaio comune, level 1, January 2026: minimo 1,067.36, contingenza 512.87,
EDR 10.33.  A full month of 173 hours pays them in full; the base of the
percentages is 1,067.36 + 512.87 = 1,580.23: riposi 78.22, Cassa Edile
292.34, accrual 224.39.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment, InvalidInputError
from ccnl_engine.events import AbsenceEvent, SicknessEpisode
from ccnl_engine.inputs import (
    Apprentice,
    ContributableHours,
    NoPensionFund,
    Permanent,
    WeeklyHours,
    WorkerCategory,
)
from tests.knowledge.ccnl_engine.irpef.other_income.builders import (
    employment_only,
)
from tests.knowledge.ccnl_engine.seniority.builders import new_hire
from tests.knowledge.ccnl_engine.support import regular_period

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.events import WorkEvent

pytestmark = pytest.mark.legal_scenario

_OPERAIO = Employment(
    ccnl_id="edilizia-ance",
    level_code="1",
    category=WorkerCategory.OPERAIO,
    seniority=new_hire(),
    pension_fund=NoPensionFund(),
    contract_type=Permanent(),
)


def _january(
    hours: Decimal | None,
    employment: Employment = _OPERAIO,
    events: tuple[WorkEvent, ...] = (),
) -> PeriodResult:
    return regular_period(
        employment=employment,
        events=events,
        current_year=employment_only(),
        ordinary_hours_worked=None if hours is None else ContributableHours(hours),
    )


def _kind(result: PeriodResult, kind: str) -> Decimal:
    return sum(
        (i.amount for i in result.pay_items if i.kind == kind),
        Decimal(0),
    )


def _item(result: PeriodResult, prefix: str) -> Decimal:
    (item,) = [i for i in result.pay_items if i.item_id.startswith(prefix)]
    return item.amount


def _account(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def test_full_month_pays_the_monthly_elements_and_both_percentages() -> None:
    """173 hours: the table in full, riposi 78.22 and Cassa Edile 292.34."""
    result = _january(Decimal(173))

    assert _kind(result, "base_salary_earning") == Decimal("1067.36")
    assert _kind(result, "fixed_allowance_earning") == Decimal("523.20")
    assert _item(result, "riposi_annui_") == Decimal("78.22")
    assert _item(result, "cassa_edile_2") == Decimal("292.34")
    assert result.period_gross == Decimal("1961.12")


def test_cassa_edile_is_withheld_net_of_contributions_and_taxes() -> None:
    """Allegato D: net = gross - contributions - taxes - 14.2% accrual."""
    result = _january(Decimal(173))
    accrual = _account(result, "bilateral_fund_employee")
    taxes = (
        _account(result, "ordinary_tax")
        + _account(result, "surtax")
        - _account(result, "tax_refunds")
        - _account(result, "credits")
    )

    assert accrual == Decimal("224.39")
    assert _item(result, "cassa_edile_accrual_") == accrual
    assert result.period_net == (
        result.period_gross
        - _account(result, "employee_contributions")
        - taxes
        - accrual
    )
    # Of the 18.5% the pay keeps only the 4.3% that covers its withholdings.
    assert _item(result, "cassa_edile_2") - accrual == Decimal("67.95")


def test_employer_cost_keeps_the_accrual() -> None:
    """The employer pays the 18.5% to the worker's account at the Cassa.

    Beside the gross: INPS, TFR and the Prevedi 0.0685 x 173 -> 12.
    """
    result = _january(Decimal(173))

    assert _account(result, "pension_fund_employer") == Decimal(12)
    assert result.period_employer_cost == (
        result.period_gross
        + _account(result, "employer_contributions")
        + _account(result, "tfr_accrual")
        + _account(result, "pension_fund_employer")
    )


def test_percentages_enter_the_tfr_base() -> None:
    """Art. 33: 1,580.23 (the EDR is out) + 78.22 + 292.34 = 1,950.79."""
    result = _january(Decimal(173))
    (tfr,) = [d for d in result.decisions if d.capability == "tfr"]

    assert tfr.inputs["base"] == Decimal("1950.79")


def test_a_month_with_ferie_pays_only_the_hours_worked() -> None:
    """40 hours of ferie, 133 worked: the ferie are the Cassa Edile's.

    Minimo 1,067.36 x 133 / 173 = 820.57, contingenza 394.29, EDR 7.94;
    riposi 4.95% and Cassa Edile 18.5% of 1,214.86: 60.14 and 224.75.
    """
    result = _january(Decimal(133))

    assert _kind(result, "base_salary_earning") == Decimal("820.57")
    assert _kind(result, "fixed_allowance_earning") == Decimal("402.23")
    assert _kind(result, "hourly_percentage_earning") == Decimal("284.89")
    assert _kind(result, "leave_settlement_item") == 0
    assert result.period_gross == Decimal("1507.69")


def test_hours_unknown_leave_the_pay_out_with_a_missing_fact() -> None:
    """Without the hours the run pays nothing and names the fact."""
    result = _january(None)
    (salary,) = [
        d
        for d in result.decisions
        if d.capability == "base_salary" and d.rule.endswith("base_salary[2025-02-01]")
    ]
    codes = {i.code: i.fact for i in result.issues}

    assert _kind(result, "base_salary_earning") == 0
    assert _kind(result, "hourly_percentage_earning") == 0
    assert codes["hourly_pay_hours_unknown"] == "ordinary_hours_worked"
    assert salary.amount is None
    assert salary.reason_code == "hourly_pay_hours_unknown"
    assert not result.is_payable


def test_percentage_decisions_name_their_clause() -> None:
    """One base_salary decision per percentage, the accrual on Cassa Edile."""
    result = _january(Decimal(173))
    decisions = {
        d.reason_code: d for d in result.decisions if ".percentages[" in d.rule
    }

    assert decisions["hourly_percentage_paid"].amount == Decimal("78.22")
    accrued = decisions["cassa_edile_accrued"]
    assert accrued.inputs["accrual"] == Decimal("224.39")
    assert accrued.rule == "ccnl/edilizia-ance:hourly_pay.percentages[CASSA_EDILE]"
    assert accrued.source is not None


def test_part_time_is_paid_the_full_rate_on_its_hours() -> None:
    """20 of 40 weekly hours, 86.5 hours: half of the full month."""
    employment = replace(
        _OPERAIO,
        weekly_hours=WeeklyHours(Decimal(20)),
        full_time_weekly_hours=WeeklyHours(Decimal(40)),
    )
    result = _january(Decimal("86.5"), employment)

    assert _kind(result, "base_salary_earning") == Decimal("533.68")


def test_apprentice_is_paid_the_reduced_hourly_elements() -> None:
    """Level 2 at 72%: minimo 899.14 and contingenza 371.83 a full month.

    Riposi 4.95% of 1,270.97 = 62.91.
    """
    employment = replace(
        _OPERAIO, level_code="2", contract_type=Apprentice(months_elapsed=6)
    )
    result = _january(Decimal(173), employment)

    assert _kind(result, "base_salary_earning") == Decimal("899.14")
    assert _item(result, "riposi_annui_") == Decimal("62.91")


def test_sick_days_are_not_deducted_from_the_hours() -> None:
    """The sick hours are not worked: no day is deducted from the pay."""
    sickness = SicknessEpisode("S1", date(2026, 1, 12), date(2026, 1, 23))
    result = _january(Decimal(109), events=(sickness,))

    assert _kind(result, "absence_deduction") == 0
    assert _kind(result, "sickness_inps_item") > 0


def test_absence_event_is_rejected() -> None:
    """The absent hours are not worked: an AbsenceEvent would deduct twice."""
    absence = AbsenceEvent(
        date(2026, 1, 12),
        Decimal(16),
        Decimal("6.17"),
        end_date=date(2026, 1, 13),
        suspends_accrual=False,
        no_pay_due=True,
    )

    with pytest.raises(InvalidInputError, match="already excluded") as raised:
        _january(Decimal(157), events=(absence,))

    assert raised.value.field == "PeriodFacts.events[0]"


def test_no_hours_worked_pay_no_percentage() -> None:
    """A month without hours worked pays neither percentage."""
    result = _january(Decimal(0))

    assert _kind(result, "hourly_percentage_earning") == 0
    assert _account(result, "bilateral_fund_employee") == 0


def test_projection_counts_the_percentages_of_the_months_to_come() -> None:
    """The tax year is projected on 1,961.12 a month, not on 1,590.56.

    January 1,961.12 and eleven months of the chain 1,590.56 with the 370.56
    of percentages: a gross of 23,533.44, above the 20,000 of the somma
    esente (L. 207/2024 art. 1 c. 4), which the run does not pay.
    """
    result = _january(Decimal(173))
    (irpef,) = [d for d in result.decisions if d.capability == "irpef"]
    (somma,) = [d for d in result.decisions if d.capability == "somma_esente"]

    assert Decimal(irpef.inputs["projected_taxable"]) > Decimal(20_000)
    assert somma.reason_code == "not_due"
    assert _account(result, "credits") == 0
