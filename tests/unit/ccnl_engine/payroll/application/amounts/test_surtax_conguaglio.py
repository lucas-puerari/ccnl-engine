"""The conguaglio settles the surtax of the year less what it already withheld."""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.payroll.application.amounts._surtax_conguaglio import (
    conguaglio_surtax,
)
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.surtax_obligations import SurtaxComponent
from ccnl_engine.payroll.domain.ytd_accounts import TaxYtd
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome

_FRACTION = Decimal("0.30")


def _decision(capability: str, code: str, amount: Decimal) -> CalculationDecision:
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL,
        reason_code="table_applied",
        rule="surtax/2026",
        rule_version="2026",
        inputs={"code": code},
        amount=amount,
    )


def _annual(regional: str, municipal: str) -> SurtaxOutcome:
    r, m = Decimal(regional), Decimal(municipal)
    return SurtaxOutcome(
        regional=r,
        municipal=m,
        decisions=(
            _decision("addizionale_regionale", "IT-88", r),
            _decision("addizionale_comunale", "I452", m),
        ),
    )


def test_ordinary_conguaglio_defers_the_saldi_and_the_acconto() -> None:
    """300 regional, 200 municipal less 60 acconto: 300, 140 and 60 deferred."""
    tax = TaxYtd(surtax=Decimal(60), municipal_advance=Decimal(60))

    out = conguaglio_surtax(
        _annual("300", "200"), 2026, tax, final=False, fraction=_FRACTION
    )

    assert [(o.component, o.plan.original_amount) for o in out.obligations] == [
        (SurtaxComponent.REGIONAL_BALANCE, Decimal(300)),
        (SurtaxComponent.MUNICIPAL_BALANCE, Decimal(140)),
        (SurtaxComponent.MUNICIPAL_ADVANCE, Decimal(60)),
    ]
    assert (out.parts, out.refund) == ((), Decimal(0))


def test_zero_components_are_neither_withheld_nor_deferred() -> None:
    """No regional and no municipal surtax: nothing to settle."""
    out = conguaglio_surtax(
        _annual("0", "0"), 2026, TaxYtd(), final=True, fraction=_FRACTION
    )

    assert (out.parts, out.obligations, out.decisions) == ((), (), ())


def test_second_conguaglio_refunds_what_it_withheld_above_the_due() -> None:
    """Regional 300 and saldo 150 already withheld, now 280 and 120 due.

    The regional refund is 20.  The municipal surtax falls to 120 against
    60 of acconto and 150 of saldo withheld: 90 is refunded, taken from the
    saldo first, so no acconto is given back.
    """
    tax = TaxYtd(
        surtax=Decimal(510),
        municipal_advance=Decimal(60),
        regional_settled=Decimal(300),
        municipal_settled=Decimal(150),
    )

    out = conguaglio_surtax(
        _annual("280", "120"), 2026, tax, final=True, fraction=_FRACTION
    )

    assert out.refund == Decimal(110)
    assert (out.regional_settled, out.municipal_settled) == (Decimal(-20), Decimal(-90))
    assert out.advance_refunded == Decimal(0)
    assert [d.reason_code for d in out.decisions] == ["surtax_refunded"] * 2


def test_refund_above_the_saldo_comes_from_the_acconto() -> None:
    """Municipal due 20, acconto 60 and saldo 10 withheld: 50 refunded.

    10 comes from the saldo, 40 from the acconto.
    """
    tax = TaxYtd(
        surtax=Decimal(70),
        municipal_advance=Decimal(60),
        municipal_settled=Decimal(10),
    )

    out = conguaglio_surtax(
        _annual("0", "20"), 2026, tax, final=True, fraction=_FRACTION
    )

    assert (out.refund, out.municipal_settled, out.advance_refunded) == (
        Decimal(50),
        Decimal(-10),
        Decimal(40),
    )
