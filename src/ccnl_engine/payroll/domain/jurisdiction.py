"""Surtax jurisdiction codes: region code and municipality Belfiore code.

A region is identified by a two-letter upper-case code of this engine,
listed in :data:`REGION_CODES`.  The codes are not ISO 3166-2 codes: they
are stable short names for the rows of the bundled regional surtax table,
which is keyed by the Italian name of the region or autonomous province.
No code is the vehicle plate (sigla) of a province of another region, so a
province sigla passed by mistake never selects the wrong regional table:
``CZ``, ``LO`` and ``VE`` are provinces of their own region, ``BZ`` and
``TN`` are the autonomous provinces themselves.

A municipality is identified by its *codice catastale* (Belfiore code): one
upper-case letter and three digits, e.g. ``"F257"`` for Modena.

A malformed code is invalid input.  A well-formed code that is not in the
bundled table of the tax year is not an input error: the surtax is unknown
and the result is incomplete.
"""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "REGION_CODES",
    "check_surtax_codes",
    "region_table_name",
]

#: Region code to the name keying the bundled regional surtax table.
REGION_CODES: Mapping[str, str] = MappingProxyType({
    "AB": "Abruzzo",
    "BC": "Basilicata",
    "BZ": "Provincia Autonoma di Bolzano",
    "CM": "Campania",
    "CZ": "Calabria",
    "ER": "Emilia-Romagna",
    "FV": "Friuli-Venezia Giulia",
    "LA": "Lazio",
    "LG": "Liguria",
    "LO": "Lombardia",
    "MA": "Marche",
    "ML": "Molise",
    "PL": "Puglia",
    "PM": "Piemonte",
    "SC": "Sicilia",
    "SD": "Sardegna",
    "TC": "Toscana",
    "TN": "Provincia Autonoma di Trento",
    "UM": "Umbria",
    "VD": "Valle d'Aosta",
    "VE": "Veneto",
})

_REGION_CODE = re.compile(r"[A-Z]{2}")
_BELFIORE_CODE = re.compile(r"[A-Z][0-9]{3}")


def check_surtax_codes(regione: str | None, comune_belfiore: str | None) -> None:
    """Reject a malformed region or Belfiore code.

    Args:
        regione: Region code, two upper-case letters, or ``None``.
        comune_belfiore: Belfiore code, one upper-case letter and three
            digits, or ``None``.

    Raises:
        InvalidInputError: When a code is given and does not match its
            format.
    """
    if regione is not None and not _REGION_CODE.fullmatch(regione):
        msg = (
            f"regione must be a two-letter upper-case region code "
            f"(e.g. 'ER' for Emilia-Romagna); got {regione!r}"
        )
        raise InvalidInputError(
            msg,
            feature="addizionale_regionale",
            remediation=f"use one of: {', '.join(sorted(REGION_CODES))}",
        )
    if comune_belfiore is not None and not _BELFIORE_CODE.fullmatch(comune_belfiore):
        msg = (
            "comune_belfiore must be a Belfiore code, one upper-case letter "
            f"and three digits (e.g. 'F257' for Modena); got {comune_belfiore!r}"
        )
        raise InvalidInputError(msg, feature="addizionale_comunale")


def region_table_name(regione: str) -> str | None:
    """Return the name keying the regional surtax table for a region code.

    Returns:
        The Italian name of the region or autonomous province, or ``None``
        when the code is not a known region code.
    """
    return REGION_CODES.get(regione)
