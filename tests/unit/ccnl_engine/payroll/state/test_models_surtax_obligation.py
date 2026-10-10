"""Surtax determined by a conguaglio and its statutory installment windows."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.payroll.state.models_obligation import EmploymentObligations
from ccnl_engine.payroll.state.models_surtax_obligation import (
    SURTAX_WINDOWS,
    SurtaxComponent,
    SurtaxObligation,
)
from ccnl_engine.payroll.withholding.models_recovery_plan import (
    InstallmentRun,
    RecoveryPlan,
)

_REGIONAL = SurtaxComponent.REGIONAL_BALANCE
_ADVANCE = SurtaxComponent.MUNICIPAL_ADVANCE
_RUN = InstallmentRun()


def _regional(amount: str = "110.00") -> SurtaxObligation:
    return SurtaxObligation.open(_REGIONAL, 2025, "IT-88", Decimal(amount))


def test_windows_follow_the_statutory_months() -> None:
    """Eleven balance installments from January, nine acconto from March.

    D.Lgs. 446/1997 art. 50 c. 4 and D.Lgs. 360/1998 art. 1 c. 5: the last
    installment is on the November payslip, remitted in December.
    """
    windows = {c: (w.first_month, w.installments) for c, w in SURTAX_WINDOWS.items()}

    assert windows == {
        SurtaxComponent.REGIONAL_BALANCE: (1, 11),
        SurtaxComponent.MUNICIPAL_BALANCE: (1, 11),
        SurtaxComponent.MUNICIPAL_ADVANCE: (3, 9),
    }
    assert {w.remittance_code for w in SURTAX_WINDOWS.values()} == {
        "3802",
        "3847",
        "3848",
    }


def test_open_spreads_the_amount_over_the_window() -> None:
    """110.00 of regional surtax: eleven installments of 10.00."""
    obligation = _regional()

    assert obligation.plan.installments_total == 11
    assert obligation.plan.installment_amount == Decimal("10.00")
    assert (obligation.withheld_in, obligation.reference_year) == (2026, 2025)


def test_acconto_refers_to_the_year_it_is_withheld_in() -> None:
    """The 2025 conguaglio determines the acconto of 2026."""
    obligation = SurtaxObligation.open(_ADVANCE, 2025, "I452", Decimal(9))

    assert (obligation.withheld_in, obligation.reference_year) == (2026, 2026)
    assert obligation.part(Decimal(1)).stem == "surtax_municipal_advance_2026"


def test_open_uses_fewer_installments_for_a_few_cents() -> None:
    """0.05 EUR runs over five installments of 0.01, none of them zero."""
    assert _regional("0.05").plan.installments_total == 5
    with pytest.raises(ValueError, match=r"0\.01"):
        _regional("0.00")


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        ({"tax_year": 2019}, "tax_year"),
        ({"jurisdiction": ""}, "jurisdiction"),
        ({"plan": RecoveryPlan.create("somma_esente", Decimal(10), 1)}, r"plan\.kind"),
        (
            {"plan": RecoveryPlan.create("regional_balance", Decimal(12), 12)},
            "at most 11",
        ),
    ],
)
def test_rejects_an_invalid_obligation(kwargs: dict[str, object], match: str) -> None:
    """Year, jurisdiction, plan kind and installment count are validated."""
    fields: dict[str, object] = {
        "component": "regional_balance",
        "tax_year": 2025,
        "jurisdiction": "IT-88",
        "plan": RecoveryPlan.create("regional_balance", Decimal(11), 11),
    }
    fields.update(kwargs)
    with pytest.raises(InvalidInputError, match=match):
        SurtaxObligation(**fields)  # type: ignore[arg-type]


def test_nothing_is_withheld_outside_the_window() -> None:
    """Before the year, on an extra-month run or before March: nothing."""
    advance = SurtaxObligation.open(_ADVANCE, 2025, "I452", Decimal(9))

    for year, month, regular in ((2025, 12, True), (2026, 6, False), (2026, 2, True)):
        posted, after = advance.post(_RUN, year=year, month=month, regular=regular)
        assert (posted, after) == (None, advance)


def test_regular_run_in_the_window_withholds_one_installment() -> None:
    """January withholds the first 10.00; the plan moves on."""
    posted, after = _regional().post(_RUN, year=2026, month=1, regular=True)

    assert posted is not None
    assert (posted.amount, posted.reason) == (Decimal(10), "installment_posted")
    assert after is not None
    assert after.plan.installments_posted == 1


def test_november_or_a_later_year_withholds_the_residual() -> None:
    """The window closes in November: any installment left is taken then."""
    for year, month in ((2026, 11), (2027, 1)):
        posted, after = _regional().post(_RUN, year=year, month=month, regular=True)
        assert posted is not None
        assert (posted.amount, after) == (Decimal(110), None)


def test_final_run_withholds_the_residual_on_any_run() -> None:
    """The last run of the employment takes everything, even an extra month."""
    posted, after = _regional().post(
        InstallmentRun(final=True), year=2026, month=6, regular=False
    )

    assert posted is not None
    assert (posted.amount, posted.reason, after) == (
        Decimal(110),
        "settled_at_termination",
        None,
    )


def test_a_short_plan_settles_before_november() -> None:
    """A two-installment plan is settled on the February payslip."""
    first, after = _regional("0.02").post(_RUN, year=2026, month=1, regular=True)
    assert after is not None
    second, settled = after.post(_RUN, year=2026, month=2, regular=True)

    assert first is not None
    assert second is not None
    assert (second.reason, settled) == ("last_installment_posted", None)


def test_obligations_reject_two_of_the_same_component_and_year() -> None:
    """One regional surtax per conguaglio."""
    with pytest.raises(ValueError, match="same component"):
        EmploymentObligations(surtax=(_regional(), _regional("20.00")))


def test_latest_tax_year_includes_the_surtax() -> None:
    """A surtax of the 2025 conguaglio binds the obligations to 2025."""
    assert EmploymentObligations(surtax=(_regional(),)).latest_tax_year == 2025
