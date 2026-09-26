"""Eligibility of a pay item for a preferential tax regime.

:func:`assess_regime` checks a
:class:`~ccnl_engine.engine.tax.domain.preferential_regime.PreferentialTaxRegime`
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
from datetime import date  # noqa: TC003
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.tax.domain.preferential_regime import (
        EmployerActivity,
        EmploymentSector,
        PreferentialTaxRegime,
    )

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
class RegimeFacts:
    """Worker facts the requirements of a regime are checked against.

    Attributes:
        prior_income: Employment income (reddito di lavoro dipendente) of the
            year before the tax year, in EUR.  ``None`` when not provided.
        sector: Sector of the employment.  ``None`` when not known.
        activity: Activity of the employer.  ``None`` when not known.
        waived_regimes: Regime ids the worker renounced in writing.
        agreement_signed_on: Signing date of the agreement the amount is
            paid under, for a regime with a signing window.  ``None`` when
            not known or not applicable.
    """

    prior_income: Decimal | None = None
    sector: EmploymentSector | None = None
    activity: EmployerActivity | None = None
    waived_regimes: frozenset[str] = frozenset()
    agreement_signed_on: date | None = None

    def waived(self, regime: PreferentialTaxRegime) -> bool:
        """Return whether the worker renounced ``regime`` in writing.

        Returns:
            ``True`` when the id of ``regime`` is in :attr:`waived_regimes`.
        """
        return regime.regime_id in self.waived_regimes


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
    """

    regime: PreferentialTaxRegime
    facts: RegimeFacts
    tax_year: int
    eligibility: RegimeEligibility
    reason_code: str
    eligible_amount: Decimal
    ordinary_amount: Decimal
    cap_available: Decimal | None = None

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
            An issue coded ``"<regime_id>_eligibility_unknown"`` when the
            eligibility is unknown, else ``None``.
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
        )


def _ineligibility(
    regime: PreferentialTaxRegime, facts: RegimeFacts, tax_year: int
) -> str | None:
    """Return the reason a known fact excludes the worker.

    Returns:
        The reason code, or ``None`` when no known fact excludes the worker.
    """
    signed = facts.agreement_signed_on
    income = facts.prior_income
    ceiling = regime.income_ceiling
    required = regime.required_sector
    excluded = (
        (not regime.in_force(tax_year), "regime_not_in_force"),
        (regime.waivable and facts.waived(regime), "waived_by_worker"),
        (
            required is not None and facts.sector not in {None, required},
            "sector_not_eligible",
        ),
        (facts.activity in regime.excluded_activities, "employer_activity_excluded"),
        (
            signed is not None and not regime.signed_within_window(signed),
            "agreement_signed_outside_window",
        ),
        (
            ceiling is not None and income is not None and income > ceiling,
            "prior_income_above_ceiling",
        ),
    )
    return next((reason for applies, reason in excluded if applies), None)


def _missing_fact(regime: PreferentialTaxRegime, facts: RegimeFacts) -> str | None:
    """Return the reason a required fact is missing.

    Returns:
        The reason code, or ``None`` when every required fact is known.
    """
    missing = (
        (regime.required_sector is not None and facts.sector is None, "sector"),
        (bool(regime.excluded_activities) and facts.activity is None, "activity"),
        (
            regime.has_signing_window and facts.agreement_signed_on is None,
            "agreement_signing_date",
        ),
        (
            regime.income_ceiling is not None and facts.prior_income is None,
            "prior_income",
        ),
    )
    return next((f"{name}_unknown" for absent, name in missing if absent), None)


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
    ineligible = _ineligibility(regime, facts, tax_year)
    missing = _missing_fact(regime, facts) if ineligible is None else None
    if ineligible is not None:
        eligibility, reason = RegimeEligibility.INELIGIBLE, ineligible
    elif missing is not None:
        eligibility, reason = RegimeEligibility.UNKNOWN, missing
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
    )
