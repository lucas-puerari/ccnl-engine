"""Previambiente on the CCNL Servizi Ambientali (art. 65 lett. A).

Enrolled: 2.033% employer and 1.30% employee "sulla base retributiva
convenzionale" (c. 5-6), 22 EUR a month (c. 5 lett. e) and the 5 EUR
insurance of c. 13, on 12 monthly payments.  Not enrolled: 10 EUR (c. 11)
and the 5 EUR insurance, on a permanent contract or an apprenticeship.

Q, conventional base 2077.84 (the table of the CCNL: 42.24 employer, 27.01
employee): employer 2077.84 x 2.033% = 42.2424 -> 42.24, plus 22 + 5 =
69.24, solidarity 6.924 -> 6.92; employee 2077.84 x 1.30% = 27.01192 ->
27.01.  At 2% the employee rate goes on the TFR base (c. 9): March 2026,
3518.41 + 10.33 EDR + 50.00 indennita integrativa = 3578.74 x 2% =
71.5748 -> 71.57.  Not enrolled: 15.00, solidarity 1.50.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.events import AbsenceEvent
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NaspiExclusion,
    NoPensionFund,
    PensionFundEnrolment,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.events import WorkEvent

pytestmark = pytest.mark.legal_scenario

_SLUG = "igiene-ambientale-utilitalia"
_PAID_MONTH = f"{_SLUG}/fund_paid_month"
_FIXED_TERM = FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE)


def _enrolled(
    base: Decimal | None = Decimal("2077.84"), rate: str = "0.013"
) -> PensionFundEnrolment:
    return PensionFundEnrolment(
        "PREVIAMBIENTE", Decimal(rate), tfr_to_fund=True, conventional_base=base
    )


def _march(
    pension: PensionFundEnrolment | NoPensionFund,
    contract: Permanent | FixedTerm | None = None,
    events: tuple[WorkEvent, ...] = (),
) -> PeriodResult:
    employment = Employment(
        ccnl_slug=f"{_SLUG}.json",
        level_code="Q",
        seniority=new_hire(),
        employment_period=EmploymentPeriod(date(2026, 1, 1)),
        pension_fund=pension,
        contract_type=contract or Permanent(),
    )
    return regular_period(
        employment=employment,
        month=3,
        events=events,
        current_year=employment_only(),
    )


def _entry(result: PeriodResult, account: str) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )


def _limitations(result: PeriodResult) -> set[str]:
    return {limitation.id for limitation in result.assurance.limitations}


@pytest.mark.parametrize("contract", [Permanent(), _FIXED_TERM], ids=str)
def test_enrolled_on_the_conventional_base(contract: Permanent | FixedTerm) -> None:
    """42.24 + 22 + 5 = 69.24 employer, 27.01 employee, any contract."""
    result = _march(_enrolled(), contract)
    assert _entry(result, "pension_fund_employer") == Decimal("69.24")
    assert _entry(result, "pension_fund_employee") == Decimal("27.01")
    (decision,) = [
        d for d in result.decisions if d.capability == "pension_fund_contribution"
    ]
    assert decision.inputs["solidarity"] == Decimal("6.92")
    assert _PAID_MONTH not in _limitations(result)


def test_higher_employee_rate_on_the_tfr_base() -> None:
    """2% of 3578.74 = 71.57; the employer part stays on the conventional base."""
    result = _march(_enrolled(rate="0.02"))
    assert _entry(result, "pension_fund_employee") == Decimal("71.57")
    assert _entry(result, "pension_fund_employer") == Decimal("69.24")


@pytest.mark.parametrize(
    ("contract", "employer"),
    [(Permanent(), "15.00"), (_FIXED_TERM, "0")],
    ids=["permanent", "fixed_term"],
)
def test_not_enrolled(contract: Permanent | FixedTerm, employer: str) -> None:
    """10 + 5 on a permanent contract, nothing on a fixed term (c. 11)."""
    result = _march(NoPensionFund(), contract)
    assert _entry(result, "pension_fund_employer") == Decimal(employer)


def test_unknown_conventional_base_is_a_missing_fact() -> None:
    """The rates are left out: 22 + 5 employer, an incomplete issue."""
    result = _march(_enrolled(base=None))
    assert _entry(result, "pension_fund_employer") == Decimal("27.00")
    assert _entry(result, "pension_fund_employee") == 0
    (issue,) = [
        i for i in result.issues if i.code == "pension_fund_conventional_base_unknown"
    ]
    assert issue.fact == "conventional_base"
    assert not result.is_payable


def test_month_without_pay_owes_the_insurance_alone() -> None:
    """C. 8: nothing of c. 5 for a month without pay; the 5 EUR stays."""
    absence = AbsenceEvent(
        event_date=date(2026, 3, 1),
        hours=Decimal(1),
        hourly_rate=Decimal("3578.74"),
        end_date=date(2026, 3, 31),
        suspends_accrual=False,
        no_pay_due=True,
    )
    result = _march(_enrolled(), events=(absence,))
    assert _entry(result, "pension_fund_employer") == Decimal("5.00")
    assert _entry(result, "pension_fund_employee") == 0
    assert _PAID_MONTH not in _limitations(result)


def test_month_paid_in_part_is_an_open_limitation() -> None:
    """An unpaid day: c. 8 proportions to the pay, which is not computed."""
    absence = AbsenceEvent(
        event_date=date(2026, 3, 10),
        hours=Decimal(8),
        hourly_rate=Decimal(20),
        suspends_accrual=False,
        no_pay_due=True,
    )
    result = _march(_enrolled(), events=(absence,))
    assert _PAID_MONTH in _limitations(result)
    assert not result.is_payable
