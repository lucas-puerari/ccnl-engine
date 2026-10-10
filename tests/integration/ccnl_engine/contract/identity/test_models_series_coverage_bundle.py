"""Temporal coverage of the series each bundled CCNL reads with a level.

Every series a run reads has a value or a declared gap from the first day
of the pay table it applies to.  The declared gaps are listed here, so a
new one is a reviewed change of the data, not a silent hole.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.catalog.loaders_discovery import list_contracts
from ccnl_engine.contract.identity.models_series_coverage import required_series
from ccnl_engine.contract.identity.rules_validity import SalaryGapKind, SeriesGapError

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL

_ALL_CCNL: list[CCNL] = [load_ccnl(c.ccnl_id + ".json") for c in list_contracts()]
_MISSING, _NOT_APPLICABLE = SalaryGapKind.MISSING, SalaryGapKind.NOT_APPLICABLE

#: Declared gaps of the required series: CCNL, gap kind, first date with a
#: value, and how many series declare it.
_DECLARED_GAPS: dict[tuple[str, SalaryGapKind, date], int] = {
    # Scatto amounts of the previous rinnovo not recovered (12 levels).
    ("grafica-editoria-aieg", _MISSING, date(2026, 7, 1)): 12,
    # Scatto amounts before the 23 April 2024 table not recovered (8 levels).
    ("dmo-federdistribuzione", _MISSING, date(2024, 4, 23)): 8,
    # Apprentice scatto amount before the October 2024 table not recovered.
    ("acconciatura-estetica-confartigianato", _MISSING, date(2024, 10, 1)): 1,
    # Apprentice scatto amount before the 2025 table not recovered.
    ("panificazione-artigianato-confartigianato", _MISSING, date(2025, 1, 1)): 1,
    # Premio di produzione before the February 2024 table not recovered.
    ("panificazione-assipan", _MISSING, date(2024, 2, 1)): 7,
    # EDR introduced by the verbale of 23 May 2025: not in force before.
    ("noleggio-autobus-conducente-anav", _NOT_APPLICABLE, date(2025, 7, 1)): 11,
}


def _gaps(ccnl: CCNL) -> Counter[tuple[str, SalaryGapKind, date]]:
    found: Counter[tuple[str, SalaryGapKind, date]] = Counter()
    for _path, _start, series in required_series(ccnl.levels, ccnl.parameters):
        for period in series.periods:
            if period.gap_kind is not None and period.valid_until is not None:
                key = (ccnl.meta.ccnl_id, period.gap_kind, period.valid_until)
                found[key] += 1
    return found


@pytest.mark.parametrize("ccnl", _ALL_CCNL, ids=lambda c: c.meta.ccnl_id)
def test_required_series_cover_their_pay_table(ccnl: CCNL) -> None:
    """On its first date each required series has a value or a declared gap."""
    starting_late = []
    for path, start, series in required_series(ccnl.levels, ccnl.parameters):
        try:
            series.value_at(start)
        except SeriesGapError as gap:
            if gap.gap_kind is None:
                starting_late.append(f"{path} from {start}")
    assert starting_late == []


def test_declared_gaps_are_the_reviewed_ones() -> None:
    """The bundle declares exactly the reviewed gaps."""
    found: Counter[tuple[str, SalaryGapKind, date]] = Counter()
    for ccnl in _ALL_CCNL:
        found += _gaps(ccnl)
    assert dict(found) == _DECLARED_GAPS
