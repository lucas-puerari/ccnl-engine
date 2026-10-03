"""Eligibility of a pay item for a preferential tax regime.

:func:`assess_regime` checks a
:class:`~ccnl_engine.tax.domain.preferential_regime.PreferentialTaxRegime`
against the worker facts of the request and splits the amount into the part
taxed at the substitute rate and the part taxed as ordinary income.

A definite ineligibility wins over a missing fact: a public-sector worker is
ineligible whatever the prior-year income.  The sector, the employer
activity, the prior-year income and the signing date of a renewal are facts
the caller declares; the engine does not infer them from the CCNL.  When a
required fact is missing
and nothing else excludes the worker, the eligibility is ``unknown``: the
ordinary regime applies and the result becomes provisional, so the
substitute rate is never applied to a worker who may turn out ineligible.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.service.regime_requirements import (
    RegimeFacts,
    ineligibility,
    missing_fact,
)

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.preferential_regime import PreferentialTaxRegime

__all__ = [
    "RegimeAssessment",
    "RegimeEligibility",
    "RegimeFacts",
    "assess_regime",
]

_ZERO = Decimal(0)
_UNKNOWN = "unknown"


class RegimeEligibility(StrEnum):
    """Outcome of checking a worker against a preferential regime.

    Attributes:
        ELIGIBLE: Every requirement is met; the substitute rate applies.
        INELIGIBLE: A requirement is not met; the ordinary regime applies.
        UNKNOWN: A required fact is missing; the ordinary regime applies
            and the result is provisional.
    """

    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RegimeAssessment:
    """Eligibility of one amount for a regime, and how it is split.

    Attributes:
        regime: The regime assessed.
        facts: The worker facts the assessment was taken from.
        tax_year: Tax year of the payment.
        eligibility: Whether the regime applies.
        reason_code: Stable lower snake case reason, e.g.
            ``"prior_income_above_ceiling"``.
        eligible_amount: Part of the amount taxed at the substitute rate.
        ordinary_amount: Part of the amount taxed as ordinary income.
        cap_available: Part of the annual cap not yet used before this
            amount, or ``None`` when the regime has no cap.
        missing_fact: Public input field of the missing fact, ``None``
            unless the eligibility is unknown.
    """

    regime: PreferentialTaxRegime
    facts: RegimeFacts
    tax_year: int
    eligibility: RegimeEligibility
    reason_code: str
    eligible_amount: Decimal
    ordinary_amount: Decimal
    cap_available: Decimal | None = None
    missing_fact: str | None = None

    @property
    def status(self) -> CalculationStatus:
        """Provisional when a fact is missing, final otherwise."""
        if self.eligibility is RegimeEligibility.UNKNOWN:
            return CalculationStatus.PROVISIONAL
        return CalculationStatus.FINAL

    def decision(self, substitute_tax: Decimal) -> CalculationDecision:
        """Return the calculation decision recording this assessment.

        Args:
            substitute_tax: Substitute tax posted on :attr:`eligible_amount`.

        Returns:
            A decision for capability ``"<regime_id>_substitute_tax"`` whose
            amount is ``substitute_tax``.  A capped regime also records
            ``annual_cap`` and the ``cap_available`` before this amount.
        """
        ruleset = self.regime.ruleset
        facts = self.facts
        prior_income = facts.prior_income
        inputs: dict[str, Decimal | str] = {
            "eligibility": self.eligibility.value,
            "tax_year": str(self.tax_year),
            "prior_income": _UNKNOWN if prior_income is None else prior_income,
            "sector": _UNKNOWN if facts.sector is None else facts.sector.value,
            "waived": str(facts.waived(self.regime)).lower(),
            "eligible_amount": self.eligible_amount,
            "ordinary_amount": self.ordinary_amount,
        }
        if self.regime.excluded_activities:
            activity = facts.activity
            inputs["employer_activity"] = _UNKNOWN if activity is None else activity
        if self.regime.has_signing_window:
            signed = facts.agreement_signed_on
            inputs["agreement_signed_on"] = (
                _UNKNOWN if signed is None else signed.isoformat()
            )
        if self.regime.annual_cap is not None and self.cap_available is not None:
            inputs["annual_cap"] = self.regime.annual_cap
            inputs["cap_available"] = self.cap_available
        return CalculationDecision(
            capability=f"{self.regime.regime_id}_substitute_tax",
            status=self.status,
            reason_code=self.reason_code,
            rule=self.regime.regime_id if ruleset is None else ruleset.id,
            rule_version=(str(self.tax_year) if ruleset is None else ruleset.version),
            inputs=inputs,
            source=self.regime.source,
            amount=substitute_tax,
        )

    def issue(self) -> CalculationIssue | None:
        """Return the provisional issue of an unknown eligibility, if any.

        Returns:
            An issue coded ``"<regime_id>_eligibility_unknown"``, or ``None``.
        """
        if self.eligibility is not RegimeEligibility.UNKNOWN:
            return None
        return CalculationIssue(
            code=f"{self.regime.regime_id}_eligibility_unknown",
            message=(
                f"{self.regime.regime_id} substitute tax not applied "
                f"({self.reason_code}): ordinary taxation used until the "
                "missing fact is provided"
            ),
            status=CalculationStatus.PROVISIONAL,
            source=self.regime.source,
            fact=self.missing_fact,
        )


def assess_regime(
    regime: PreferentialTaxRegime,
    facts: RegimeFacts,
    amount: Decimal,
    tax_year: int,
    cap_available: Decimal | None = None,
) -> RegimeAssessment:
    """Assess ``amount`` against ``regime`` and split it between regimes.

    Args:
        regime: The preferential regime.
        facts: Worker facts from the request.
        amount: Amount of the pay item, non-negative.
        tax_year: Tax year of the payment.
        cap_available: Part of the annual cap not yet used this tax year.
            ``None`` takes the whole :attr:`PreferentialTaxRegime.annual_cap`.
            Ignored when the regime has no cap.

    Returns:
        The assessment.  An eligible amount above the available cap is split:
        the excess is ordinary.  An ineligible or unknown amount is wholly
        ordinary.
    """
    ineligible = ineligibility(regime, facts, tax_year)
    missing = missing_fact(regime, facts) if ineligible is None else None
    if ineligible is not None:
        eligibility, reason = RegimeEligibility.INELIGIBLE, ineligible
    elif missing is not None:
        eligibility, reason = RegimeEligibility.UNKNOWN, missing[0]
    else:
        eligibility, reason = RegimeEligibility.ELIGIBLE, "requirements_met"
    eligible = amount if eligibility is RegimeEligibility.ELIGIBLE else _ZERO
    available: Decimal | None = None
    if regime.annual_cap is not None:
        cap = regime.annual_cap if cap_available is None else cap_available
        available = max(cap, _ZERO)
        eligible = min(eligible, available)
    return RegimeAssessment(
        regime=regime,
        facts=facts,
        tax_year=tax_year,
        eligibility=eligibility,
        reason_code=reason,
        eligible_amount=eligible,
        ordinary_amount=amount - eligible,
        cap_available=available,
        missing_fact=None if missing is None else missing[1],
    )
