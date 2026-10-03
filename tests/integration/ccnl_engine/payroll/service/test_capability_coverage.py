"""Capability coverage of a CCNL: the registry lowered by its missing notes."""

from __future__ import annotations

import pytest

from ccnl_engine.contract.domain.identity import CCNL, CoverageNote, NoteKind
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.knowledge.service.capability_catalog_loader import (
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
from ccnl_engine.shared.domain.errors import DataIntegrityError

_CATALOG = load_capability_catalog(2026)
_IMPL = CapabilityImplementation


def _with_missing(ccnl: CCNL, *capabilities: str) -> CCNL:
    notes = tuple(
        CoverageNote(kind=NoteKind.MISSING, text="not in the file", capability=c)
        for c in capabilities
    )
    coverage = ccnl.coverage.model_copy(update={"notes": notes})
    return ccnl.model_copy(update={"coverage": coverage})


def _by_feature(ccnl: CCNL) -> dict[str, tuple[CapabilityImplementation, bool]]:
    return {
        c.feature: (c.implementation, c.limited_by_ccnl)
        for c in ccnl_capabilities(_CATALOG, ccnl)
    }


def test_without_notes_the_registry_applies() -> None:
    """Every capability keeps the implementation of the registry."""
    rows = _by_feature(load_ccnl("metalmeccanico-federmeccanica.json"))
    assert rows == {e.feature: (e.implementation, False) for e in _CATALOG.capabilities}


def test_missing_note_lowers_its_capability() -> None:
    """A native or caller-supplied capability becomes partial; others stay."""
    ccnl = _with_missing(
        load_ccnl("metalmeccanico-federmeccanica.json"),
        "base_salary",
        "overtime",
        "sickness",
        "inail",
    )
    rows = _by_feature(ccnl)
    assert rows["base_salary"] == (_IMPL.PARTIAL, True)
    assert rows["overtime"] == (_IMPL.PARTIAL, True)
    assert rows["sickness"] == (_IMPL.PARTIAL, True)
    assert rows["inail"] == (_IMPL.UNSUPPORTED, True)
    assert rows["irpef"] == (_IMPL.NATIVE, False)


def test_bundled_missing_notes() -> None:
    """The bundle's missing notes name the capabilities they limit."""
    limited = {
        filename: sorted(
            f for f, (_, named) in _by_feature(load_ccnl(filename)).items() if named
        )
        for filename in (
            "assicurazioni-ania.json",
            "ced-assoced.json",
            "ortofrutticoli-agrumari.json",
        )
    }
    assert limited == {
        "assicurazioni-ania.json": ["base_salary"],
        "ced-assoced.json": ["base_salary"],
        "ortofrutticoli-agrumari.json": ["leave", "sickness"],
    }


def test_unknown_capability_is_rejected() -> None:
    """A note naming a capability outside the registry is a data error."""
    ccnl = _with_missing(load_ccnl("metalmeccanico-federmeccanica.json"), "ghost")
    with pytest.raises(DataIntegrityError, match=r"\['ghost'\]"):
        ccnl_capabilities(_CATALOG, ccnl)


def test_layer_is_its_worst_capability() -> None:
    """A layer is as covered as its weakest capability."""
    capabilities = ccnl_capabilities(
        _CATALOG, load_ccnl("metalmeccanico-federmeccanica.json")
    )
    assert layer_coverage(capabilities) == dict.fromkeys(
        CapabilityLayer, _IMPL.UNSUPPORTED
    )
    native = [c for c in capabilities if c.implementation is _IMPL.NATIVE]
    assert layer_coverage(native) == dict.fromkeys(CapabilityLayer, _IMPL.NATIVE)
