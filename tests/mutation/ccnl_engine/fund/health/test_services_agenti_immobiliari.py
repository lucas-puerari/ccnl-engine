"""Hand oracle: the EBNAIP contributions of the Agenti immobiliari (art. 11).

CCNL 2025 (EBNAIP text, p. 23): the QSC is 1.90% of the monthly pay on 14
months, 0.30% from the worker and 1.60% from the employer, on the whole
"retribuzione mensile" (``rate_base: monthly_pay``); the employer also pays a
flat 12 EUR a month on twelve months. An employer that does not pay the QSC
owes the worker 2.40% of the monthly pay on 14 months.
"""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.inputs import (
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2026, 1, 1)
_DAY = date(2026, 6, 1)
_CCNL = load_ccnl("agenti-immobiliari-fiaip")
_LEVEL = _CCNL.levels[-1]
_PAY = _LEVEL.base_salary.value_at(_DAY) + sum(
    (a.monthly.value_at(_DAY) for a in _LEVEL.fixed_allowances if a.role is None),
    Decimal(0),
)


def _pct(rate: str) -> Decimal:
    return (Decimal(rate) * _PAY).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _run(funds: frozenset[str], *, thirteenth: bool = False) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.thirteenth(2026, 12)
            if thirteenth
            else PayrollRun.regular(2026, 6),
            payment_date=date(2026, 12, 15) if thirteenth else date(2026, 6, 27),
            employment=Employment(
                ccnl_id=_CCNL.meta.ccnl_id,
                level_code=_LEVEL.code,
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


def test_paid_qsc_is_a_share_of_the_whole_monthly_pay() -> None:
    """1.60% + 12 EUR from the employer, 0.30% from the worker."""
    result = _run(frozenset({"ebnaip_qsc", "ebnaip_quota_forfetaria"}))

    employer = _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER)
    assert employer == _pct("0.016") + Decimal(12)
    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == _pct("0.003")


def test_the_thirteenth_pays_the_qsc_without_the_flat_quota() -> None:
    """The QSC runs on 14 months, the flat quota on twelve."""
    result = _run(frozenset({"ebnaip_qsc", "ebnaip_quota_forfetaria"}), thirteenth=True)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYER) == _pct("0.016")


def test_unpaid_qsc_owes_the_worker_two_point_four_percent() -> None:
    """Art. 11 d): 2.40% of the monthly pay, also on the extra months."""
    for thirteenth in (False, True):
        result = _run(frozenset({"ebnaip_quota_forfetaria"}), thirteenth=thirteenth)
        elements = [i.amount for i in result.pay_items if "_element_" in i.item_id]
        assert elements == [_pct("0.024")]


def test_the_qsc_reads_seniority_and_allowances_too() -> None:
    """Level Q head of unit with two scatti: the whole monthly pay, not the minimo.

    The QSC is 1.60% of the minimo, the two scatti and the indennità di
    funzione, not of the minimo alone.
    """
    level = _CCNL.level_by_code("Q")
    increments = _CCNL.parameters.seniority_increments
    scatto = increments.amount_by_level["Q"].value_at(_DAY)
    funzione = next(
        a.monthly.value_at(_DAY)
        for a in level.fixed_allowances
        if a.code == "IND_FUNZIONE"
    )
    pay = level.base_salary.value_at(_DAY) + 2 * scatto + funzione
    hired = date(2020, 1, 1)
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 6),
            payment_date=date(2026, 6, 27),
            employment=Employment(
                ccnl_id=_CCNL.meta.ccnl_id,
                level_code="Q",
                roles=frozenset({"responsabile_unita"}),
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(hired, None),
                seniority=SeniorityFact(72, _DAY, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(
                headcount=Headcount(10),
                contractual_funds=frozenset({"ebnaip_qsc", "ebnaip_quota_forfetaria"}),
            ),
        )
    )
    qsc = (Decimal("0.003") * pay).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    assert _posted(result, AccountKind.BILATERAL_FUND_EMPLOYEE) == qsc
    assert funzione > 0
    assert scatto > 0
