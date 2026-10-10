"""The renewal regime on the increments paid inside the CCNL minimo.

L. 199/2025 art. 1 c. 7 taxes at 5% the pay increments paid in 2026 under
renewals signed from 1 January 2024 to 31 December 2026, for private-sector
workers whose 2025 employment income did not exceed 33,000 EUR.  A renewal
raises the minimo tabellare, so its increments are paid inside the base
salary, not as a separate event.  How much of the minimo counts as a
renewal increment is a reading the engine does not settle: the bundle does
not tie each table of the minimo to the agreement that set it.

:func:`assess_renewal_minimum` therefore never posts the substitute tax on
the minimo.  It decides what the worker facts alone decide: a known fact
that excludes the worker ends the matter with a final decision; a missing
fact is reported with the public field that supplies it; an eligible worker
gets a provisional decision and an issue, because the increment is not
quantified and the ordinary taxation of the run may be too high.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.service.regime_requirements import (
    ineligibility,
    missing_facts,
)

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.identity.rules_validity import TimeSeries
    from ccnl_engine.payroll.service.regime_requirements import RegimeFacts
    from ccnl_engine.tax.regime.models import PreferentialTaxRegime

__all__ = [
    "INCREMENT_UNQUANTIFIED",
    "RenewalMinimum",
    "RenewalMinimumAssessment",
    "assess_renewal_minimum",
    "renewal_table_from",
]

#: Reason of an eligible worker whose renewal increments in the minimo are
#: not quantified.
INCREMENT_UNQUANTIFIED = "renewal_increment_in_minimum_unquantified"

_UNKNOWN = "unknown"
_ZERO = Decimal(0)


@dataclass(frozen=True, slots=True)
class RenewalMinimum:
    """The minimo a run pays and the table that may carry renewal increments.

    Attributes:
        minimum: Monthly minimo tabellare of the run.
        table_from: Earliest date a table of the minimo took effect within
            the signing window of the regime, on or before the competence
            date of the run.
    """

    minimum: Decimal
    table_from: date


@dataclass(frozen=True, slots=True)
class RenewalMinimumAssessment:
    """Decision and issues of the renewal regime on the minimo of a run.

    Attributes:
        decision: The ``rinnovo_substitute_tax`` decision; its amount is
            always zero, nothing is posted.
        issues: One issue per missing fact, or the issue of the unquantified
            increment; empty when a known fact excludes the worker.
    """

    decision: CalculationDecision
    issues: tuple[CalculationIssue, ...]


def renewal_table_from(
    series: TimeSeries, regime: PreferentialTaxRegime, competence: date
) -> date | None:
    """Return the first table of a minimo dated within the signing window.

    A table that took effect within the window may carry increments of a
    renewal signed within it; the bundle does not record which agreement
    set each table, so the date of the table is the signal.

    Args:
        series: Monthly minimo of the level.
        regime: The renewal regime.
        competence: Competence date of the run.

    Returns:
        The earliest ``valid_from`` of a table with a value within the
        window and not after ``competence``, or ``None``, also for a regime
        without a signing window.
    """
    signed_from = regime.agreements_signed_from
    signed_until = regime.agreements_signed_until
    if signed_from is None or signed_until is None:
        return None
    last = min(signed_until, competence)
    return next(
        (
            p.valid_from
            for p in series.periods
            if signed_from <= p.valid_from <= last and not p.is_gap
        ),
        None,
    )


def assess_renewal_minimum(
    regime: PreferentialTaxRegime,
    facts: RegimeFacts,
    tax_year: int,
    paid: RenewalMinimum,
) -> RenewalMinimumAssessment:
    """Assess the renewal regime on the minimo of a run.

    The signing date of the agreement is not asked for: the minimo has no
    event to carry it, and the table dated within the signing window is
    what makes the increment possible.

    Args:
        regime: The renewal regime, in force in ``tax_year``.
        facts: Worker facts of the run.
        tax_year: Tax year of the payment.
        paid: The minimo of the run and its table dated within the window.

    Returns:
        A final decision with the reason that excludes the worker; a
        provisional one with an issue per missing fact; or a provisional
        one with reason :data:`INCREMENT_UNQUANTIFIED` and its issue.
    """
    excluded = ineligibility(regime, facts, tax_year)
    missing = (
        () if excluded is not None else missing_facts(regime, facts, signing=False)
    )
    issues: tuple[CalculationIssue, ...] = ()
    if excluded is not None:
        reason, status = excluded, CalculationStatus.FINAL
    elif missing:
        reason, status = missing[0][0], CalculationStatus.PROVISIONAL
        issues = tuple(_missing_issue(regime, code, fact) for code, fact in missing)
    else:
        reason, status = INCREMENT_UNQUANTIFIED, CalculationStatus.PROVISIONAL
        issues = (_unquantified_issue(regime),)
    return RenewalMinimumAssessment(
        decision=_decision(regime, facts, tax_year, paid, reason, status),
        issues=issues,
    )


def _decision(
    regime: PreferentialTaxRegime,
    facts: RegimeFacts,
    tax_year: int,
    paid: RenewalMinimum,
    reason: str,
    status: CalculationStatus,
) -> CalculationDecision:
    ruleset = regime.ruleset
    prior_income = facts.prior_income
    return CalculationDecision(
        capability=f"{regime.regime_id}_substitute_tax",
        status=status,
        reason_code=reason,
        rule=regime.regime_id if ruleset is None else ruleset.id,
        rule_version=str(tax_year) if ruleset is None else ruleset.version,
        inputs={
            "paid_in": "minimum",
            "tax_year": str(tax_year),
            "minimum": paid.minimum,
            "table_from": paid.table_from.isoformat(),
            "prior_income": _UNKNOWN if prior_income is None else prior_income,
            "sector": _UNKNOWN if facts.sector is None else facts.sector.value,
            "waived": str(facts.waived(regime)).lower(),
        },
        source=regime.source,
        amount=_ZERO,
    )


def _missing_issue(
    regime: PreferentialTaxRegime, code: str, fact: str
) -> CalculationIssue:
    return CalculationIssue(
        code=f"{regime.regime_id}_eligibility_unknown",
        message=(
            f"{regime.regime_id} substitute tax on the renewal increments of "
            f"the minimo undetermined ({code}): ordinary taxation used until "
            "the missing fact is provided"
        ),
        status=CalculationStatus.PROVISIONAL,
        source=regime.source,
        fact=fact,
    )


def _unquantified_issue(regime: PreferentialTaxRegime) -> CalculationIssue:
    return CalculationIssue(
        code=f"{regime.regime_id}_minimum_increment_unquantified",
        message=(
            f"the minimo may carry increments of a renewal signed within the "
            f"window of the {regime.regime_id} regime and the worker meets its "
            "requirements: the part of the minimo taxed at the substitute rate "
            "is not quantified, so ordinary taxation was used on all of it"
        ),
        status=CalculationStatus.PROVISIONAL,
        source=regime.source,
    )
