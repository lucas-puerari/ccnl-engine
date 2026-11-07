"""The levels that exist only for one sub-sector of the employer."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.working_time.subsector.rules import subsectors_of, with_subsector

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
