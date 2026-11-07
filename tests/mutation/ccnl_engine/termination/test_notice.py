"""The notice tables of the CCNLs that state one, by family shape.

Metalmeccanico Federmeccanica (CCNL 5 February 2021, Sez. Quarta, Tit. VIII,
Art. 1) and Confapi (CCNL 3 July 2017, Art. 75): months and days with the
indemnity in monthly pays, the same for either cause.  Terziario
Confcommercio (artt. 247, 254) and Confesercenti (the same articles):
calendar days apart for each cause.  Cooperative sociali (Art. 33) and
Turismo (Art. 187) and Pubblici esercizi (Art. 208): months or calendar
days, the same for either cause.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employment.period.inputs import TerminationCause

if TYPE_CHECKING:
    from ccnl_engine.termination.notice.models import NoticeRules

_D, _R = TerminationCause.DISMISSAL, TerminationCause.RESIGNATION


def _notice(ccnl_id: str) -> NoticeRules:
    work = load_ccnl(ccnl_id).work_rules
    assert work is not None
    assert work.notice is not None
    return work.notice


@pytest.mark.parametrize(
    ("ccnl_id", "level", "service", "months", "days", "indemnity"),
    [
        ("metalmeccanico-federmeccanica", "A1", 60, 2, 0, "2"),
        ("metalmeccanico-federmeccanica", "B3", 61, 3, 0, "3"),
        ("metalmeccanico-federmeccanica", "B2", 121, 4, 0, "4"),
        ("metalmeccanico-federmeccanica", "C3", 60, 1, 15, "1.5"),
        ("metalmeccanico-federmeccanica", "B1", 120, 2, 0, "2"),
        ("metalmeccanico-federmeccanica", "C2", 300, 2, 15, "2.5"),
        ("metalmeccanico-federmeccanica", "D1", 1, 0, 10, "0.33"),
        ("metalmeccanico-federmeccanica", "C1", 119, 0, 20, "0.67"),
        ("metalmeccanico-federmeccanica", "D2", 121, 1, 0, "1"),
        ("metalmeccanico-confapi", "9", 60, 2, 0, "2"),
        ("metalmeccanico-confapi", "7", 121, 4, 0, "4"),
        ("metalmeccanico-confapi", "4", 61, 2, 0, "2"),
        ("metalmeccanico-confapi", "6", 121, 2, 15, "2.5"),
        ("metalmeccanico-confapi", "3", 120, 0, 20, "0.67"),
        ("metalmeccanico-confapi", "2", 121, 0, 30, "1"),
        ("metalmeccanico-confapi", "1", 60, 0, 7, "0.24"),
        ("metalmeccanico-confapi", "1", 61, 0, 15, "0.5"),
    ],
)
@pytest.mark.parametrize("cause", [_D, _R])
def test_the_monthly_pay_tables_of_the_metalworkers(
    ccnl_id: str,
    level: str,
    service: int,
    months: int,
    days: int,
    indemnity: str,
    cause: TerminationCause,
) -> None:
    """Each level group and service band, for either cause."""
    band = _notice(ccnl_id).band(level, cause, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (
        months,
        days,
        Decimal(indemnity),
    )


@pytest.mark.parametrize(
    ("ccnl_id", "level", "service", "dismissal", "resignation"),
    [
        ("commercio-confcommercio", "Q", 60, 60, 45),
        ("commercio-confcommercio", "1", 61, 90, 60),
        ("commercio-confcommercio", "2", 121, 60, 45),
        ("commercio-confcommercio", "3", 1, 30, 20),
        ("commercio-confcommercio", "4", 120, 30, 20),
        ("commercio-confcommercio", "5", 121, 45, 30),
        ("commercio-confcommercio", "6", 60, 15, 10),
        ("commercio-confcommercio", "7", 121, 20, 15),
        ("terziario-confesercenti", "I", 121, 120, 90),
        ("terziario-confesercenti", "III", 61, 45, 30),
        ("terziario-confesercenti", "V", 60, 20, 15),
        ("terziario-confesercenti", "VI", 121, 20, 15),
    ],
)
def test_the_calendar_day_tables_of_the_terziario(
    ccnl_id: str, level: str, service: int, dismissal: int, resignation: int
) -> None:
    """Calendar days by level group and service, apart for each cause."""
    rules = _notice(ccnl_id)
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


@pytest.mark.parametrize(
    ("ccnl_id", "level", "service", "months", "days", "indemnity"),
    [
        ("cooperative-sociali", "B", 36, 0, 15, None),
        ("cooperative-sociali", "C2", 37, 0, 45, None),
        ("cooperative-sociali", "D3", 1, 0, 45, None),
        ("cooperative-sociali", "F1Q", 37, 0, 120, None),
        ("turismo-federalberghi", "A", 60, 4, 0, "4"),
        ("turismo-federalberghi", "1", 121, 4, 0, "4"),
        ("turismo-federalberghi", "3", 61, 0, 45, None),
        ("turismo-federalberghi", "2", 121, 2, 0, "2"),
        ("turismo-federalberghi", "6s", 121, 0, 20, None),
        ("pubblici-esercizi-fipe-angem", "Qa", 121, 6, 0, "6"),
        ("pubblici-esercizi-fipe-angem", "5", 61, 0, 30, None),
    ],
)
@pytest.mark.parametrize("cause", [_D, _R])
def test_the_tables_alike_for_either_cause(
    ccnl_id: str,
    level: str,
    service: int,
    months: int,
    days: int,
    indemnity: str | None,
    cause: TerminationCause,
) -> None:
    """Months or calendar days; the pay of the days where no months are set."""
    rules = _notice(ccnl_id)
    band = rules.band(level, cause, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (
        months,
        days,
        None if indemnity is None else Decimal(indemnity),
    )
    assert (rules.starts.value, rules.extra_months_included, rules.tfr_base) == (
        "day_after",
        False,
        None,
    )
