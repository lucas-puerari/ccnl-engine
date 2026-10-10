"""settle_ulteriore: what one run recognizes or recovers of the ulteriore detrazione.

L. 207/2024 art. 1 c. 7: the deduction found not due at the conguaglio is
recovered in ten installments when above 60 EUR, in full otherwise.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine.contract.identity.facade import TaxSector
from ccnl_engine.payroll.domain.credit_accounts import UlterioreDetrazioneAccount
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.service.ulteriore_settlement import settle_ulteriore
from ccnl_engine.tax.annual.loaders import load_year_rules

_ZERO = Decimal(0)
_RULES = load_year_rules(2026, TaxSector.INDUSTRIA, 50)


def _account(recognized: str, recovered: str = "0") -> UlterioreDetrazioneAccount:
    return UlterioreDetrazioneAccount(
        recognized=Decimal(recognized), recovered=Decimal(recovered)
    )


class TestSettleUlteriore:
    """What one run recognizes or recovers."""

    def test_share_before_the_conguaglio(self) -> None:
        """The run recognizes what its withholding is lower by."""
        settled = settle_ulteriore(
            Decimal(100),
            Decimal("176.92"),
            Decimal(1000),
            _account("0"),
            last_slot=False,
        )
        assert settled.amount == Decimal("76.92")
        assert settled.reason == "share_recognized"
        assert settled.deferred == _ZERO

    def test_taken_back_before_the_conguaglio_is_not_deferred(self) -> None:
        """A run taking back the deduction recovers it by withholding."""
        settled = settle_ulteriore(
            Decimal(900), Decimal(100), _ZERO, _account("500"), last_slot=False
        )
        assert settled.amount == Decimal(-500)
        assert settled.reason == "recovered_by_withholding"
        assert settled.plan is None

    def test_nothing_recognized(self) -> None:
        """Without the deduction the withholding is the same."""
        settled = settle_ulteriore(
            Decimal(100), Decimal(100), _ZERO, _account("0"), last_slot=False
        )
        assert settled.reason == "not_recognized"

    def test_conguaglio_completes_the_deduction(self) -> None:
        """At the conguaglio a positive balance is recognized."""
        settled = settle_ulteriore(
            Decimal(100),
            Decimal("176.93"),
            Decimal(1000),
            _account("923.07"),
            last_slot=True,
        )
        assert settled.amount == Decimal("76.93")
        assert settled.reason == "settled_at_conguaglio"
        assert settled.decisions(_RULES) == ()

    def test_excess_up_to_sixty_is_recovered_in_full(self) -> None:
        """60 EUR found not due are withheld on the conguaglio payslip."""
        settled = settle_ulteriore(
            Decimal(160), Decimal(100), _ZERO, _account("60"), last_slot=True
        )
        assert settled.amount == Decimal(-60)
        assert settled.reason == "overpayment_recovered"
        assert settled.deferred == _ZERO
        assert settled.plan is None

    def test_excess_above_sixty_opens_ten_installments(self) -> None:
        """60.10 EUR: 6.01 on the conguaglio, nine installments deferred."""
        settled = settle_ulteriore(
            Decimal("160.10"),
            Decimal(100),
            _ZERO,
            _account("60.10"),
            last_slot=True,
        )
        assert settled.reason == "overpayment_recovery_opened"
        assert settled.deferred == Decimal("54.09")
        assert settled.plan is not None
        assert settled.plan.installments_posted == 1
        assert settled.plan.residual == Decimal("54.09")
        (decision,) = settled.decisions(_RULES)
        assert decision.capability == "ulteriore_detrazione_lavoro_recovery"
        assert decision.amount == Decimal("-60.10")
        assert decision.status == CalculationStatus.FINAL


def test_excess_is_not_deferred_without_a_later_payslip() -> None:
    """At the cessation the whole excess stays in the conguaglio IRPEF."""
    settled = settle_ulteriore(
        Decimal(500),
        Decimal(100),
        _ZERO,
        _account("400"),
        last_slot=True,
        defer=False,
    )
    assert settled.reason == "overpayment_recovered_at_termination"
    assert settled.deferred == _ZERO
    assert settled.plan is None
