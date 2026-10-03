"""Income of the worker in the current tax year beyond this employment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import (
    parse_enum,
    require_date,
    require_decimal,
    require_int,
)

__all__ = ["CurrentYearTaxFacts", "IncomeEstimateQuality"]

_FEATURE = "current_year_tax_facts"
_OWNER = "CurrentYearTaxFacts"
_ZERO = Decimal(0)


class IncomeEstimateQuality(StrEnum):
    """How the income of :class:`CurrentYearTaxFacts` is known.

    Attributes:
        CERTIFIED: Final amounts from a certification (Certificazione Unica
            of another employer) or from the worker's tax return.
        DECLARED: The worker's declaration to the employer of the income
            expected in the year.
        ESTIMATED: The employer's own estimate: enough for the runs of the
            year, not for the conguaglio, which then stays provisional.
    """

    CERTIFIED = "certified"
    DECLARED = "declared"
    ESTIMATED = "estimated"


@dataclass(frozen=True, slots=True)
class CurrentYearTaxFacts:
    """Income of the tax year that enters the reddito complessivo.

    The family deductions of art. 12 TUIR depend on the reddito complessivo
    of the worker, not on the income of this employment alone.  The engine
    adds to its own projection of the employment income of the year:

        reddito complessivo = this employment + other_employment_income
            + other_income - main_dwelling_income

    Every amount is required: declaring no other income is a fact, stated
    with zeros (see :meth:`employment_only`).  Without these facts the
    reddito complessivo is unknown, and a run whose family deductions depend
    on it is not payable.

    Attributes:
        tax_year: The tax year the income belongs to.  Facts of another
            tax year are not used.
        other_employment_income: Employment and pension income of the tax
            year from other employers or payers (e.g. a previous employer of
            the year), net of their exclusions, ``>= 0``.
        other_income: Every other income of the tax year in the reddito
            complessivo (land and buildings, self-employment, rents under
            cedolare secca, art. 3 c. 7 D.Lgs. 23/2011), ``>= 0``.
        main_dwelling_income: Income of the main dwelling and its
            appurtenances included in ``other_income``, excluded from the
            reddito complessivo of art. 12 (c. 4-bis), ``>= 0`` and not above
            ``other_income``.
        estimated_on: Date the amounts were stated.
        quality: How the amounts are known.

    Raises:
        InvalidInputError: When a field is not of its type or in its range.
    """

    tax_year: int
    other_employment_income: Decimal
    other_income: Decimal
    main_dwelling_income: Decimal
    estimated_on: date
    quality: IncomeEstimateQuality

    def __post_init__(self) -> None:  # noqa: D105
        require_int(
            self.tax_year,
            f"{_OWNER}.tax_year",
            feature=_FEATURE,
            minimum=1970,
            maximum=9999,
        )
        for name in ("other_employment_income", "other_income", "main_dwelling_income"):
            require_decimal(
                getattr(self, name), f"{_OWNER}.{name}", feature=_FEATURE, minimum=_ZERO
            )
        require_date(self.estimated_on, f"{_OWNER}.estimated_on", feature=_FEATURE)
        quality = parse_enum(
            self.quality,
            IncomeEstimateQuality,
            f"{_OWNER}.quality",
            feature=_FEATURE,
        )
        object.__setattr__(self, "quality", quality)
        if self.main_dwelling_income > self.other_income:
            msg = (
                f"main_dwelling_income {self.main_dwelling_income} is excluded "
                f"from other_income and cannot exceed it ({self.other_income})"
            )
            raise InvalidInputError(
                msg, field=f"{_OWNER}.main_dwelling_income", feature=_FEATURE
            )

    @classmethod
    def employment_only(
        cls,
        tax_year: int,
        estimated_on: date,
        quality: IncomeEstimateQuality = IncomeEstimateQuality.DECLARED,
    ) -> CurrentYearTaxFacts:
        """Return the facts of a worker whose only income is this employment.

        Returns:
            Facts with every other income stated as zero.
        """
        return cls(
            tax_year=tax_year,
            other_employment_income=_ZERO,
            other_income=_ZERO,
            main_dwelling_income=_ZERO,
            estimated_on=estimated_on,
            quality=quality,
        )

    @property
    def external_income(self) -> Decimal:
        """Reddito complessivo of the year beyond this employment."""
        return (
            self.other_employment_income + self.other_income - self.main_dwelling_income
        )
