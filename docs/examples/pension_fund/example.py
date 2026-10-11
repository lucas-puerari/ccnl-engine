"""Pension fund: enrol the worker in the CCNL fund to post its contributions."""

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import NoPensionFund, PensionFundEnrolment, Permanent

engine = PayrollEngine.bundled()


def run(pension_fund: PensionFundEnrolment | NoPensionFund) -> None:
    """Print the fund lines, net and employer cost of January 2026."""
    result = engine.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year=2026, month=1),
            payment_date=date(2026, 1, 27),
            employment=Employment(
                ccnl_slug="tabacco-apti.json",
                level_code="4A",
                pension_fund=pension_fund,
                contract_type=Permanent(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    for entry in result.ledger_entries:
        if entry.account.startswith("pension_fund"):
            print(f"  {entry.account:<22} {entry.amount:>8}")
    print(f"  net {result.period_net}  employer cost {result.period_employer_cost}")


print("Not enrolled:")
run(NoPensionFund())
print("Enrolled in ALIFOND, 1% employee, TFR to the fund:")
run(PensionFundEnrolment("ALIFOND", Decimal("0.01"), tfr_to_fund=True))
