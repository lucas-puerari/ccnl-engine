"""Select the INPS sector of a multi-sector agreement."""

from __future__ import annotations

from ccnl_engine.agreement.facade import CCNL, TaxSector
from ccnl_engine.errors import InvalidInputError


def with_employer_sector(
    ccnl: CCNL, stated: TaxSector | None
) -> tuple[CCNL, tuple[TaxSector, ...]]:
    """Return the CCNL read in the INPS sector of the employer.

    A CCNL applied by employers of more than one INPS sector
    (``CCNLMeta.inps_sectors``) is read in the sector the employer states,
    so every rule that follows the sector (INPS rates, sickness cover, the
    Fondo Tesoreria) follows the classification of the employer.

    Returns:
        The CCNL, with ``tax_sector`` the stated sector, and the sectors
        left open when the CCNL lists several and none is stated.

    Raises:
        InvalidInputError: When the stated sector is not one the CCNL lists.
    """
    meta = ccnl.meta
    allowed = meta.inps_sectors or frozenset({meta.tax_sector})
    if stated is None:
        open_sectors = () if len(allowed) == 1 else tuple(sorted(allowed))
        return ccnl, open_sectors
    if stated not in allowed:
        msg = (
            f"EmployerProfile.inps_sector is {stated}, but the employers of "
            f"{meta.ccnl_id} are classified in {', '.join(sorted(allowed))}"
        )
        raise InvalidInputError(
            msg,
            field="EmployerProfile.inps_sector",
            feature="inps_employer",
            ruleset=meta.ccnl_id,
        )
    if stated is meta.tax_sector:
        return ccnl, ()
    sector_meta = meta.model_copy(update={"tax_sector": stated})
    return ccnl.model_copy(update={"meta": sector_meta}), ()
