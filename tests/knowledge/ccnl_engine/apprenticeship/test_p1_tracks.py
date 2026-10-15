"""Apprenticeship tracks and part-time hours of the first-round CCNLs.

- Sanità privata (CCNL 8 October 2020, p. 31): 85% then 90% of the pay of
  the qualifica, by the length of the contract (18, 24, 36 months).
- Logistica (testo unico p. 75): Tabella B pays the profili artigiani 90%,
  95% and 100%.
- Metalmeccanico artigianato (renewal of 19 November 2024, p. 6): the
  impiegati amministrativi by semester, 70, 70, 75, 80, 85, 90%.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.apprenticeship.models import ApprenticeshipPeriod
from ccnl_engine.catalog.loaders import load_ccnl


def _track(slug: str, name: str) -> list[tuple[int, Decimal]]:
    ccnl = load_ccnl(f"{slug}.json")
    (track,) = [t for t in ccnl.apprenticeship if t.name == name]
    periods = [p for p in track.periods if isinstance(p, ApprenticeshipPeriod)]
    assert len(periods) == len(track.periods)
    return [(p.months_from, p.percentage) for p in periods]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Apprendistato professionalizzante 18 mesi", [(0, "0.85"), (9, "0.90")]),
        ("Apprendistato professionalizzante 24 mesi", [(0, "0.85"), (12, "0.90")]),
        ("Apprendistato professionalizzante 36 mesi", [(0, "0.85"), (18, "0.90")]),
    ],
)
def test_sanita_privata_tracks(name: str, expected: list[tuple[int, str]]) -> None:
    """One track per length of the contract."""
    track = _track("sanita-privata-aiop-aris", name)

    assert track == [(m, Decimal(p)) for m, p in expected]


def test_logistica_tabella_b() -> None:
    """90%, 95%, then 100%."""
    track = _track("logistica-trasporto-confetra", "profili_artigiani")

    assert [p for _, p in track] == [Decimal("0.90"), Decimal("0.95"), Decimal("1.00")]


def test_artisan_impiegati_by_semester() -> None:
    """Six semesters, then the full pay."""
    track = _track("metalmeccanico-artigianato", "impiegati")

    assert [p for _, p in track] == [
        Decimal(x) for x in ("0.70", "0.75", "0.80", "0.85", "0.90", "1.00")
    ]


@pytest.mark.parametrize(
    "slug",
    [
        "sanita-privata-aiop-aris",
        "logistica-trasporto-confetra",
        "metalmeccanico-federmeccanica",
        "edilizia-ance",
    ],
)
def test_part_time_supplementary_rate_is_declared(slug: str) -> None:
    """The request cannot state supplementary hours apart from overtime."""
    ccnl = load_ccnl(f"{slug}.json")
    variants = {n.limitation.variant for n in ccnl.coverage.notes if n.limitation}

    assert "part_time_supplementary_rate" in variants
