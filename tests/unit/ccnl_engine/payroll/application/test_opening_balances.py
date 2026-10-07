"""Tests for OpeningBalances: validated totals of a previous provider."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.payroll.application.opening_balances import OpeningBalances
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.obligations import (
    RecoveryObligation,
)
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.recovery_plan import RecoveryPlan
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.shortfall_deferral import DeferredShortfall
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_PLAN = RecoveryPlan(
    kind="trattamento_integrativo",
    original_amount=Decimal(160),
    installment_amount=Decimal(20),
    installments_total=8,
    installments_posted=3,
)


@pytest.mark.parametrize(
    "value", [Decimal(-1), Decimal("NaN"), Decimal("Infinity")], ids=str
)
def test_rejects_an_amount_that_is_not_a_non_negative_number(value: Decimal) -> None:
    """Negative and non-finite amounts are rejected, naming the field."""
    with pytest.raises(
        InvalidInputError, match=r"OpeningBalances\.gross must be a finite Decimal >= 0"
    ) as info:
        OpeningBalances(
            tax_year=2026,
            gross=value,
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )

    assert info.value.feature == "opening_balances"


def test_rejects_an_amount_finer_than_a_cent() -> None:
    """Amounts are in EUR with at most two decimals."""
    with pytest.raises(InvalidInputError, match="at most two decimals"):
        OpeningBalances(
            tax_year=2026,
            taxable=Decimal("0.001"),
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )


def test_rejects_inconsistent_totals_as_invalid_input() -> None:
    """More trattamento recovered than recognized is not a valid state."""
    with pytest.raises(InvalidInputError, match="recovered") as info:
        OpeningBalances(
            tax_year=2026,
            trattamento_recovered=Decimal(10),
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )

    assert info.value.feature == "opening_balances"


def test_rejects_a_recovery_opened_after_the_tax_year() -> None:
    """A recovery cannot originate after the year of the balances."""
    with pytest.raises(InvalidInputError, match="opened in 2027"):
        OpeningBalances(
            tax_year=2026,
            recoveries=(RecoveryObligation(tax_year=2027, plan=_PLAN),),
            inps_bases=(),
            surtax_obligations=(),
        )


def test_rejects_a_reason_that_is_not_a_code() -> None:
    """A reason is a lower snake case code, as on the engine's own accounts."""
    with pytest.raises(InvalidInputError, match="lower snake case"):
        OpeningBalances(
            tax_year=2026,
            trattamento_reason="Full amount",
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )


def test_rejects_surtax_of_the_conguaglio_of_the_tax_year() -> None:
    """Surtax the 2026 conguaglio determines cannot open 2026."""
    late = SurtaxObligation.open(
        SurtaxComponent.MUNICIPAL_ADVANCE, 2026, "I452", Decimal(9)
    )
    with pytest.raises(InvalidInputError, match="year before 2026"):
        OpeningBalances(
            tax_year=2026, surtax_obligations=(late,), inps_bases=(), recoveries=()
        )


def _deferred(tax_year: int) -> DeferredShortfall:
    return DeferredShortfall(
        tax_year=tax_year,
        signed_on=date(tax_year, 12, 10),
        deferred_from=date(tax_year, 12, 1),
        irpef=Decimal("300.00"),
    )


@pytest.mark.parametrize("tax_year", [2024, 2026])
def test_rejects_a_deferral_of_another_conguaglio(tax_year: int) -> None:
    """Only the conguaglio of 2025 defers IRPEF to 2026."""
    with pytest.raises(InvalidInputError, match="deferred_shortfall"):
        OpeningBalances(
            tax_year=2026,
            deferred_shortfall=_deferred(tax_year),
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )


@pytest.mark.parametrize(
    ("payments", "field"),
    [
        (("2026-06-regular@2026-06-27",), "OpeningBalances.payments[0]"),
        (
            (
                PaymentId.parse("2026-06-regular@2026-06-27"),
                PaymentId.parse("2026-06-regular@2026-06-28"),
            ),
            "TaxCashState.payments",
        ),
        (
            (PaymentId.parse("2026-12-regular@2027-01-13"),),
            "TaxCashState.payments",
        ),
    ],
)
def test_rejects_payments_that_do_not_fit_the_tax_year(
    payments: tuple[object, ...], field: str
) -> None:
    """A payment id is typed, paid once and of the tax year of the totals."""
    with pytest.raises(InvalidInputError) as info:
        OpeningBalances(
            tax_year=2026,
            payments=payments,  # type: ignore[arg-type]
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )

    assert info.value.field == field
    assert info.value.feature == "opening_balances"


def test_rejects_totals_without_the_payments_that_produced_them() -> None:
    """Totals of unidentified payments could be computed again: rejected."""
    with pytest.raises(InvalidInputError, match="need the payments") as info:
        OpeningBalances(
            tax_year=2026,
            gross=Decimal("100.00"),
            inps_bases=(),
            recoveries=(),
            surtax_obligations=(),
        )

    assert info.value.field == "OpeningBalances.payments"


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        (
            {"competence_runs": ("2026-01-regular",)},
            "OpeningBalances.competence_runs[0]",
        ),
        ({"inps_bases": (Decimal(1),)}, "OpeningBalances.inps_bases[0]"),
    ],
)
def test_rejects_collections_of_the_wrong_elements(
    kwargs: dict[str, object], field: str
) -> None:
    """Every element of an imported collection is typed."""
    required: dict[str, object] = {
        "inps_bases": (),
        "recoveries": (),
        "surtax_obligations": (),
    }
    with pytest.raises(InvalidInputError) as info:
        OpeningBalances(tax_year=2026, **(required | kwargs))  # type: ignore[arg-type]

    assert info.value.field == field


@pytest.mark.parametrize(
    "closed",
    [
        {"payments": (PaymentId.parse("2026-06-regular@2026-06-27"),)},
        {"competence_runs": (PayrollRunId(2025, 11, RunKind.REGULAR),)},
    ],
    ids=["payment", "competence_run"],
)
def test_rejects_a_closed_run_without_the_inps_base_of_its_year(
    closed: dict[str, object],
) -> None:
    """A run closed by the previous provider needs the base of its year."""
    with pytest.raises(InvalidInputError, match="no base for the competence") as info:
        OpeningBalances(
            tax_year=2026,
            inps_bases=(InpsBaseYtd(2024),),
            recoveries=(),
            surtax_obligations=(),
            **closed,  # type: ignore[arg-type]
        )

    assert info.value.field == "OpeningBalances.inps_bases"


def test_the_carried_obligations_and_bases_have_no_default() -> None:
    """What the previous provider determined is stated, () when nothing."""
    with pytest.raises(TypeError, match=r"inps_bases.*recoveries.*surtax_obligations"):
        OpeningBalances(tax_year=2026)  # type: ignore[call-arg]
