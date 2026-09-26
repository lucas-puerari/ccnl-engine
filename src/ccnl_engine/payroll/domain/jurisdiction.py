"""Surtax jurisdiction codes: ISO 3166-2:IT region code and Belfiore code.

A region is identified by its ISO 3166-2:IT subdivision code, e.g.
``"IT-45"`` for Emilia-Romagna, listed in :data:`REGION_CODES`.  The bundled
regional surtax table has separate rows for the autonomous provinces of
Bolzano and Trento, so they are identified by ``"IT-BZ"`` and ``"IT-TN"``;
the region code of Trentino-Alto Adige, ``"IT-32"``, is rejected.

Source: ISO Online Browsing Platform, ISO 3166-2:IT,
https://www.iso.org/obp/ui/#iso:code:3166:IT (list cross-checked on
https://en.wikipedia.org/wiki/ISO_3166-2:IT, 26 September 2026).

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

from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "REGION_CODES",
    "TRENTINO_ALTO_ADIGE",
    "check_surtax_codes",
    "region_table_name",
]

#: Region code to the name keying the bundled regional surtax table.
REGION_CODES: Mapping[str, str] = MappingProxyType({
    "IT-21": "Piemonte",
    "IT-23": "Valle d'Aosta",
    "IT-25": "Lombardia",
    "IT-34": "Veneto",
    "IT-36": "Friuli-Venezia Giulia",
    "IT-42": "Liguria",
    "IT-45": "Emilia-Romagna",
    "IT-52": "Toscana",
    "IT-55": "Umbria",
    "IT-57": "Marche",
    "IT-62": "Lazio",
    "IT-65": "Abruzzo",
    "IT-67": "Molise",
    "IT-72": "Campania",
    "IT-75": "Puglia",
    "IT-77": "Basilicata",
    "IT-78": "Calabria",
    "IT-82": "Sicilia",
    "IT-88": "Sardegna",
    "IT-BZ": "Provincia Autonoma di Bolzano",
    "IT-TN": "Provincia Autonoma di Trento",
})

#: ISO code of Trentino-Alto Adige, whose surtax is set per autonomous province.
TRENTINO_ALTO_ADIGE = "IT-32"

_REGION_CODE = re.compile(r"IT-(?:[0-9]{2}|BZ|TN)")
_BELFIORE_CODE = re.compile(r"[A-Z][0-9]{3}")


def check_surtax_codes(regione: str | None, comune_belfiore: str | None) -> None:
    """Reject a malformed region or Belfiore code.

    Args:
        regione: ISO 3166-2:IT region code, ``IT-`` and two digits, or
            ``IT-BZ`` / ``IT-TN``, or ``None``.
        comune_belfiore: Belfiore code, one upper-case letter and three
            digits, or ``None``.

    Raises:
        InvalidInputError: When a code is given and does not match its
            format, or when ``regione`` is Trentino-Alto Adige (``IT-32``).
    """
    if regione == TRENTINO_ALTO_ADIGE:
        msg = (
            "regione 'IT-32' (Trentino-Alto Adige) has no regional surtax "
            "table: use the autonomous province code 'IT-BZ' (Bolzano) or "
            "'IT-TN' (Trento)"
        )
        raise InvalidInputError(msg, feature="addizionale_regionale")
    if regione is not None and not _REGION_CODE.fullmatch(regione):
        msg = (
            "regione must be an ISO 3166-2:IT region code, 'IT-' and two "
            f"digits or 'IT-BZ'/'IT-TN' (e.g. 'IT-45' for Emilia-Romagna); "
            f"got {regione!r}"
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
