"""Hand oracle: the funds of the Autoscuole UNASCA, June 2026, level 3.

- Fondo EST (Art. 46, pp. 57-58): 15 EUR a month of the employer and 2 of
  the worker, a health fund (1.50 EUR of INPS solidarity); a firm that does
  not pay owes an element of 16 EUR on 14 months.
- Ente bilaterale (p. 7): 2 EUR a month of the employer from September
  2021, on 12 months; a firm that does not pay owes 3 EUR a month.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2025, 1, 1)
_BOTH = frozenset({"fondo_est", "ente_bilaterale"})


def _run(funds: frozenset[str], *, fourteenth: bool = False) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.fourteenth(2026, 6)
            if fourteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id="autoscuole-unasca",
                level_code="3",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10), contractual_funds=funds),
        )
    )


def _posted(result: PeriodResult, account: AccountKind) -> Decimal:
    return sum(
        (e.amount for e in result.ledger_entries if e.account is account), Decimal(0)
    )


def _elements(result: PeriodResult) -> dict[str, Decimal]:
    return {
        i.item_id.split("_element")[0]: i.amount
        for i in result.pay_items
        if "_element" in i.item_id
    }


def test_both_funds_paid_post_their_shares() -> None:
    """Employer 15 + 2, worker 2, solidarity 10% of the 15."""
    result = _run(_BOTH)
    solidarity = [
        e.amount for e in result.ledger_entries if e.entry_id.endswith("_solidarity")
    ]

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == Decimal("17.00")
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == Decimal("2.00")
    assert solidarity == [Decimal("1.50")]
    assert not _elements(result)


def test_unpaid_funds_owe_their_elements() -> None:
    """16 EUR for Fondo EST and 3 EUR for the ente bilaterale."""
    result = _run(frozenset())

    assert _elements(result) == {
        "fondo_est": Decimal("16.00"),
        "ente_bilaterale": Decimal("3.00"),
    }
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == 0


def test_only_the_fondo_est_element_is_due_on_the_fourteenth() -> None:
    """16 EUR 'per 14 mensilità'; the 3 EUR are 'per 12 mensilità'."""
    result = _run(frozenset(), fourteenth=True)

    assert _elements(result) == {"fondo_est": Decimal("16.00")}
