"""The rota of a security guard: parsed from its value, else rejected."""

from __future__ import annotations

import pytest

from ccnl_engine.employment.rota.inputs import Rota, check_rota
from ccnl_engine.errors import InvalidInputError


@pytest.mark.parametrize(
    ("value", "rota"),
    [(None, None), ("5+1", Rota.FIVE_ONE), (Rota.SIX_ONE_ONE, Rota.SIX_ONE_ONE)],
)
def test_a_rota_is_parsed(value: object, rota: Rota | None) -> None:
    """A member or its value is accepted, ``None`` when not stated."""
    assert check_rota(value) is rota


def test_an_unknown_rota_is_rejected() -> None:
    """Only the rotas the CCNLs name are accepted."""
    with pytest.raises(InvalidInputError, match=r"Employment\.rota"):
        check_rota("4+3")
