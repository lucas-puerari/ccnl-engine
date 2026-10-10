"""Coverage of the bundled CCNLs: one derivation, no flag of their own.

A CCNL file used to declare ``gross``, ``net`` and ``work_rules`` flags
beside per-feature statuses, and the two disagreed.  Coverage now derives
from the capability registry, lowered by the ``missing`` notes of the file:
no file declares a flag, and no layer reads implemented while one of its
capabilities is not.
"""

from __future__ import annotations

import importlib.resources
import json

import pytest

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityImplementation,
    CapabilityLayer,
)
from ccnl_engine.payroll.service.capability_coverage import (
    ccnl_capabilities,
    layer_coverage,
)

_DATA = importlib.resources.files("ccnl_engine.knowledge").joinpath(
    "contract", "agreement"
)
_FILENAMES = sorted(
    entry.name for entry in _DATA.iterdir() if entry.name.endswith(".json")
)
_FLAGS = frozenset({"gross", "net", "work_rules", "work_rules_features"})


def test_bundle_is_not_empty() -> None:
    """A packaging mistake must not make the contract below vacuous."""
    assert _FILENAMES


@pytest.mark.parametrize("filename", _FILENAMES)
def test_no_file_declares_a_coverage_flag(filename: str) -> None:
    """The coverage block of a file holds notes only."""
    coverage = json.loads(_DATA.joinpath(filename).read_text(encoding="utf-8"))[
        "coverage"
    ]
    assert not _FLAGS & coverage.keys()


def _contradictions(filename: str) -> list[str]:
    """Return the layers of a CCNL that read native over a lesser capability.

    Returns:
        One ``"<layer>: <capabilities>"`` entry per contradicting layer.
    """
    capabilities = ccnl_capabilities(load_capability_catalog(2026), load_ccnl(filename))
    layers = layer_coverage(capabilities)
    found = []
    for layer in CapabilityLayer:
        lacking = [
            c.feature
            for c in capabilities
            if c.layer is layer
            and c.implementation is not CapabilityImplementation.NATIVE
        ]
        if layers[layer] is CapabilityImplementation.NATIVE and lacking:
            found.append(f"{layer}: {', '.join(lacking)}")
    return found


def test_implemented_work_rules_have_every_feature_implemented() -> None:
    """No CCNL shows a layer implemented with a capability not implemented.

    The layer status the index and the matrix print is the worst of its
    capabilities for the CCNL, so a layer reads native only when each of its
    capabilities is native.
    """
    contradicting = {
        filename: found
        for filename in _FILENAMES
        if (found := _contradictions(filename))
    }
    assert contradicting == {}


def test_layer_is_the_worst_of_its_capabilities() -> None:
    """The printed layer status is derived from its capabilities, never stored."""
    catalog = load_capability_catalog(2026)
    for filename in _FILENAMES:
        capabilities = ccnl_capabilities(catalog, load_ccnl(filename))
        assert layer_coverage(capabilities) == {
            layer: CapabilityImplementation.worst(
                c.implementation for c in capabilities if c.layer is layer
            )
            for layer in CapabilityLayer
        }
