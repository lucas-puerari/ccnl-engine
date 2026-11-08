"""Tessile-moda artigianato: the increments and tracks of chimica and ceramica.

Stesura of 16 July 2024, art. 67 (p. 90): chimica 6° 17,04, ceramica A
11,36, five biennial increments each; art. 68 (pp. 94-95): three groups of
apprenticeship per sector; apprentices 6 EUR per increment from 2025.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.apprenticeship.models import ApprenticeshipPercentage
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.working_time.subsector.rules import with_subsector

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_CCNL = load_ccnl("tessile-moda-artigianato-confartigianato")
_DAY = date(2026, 1, 1)


def _in(subsector: str | None, level: str) -> CCNL:
    ccnl, _ = with_subsector(_CCNL, subsector, WorkerCategory.OPERAIO, level_code=level)
    return ccnl


def test_chimica_takes_its_increments_and_tracks() -> None:
    """Five increments, 17.04 at the 6th level; the three chimica groups."""
    ccnl = _in("chimica", "6")
    increments = ccnl.parameters.seniority_increments
    assert increments.maximum_count == 5
    assert increments.amount_by_level["6"].value_at(_DAY) == Decimal("17.04")
    assert [t.name for t in ccnl.apprenticeship] == [
        "gruppo_1_chimica",
        "gruppo_2_chimica",
        "gruppo_3_chimica",
    ]


def test_ceramica_takes_its_own() -> None:
    """A 11.36; group 1 at 70% in the first semester."""
    ccnl = _in("ceramica", "A")
    increments = ccnl.parameters.seniority_increments
    assert increments.amount_by_level["A"].value_at(_DAY) == Decimal("11.36")
    assert increments.apprentice_amount is not None
    assert increments.apprentice_amount.value_at(_DAY) == Decimal("6.00")
    (first, *_) = ccnl.apprenticeship
    assert isinstance(first, ApprenticeshipPercentage)
    assert (first.name, first.periods[0].percentage) == (
        "gruppo_1_ceramica",
        Decimal("0.70"),
    )


def test_without_a_subsector_the_tessile_rules_hold() -> None:
    """Four increments and the abbigliamento groups."""
    ccnl = _in(None, "6")
    assert ccnl.parameters.seniority_increments.maximum_count == 4
    assert [t.name for t in ccnl.apprenticeship] == [
        "gruppo_1_abb",
        "gruppo_2_abb",
        "gruppo_3_abb",
    ]
