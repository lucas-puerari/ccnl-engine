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

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.validation import reject, require_decimal

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
            reject(
                "ForeignTaxPaid.country",
                "an ISO 3166-1 alpha-2 code of a foreign State",
                self.country,
                feature=_FEATURE,
            )
        require_decimal(
            self.income, "ForeignTaxPaid.income", feature=_FEATURE, positive=True
        )
        require_decimal(
            self.tax, "ForeignTaxPaid.tax", feature=_FEATURE, minimum=Decimal(0)
        )


def check_one_per_state(taxes: tuple[ForeignTaxPaid, ...]) -> None:
    """Reject two entries of the same State: the credit is per State.

    Raises:
        InvalidInputError: When two entries share ``country``.
    """
    countries = [t.country for t in taxes]
    if len(set(countries)) != len(countries):
        msg = (
            "foreign_taxes holds two entries of the same State; sum them: the "
            f"credit is computed per State (art. 165 c. 3 TUIR): {countries}"
        )
        raise InvalidInputError(
            msg, field="PriorYearTaxFacts.foreign_taxes", feature=_FEATURE
        )
