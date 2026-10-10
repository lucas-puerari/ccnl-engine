"""Destination of the TFR of a run and the issue of an unknown one.

L. 296/2006 art. 1 c. 756 (Normattiva, text in force from 12-8-2026): the
TFR not destined to a complementary pension fund is paid to the Fondo
Tesoreria INPS by the employers the comma names; the TFR a worker destines
to a pension fund goes to it (D.Lgs. 252/2005 art. 8).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.contribution.services import (
    TFR_TREASURY_FUND_CODE,
    TfrAccrual,
)
from ccnl_engine.payroll.employment.inputs_fact import PublicEndOfService
from ccnl_engine.payroll.ledger.models import AccountKind

_QUOTA = Decimal("152.02")


@pytest.mark.parametrize(
    ("to_pension_fund", "treasury_fund", "account"),
    [
        (True, True, AccountKind.PENSION_FUND_TFR),
        (True, None, AccountKind.PENSION_FUND_TFR),
        (False, True, AccountKind.TFR_TREASURY_FUND),
        (False, False, AccountKind.TFR_ACCRUAL),
        (False, None, AccountKind.TFR_ACCRUAL),
    ],
)
def test_account_follows_the_destination(
    *, to_pension_fund: bool, treasury_fund: bool | None, account: AccountKind
) -> None:
    """The pension fund first, then the Fondo Tesoreria, else the company."""
    accrual = TfrAccrual(
        quota=_QUOTA, to_pension_fund=to_pension_fund, treasury_fund=treasury_fund
    )
    assert accrual.account is account


@pytest.mark.parametrize(
    ("quota", "to_pension_fund", "treasury_fund"),
    [
        (_QUOTA, True, None),
        (_QUOTA, False, True),
        (_QUOTA, False, False),
        (Decimal(0), False, None),
    ],
)
def test_known_or_irrelevant_destination_raises_no_issue(
    *, quota: Decimal, to_pension_fund: bool, treasury_fund: bool | None
) -> None:
    """A pension fund, a stated destination or a nil TFR need no fact."""
    accrual = TfrAccrual(
        quota=quota, to_pension_fund=to_pension_fund, treasury_fund=treasury_fund
    )
    assert accrual.issues() == ()


def test_unknown_destination_of_a_tfr_is_a_missing_fact() -> None:
    """A TFR kept out of a pension fund needs to know about the Fondo."""
    (issue,) = TfrAccrual(quota=_QUOTA, treasury_fund=None).issues()
    assert issue.code == TFR_TREASURY_FUND_CODE
    assert issue.fact == "tfr_treasury_fund"
    assert issue.status is CalculationStatus.PROVISIONAL


@pytest.mark.parametrize(
    ("to_pension_fund", "treasury_fund", "public", "conferred"),
    [
        (True, None, None, True),
        (False, True, None, True),
        (False, False, None, False),
        (False, None, None, False),
        (True, None, PublicEndOfService.TFR_INPS, False),
    ],
)
def test_conferred_when_the_tfr_leaves_the_company(
    *,
    to_pension_fund: bool,
    treasury_fund: bool | None,
    public: PublicEndOfService | None,
    conferred: bool,
) -> None:
    """A pension fund or the Fondo Tesoreria; not an unknown or notional one."""
    accrual = TfrAccrual(
        quota=_QUOTA,
        to_pension_fund=to_pension_fund,
        treasury_fund=treasury_fund,
        public=public,
    )
    assert accrual.conferred is conferred
