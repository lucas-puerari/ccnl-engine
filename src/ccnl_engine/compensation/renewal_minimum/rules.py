"""The renewal regime on the increments paid inside the CCNL minimo.

L. 199/2025 art. 1 c. 7 taxes at 5% the pay increments paid in 2026 under
renewals signed from 1 January 2024 to 31 December 2026, for private-sector
workers whose 2025 employment income did not exceed 33,000 EUR.  A renewal
raises the minimo tabellare, so its increments are paid inside the base
salary, not as a separate event.  Agenzia delle Entrate circ. 2/E of 24
February 2026 (par. 1, the ``increment_source`` of the regime) reads the
increment as every tranche of a qualifying renewal paid in 2026, started
before or not, measured on the table in force before the renewal, on the
direct pay (twelve months, 13th, 14th) and never on the seniority
increments.  A CCNL that lists its renewals (``parameters.renewals``) ties
its tables to them: the increment of a run is the minimo it pays less the
minimo in force the day before the first tranche of the earliest renewal
signed within the window, scaled like the minimo of the run.  The substitute
tax is posted on it, at the gross like a renewal increment paid as an event.
Without the renewal, or without the table before it, the increment is not
quantified.

:func:`assess_renewal_minimum` therefore never posts the substitute tax on
the minimo.  It decides what the worker facts alone decide: a known fact
that excludes the worker ends the matter with a final decision; a missing
fact is reported with the public field that supplies it; an eligible worker
gets a provisional decision and an issue, because the increment is not
quantified and the ordinary taxation of the run may be too high.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    IssueCause,
)
from ccnl_engine.pay_item.rounding.policies import money
from ccnl_engine.regime.eligibility.rules import RegimeEligibility
from ccnl_engine.regime.requirement.rules import ineligibility, missing_facts

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.agreement.validity.rules import TimeSeries
    from ccnl_engine.compensation.renewal_minimum.models import RenewalAgreement
    from ccnl_engine.regime.models import PreferentialTaxRegime
    from ccnl_engine.regime.requirement.rules import RegimeFacts

__all__ = [
    "INCREMENT_TAXED",
    "INCREMENT_UNQUANTIFIED",
    "RenewalMinimum",
    "RenewalMinimumAssessment",
    "assess_renewal_minimum",
    "pre_renewal_minimum",
    "qualifying_starts",
    "renewal_table_from",
    "substitute_tax",
]

#: Reason of an eligible worker whose renewal increments in the minimo are
#: not quantified.
INCREMENT_UNQUANTIFIED = "renewal_increment_in_minimum_unquantified"
#: Reason of an eligible worker whose renewal increment was taxed.
INCREMENT_TAXED = "renewal_increment_in_minimum_taxed"

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
        increment: Renewal increment inside the minimo of the run, ``None``
            when it cannot be measured.
        pre_renewal: Full-time minimo in force before the renewal, ``None``
            with ``increment``.
    """

    minimum: Decimal
    table_from: date
    increment: Decimal | None = None
    pre_renewal: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RenewalMinimumAssessment:
    """Decision and issues of the renewal regime on the minimo of a run.

    Attributes:
        decision: The ``rinnovo_substitute_tax`` decision; its amount is
            the substitute tax posted, zero when the increment is not taxed.
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


def pre_renewal_minimum(
    series: TimeSeries,
    renewals: tuple[RenewalAgreement, ...],
    regime: PreferentialTaxRegime,
    competence: date,
    level_code: str,
) -> Decimal | None:
    """Return the full-time minimo before the renewals the regime covers.

    Args:
        series: Monthly minimo of the level.
        renewals: Renewals of the CCNL.
        regime: The renewal regime.
        competence: Competence date of the run.
        level_code: Level of the run, read in ``minimum_before``.

    Returns:
        The ``minimum_before`` of the level that the earliest renewal signed
        within the window, started by ``competence``, states; else the
        minimo in force the day before its first tranche.  ``None`` without
        such a renewal, without a signing window, for a level its
        ``minimum_before`` omits or without a table on that day.
    """
    starts = qualifying_starts(renewals, regime, competence)
    if not starts:
        return None
    first = min(starts)
    earliest = next(r for r in renewals if r.tables_from == first)
    if earliest.minimum_before:
        return earliest.minimum_before.get(level_code)
    period = series.period_at(first - timedelta(days=1))
    return None if period is None else period.value


def qualifying_starts(
    renewals: tuple[RenewalAgreement, ...],
    regime: PreferentialTaxRegime,
    competence: date,
) -> tuple[date, ...]:
    """Return the first tranches of the renewals the regime covers, started.

    Returns:
        The ``tables_from`` of each renewal signed within the window whose
        first tranche started by ``competence``; empty without a window.
    """
    signed_from = regime.agreements_signed_from
    signed_until = regime.agreements_signed_until
    if signed_from is None or signed_until is None:
        return ()
    return tuple(
        r.tables_from
        for r in renewals
        if signed_from <= r.signed_on <= signed_until and r.tables_from <= competence
    )


def substitute_tax(regime: PreferentialTaxRegime, increment: Decimal) -> Decimal:
    """Return the substitute tax on a renewal increment.

    Returns:
        The increment at the flat rate of the regime, to the cent.
    """
    return money(increment * regime.flat_tax_rate)


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
        provisional one with an issue per missing fact; a final one with
        reason :data:`INCREMENT_TAXED` and the substitute tax as amount when
        the increment is measured; or a provisional one with reason
        :data:`INCREMENT_UNQUANTIFIED` and its issue.
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
    elif paid.increment is not None:
        reason, status = INCREMENT_TAXED, CalculationStatus.FINAL
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
    taxed = reason == INCREMENT_TAXED and paid.increment is not None
    measured: dict[str, Decimal | str] = {}
    if paid.increment is not None and paid.pre_renewal is not None:
        measured = {
            "increment": paid.increment,
            "pre_renewal_minimum": paid.pre_renewal,
        }
    if taxed and paid.increment is not None:
        measured |= {
            "eligibility": RegimeEligibility.ELIGIBLE.value,
            "eligible_amount": paid.increment,
        }
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
            **measured,
        },
        source=(regime.increment_source or regime.source) if taxed else regime.source,
        amount=substitute_tax(regime, paid.increment)
        if taxed and paid.increment is not None
        else _ZERO,
    )


def _missing_issue(
    regime: PreferentialTaxRegime, code: str, fact: str
) -> CalculationIssue:
    return CalculationIssue(
        code=f"{regime.regime_id}_eligibility_unknown",
        capability=f"{regime.regime_id}_substitute_tax",
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
        capability=f"{regime.regime_id}_substitute_tax",
        message=(
            f"the minimo may carry increments of a renewal signed within the "
            f"window of the {regime.regime_id} regime and the worker meets its "
            "requirements: the part of the minimo taxed at the substitute rate "
            "is not quantified, so ordinary taxation was used on all of it"
        ),
        status=CalculationStatus.PROVISIONAL,
        source=regime.source,
        cause=IssueCause.RULE,
    )
