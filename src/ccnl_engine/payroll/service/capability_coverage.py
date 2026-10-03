"""Capability coverage of a CCNL, derived from the capability registry.

The coverage of every capability for a CCNL is the implementation the
registry declares, lowered to ``partial`` when a ``missing`` note of the
CCNL names the capability (data the engine supports but the file lacks) or
an open limitation of the CCNL with a monetary impact limits it.
A layer (gross, net, work rules) is as covered as its worst capability.

The contracts index, the capability matrix and the contract pages all read
this derivation, so they cannot disagree; no CCNL file declares a coverage
flag of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.contract.domain.identity import NoteKind
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityImplementation,
    CapabilityLayer,
)
from ccnl_engine.shared.domain.errors import DataIntegrityError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.capability_catalog import CapabilityCatalog

__all__ = ["CcnlCapability", "ccnl_capabilities", "layer_coverage"]

#: Implementations a ``missing`` note of the CCNL lowers to partial.
_LOWERED = frozenset({
    CapabilityImplementation.NATIVE,
    CapabilityImplementation.CALLER_SUPPLIED,
})


@dataclass(frozen=True)
class CcnlCapability:
    """Coverage of one registry capability for one CCNL.

    Attributes:
        feature: The capability name.
        layer: Payslip layer of the capability.
        implementation: Implementation for this CCNL.
        limited_by_ccnl: Whether a ``missing`` note or a blocking limitation
            of the CCNL names it.
    """

    feature: str
    layer: CapabilityLayer
    implementation: CapabilityImplementation
    limited_by_ccnl: bool = False


def ccnl_capabilities(
    catalog: CapabilityCatalog, ccnl: CCNL
) -> tuple[CcnlCapability, ...]:
    """Return the coverage of every registry capability for *ccnl*.

    Returns:
        One entry per capability, in registry order.

    Raises:
        DataIntegrityError: When a note of the CCNL names a capability the
            registry does not hold.
    """
    limited = {
        note.capability
        for note in ccnl.coverage.notes
        if note.kind is NoteKind.MISSING and note.capability is not None
    } | {limitation.capability for limitation in ccnl.limitations if limitation.blocks}
    unknown = sorted(limited - {entry.feature for entry in catalog.capabilities})
    if unknown:
        msg = (
            f"CCNL {ccnl.meta.ccnl_id}: coverage notes name capabilities "
            f"missing from the {catalog.year} registry: {unknown}"
        )
        raise DataIntegrityError(msg)
    rows: list[CcnlCapability] = []
    for entry in catalog.capabilities:
        named = entry.feature in limited
        rows.append(
            CcnlCapability(
                feature=entry.feature,
                layer=entry.layer,
                implementation=(
                    CapabilityImplementation.PARTIAL
                    if named and entry.implementation in _LOWERED
                    else entry.implementation
                ),
                limited_by_ccnl=named,
            )
        )
    return tuple(rows)


def layer_coverage(
    capabilities: Iterable[CcnlCapability],
) -> dict[CapabilityLayer, CapabilityImplementation]:
    """Return the coverage of each layer: its worst capability.

    Returns:
        Every layer to the worst implementation of its capabilities.
    """
    capabilities = tuple(capabilities)
    return {
        layer: CapabilityImplementation.worst(
            c.implementation for c in capabilities if c.layer is layer
        )
        for layer in CapabilityLayer
    }
