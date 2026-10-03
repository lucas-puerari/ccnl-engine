"""Tax facts of the worker declared once for the tax year."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ccnl_engine.payroll.domain.foreign_tax import (
    ForeignTaxPaid,
    check_one_per_state,
)
from ccnl_engine.payroll.domain.shortfall_deferral import ShortfallDeferralRequest
from ccnl_engine.shared.domain.collection_validation import (
    frozenset_of,
    items_of_type,
    tuple_of,
)
from ccnl_engine.shared.domain.validation import (
    parse_enum,
    require_decimal,
    require_instance,
)
from ccnl_engine.tax.domain.preferential_regime import SubstituteTaxRegime

__all__ = [
    "ForeignTaxPaid",
    "PriorYearTaxFacts",
    "ShortfallDeferralRequest",
    "SubstituteTaxRegime",
]

_FEATURE = "prior_year_tax_facts"


@dataclass(frozen=True, slots=True)
class PriorYearTaxFacts:
    """Prior-year income, written waivers and requests of the tax year.

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
        shortfall_deferral: The worker's written request to have the IRPEF
            the conguaglio cannot withhold for lack of pay withheld on the
            payslips of the next year, with interest (art. 23 c. 3 DPR
            600/1973).  ``None``: what is not withheld is communicated to
            the worker.  Read on the conguaglio only.
        foreign_taxes: Foreign tax paid on employment income of the tax
            year, one entry per State, credited at the conguaglio (art. 165
            TUIR, art. 23 c. 3 DPR 600/1973).  A list is accepted and
            stored as a tuple.

    Raises:
        InvalidInputError: When ``employment_income`` is not a finite,
            non-negative ``Decimal``, a waiver names no regime,
            ``shortfall_deferral`` is not a request, or two foreign taxes
            name the same State.
    """

    employment_income: Decimal | None = None
    waived_regimes: frozenset[SubstituteTaxRegime] = frozenset()
    shortfall_deferral: ShortfallDeferralRequest | None = None
    foreign_taxes: tuple[ForeignTaxPaid, ...] = ()

    def __post_init__(self) -> None:  # noqa: D105
        owner = "PriorYearTaxFacts"
        require_decimal(
            self.employment_income,
            f"{owner}.employment_income",
            feature=_FEATURE,
            minimum=Decimal(0),
            optional=True,
        )
        waived = frozenset_of(
            self.waived_regimes, f"{owner}.waived_regimes", _regime, feature=_FEATURE
        )
        object.__setattr__(self, "waived_regimes", waived)
        require_instance(
            self.shortfall_deferral,
            ShortfallDeferralRequest,
            f"{owner}.shortfall_deferral",
            feature=_FEATURE,
            optional=True,
        )
        taxes = tuple_of(
            self.foreign_taxes,
            f"{owner}.foreign_taxes",
            items_of_type(ForeignTaxPaid, feature=_FEATURE),
            feature=_FEATURE,
        )
        check_one_per_state(taxes)
        object.__setattr__(self, "foreign_taxes", taxes)


def _regime(value: object, path: str) -> SubstituteTaxRegime:
    return parse_enum(value, SubstituteTaxRegime, path, feature=_FEATURE)
