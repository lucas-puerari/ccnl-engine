"""Surtax of 2025 imported from a previous provider into the 2026 state.

The conguaglio of 2025 determines the regional surtax and the municipal
saldo of 2025 and the municipal acconto of 2026, withheld in 2026.  The
amounts here are round figures stated by the test, not computed: they
stand for what the previous provider certified (CU 2026 points 22, 27 and
29), so every run of 2026 has surtax to withhold.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine import OpeningBalances, PeriodState, SurtaxComponent, SurtaxObligation

__all__ = ["imported_2025_surtax", "opening_with_2025_surtax"]

#: Regional surtax of 2025: 11 installments of 30.00.
REGIONAL_2025 = Decimal("330.00")
#: Municipal saldo of 2025: 11 installments of 10.00.
MUNICIPAL_BALANCE_2025 = Decimal("110.00")
#: Municipal acconto of 2026: 9 installments of 5.00.
MUNICIPAL_ADVANCE_2026 = Decimal("45.00")


def imported_2025_surtax(
    regione: str = "IT-25", comune_belfiore: str = "F205"
) -> tuple[SurtaxObligation, ...]:
    """Return the three surtax obligations of the 2025 conguaglio.

    Returns:
        Regional saldo, municipal saldo and municipal acconto, none posted.
    """
    return (
        SurtaxObligation.open(
            SurtaxComponent.REGIONAL_BALANCE, 2025, regione, REGIONAL_2025
        ),
        SurtaxObligation.open(
            SurtaxComponent.MUNICIPAL_BALANCE,
            2025,
            comune_belfiore,
            MUNICIPAL_BALANCE_2025,
        ),
        SurtaxObligation.open(
            SurtaxComponent.MUNICIPAL_ADVANCE,
            2025,
            comune_belfiore,
            MUNICIPAL_ADVANCE_2026,
        ),
    )


def opening_with_2025_surtax(
    regione: str = "IT-25", comune_belfiore: str = "F205"
) -> PeriodState:
    """Return the opening state of January 2026 with the 2025 surtax.

    Returns:
        A zero 2026 state carrying :func:`imported_2025_surtax`.
    """
    return OpeningBalances(
        tax_year=2026,
        surtax_obligations=imported_2025_surtax(regione, comune_belfiore),
    ).to_state()
