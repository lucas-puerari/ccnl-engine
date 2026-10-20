"""Capability coverage of a CCNL: the registry lowered by its missing notes."""

from __future__ import annotations

import pytest

from ccnl_engine.agreement.facade import CCNL, CoverageNote, NoteKind
from ccnl_engine.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.capability.registry.models import (
    CapabilityImplementation,
)
from ccnl_engine.capability.support.services import (
    ccnl_capabilities,
)
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import DataIntegrityError

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
    rows = _by_feature(load_ccnl("energia-petrolio-confindustria"))
    assert rows == {e.feature: (e.implementation, False) for e in _CATALOG.capabilities}


def test_missing_note_lowers_its_capability() -> None:
    """A native or caller-supplied capability becomes partial; others stay."""
    ccnl = _with_missing(
        load_ccnl("metalmeccanico-federmeccanica"),
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
        ccnl_id: sorted(
            f for f, (_, named) in _by_feature(load_ccnl(ccnl_id)).items() if named
        )
        for ccnl_id in (
            "assicurazioni-ania",
            "ced-assoced",
            "ortofrutticoli-agrumari",
        )
    }
    assert limited == {
        "assicurazioni-ania": ["base_salary", "inps_employer", "seniority"],
        "ced-assoced": ["base_salary", "inps_employer"],
        "ortofrutticoli-agrumari": [
            "base_salary",
            "leave",
            "seniority",
            "sickness",
        ],
    }


@pytest.mark.parametrize(
    ("ccnl_id", "features"),
    [
        ("impianti-sportivi-sport", ("overtime", "sickness")),
        ("concia-unic", ("overtime",)),
        ("ortofrutticoli-agrumari", ("sickness",)),
        (
            "pulizia-artigianato-confartigianato",
            ("holiday_work", "night_work"),
        ),
    ],
)
def test_work_rules_partials_are_derived(
    ccnl_id: str, features: tuple[str, ...]
) -> None:
    """The work-rule gaps these files once declared as flags are partial."""
    rows = _by_feature(load_ccnl(ccnl_id))
    assert all(rows[feature][0] is _IMPL.PARTIAL for feature in features)


def test_a_missing_note_on_leave_lowers_it_to_partial() -> None:
    """A missing note on leave lowers the native capability to partial."""
    rows = _by_feature(load_ccnl("ortofrutticoli-agrumari"))
    assert rows["leave"] == (_IMPL.PARTIAL, True)


def test_unknown_capability_is_rejected() -> None:
    """A note naming a capability outside the registry is a data error."""
    ccnl = _with_missing(load_ccnl("metalmeccanico-federmeccanica"), "ghost")
    with pytest.raises(DataIntegrityError, match=r"\['ghost'\]"):
        ccnl_capabilities(_CATALOG, ccnl)
