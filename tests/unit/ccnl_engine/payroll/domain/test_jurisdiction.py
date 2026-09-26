"""Region and Belfiore code formats of the surtax jurisdiction."""

from __future__ import annotations

import pytest

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.payroll.domain.jurisdiction import (
    REGION_CODES,
    check_surtax_codes,
    region_table_name,
)


@pytest.mark.parametrize(
    ("regione", "comune_belfiore"),
    [(None, None), ("ER", "F257"), ("ZZ", "Z999"), ("BZ", None), (None, "H501")],
)
def test_well_formed_codes_are_accepted(
    regione: str | None, comune_belfiore: str | None
) -> None:
    """Well-formed codes pass, whether or not a table has a row for them."""
    check_surtax_codes(regione, comune_belfiore)


@pytest.mark.parametrize("regione", ["LOM", "Lombardia", "er", "E", "03", ""])
def test_malformed_region_code_is_invalid_input(regione: str) -> None:
    """A region code is exactly two upper-case letters."""
    with pytest.raises(InvalidInputError, match="two-letter") as info:
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
    assert region_table_name("ER") == "Emilia-Romagna"
    assert region_table_name("ZZ") is None
    assert len(REGION_CODES) == 21
    assert all(len(code) == 2 and code.isupper() for code in REGION_CODES)
