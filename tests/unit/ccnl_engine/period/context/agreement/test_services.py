"""Unit tests for the INPS sector the employer states for a CCNL."""

from __future__ import annotations

import pytest

from ccnl_engine.agreement.types import TaxSector
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.period.context.agreement.services import with_employer_sector

_LOGISTICA = load_ccnl("logistica-trasporto-confetra")
_METAL = load_ccnl("metalmeccanico-federmeccanica")


def test_a_single_sector_ccnl_needs_no_stated_sector() -> None:
    """A CCNL of one sector is read in it and leaves nothing open."""
    assert with_employer_sector(_METAL, None) == (_METAL, ())


def test_a_ccnl_of_several_sectors_leaves_them_open_when_none_is_stated() -> None:
    """Logistica reads the industria and names both sectors as open."""
    ccnl, open_sectors = with_employer_sector(_LOGISTICA, None)

    assert ccnl is _LOGISTICA
    assert open_sectors == (TaxSector.INDUSTRIA, TaxSector.TERZIARIO)


def test_the_stated_sector_replaces_the_sector_of_the_ccnl() -> None:
    """A spedizioniere is read in the terziario; nothing stays open."""
    ccnl, open_sectors = with_employer_sector(_LOGISTICA, TaxSector.TERZIARIO)

    assert ccnl.meta.tax_sector is TaxSector.TERZIARIO
    assert ccnl.levels == _LOGISTICA.levels
    assert open_sectors == ()


def test_the_sector_of_the_ccnl_keeps_the_ccnl() -> None:
    """Stating the sector the CCNL already reads changes nothing."""
    assert with_employer_sector(_LOGISTICA, TaxSector.INDUSTRIA) == (_LOGISTICA, ())
    assert with_employer_sector(_METAL, TaxSector.INDUSTRIA) == (_METAL, ())


@pytest.mark.parametrize(
    ("ccnl", "sector"),
    [
        (_LOGISTICA, TaxSector.PUBBLICA_AMMINISTRAZIONE),
        (_METAL, TaxSector.TERZIARIO),
    ],
)
def test_a_sector_the_ccnl_does_not_list_is_rejected(
    ccnl: object, sector: TaxSector
) -> None:
    """No caller can move a run to a sector the employers are not in."""
    with pytest.raises(InvalidInputError, match="inps_sector"):
        with_employer_sector(ccnl, sector)  # type: ignore[arg-type]
