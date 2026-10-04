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
    rows = _by_feature(load_ccnl("chimica-farmaceutica-federchimica.json"))
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


def test_bundled_missing_notes_and_limitations() -> None:
    """Missing notes and blocking limitations name the capabilities they limit."""
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
        "assicurazioni-ania.json": ["base_salary", "inps_employer", "seniority"],
        "ced-assoced.json": ["base_salary", "inps_employer"],
        "ortofrutticoli-agrumari.json": [
            "base_salary",
            "leave",
            "seniority",
            "sickness",
        ],
    }


@pytest.mark.parametrize(
    ("filename", "features"),
    [
        ("impianti-sportivi-sport.json", ("overtime", "sickness")),
        ("concia-unic.json", ("overtime", "sickness")),
        ("ortofrutticoli-agrumari.json", ("sickness",)),
        (
            "pulizia-artigianato-confartigianato.json",
            ("holiday_work", "night_work"),
        ),
    ],
)
def test_work_rules_partials_are_derived(
    filename: str, features: tuple[str, ...]
) -> None:
    """The work-rule gaps these files once declared as flags are partial."""
    rows = _by_feature(load_ccnl(filename))
    assert all(rows[feature][0] is _IMPL.PARTIAL for feature in features)


def test_leave_without_an_event_stays_unsupported() -> None:
    """A missing note on leave, which no event computes, keeps it unsupported."""
    rows = _by_feature(load_ccnl("ortofrutticoli-agrumari.json"))
    assert rows["leave"] == (_IMPL.UNSUPPORTED, True)


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
