"""What the conguaglio takes in from the earlier employments of the year.

The income of an earlier employment is part of the reddito complessivo
beyond this employment (``CurrentYearTaxFacts.other_employment_income``)
until the conguaglio takes it in: then it is taxed with this employment's
pay, its withholdings and the trattamento integrativo it paid count as
already withheld and paid, and it leaves the other income, so the
reddito complessivo counts it once.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import CalculationDecision, CalculationStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ccnl_engine.employment.spell.models import EmploymentSpell
    from ccnl_engine.irpef.other_income.inputs import CurrentYearTaxFacts

__all__ = [
    "ADDITIONAL_IRPEF_BASE",
    "ConguaglioIntake",
    "PriorTotals",
    "conguaglio_facts",
    "conguaglio_intake",
    "prior_decision",
    "prior_spells",
    "prior_totals",
    "taken_in",
]

#: Capability of the earlier employments the conguaglio takes in.
ADDITIONAL_IRPEF_BASE = "additional_irpef_base"

_ZERO = Decimal(0)


@dataclass(frozen=True)
class PriorTotals:
    """The certified amounts of the earlier employments taken in."""

    taxable: Decimal = _ZERO
    irpef_withheld: Decimal = _ZERO
    trattamento_paid: Decimal = _ZERO


def prior_totals(facts: CurrentYearTaxFacts | None) -> PriorTotals:
    """Return the sums of the earlier employments of ``facts``.

    Returns:
        Zeros without facts or earlier employments.
    """
    prior = () if facts is None else facts.prior_employers
    return PriorTotals(
        sum((p.taxable for p in prior), _ZERO),
        sum((p.irpef_withheld for p in prior), _ZERO),
        sum((p.trattamento_paid for p in prior), _ZERO),
    )


def conguaglio_facts(facts: CurrentYearTaxFacts) -> CurrentYearTaxFacts:
    """Return ``facts`` with the income the conguaglio takes in moved out.

    Returns:
        ``facts`` whose other employment income no longer holds the
        taxable income of the earlier employments, which it no longer
        lists: :func:`prior_totals` carries them into the tax.
    """
    moved = prior_totals(facts).taxable
    return replace(
        facts,
        other_employment_income=facts.other_employment_income - moved,
        prior_employers=(),
    )


def prior_spells(facts: CurrentYearTaxFacts | None) -> tuple[EmploymentSpell, ...]:
    """Return the days of the earlier employments of ``facts``.

    Returns:
        Their spells, none without facts.
    """
    return () if facts is None else tuple(p.spell for p in facts.prior_employers)


def prior_decision(prior: PriorTotals, year: int) -> CalculationDecision | None:
    """Return the decision of the earlier employments a conguaglio took in.

    Returns:
        A final decision with the certified taxable income as its amount
        and the IRPEF and trattamento of the other payers as inputs; none
        when the run took in nothing.
    """
    if prior == PriorTotals():
        return None
    return CalculationDecision(
        capability=ADDITIONAL_IRPEF_BASE,
        status=CalculationStatus.FINAL,
        reason_code="prior_employment_conguagliated",
        rule="dpr-600-1973-art23-c4",
        rule_version=str(year),
        inputs={
            "irpef_withheld": str(prior.irpef_withheld),
            "trattamento_paid": str(prior.trattamento_paid),
        },
        amount=prior.taxable,
    )


@dataclass(frozen=True)
class ConguaglioIntake:
    """What a run's tax reads of the earlier employments of the year."""

    facts: CurrentYearTaxFacts | None
    spells: tuple[EmploymentSpell, ...]
    prior: PriorTotals


def conguaglio_intake(
    facts: CurrentYearTaxFacts | None,
    spells: tuple[EmploymentSpell, ...],
    *,
    conguaglio: bool,
    settled: bool,
) -> ConguaglioIntake:
    """Return the facts, days and amounts the run's tax reads.

    The conguaglio moves the income of the earlier employments into this
    employment's tax and counts their days; it takes their withholdings
    in once, on the payment that settles the year first (``settled`` is a
    conguaglio already in the opening state).

    Returns:
        ``facts`` and ``spells`` unchanged outside a conguaglio.
    """
    if not conguaglio or facts is None or not facts.prior_employers:
        return ConguaglioIntake(facts, spells, PriorTotals())
    prior = PriorTotals() if settled else prior_totals(facts)
    return ConguaglioIntake(
        conguaglio_facts(facts), spells + prior_spells(facts), prior
    )


def taken_in(decisions: Iterable[CalculationDecision], key: str) -> Decimal:
    """Return the amount ``key`` a conguaglio took in from other payers.

    Returns:
        The sum of the ``key`` input of the run's ``additional_irpef_base``
        decisions: ``irpef_withheld`` or ``trattamento_paid``.
    """
    return sum(
        (
            Decimal(str(d.inputs[key]))
            for d in decisions
            if d.capability == ADDITIONAL_IRPEF_BASE
        ),
        _ZERO,
    )
