"""The levels that exist only for one sub-sector of the employer."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.working_time.subsector.rules import subsectors_of, with_subsector

if TYPE_CHECKING:
    from ccnl_engine.agreement.facade import CCNL

_PMI = load_ccnl("tessile-pmi-uniontessile")
_ART = load_ccnl("tessile-moda-artigianato-confartigianato")


def test_the_subsectors_of_the_levels_are_accepted() -> None:
    """The sub-sectors of the levels join those of the pay tables."""
    assert subsectors_of(_PMI) == {"calzature", "pelli_cuoio", "occhiali", "giocattoli"}
    assert subsectors_of(_ART) == {"chimica", "ceramica"}


@pytest.mark.parametrize(
    ("subsector", "codes"),
    [
        (None, ["1", "2", "3", "4", "5", "6", "6S"]),
        ("chimica", ["1", "2", "3", "4", "5", "5s", "6", "6S", "7"]),
        (
            "ceramica",
            ["1", "2", "3", "4", "5", "6", "6S", "G", "F", "E", "D", "C", "B", "A"],
        ),
    ],
)
def test_a_run_keeps_the_levels_of_its_subsector(
    subsector: str | None, codes: list[str]
) -> None:
    """The levels of another sub-sector are dropped from the run."""
    ccnl, unknown = with_subsector(_ART, subsector, None, level_code="4")
    assert [lv.code for lv in ccnl.levels] == codes
    assert not unknown


def test_a_subsector_level_is_paid_the_table_of_the_stated_subsector() -> None:
    """4s from January 2026: giocattoli 2,042.84, occhiali 2,066.31."""
    for subsector, value in (("giocattoli", "2042.84"), ("occhiali", "2066.31")):
        ccnl, _ = with_subsector(_PMI, subsector, None, level_code="4s")
        assert ccnl.level_by_code("4s").base_salary.periods[2].value == Decimal(value)


def test_a_subsector_level_without_a_subsector_names_the_employer_field() -> None:
    """4s needs EmployerProfile.subsector."""
    with pytest.raises(
        InvalidInputError, match="exists only for the sub-sectors"
    ) as exc:
        with_subsector(_PMI, None, None, level_code="4s")
    assert exc.value.field == "EmployerProfile.subsector"


def test_a_subsector_level_of_another_subsector_names_the_level_field() -> None:
    """The ceramica level A is no level of a chimica employer."""
    with pytest.raises(InvalidInputError, match="not for 'chimica'") as exc:
        with_subsector(_ART, "chimica", None, level_code="A")
    assert exc.value.field == "Employment.level_code"


def test_an_unknown_level_is_left_to_the_level_lookup() -> None:
    """A code no level has is not checked here."""
    ccnl, _ = with_subsector(_PMI, "calzature", None, level_code="99")
    assert "4s" not in {lv.code for lv in ccnl.levels}


def test_without_subsector_levels_the_ccnl_is_unchanged() -> None:
    """No sub-sector level and no table of the run: the same CCNL."""
    commercio = load_ccnl("commercio-confcommercio")
    assert with_subsector(commercio, None, None, level_code="4") == (commercio, False)


def _works(ccnl: CCNL) -> dict[str, Decimal | None]:
    rules = ccnl.work_rules
    assert rules is not None
    assert rules.time_supplements is not None
    return {
        b.work.value: b.rate.periods[0].value
        for b in rules.time_supplements.supplement_bands
    }


def test_a_run_of_no_subsector_is_of_the_main_sector() -> None:
    """Tessile-moda artigianato has rules of its own: no chimica band, not unknown."""
    ccnl, unknown = with_subsector(_ART, None, None, level_code="4")
    works = _works(ccnl)
    assert not unknown
    assert works.get("night_holiday") == Decimal("0.50")
    assert "night" not in works


@pytest.mark.parametrize(
    ("subsector", "night"), [("chimica", "0.30"), ("ceramica", "0.30")]
)
def test_a_run_of_a_subsector_takes_its_bands(subsector: str, night: str) -> None:
    """Art. 43: each sector its own night work."""
    ccnl, unknown = with_subsector(_ART, subsector, None, level_code="4")
    assert not unknown
    assert _works(ccnl)["night"] == Decimal(night)


def test_without_a_main_sector_the_first_subsector_prices_the_run() -> None:
    """Alimentari has bands of its sub-sectors only: unknown, the first one."""
    ccnl, unknown = with_subsector(
        load_ccnl("alimentari-federalimentare"), None, None, level_code="3"
    )
    assert unknown
    assert ccnl.work_rules is not None
