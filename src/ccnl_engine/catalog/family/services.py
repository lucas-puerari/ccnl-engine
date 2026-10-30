"""List the contract families and filter the contracts by family."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.agreement.family.loaders import load_family_catalog
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validators import require_str

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.agreement.family.models import ContractFamily
    from ccnl_engine.catalog.loaders import ContractSummary

__all__ = ["list_families", "of_family"]


def list_families() -> tuple[ContractFamily, ...]:
    """Return the contract families of the central catalog, sorted by id.

    Returns:
        Every family a CCNL can name in ``meta.family``.
    """
    return load_family_catalog().families


def of_family(
    contracts: Iterable[ContractSummary], family: str | None
) -> tuple[ContractSummary, ...]:
    """Return the contracts of *family*, or all of them when it is ``None``.

    Args:
        contracts: The contracts to filter, e.g. those of a repository.
        family: Id of a family of :func:`list_families`, or ``None``.

    Returns:
        The contracts whose main family is *family*, in their order.

    Raises:
        InvalidInputError: When *family* is not a family of the catalog.
    """
    if family is None:
        return tuple(contracts)
    require_str(family, "family", feature="catalog")
    known = load_family_catalog().by_id
    if family not in known:
        msg = f"family {family!r} is not a contract family of the catalog"
        raise InvalidInputError(
            msg,
            field="family",
            feature="catalog",
            remediation=f"Use one of: {', '.join(known)}.",
        )
    return tuple(info for info in contracts if info.family == family)
