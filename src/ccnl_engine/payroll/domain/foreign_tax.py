"""Foreign tax paid on employment income taxed by the withholding agent.

Art. 23 c. 3 DPR 600/1973 (in force for 2026; art. 33 c. 4 D.Lgs. 33/2025
from 2027) lets the withholding agent apply the credit of art. 165 TUIR at
the conguaglio: "Se alla formazione del reddito di lavoro dipendente
concorrono somme o valori prodotti all'estero le imposte ivi pagate a
titolo definitivo sono ammesse in detrazione fino a concorrenza
dell'imposta relativa ai predetti redditi prodotti all'estero. [...] Se
concorrono redditi prodotti in più Stati esteri la detrazione si applica
separatamente per ciascuno Stato."
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import final

from ccnl_engine.shared.domain.errors import InvalidInputError

__all__ = ["ForeignTaxPaid", "check_one_per_state"]

_FEATURE = "foreign_tax_credit"
_COUNTRY = re.compile(r"[A-Z]{2}")


@final
@dataclass(frozen=True, slots=True)
class ForeignTaxPaid:
    """Tax paid in one foreign State on income taxed in Italy this year.

    Attributes:
        country: ISO 3166-1 alpha-2 code of the State, not ``"IT"``.
        income: Foreign-source employment income as it entered the Italian
            taxable income of the tax year (the conventional pay when art.
            51 c. 8-bis TUIR applies), in EUR, positive.
        tax: Foreign tax paid on it "a titolo definitivo", in EUR, ``>= 0``,
            within the rate of a tax treaty.  Pass it already reduced as
            art. 165 c. 10 TUIR requires when the income entered the
            taxable income only in part: on the conventional pay, by the
            ratio of that pay to the income that would be taxable under
            art. 51 without c. 8-bis (circ. AdE 9/E/2015 par. 5).

    Raises:
        InvalidInputError: When ``country`` is not an ISO code of a foreign
            State, or an amount is not a finite ``Decimal`` in its range.
    """

    country: str
    income: Decimal
    tax: Decimal

    def __post_init__(self) -> None:  # noqa: D105
        if (
            not isinstance(self.country, str)
            or not _COUNTRY.fullmatch(self.country)
            or self.country == "IT"
        ):
            msg = (
                "country must be an ISO 3166-1 alpha-2 code of a foreign State; "
                f"got {self.country!r}"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        for name, value, positive in (
            ("income", self.income, True),
            ("tax", self.tax, False),
        ):
            if (
                not isinstance(value, Decimal)
                or not value.is_finite()
                or value < 0
                or (positive and value == 0)
            ):
                bound = "> 0" if positive else ">= 0"
                msg = f"{name} must be a finite Decimal {bound}; got {value!r}"
                raise InvalidInputError(msg, feature=_FEATURE)


def check_one_per_state(taxes: tuple[ForeignTaxPaid, ...]) -> None:
    """Reject two entries of the same State: the credit is per State.

    Raises:
        InvalidInputError: When an entry is not a :class:`ForeignTaxPaid`
            or two entries share ``country``.
    """
    if any(not isinstance(t, ForeignTaxPaid) for t in taxes):
        msg = f"foreign_taxes entries must be ForeignTaxPaid; got {taxes!r}"
        raise InvalidInputError(msg, feature=_FEATURE)
    countries = [t.country for t in taxes]
    if len(set(countries)) != len(countries):
        msg = (
            "foreign_taxes holds two entries of the same State; sum them: the "
            f"credit is computed per State (art. 165 c. 3 TUIR): {countries}"
        )
        raise InvalidInputError(msg, feature=_FEATURE)
