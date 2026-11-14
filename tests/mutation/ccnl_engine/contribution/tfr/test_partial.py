"""The shares of a TFR conferred in part to a pension fund.

D.Lgs. 252/2005 art. 8 c. 7 lett. c) and c. 9-bis: a worker enrolled in a
compulsory scheme before 29 April 1993 may pay the fund only part of the
TFR maturando; the rest stays in the company, or goes to the Fondo
Tesoreria INPS (L. 296/2006 art. 1 c. 756).
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.contribution.tfr.services import TfrAccrual
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.ledger.models import AccountKind

_HALF = Decimal("0.5")


def _accrual(**kwargs: object) -> TfrAccrual:
    return TfrAccrual(quota=Decimal("130.65"), to_pension_fund=True, **kwargs)  # type: ignore[arg-type]


def test_half_to_the_fund_half_kept_in_the_company() -> None:
    """130.65 at 50%: 65.33 to the fund, 65.32 kept in the company."""
    accrual = _accrual(fund_share=_HALF)
    assert accrual.fund_amount == Decimal("65.33")
    assert accrual.kept_amount == Decimal("65.32")
    assert accrual.account_amount == Decimal("65.33")
    assert accrual.account is AccountKind.PENSION_FUND_TFR
    assert accrual.kept_account is AccountKind.TFR_ACCRUAL
    assert accrual.paid_share == _HALF
    assert accrual.conferred_share == _HALF
    assert accrual.conferred


def test_rest_to_the_treasury_fund_confers_it_all() -> None:
    """The rest at the Fondo Tesoreria: the whole TFR leaves the company."""
    accrual = _accrual(fund_share=_HALF, treasury_fund=True)
    assert accrual.kept_account is AccountKind.TFR_TREASURY_FUND
    assert accrual.conferred_share == 1


def test_unknown_treasury_destination_confers_the_fund_share() -> None:
    """Treasury destination unknown: only the fund share counts."""
    accrual = _accrual(fund_share=_HALF, treasury_fund=None)
    assert accrual.conferred_share == _HALF


def test_whole_conferment_keeps_nothing() -> None:
    """The default share: all of it to the fund."""
    accrual = _accrual()
    assert accrual.fund_amount == accrual.amount == Decimal("130.65")
    assert accrual.kept_amount == 0
    assert accrual.conferred_share == 1


def test_kept_tfr_pays_nothing_to_the_fund() -> None:
    """No enrolment: the share is ignored, the TFR stays."""
    accrual = TfrAccrual(quota=Decimal("130.65"), fund_share=_HALF)
    assert accrual.fund_amount == 0
    assert accrual.paid_share == 0
    assert accrual.account_amount == accrual.kept_amount == Decimal("130.65")
    assert accrual.conferred_share == 0
    assert not accrual.conferred


def test_inps_regime_confers_nothing() -> None:
    """TFR at INPS: nothing accrues in the company or leaves it."""
    accrual = _accrual(
        fund_share=_HALF,
        treasury_fund=True,
        public=PublicEndOfService.TFR_INPS,
    )
    assert accrual.conferred_share == 0
    assert accrual.fund_amount == 0
