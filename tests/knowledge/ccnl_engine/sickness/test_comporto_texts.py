"""The comporto of several illnesses, read off the clause of each CCNL.

- CED Assoced (p. 96), Ortofrutticoli (p. 17) and Scuole private laiche
  Aninsei (p. 71): 180 days "in un anno solare", counted over the calendar
  year.
- Studi professionali (pp. 65-66): 180 days in the "anno solare" the CCNL
  defines as "un periodo di 365 giorni partendo a ritroso dell'ultimo
  evento morboso", the 12 months before the day.
- Multiservizi (p. 22): "12 mesi di assenza nell'arco di 36 mesi
  consecutivi"; Cooperative sociali (p. 104): "12 mesi nell'arco
  dell'ultimo triennio"; 360 days of 30-day months.
- Laterizi (p. 9): "425 giorni (14 mesi) di calendario su 912 (30 mesi)".
- Agenzie di viaggio (p. 67) and Industria turistica (p. 130): "centottanta
  giorni per anno, intendendosi per tale il periodo compreso tra il 1°
  gennaio e il 31 dicembre"; Fiori recisi (p. 33): "180 giorni in un anno
  solare".
- Funivie (pp. 25-26): 180 days, "nei ventiquattro mesi precedenti ogni
  nuovo ultimo episodio morboso".
- Alimentari PMI Unionalimentari (art. 36, p. 109): 180 days in the 17
  months before up to five years of seniority, 365 in the 24 months after.
- Formazione professionale (art. 50, p. 33): 18 months, summing "tutte le
  assenze per malattia intervenute nei tre anni precedenti", paid 100% for
  12 months and 75% for 6 more.
- Federcasa (art. 51, p. 47): 12 months, over "un arco temporale pari a tre
  anni" for a non-continuous absence, the hospital stays left out of the
  window only.
- Panificazione Assipan (p. 58): 180 days "anche in caso di diverse
  malattie, nei 12 mesi precedenti".
- Anaste (p. 52): more than 180 days "nell'arco del triennio precedente
  l'ultimo evento morboso".
- Uneba (p. 75): 365 days "nell'arco dell'ultimo triennio".
- The ARAN areas of the dirigenza: 18 months, summing "tutte le assenze per
  malattia intervenute nei tre anni precedenti l'ultimo episodio morboso".
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl

if TYPE_CHECKING:
    from ccnl_engine.sickness.integration.models import SicknessRules


def _sickness(ccnl_id: str) -> SicknessRules:
    work = load_ccnl(ccnl_id).work_rules
    assert work is not None
    assert work.sickness_rules is not None
    return work.sickness_rules


@pytest.mark.parametrize(
    "ccnl_id",
    [
        "ced-assoced",
        "ortofrutticoli-agrumari",
        "scuole-private-laiche-aninsei",
        "agenzie-viaggio-fiavet",
        "industria-turistica-federturismo",
        "fiori-recisi-ancef",
    ],
)
def test_the_comporto_of_the_calendar_year(ccnl_id: str) -> None:
    """180 days summed over the calendar year, no window."""
    rules = _sickness(ccnl_id)

    assert (rules.comporto_calendar_year, rules.max_duration_days) == (True, 180)
    assert not rules.comporto_windows


@pytest.mark.parametrize(
    ("ccnl_id", "months", "days"),
    [
        ("panificazione-assipan", 12, 180),
        ("studi-professionali-confprofessioni", 12, 180),
        ("multiservizi-anip", 36, 360),
        ("cooperative-sociali", 36, 360),
        ("laterizi-industria-f021", 30, 425),
        ("funivie-anef", 24, 180),
        ("istituzioni-servizi-socio-assistenziali-anaste", 36, 180),
        ("uneba-uneba", 36, 365),
        ("dirigenza-funzioni-centrali-aran", 36, 540),
        ("dirigenza-funzioni-locali-aran", 36, 540),
        ("dirigenza-istruzione-ricerca-aran", 36, 540),
        ("dirigenza-sanitaria-area-sanita-aran", 36, 540),
        ("dirigenza-sanitaria-medico-veterinaria-aran", 36, 540),
    ],
)
def test_the_comporto_summed_over_a_window(
    ccnl_id: str, months: int, days: int
) -> None:
    """One window from the first month of service, not the calendar year."""
    rules = _sickness(ccnl_id)
    (window,) = rules.comporto_windows

    assert (window.seniority_months_from, window.window_months) == (0, months)
    assert window.comporto_days == days
    assert not rules.comporto_calendar_year


def test_federcasa_leaves_the_hospital_stays_out_of_its_window() -> None:
    """12 months of one illness, 12 in three years without hospital days."""
    rules = _sickness("federcasa")
    (window,) = rules.comporto_windows

    assert rules.max_duration_days == 360
    assert (window.window_months, window.comporto_days) == (36, 360)
    assert window.hospital_excluded


def test_alimentari_pmi_widens_the_window_after_five_years() -> None:
    """180 days in 17 months, 365 in 24 from the 61st month of seniority."""
    windows = _sickness("alimentari-pmi-unionalimentari").comporto_windows

    assert [
        (w.seniority_months_from, w.window_months, w.comporto_days) for w in windows
    ] == [(0, 17, 180), (61, 24, 365)]


def test_formazione_pays_two_tiers_over_eighteen_months() -> None:
    """540 days of one illness and over three years; 100% then 75%."""
    rules = _sickness("formazione-professionale")
    (window,) = rules.comporto_windows

    assert (rules.max_duration_days, window.window_months) == (540, 36)
    assert window.comporto_days == 540
    assert [(t.month_from, t.month_until, t.integration_rate) for t in rules.tiers] == [
        (1, 13, Decimal(1)),
        (13, 19, Decimal("0.75")),
    ]
