"""The limitation registry of the bundle: complete, consistent, executable.

Every simplification note of a CCNL states its monetary impact, and every
one that can move an amount declares a limitation (the CCNL model rejects
the file otherwise).  Here the registry is checked across files: each
capability exists in the registry of the year, each engine limitation is
raised by the code that holds it, and its rulesets are exactly the CCNLs
whose data can take its code path.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine import PayrollEngine
from ccnl_engine.contract.domain.apprenticeship import ApprenticeshipUnderClassification
from ccnl_engine.contract.domain.identity import NoteKind
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.knowledge.service.limitation_loader import load_engine_limitations
from ccnl_engine.payroll.application.handlers.sickness import (
    CUMULATION_LIMITATION,
    INPS_DAILY_BASE_LIMITATION,
)
from ccnl_engine.payroll.service.apprenticeship import MIDPOINT_VARIANT
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.service.seniority import APPRENTICE_SENIORITY_VARIANT
from ccnl_engine.shared.domain.limitation import LimitationStatus, MonetaryImpact

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL


@pytest.fixture(scope="module")
def ccnls() -> tuple[CCNL, ...]:
    """Return every bundled CCNL.

    Returns:
        The CCNLs of the bundle.
    """
    repo = BundledKnowledgeRepository()
    return tuple(
        repo.load_ccnl(f"{info.ccnl_id}.json")
        for info in PayrollEngine.list_contracts()
    )


def test_every_monetary_simplification_is_mapped(ccnls: tuple[CCNL, ...]) -> None:
    """Every simplification with a monetary impact is a registry limitation."""
    notes = [
        note
        for ccnl in ccnls
        for note in ccnl.coverage.notes
        if note.kind is NoteKind.SIMPLIFICATION
    ]
    monetary = [n for n in notes if n.monetary_impact is not MonetaryImpact.NO]
    assert len(notes) >= 224
    assert all(note.limitation is not None for note in monetary)
    assert sum(len(ccnl.limitations) for ccnl in ccnls) == len(monetary)


def test_limitations_name_registry_capabilities(ccnls: tuple[CCNL, ...]) -> None:
    """A limitation limits a capability the registry of the year holds."""
    features = {e.feature for e in load_capability_catalog(2026).capabilities}
    limitations = [
        *load_engine_limitations(),
        *(lim for ccnl in ccnls for lim in ccnl.limitations),
    ]
    assert {lim.capability for lim in limitations} <= features


_APPRENTICE_SENIORITY = "apprentice_seniority_simplified"
_MIDPOINT = "apprenticeship_midpoint_allowances"


def test_engine_limitations_are_raised_by_their_code() -> None:
    """Each open engine limitation id is the one its code path records.

    A resolved one stays in the bundle as the record of what closed it;
    no code path records it any more.
    """
    by_status = {
        status: {lim.id for lim in load_engine_limitations() if lim.status is status}
        for status in LimitationStatus
    }
    assert by_status[LimitationStatus.OPEN] == {
        INPS_DAILY_BASE_LIMITATION,
        CUMULATION_LIMITATION,
    }
    assert by_status[LimitationStatus.RESOLVED] == {_MIDPOINT, _APPRENTICE_SENIORITY}


def _has_midpoint(ccnl: CCNL) -> bool:
    return any(
        period.midpoint_to_destination
        for track in ccnl.apprenticeship
        if isinstance(track, ApprenticeshipUnderClassification)
        for period in track.periods
    )


def _has_level_seniority_for_apprentices(ccnl: CCNL) -> bool:
    increments = ccnl.parameters.seniority_increments
    levels = {
        *increments.amount_by_level,
        *(code for tier in increments.tiers for code in tier.amount_by_level),
        *(
            code
            for amounts in increments.amount_by_level_by_category.values()
            for code in amounts
        ),
    }
    return any(set(track.destination_levels) & levels for track in ccnl.apprenticeship)


def test_engine_limitation_rulesets_are_derived_from_data(
    ccnls: tuple[CCNL, ...],
) -> None:
    """The rulesets of an engine limitation are the CCNLs that can take its path."""
    rulesets = {lim.id: set(lim.rulesets) for lim in load_engine_limitations()}
    assert rulesets[_MIDPOINT] == {c.meta.ccnl_id for c in ccnls if _has_midpoint(c)}
    assert rulesets[_APPRENTICE_SENIORITY] == {
        c.meta.ccnl_id for c in ccnls if _has_level_seniority_for_apprentices(c)
    }


def _apprentice_seniority_notes(ccnl: CCNL) -> list[LimitationStatus]:
    return [
        lim.status
        for lim in ccnl.limitations
        if lim.variant == APPRENTICE_SENIORITY_VARIANT
    ]


def test_unsourced_apprentice_seniority_is_an_open_limitation(
    ccnls: tuple[CCNL, ...],
) -> None:
    """A CCNL whose levels pay apprentices increments states the apprentice rule.

    With an apprentice amount the rule is modelled; without one the
    engine pays none and the CCNL carries an open limitation, which the
    chain records when the level pays matured increments.
    """
    for ccnl in ccnls:
        unsourced = (
            _has_level_seniority_for_apprentices(ccnl)
            and ccnl.parameters.seniority_increments.apprentice_amount is None
        )
        expected = [LimitationStatus.OPEN] if unsourced else []
        assert _apprentice_seniority_notes(ccnl) == expected, ccnl.meta.ccnl_id


def test_unsourced_midpoint_components_are_an_open_limitation(
    ccnls: tuple[CCNL, ...],
) -> None:
    """Of the CCNLs with a midpoint period, only Federterme states its components.

    Its Art. 13 lett. g averages the whole pay; the others carry an open
    limitation the midpoint path records.
    """
    unsourced = {
        ccnl.meta.ccnl_id
        for ccnl in ccnls
        for lim in ccnl.limitations
        if lim.variant == MIDPOINT_VARIANT and lim.status is LimitationStatus.OPEN
    }
    midpoint = {c.meta.ccnl_id for c in ccnls if _has_midpoint(c)}
    assert unsourced == midpoint - {"aziende-termali-federterme"}
