"""Small fiscal computation helpers: indemnities, conguaglio, simplification flags."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.metadata import RulesetIdentity

_ZERO = Decimal(0)
_UNVERIFIED = "unverified"


def _vs(identity: RulesetIdentity | None) -> str:
    """Return verification status string, or ``"unverified"`` when absent.

    Returns:
        Verification status value, or ``"unverified"`` for absent identities.
    """
    return identity.verification_status.value if identity is not None else _UNVERIFIED


def _injury_indemnity(raw: Decimal | None) -> Decimal:
    """Return the caller-declared workplace injury INAIL indemnity, or zero.

    Returns:
        The indemnity amount, or zero when absent.
    """
    return money(raw) if raw is not None else _ZERO


def _termination_amount(raw: Decimal | None) -> Decimal:
    """Return the caller-declared termination amount, or zero when absent.

    Returns:
        The termination amount, or zero when absent.
    """
    return money(raw) if raw is not None else _ZERO


def _maternity_indemnity(raw: Decimal | None) -> Decimal:
    """Return the caller-declared maternity/parental INPS indemnity, or zero.

    Returns:
        The indemnity amount, or zero when absent.
    """
    return money(raw) if raw is not None else _ZERO


def _conguaglio(irpef_net: Decimal, prior_withheld: Decimal | None) -> Decimal:
    """Compute fiscal adjustment (conguaglio) against prior-period withholding.

    Returns:
        Difference (positive = under-withheld, negative = over-withheld),
        or zero when no prior figure is supplied.
    """
    return money(irpef_net - prior_withheld) if prior_withheld is not None else _ZERO


def _inps_exemption(inps_employer_annual: Decimal, raw: Decimal | None) -> Decimal:
    """Apply the caller-declared INPS employer exemption, capped at the contribution.

    Returns:
        Exemption amount to subtract from employer cost, or zero when absent.
    """
    return money(min(inps_employer_annual, raw)) if raw is not None else _ZERO


def _update_simplification_flags(
    sfs: frozenset[FiscalSimplification],
    *,
    has_any_dependent: bool,
    art15_total: Decimal,
    ud_rules_present: bool,
    se_rules_present: bool,
    has_bilateral_funds: bool,
) -> frozenset[FiscalSimplification]:
    """Return updated simplification flags after applying optional-feature presence.

    Returns:
        Updated frozenset of active fiscal simplifications.
    """
    sfs_mut: set[FiscalSimplification] = set(sfs)
    if has_any_dependent:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_FAMILIARI)
    if art15_total > _ZERO:
        sfs_mut.discard(FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE)
    if not ud_rules_present:
        sfs_mut.add(FiscalSimplification.NO_ULTERIORE_DETRAZIONE_LAVORO)
    if se_rules_present:
        sfs_mut.discard(FiscalSimplification.NO_SOMMA_ESENTE)
    else:
        sfs_mut.add(FiscalSimplification.NO_SOMMA_ESENTE)
    if has_bilateral_funds:
        sfs_mut.discard(FiscalSimplification.NO_BILATERAL_FUNDS)
    return frozenset(sfs_mut)
