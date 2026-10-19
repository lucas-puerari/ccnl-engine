"""Apprenticeship of ABI and operai agricoli from the full texts.

- ABI, testo coordinato of 23 November 2023 (FABI, sha256
  4d92bc5226736682ddb1eedfaf7940df989fdc3cbbd99d0fa6347fd91979a933), Art. 36:
  every 3a area level is a destination, one level below for 18 months.
- Operai agricoli, CCNL 23 May 2022 (FLAI, sha256
  49ae5803f2081985a0e1a10f64e9019e1b999e808da9d3681eaab24c3dee674c),
  Allegato n. 10: the under-classification counts provincial levels, so an
  apprentice run is blocked.
"""

from __future__ import annotations

from ccnl_engine.catalog.loaders import load_ccnl


def test_abi_terza_area_destinations() -> None:
    """3A1 to 3A4."""
    (track,) = load_ccnl("bancari-abi").apprenticeship

    assert set(track.destination_levels) == {"3A1", "3A2", "3A3", "3A4"}


def test_agricoli_apprentices_are_blocked() -> None:
    """The provincial levels are not in the national file."""
    ccnl = load_ccnl("operai-agricoli-florovivaisti")
    scopes = {
        n.limitation.variant: n.limitation.applies_when
        for n in ccnl.coverage.notes
        if n.limitation
    }

    assert scopes["agricoli_apprentice_provincial_levels"].contract_types == frozenset({
        "apprentice"
    })
