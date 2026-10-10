"""Period requests for one worker of a 50-employee employer in 2026.

Integration tests that run one period of a bundled CCNL build the request
here: Metalmeccanico C3 by default, an impiegato (the level fixes no
category, the industria INPS employer rate depends on it), paid on the
28th of the month.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Permanent
from ccnl_engine.payroll.domain.employment_facts import ContributableHours, WeeklyHours
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.eligibility import ContributionHistory
    from ccnl_engine.payroll.domain.ledger import AccountKind
    from ccnl_engine.payroll.domain.period import PeriodResult

__all__ = ["METALMECCANICO", "YEAR", "account_total", "period_request"]

METALMECCANICO = "metalmeccanico-federmeccanica.json"
YEAR = 2026


def period_request(
    month: int = 1,
    opening: PeriodState | None = None,
    events: tuple[object, ...] = (),
    ccnl: str = METALMECCANICO,
    level: str = "C3",
    weekly_hours: int | None = None,
    contributable_hours: Decimal | None = None,
    contract_type: object | None = None,
    contribution_history: ContributionHistory | None = None,
) -> PeriodCalculationRequest:
    """Return the request of one regular period of ``month`` 2026.

    Returns:
        The request, with a zero opening state unless ``opening`` is given.
    """
    if opening is None:
        opening = PeriodState.zero()
    ct = contract_type if contract_type is not None else Permanent()
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=YEAR, month=month),
        payment_date=date(YEAR, month, 28),
        ccnl_slug=ccnl,
        level_code=level,
        opening_state=opening,
        events=events,  # type: ignore[arg-type]
        weekly_hours=None if weekly_hours is None else WeeklyHours(weekly_hours),
        contributable_hours=(
            None
            if contributable_hours is None
            else ContributableHours(contributable_hours)
        ),
        contract_type=ct,  # type: ignore[arg-type]
        contribution_history=contribution_history,
        category=WorkerCategory.IMPIEGATO if ccnl == METALMECCANICO else None,
    )


def account_total(result: PeriodResult, account: AccountKind) -> Decimal:
    """Return the sum of the ledger entries of ``result`` on ``account``.

    Returns:
        The total, zero when no entry is on the account.
    """
    return sum(
        (e.amount for e in result.ledger_entries if e.account == account),
        Decimal(0),
    )
