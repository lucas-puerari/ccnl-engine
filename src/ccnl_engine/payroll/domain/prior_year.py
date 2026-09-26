"""Tax facts of the worker declared once for the tax year."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.tax.domain.preferential_regime import SubstituteTaxRegime

__all__ = ["PriorYearTaxFacts", "SubstituteTaxRegime"]

_FEATURE = "prior_year_tax_facts"


@dataclass(frozen=True, slots=True)
class PriorYearTaxFacts:
    """Prior-year income and written waivers, read by every tax regime.

    The single source of the requirements the preferential regimes check:
    the premio di risultato (L. 208/2015 art. 1 c. 182, prior-year income
    up to 80,000 EUR), the renewal increments (L. 199/2025 art. 1 c. 7, 2025
    income up to 33,000 EUR) and the night, holiday and shift supplements
    (L. 199/2025 art. 1 cc. 10-11, 2025 income up to 40,000 EUR).  For a
    2026 payment the prior year is 2025, the reference year of both
    L. 199/2025 regimes.

    Attributes:
        employment_income: Employment income (reddito di lavoro dipendente)
            of the year before the tax year, in EUR, ``>= 0``.  ``None``
            means not known: the PdR substitute rate is not applied and the
            L. 199/2025 regimes are ``unknown``, so the result is
            provisional.
        waived_regimes: Regimes the worker renounced in writing; their
            amounts are taxed as ordinary income.  String values are
            accepted and normalized.

    Raises:
        InvalidInputError: When ``employment_income`` is not a finite,
            non-negative ``Decimal`` or a waiver names no regime.
    """

    employment_income: Decimal | None = None
    waived_regimes: frozenset[SubstituteTaxRegime] = frozenset()

    def __post_init__(self) -> None:  # noqa: D105
        income = self.employment_income
        if income is not None and (
            not isinstance(income, Decimal) or not income.is_finite() or income < 0
        ):
            msg = (
                "employment_income must be a finite Decimal >= 0 or None; "
                f"got {income!r}"
            )
            raise InvalidInputError(msg, feature=_FEATURE)
        waived = frozenset(_regime(r) for r in _frozenset(self.waived_regimes))
        object.__setattr__(self, "waived_regimes", waived)


def _frozenset(value: object) -> frozenset[object]:
    """Return ``value`` when it is a frozenset.

    Returns:
        ``value``, typed as a frozenset.

    Raises:
        InvalidInputError: When ``value`` is not a frozenset.
    """
    if not isinstance(value, frozenset):
        msg = f"waived_regimes must be a frozenset; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE)
    return value


def _regime(value: object) -> SubstituteTaxRegime:
    """Return ``value`` as a :class:`SubstituteTaxRegime`.

    Returns:
        The regime named by ``value``.

    Raises:
        InvalidInputError: When ``value`` names no regime.
    """
    try:
        return SubstituteTaxRegime(str(value))
    except ValueError:
        valid = [r.value for r in SubstituteTaxRegime]
        msg = f"waived_regimes entries must be one of {valid}; got {value!r}"
        raise InvalidInputError(msg, feature=_FEATURE) from None
