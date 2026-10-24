"""The input packets of the production CCNLs, replayed through the engine.

Each production CCNL (the three pilots, Ristorazione collettiva, Turismo
and Pubblici esercizi) has a
packet for each scenario of the minimum set of the validation review, ready
to hand to a payroll provider.  Until a provider
computes them they are ``engine_provisional``: valid, covering nothing,
and pinned to what the engine computes today.
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import pytest

from scripts.documentation.validation_matrix.generate import matrix
from scripts.provenance.validation_packet.check import (
    SCENARIOS,
    check_all,
    coverage,
)
from tests.knowledge.ccnl_engine.period.validation_packet.runner import (
    FOLDER,
    compute,
)

_PILOTS = (
    "commercio-confcommercio",
    "metalmeccanico-federmeccanica",
    "edilizia-ance-impiegati",
    "pubblici-esercizi-fipe-angem-ristorazione-collettiva",
    "turismo-federalberghi",
    "pubblici-esercizi-fipe-angem",
)
_PACKETS: dict[str, dict[str, Any]] = {
    path.stem: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(FOLDER.glob("*.json"))
}


def test_every_production_ccnl_has_a_packet_for_every_scenario() -> None:
    """6 production CCNLs by 7 scenarios, one file each, named after both."""
    assert set(_PACKETS) == {f"{c}_{s}" for c in _PILOTS for s in SCENARIOS}
    assert all(p["inputs"]["scenario"] in k for k, p in _PACKETS.items())


def test_the_packets_are_valid_and_cover_nothing_yet() -> None:
    """A provisional packet passes the schema and lends no independence."""
    assert check_all(FOLDER) == []
    assert coverage(FOLDER) == set()
    assert {p["artifact"]["kind"] for p in _PACKETS.values()} == {"engine_provisional"}


def test_the_employer_cost_packets_compare_the_employer_side() -> None:
    """Employer contributions, TFR and employer cost, with a pension fund."""
    for ccnl in _PILOTS:
        packet = _PACKETS[f"{ccnl}_employer_cost"]
        assert [o["output"] for o in packet["outputs"]] == [
            "employer_contributions",
            "tfr",
            "employer_cost",
        ]
        assert packet["inputs"]["pension_fund"] != "none"


@pytest.mark.parametrize("name", sorted(_PACKETS))
def test_the_engine_reproduces_the_provisional_values(name: str) -> None:
    """Each value is what the engine computes today, within the tolerance.

    A change of the engine that moves a value fails here; rewrite the
    packets with the runner when the change is meant.
    """
    packet = _PACKETS[name]
    outputs = packet["outputs"]
    found = compute(packet["inputs"], [o["output"] for o in outputs])

    for output in outputs:
        gap = abs(found[output["output"]] - Decimal(output["value"]))
        assert gap <= Decimal(output["tolerance"]), (output["output"], found)


def test_the_packets_cover_every_production_ccnl() -> None:
    """A CCNL promoted to production gets its packets in the same change."""
    rows = matrix()

    assert {c for c, r in rows.items() if r.readiness == "production"} == set(_PILOTS)
