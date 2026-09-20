"""Treatment enums for pay-item fiscal and cost classification.

These four enums are kept in their own module so that downstream code (fiscal
rules, reporting) can import them without pulling in the full PayItem union.
"""

from __future__ import annotations

from enum import StrEnum


class TaxTreatment(StrEnum):
    """How a pay item is treated for IRPEF purposes."""

    ORDINARY = "ordinary"
    SEPARATE = "separate"
    SUBSTITUTE = "substitute"
    EXEMPT = "exempt"
    NON_CASH_TAXABLE = "non_cash_taxable"


class ContributionTreatment(StrEnum):
    """How a pay item enters the INPS contribution base."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    CAPPED = "capped"
    SPECIAL_BASE = "special_base"


class TfrTreatment(StrEnum):
    """How a pay item affects the TFR accrual base."""

    INCLUDED = "included"
    EXCLUDED = "excluded"
    SPECIAL = "special"


class CostTreatment(StrEnum):
    """Perspective from which the item enters the employer cost."""

    EMPLOYEE_CASH = "employee_cash"
    EMPLOYER_COST = "employer_cost"
    THIRD_PARTY_CASH = "third_party_cash"
    ACCRUAL_ONLY = "accrual_only"
