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
from ccnl_engine.validators import (
    reject,
    require_decimal,
    require_instance,
    require_int,
)

__all__ = ["EarlierYearTax", "ForeignTaxPaid", "check_one_per_state"]

_FEATURE = "foreign_tax_credit"
_COUNTRY = re.compile(r"[A-Z]{2}")


@final
@dataclass(frozen=True, slots=True)
class EarlierYearTax:
    """The Italian tax of the earlier year the foreign income was taxed in.

    Art. 165 c. 7 TUIR, which art. 23 c. 3 DPR 600/1973 lets the conguaglio
    apply ("anche in precedenti periodi d'imposta"): the credit is measured
    on the tax of that year and deducted from the tax of the conguaglio.
    The amounts are the ones the CU of that year certifies.

    Attributes:
        year: The tax year the foreign income entered.
        gross_tax: Its imposta lorda (CU punto 361).
        net_tax: Its imposta netta (CU punto 375).
        taxable_income: Its reddito complessivo taxed in Italy.
        credit_used: Foreign tax credit already used against that year's
            tax, for any State (CU punto 376).

    Raises:
        InvalidInputError: When a field is not of its type or in its range.
    """

    year: int
    gross_tax: Decimal
    net_tax: Decimal
    taxable_income: Decimal
    credit_used: Decimal = Decimal(0)

    def __post_init__(self) -> None:  # noqa: D105
        require_int(self.year, "EarlierYearTax.year", feature=_FEATURE, minimum=1974)
        for name in ("gross_tax", "net_tax", "taxable_income", "credit_used"):
            require_decimal(
                getattr(self, name),
                f"EarlierYearTax.{name}",
                feature=_FEATURE,
                minimum=Decimal(0),
            )


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
        earlier: The Italian tax of the earlier year the income entered, for
            a foreign tax paid on income of an earlier year; ``None`` for
            income of the tax year of the conguaglio.

    Raises:
        InvalidInputError: When ``country`` is not an ISO code of a foreign
            State, or an amount is not a finite ``Decimal`` in its range.
    """

    country: str
    income: Decimal
    tax: Decimal
    earlier: EarlierYearTax | None = None

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
        require_instance(
            self.earlier,
            EarlierYearTax,
            "ForeignTaxPaid.earlier",
            feature=_FEATURE,
            optional=True,
        )


def check_one_per_state(taxes: tuple[ForeignTaxPaid, ...]) -> None:
    """Reject two entries of the same State and year: the credit is per State.

    Raises:
        InvalidInputError: When two entries share ``country`` and the year
            their income entered.
    """
    countries = [
        (t.country, None if t.earlier is None else t.earlier.year) for t in taxes
    ]
    if len(set(countries)) != len(countries):
        msg = (
            "foreign_taxes holds two entries of the same State; sum them: the "
            f"credit is computed per State (art. 165 c. 3 TUIR): {countries}"
        )
        raise InvalidInputError(
            msg, field="PriorYearTaxFacts.foreign_taxes", feature=_FEATURE
        )
