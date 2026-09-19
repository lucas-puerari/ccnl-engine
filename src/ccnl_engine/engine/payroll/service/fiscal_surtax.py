"""Surtax stage: addizionale regionale e comunale."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.service import irpef as _irpef
from ccnl_engine.engine.payroll.service.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules

_ZERO = Decimal(0)


def _comunale_amount(
    taxable_income: Decimal,
    surtax: SurtaxRules,
    comune_belfiore: str,
    sfs: set[FiscalSimplification],
) -> tuple[Decimal, bool]:
    """Compute comunale surtax and update simplification flags.

    Returns:
        ``(amount, applied)`` where *applied* is True when the entry was found.
    """
    entry_com = surtax.comunale.get(comune_belfiore)
    if entry_com is None:
        sfs.add(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
        sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
        return _ZERO, False
    amount = _irpef.surtax_from_brackets(
        taxable_income, entry_com.brackets, entry_com.exemption_threshold
    )
    sfs.discard(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
    sfs.discard(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
    if surtax.comunale_rates_are_advance:
        amount = money(amount * surtax.comunale_advance_fraction)
        sfs.add(FiscalSimplification.ADDIZIONALE_COMUNALE_ADVANCE_ONLY)
    return amount, True


def _compute_addizionali(
    taxable_income: Decimal,
    surtax: SurtaxRules | None,
    existing: frozenset[FiscalSimplification],
    *,
    regione: str | None,
    comune_belfiore: str | None,
    irpef_due: Decimal,
) -> tuple[Decimal, Decimal, frozenset[FiscalSimplification], bool, bool]:
    """Return amounts, simplifications and applied flags for addizionali.

    Returns:
        5-tuple of (regionale_amount, comunale_amount, simplifications,
        reg_applied, com_applied).
    """
    sfs: set[FiscalSimplification] = set(existing)
    addizionale_regionale = _ZERO
    addizionale_comunale = _ZERO

    if irpef_due == _ZERO:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
        sfs.discard(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
        sfs.discard(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)
        return _ZERO, _ZERO, frozenset(sfs), False, False

    reg_applied = False
    if surtax is not None and regione is not None:
        entry = surtax.regionale.get(regione)
        if entry is not None:
            reg_applied = True
            addizionale_regionale = _irpef.surtax_from_brackets(
                taxable_income, entry.brackets
            )
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
            sfs.discard(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
        else:
            sfs.add(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)
            sfs.discard(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_REGIONALE)
        sfs.discard(FiscalSimplification.ADDIZIONALE_REGIONALE_UNKNOWN)

    com_applied = False
    if surtax is not None and comune_belfiore is not None:
        addizionale_comunale, com_applied = _comunale_amount(
            taxable_income, surtax, comune_belfiore, sfs
        )
    else:
        sfs.add(FiscalSimplification.NO_ADDIZIONALE_COMUNALE)
        sfs.discard(FiscalSimplification.ADDIZIONALE_COMUNALE_UNKNOWN)

    return (
        addizionale_regionale,
        addizionale_comunale,
        frozenset(sfs),
        reg_applied,
        com_applied,
    )
