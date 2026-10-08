"""Requirements of a preferential tax regime and the facts they read.

:func:`ineligibility` names the known fact that excludes the worker from a
regime; :func:`missing_fact` names the required fact that is not known,
with the public input field that supplies it, so that
:attr:`~ccnl_engine.payroll.domain.decisions.CalculationIssue.fact` is
always a field the caller can set.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date  # noqa: TC003
from decimal import Decimal  # noqa: TC003
from typing import TYPE_CHECKING

from ccnl_engine.payroll.service.withholding_agent import NOT_WITHHOLDING_AGENT

if TYPE_CHECKING:
    from ccnl_engine.tax.domain.preferential_regime import (
        EmployerActivity,
        EmploymentSector,
        PreferentialTaxRegime,
    )

__all__ = ["RegimeFacts", "ineligibility", "missing_fact", "missing_facts"]


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
        withholding_agent: Whether the employer is a withholding agent.  A
            substitute tax is withheld by the sostituto d'imposta, so a
            household employer applies no regime (art. 23 c. 1 D.P.R.
            600/1973).
    """

    prior_income: Decimal | None = None
    sector: EmploymentSector | None = None
    activity: EmployerActivity | None = None
    waived_regimes: frozenset[str] = frozenset()
    agreement_signed_on: date | None = None
    withholding_agent: bool = True

    def waived(self, regime: PreferentialTaxRegime) -> bool:
        """Return whether the worker renounced ``regime`` in writing.

        Returns:
            ``True`` when the id of ``regime`` is in :attr:`waived_regimes`.
        """
        return regime.regime_id in self.waived_regimes


def ineligibility(
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
        (not facts.withholding_agent, NOT_WITHHOLDING_AGENT),
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


def missing_fact(
    regime: PreferentialTaxRegime, facts: RegimeFacts
) -> tuple[str, str] | None:
    """Return the reason a required fact is missing and the public field.

    Returns:
        The reason code and the public input field that supplies the fact
        (:attr:`~ccnl_engine.payroll.domain.decisions.CalculationIssue.fact`),
        or ``None`` when every required fact is known.
    """
    return next(iter(missing_facts(regime, facts)), None)


def missing_facts(
    regime: PreferentialTaxRegime, facts: RegimeFacts, *, signing: bool = True
) -> tuple[tuple[str, str], ...]:
    """Return every required fact that is missing, in checking order.

    Args:
        regime: The preferential regime.
        facts: Worker facts from the request.
        signing: Whether the signing date of the agreement is a fact the
            caller can supply.  An increment paid inside the CCNL minimo has
            no event to carry it, so it is not asked for.

    Returns:
        The reason code and public input field of each missing fact.
    """
    missing = (
        (regime.required_sector is not None and facts.sector is None, "sector"),
        (bool(regime.excluded_activities) and facts.activity is None, "activity"),
        (
            signing and regime.has_signing_window and facts.agreement_signed_on is None,
            "signing",
        ),
        (regime.income_ceiling is not None and facts.prior_income is None, "income"),
    )
    return tuple(_UNKNOWN_FACTS[name] for absent, name in missing if absent)


#: Reason code and public field of each fact a regime may require.
_UNKNOWN_FACTS: dict[str, tuple[str, str]] = {
    "sector": ("sector_unknown", "sector"),
    "activity": ("activity_unknown", "activity"),
    "signing": ("agreement_signing_date_unknown", "agreement_signed_on"),
    "income": ("prior_income_unknown", "employment_income"),
}
