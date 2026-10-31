"""The notice of Metalmeccanico Federmeccanica, as Art. 1 Tit. VIII sets it.

CCNL 5 February 2021, Sez. Quarta, Titolo VIII, Art. 1 (p. 230): the same
tables for dismissal and resignation, by level group and service.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.termination.notice.models import TerminationCause

_NOTICE = load_ccnl("metalmeccanico-federmeccanica").work_rules
assert _NOTICE is not None
assert _NOTICE.notice is not None
RULES = _NOTICE.notice
_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION


@pytest.mark.parametrize(
    ("level", "service", "months", "days", "indemnity"),
    [
        ("A1", 60, 2, 0, "2"),
        ("B3", 61, 3, 0, "3"),
        ("B2", 121, 4, 0, "4"),
        ("C3", 60, 1, 15, "1.5"),
        ("B1", 120, 2, 0, "2"),
        ("C2", 300, 2, 15, "2.5"),
        ("D1", 1, 0, 10, "0.33"),
        ("C1", 119, 0, 20, "0.67"),
        ("D2", 121, 1, 0, "1"),
    ],
)
@pytest.mark.parametrize(
    "cause", [TerminationCause.DISMISSAL, TerminationCause.RESIGNATION]
)
def test_the_table_of_art_1(
    level: str,
    service: int,
    months: int,
    days: int,
    indemnity: str,
    cause: TerminationCause,
) -> None:
    """Each level group and service band, for either cause."""
    band = RULES.band(level, cause, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (
        months,
        days,
        Decimal(indemnity),
    )


_WORK = load_ccnl("commercio-confcommercio").work_rules
assert _WORK is not None
assert _WORK.notice is not None
_COMMERCIO = _WORK.notice


@pytest.mark.parametrize(
    ("level", "service", "dismissal", "resignation"),
    [
        ("Q", 60, 60, 45),
        ("1", 61, 90, 60),
        ("2", 121, 60, 45),
        ("3", 1, 30, 20),
        ("4", 120, 30, 20),
        ("5", 121, 45, 30),
        ("6", 60, 15, 10),
        ("7", 121, 20, 15),
    ],
)
def test_the_tables_of_commercio_artt_247_and_254(
    level: str, service: int, dismissal: int, resignation: int
) -> None:
    """Calendar days by level group and service, apart for each cause."""
    rules = _COMMERCIO
    found = [rules.band(level, cause, service) for cause in (_D, _R)]

    assert [(b.months, b.days, b.indemnity_months) for b in found if b] == [
        (0, dismissal, None),
        (0, resignation, None),
    ]
    assert (rules.starts.value, rules.extra_months_included, rules.tfr_base) == (
        "first_or_sixteenth",
        True,
        False,
    )
