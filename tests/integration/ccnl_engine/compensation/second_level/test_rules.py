"""Second-level elements through a run of Commercio Confcommercio, 4th level.

A company agreement of 50 EUR a month is paid as a fixed allowance of the
level: it enters the gross, the TFR base and the extra months, and the run
records one decision under ``company_supplement``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SecondLevelAgreement,
    SecondLevelElement,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind, DecisionOrigin

_HIRED = date(2025, 1, 1)
_COMPANY = SecondLevelElement(
    "premio_presenza", Decimal(50), SecondLevelAgreement.COMPANY, date(2026, 1, 1)
)


def _run(*elements: SecondLevelElement, run: PayrollRun | None = None) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="commercio-confcommercio",
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(60),
                provincial_pay_element=False,
                second_level_elements=elements,
            ),
        )
    )


def _tfr(result: PeriodResult) -> Decimal:
    entries = result.ledger_entries
    return sum(
        (e.amount for e in entries if e.account is AccountKind.TFR_ACCRUAL), Decimal(0)
    )


def test_a_company_element_is_paid_as_an_allowance_of_the_level() -> None:
    """50 EUR more gross, a larger TFR accrual and one decision."""
    without, with_element = _run(), _run(_COMPANY)

    assert with_element.period_gross - without.period_gross == Decimal(50)
    assert _tfr(with_element) > _tfr(without)
    (decision,) = [
        d for d in with_element.decisions if d.capability == "company_supplement"
    ]
    assert decision.reason_code == "caller_supplied_amount"
    assert decision.origin is DecisionOrigin.CALLER_SUPPLIED
    assert decision.amount == Decimal(50)


def test_an_element_outside_its_levels_or_period_is_not_paid() -> None:
    """A level it does not list, or a day after it ends, pays nothing."""
    other_level = SecondLevelElement(
        "premio",
        Decimal(50),
        SecondLevelAgreement.TERRITORIAL,
        date(2026, 1, 1),
        levels=("1",),
    )
    ended = SecondLevelElement(
        "vecchio",
        Decimal(50),
        SecondLevelAgreement.COMPANY,
        date(2025, 1, 1),
        date(2025, 12, 31),
    )
    baseline = _run().period_gross
    assert _run(other_level).period_gross == baseline
    assert _run(ended).period_gross == baseline


def test_an_element_kept_off_the_tfr_base_does_not_accrue_tfr() -> None:
    """tfr_relevant false: no TFR quota, but the 0.50% offset still grows.

    The element stays in the INPS base, so the additional 0.50% contribution
    (art. 3 L. 297/1982) taken from the TFR accrual grows by 0.25 EUR.
    """
    off = SecondLevelElement(
        "rimborso",
        Decimal(50),
        SecondLevelAgreement.COMPANY,
        date(2026, 1, 1),
        tfr_relevant=False,
    )
    assert _tfr(_run()) - _tfr(_run(off)) == Decimal("0.25")


def test_two_elements_with_one_code_are_rejected() -> None:
    """The code names the earning: it is unique within the employer."""
    with pytest.raises(InvalidInputError, match="share a code"):
        EmployerProfile(
            headcount=Headcount(1), second_level_elements=(_COMPANY, _COMPANY)
        )
