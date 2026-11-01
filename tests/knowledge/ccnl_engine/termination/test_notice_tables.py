"""The notice tables of further CCNLs, read off the clause of each.

- FIAIP, Impianti sportivi and Ortofrutticoli: calendar days by level group
  and service (up to five years, up to ten, over ten), alike for either
  cause, from the 1st or the 16th.
- Farmacie private and Radiotelevisive: calendar days by level alone.
- Dirigenza sanitaria (both areas): 8 months up to two years, 15 more days
  for each later year up to 4 more months; 3 months on a resignation.
- ANAS, Poste italiane and Università: 2, 3 or 4 months on a dismissal by
  service (up to five years, up to ten, over ten).
- Consorzi agrari: 2 months up to five years, then 3, from the 1st or the
  16th.
- Formazione professionale: 3 months on a dismissal; on a resignation 2
  months up to level IV, 3 above.
- Scuole private laiche: 1 month up to ten years and 2 over for levels I
  and II, 3 months for III to VII, 4 for VIII.
- Cemento: by area and service (up to five years, up to ten, over ten).
- Ferroviario Agens: 4 months for Quadri and A, 3 for B and C, 2 for D to F.
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
    ("ccnl_id", "level", "service", "days"),
    [
        ("agenti-immobiliari-fiaip", "Q", 60, 60),
        ("agenti-immobiliari-fiaip", "I", 61, 90),
        ("agenti-immobiliari-fiaip", "III", 121, 60),
        ("agenti-immobiliari-fiaip", "IV", 120, 30),
        ("agenti-immobiliari-fiaip", "VI", 121, 20),
        ("impianti-sportivi-sport", "I", 121, 120),
        ("impianti-sportivi-sport", "II", 1, 30),
        ("impianti-sportivi-sport", "V", 121, 45),
        ("impianti-sportivi-sport", "VI", 60, 15),
        ("ortofrutticoli-agrumari", "Q", 120, 90),
        ("ortofrutticoli-agrumari", "3", 61, 45),
        ("ortofrutticoli-agrumari", "4", 60, 20),
        ("ortofrutticoli-agrumari", "6S", 121, 20),
        ("ortofrutticoli-agrumari", "7", 1, 15),
        ("farmacie-private-h121", "Q2", 1, 90),
        ("farmacie-private-h121", "1", 300, 90),
        ("farmacie-private-h121", "2", 60, 60),
        ("farmacie-private-h121", "4", 121, 45),
        ("farmacie-private-h121", "6", 1, 15),
        ("radiotelevisive-radiofonico", "6", 1, 90),
        ("radiotelevisive-radiofonico", "4", 1, 60),
        ("radiotelevisive-radiofonico", "3", 300, 45),
        ("radiotelevisive-radiofonico", "1", 1, 21),
    ],
)
@pytest.mark.parametrize("cause", [_D, _R])
def test_the_calendar_days_from_the_1st_or_the_16th(
    ccnl_id: str, level: str, service: int, days: int, cause: TerminationCause
) -> None:
    """Calendar days alike for either cause, with the rateo of the extras."""
    rules = _notice(ccnl_id)
    band = rules.band(level, cause, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (0, days, None)
    assert (rules.starts.value, rules.extra_months_included) == (
        "first_or_sixteenth",
        True,
    )


@pytest.mark.parametrize(
    "ccnl_id",
    [
        "dirigenza-sanitaria-area-sanita-aran",
        "dirigenza-sanitaria-medico-veterinaria-aran",
    ],
)
@pytest.mark.parametrize(
    ("service", "months", "days", "indemnity"),
    [
        (1, 8, 0, "8"),
        (29, 8, 0, "8"),
        (30, 8, 15, "8.5"),
        (60, 8, 45, "9.5"),
        (113, 8, 105, "11.5"),
        (114, 12, 0, "12"),
        (400, 12, 0, "12"),
    ],
)
def test_the_dirigenti_grow_by_fifteen_days_a_year(
    ccnl_id: str, service: int, months: int, days: int, indemnity: str
) -> None:
    """A part year of six months or more counts as a year; 3 months to resign."""
    rules = _notice(ccnl_id)
    band = rules.band("DIRIGENTE", _D, service)
    resign = rules.band("DIRIGENTE", _R, service)

    assert band is not None
    assert resign is not None
    assert (band.months, band.days, band.indemnity_months) == (
        months,
        days,
        Decimal(indemnity),
    )
    assert (resign.months, resign.days) == (3, 0)
    assert rules.starts.value == "first_or_sixteenth"


@pytest.mark.parametrize(
    ("ccnl_id", "level"),
    [
        ("anas", "B1"),
        ("poste-italiane-k700", "D"),
        ("universita-aran", "COLLABORATORE"),
    ],
)
@pytest.mark.parametrize(
    ("service", "months"), [(1, 2), (60, 2), (61, 3), (120, 3), (121, 4)]
)
def test_two_three_or_four_months_on_a_dismissal(
    ccnl_id: str, level: str, service: int, months: int
) -> None:
    """The resignation, half of it, is left to the caller."""
    rules = _notice(ccnl_id)
    band = rules.band(level, _D, service)

    assert band is not None
    assert (band.months, band.days) == (months, 0)
    assert rules.band(level, _R, service) is None
    assert rules.starts.value == "first_or_sixteenth"


@pytest.mark.parametrize(
    ("ccnl_id", "level", "service", "cause", "months"),
    [
        ("consorzi-agrari-assocap", "Q", 60, _D, 2),
        ("consorzi-agrari-assocap", "6", 61, _D, 3),
        ("formazione-professionale", "I", 1, _D, 3),
        ("formazione-professionale", "IV", 1, _R, 2),
        ("formazione-professionale", "V", 1, _R, 3),
        ("scuole-private-laiche-aninsei", "II", 120, _R, 1),
        ("scuole-private-laiche-aninsei", "I", 121, _D, 2),
        ("scuole-private-laiche-aninsei", "VII", 1, _D, 3),
        ("scuole-private-laiche-aninsei", "VIII_B", 1, _R, 4),
        ("trasporto-ferroviario-agens", "Q1", 1, _R, 4),
        ("trasporto-ferroviario-agens", "C1", 300, _D, 3),
        ("trasporto-ferroviario-agens", "F1", 1, _D, 2),
    ],
)
def test_the_tables_in_months(
    ccnl_id: str,
    level: str,
    service: int,
    cause: TerminationCause,
    months: int,
) -> None:
    """Whole months, the indemnity in as many monthly pays."""
    band = _notice(ccnl_id).band(level, cause, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (
        months,
        0,
        Decimal(months),
    )


def test_the_consorzi_agrari_count_from_the_1st_or_the_16th_into_the_tfr() -> None:
    """Art. 47 c. 6, from the middle or the end of each month."""
    rules = _notice("consorzi-agrari-assocap")

    assert (rules.starts.value, rules.tfr_base) == ("first_or_sixteenth", True)


@pytest.mark.parametrize(
    ("level", "service", "months", "days"),
    [
        ("AE1", 60, 0, 15),
        ("AQ2", 61, 1, 0),
        ("AQ1", 121, 1, 15),
        ("AS2", 60, 0, 30),
        ("AC3", 120, 2, 0),
        ("AS1", 121, 3, 0),
        ("AD3", 1, 0, 60),
        ("AD1", 61, 3, 0),
        ("AD2", 121, 4, 0),
    ],
)
def test_the_cemento_areas(level: str, service: int, months: int, days: int) -> None:
    """By area and service, from the day after; the indemnity on its days."""
    rules = _notice("cemento-calce-gesso-industria")
    band = rules.band(level, _D, service)

    assert band is not None
    assert (band.months, band.days, band.indemnity_months) == (months, days, None)
    assert rules.starts.value == "day_after"
