"""Region and Belfiore code formats of the surtax jurisdiction."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.jurisdiction import (
    REGION_CODES,
    TRENTINO_ALTO_ADIGE,
    check_surtax_codes,
    region_table_name,
)


@pytest.mark.parametrize(
    ("regione", "comune_belfiore"),
    [
        (None, None),
        ("IT-45", "F257"),
        ("IT-99", "Z999"),
        ("IT-BZ", None),
        ("IT-TN", None),
        (None, "H501"),
    ],
)
def test_well_formed_codes_are_accepted(
    regione: str | None, comune_belfiore: str | None
) -> None:
    """Well-formed codes pass, whether or not a table has a row for them."""
    check_surtax_codes(regione, comune_belfiore)


@pytest.mark.parametrize(
    "regione",
    ["LOM", "Lombardia", "ER", "IT45", "it-45", "IT-4", "IT-450", "IT-MI", "45", ""],
)
def test_malformed_region_code_is_invalid_input(regione: str) -> None:
    """A region code is ``IT-`` and two digits, or ``IT-BZ`` / ``IT-TN``."""
    with pytest.raises(InvalidInputError, match="ISO 3166-2:IT") as info:
        check_surtax_codes(regione, None)

    assert info.value.feature == "addizionale_regionale"


@pytest.mark.parametrize("comune", ["F25", "F2577", "f257", "257F", "Modena", ""])
def test_malformed_belfiore_code_is_invalid_input(comune: str) -> None:
    """A Belfiore code is one upper-case letter and three digits."""
    with pytest.raises(InvalidInputError, match="Belfiore") as info:
        check_surtax_codes(None, comune)

    assert info.value.feature == "addizionale_comunale"


def test_region_code_resolves_to_its_table_name() -> None:
    """Known codes map to the regional table name; others to ``None``."""
    assert region_table_name("IT-45") == "Emilia-Romagna"
    assert region_table_name("IT-99") is None
    assert len(REGION_CODES) == 21
    assert region_table_name("IT-BZ") == "Provincia Autonoma di Bolzano"
    assert region_table_name("IT-TN") == "Provincia Autonoma di Trento"
    assert TRENTINO_ALTO_ADIGE not in REGION_CODES


def test_trentino_alto_adige_region_code_is_rejected() -> None:
    """IT-32 has no surtax row: the autonomous province code is required."""
    with pytest.raises(InvalidInputError, match="IT-BZ") as info:
        check_surtax_codes(TRENTINO_ALTO_ADIGE, None)

    assert info.value.feature == "addizionale_regionale"
