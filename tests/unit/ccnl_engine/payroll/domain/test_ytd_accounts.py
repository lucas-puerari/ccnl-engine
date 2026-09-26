"""YTD accumulators and credit accounts reject impossible states."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.payroll.domain.ytd_accounts import (
    CreditAccount,
    EarningsYtd,
    FringeYtd,
    SommaEsenteAccount,
    TaxYtd,
    TrattamentoAccount,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_NEG = Decimal("-0.01")


class TestAccumulators:
    """Every running total of the tax year is non-negative."""

    @pytest.mark.parametrize(
        ("build", "match"),
        [
            (lambda: EarningsYtd(gross=_NEG), r"EarningsYtd\.gross"),
            (lambda: EarningsYtd(inps_base=_NEG), r"EarningsYtd\.inps_base"),
            (lambda: EarningsYtd(taxable=_NEG), r"EarningsYtd\.taxable"),
            (lambda: EarningsYtd(inps_employee=_NEG), r"EarningsYtd\.inps_employee"),
            (lambda: TaxYtd(irpef=_NEG), r"TaxYtd\.irpef"),
            (lambda: TaxYtd(surtax=Decimal("NaN")), r"TaxYtd\.surtax"),
            (lambda: FringeYtd(pdr=_NEG), r"FringeYtd\.pdr"),
            (lambda: TrattamentoAccount(recognized=_NEG), r"recognized"),
            (lambda: SommaEsenteAccount(due=_NEG), r"SommaEsenteAccount\.due"),
        ],
    )
    def test_rejects_a_negative_total(
        self, build: Callable[[], object], match: str
    ) -> None:
        """A negative adjustment of one run never makes a YTD total negative."""
        with pytest.raises(ValueError, match=match):
            build()

    def test_taxable_may_exceed_gross(self) -> None:
        """A fringe benefit above the threshold is taxable without cash gross."""
        earnings = EarningsYtd(gross=Decimal(100), taxable=Decimal(400))

        assert earnings.taxable > earnings.gross


class TestCreditAccount:
    """Recognized, recovered, updated due and reason of a tax credit."""

    def test_rejects_more_recovered_than_recognized(self) -> None:
        """A credit cannot be taken back beyond what was paid."""
        with pytest.raises(ValueError, match=r"SommaEsenteAccount\.recovered"):
            SommaEsenteAccount(recognized=Decimal(10), recovered=Decimal(11))

    def test_rejects_a_reason_that_is_not_a_code(self) -> None:
        """The reason is a stable machine-readable code."""
        with pytest.raises(ValueError, match="lower snake case"):
            TrattamentoAccount(reason="Not Due")

    def test_residual_is_the_excess_over_the_updated_due(self) -> None:
        """600 paid, 100 recovered, 300 due: 200 still to recover."""
        account = SommaEsenteAccount(
            recognized=Decimal(600), recovered=Decimal(100), due=Decimal(300)
        )

        assert account.net == Decimal(500)
        assert account.residual == Decimal(200)

    def test_no_residual_before_the_due_is_known(self) -> None:
        """Without a computed entitlement nothing is known to be over-paid."""
        assert CreditAccount(recognized=Decimal(600)).residual == Decimal(0)

    def test_after_splits_paid_and_recovered(self) -> None:
        """A positive amount is paid, a negative one recovered."""
        account = TrattamentoAccount(recognized=Decimal(100))

        paid = account.after(Decimal(50), Decimal(200), "within_band")
        recovered = paid.after(Decimal(-30), None, None)

        assert paid == TrattamentoAccount(
            recognized=Decimal(150), due=Decimal(200), reason="within_band"
        )
        assert recovered == TrattamentoAccount(
            recognized=Decimal(150),
            recovered=Decimal(30),
            due=Decimal(200),
            reason="within_band",
        )

    def test_kind_names_the_recovery(self) -> None:
        """Each account names the recovery plan kind of its credit."""
        assert TrattamentoAccount.KIND == "trattamento_integrativo"
        assert SommaEsenteAccount.KIND == "somma_esente"
