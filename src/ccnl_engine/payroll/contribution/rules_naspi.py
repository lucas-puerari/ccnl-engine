"""NASpI surcharge of a fixed-term contract (L. 92/2012 art. 2 c. 28).

C. 28 (text in force on Normattiva on 7 October 2026): "ai rapporti di
lavoro subordinato non a tempo indeterminato si applica un contributo
addizionale, a carico del datore di lavoro, pari all'1,4 per cento della
retribuzione imponibile ai fini previdenziali.  Il contributo addizionale
è aumentato di 0,5 punti percentuali in occasione di ciascun rinnovo del
contratto a tempo determinato, anche in regime di somministrazione.  Le
disposizioni del precedente periodo non si applicano ai contratti di
lavoro domestico, nonché nelle ipotesi di cui al comma 29."  Each renewal
adds 0.5 points to the rate of the previous contract: 1.4%, 1.9%, 2.4%,
2.9% for the original contract and three renewals (INPS circ. 121/2019
par. 2.3).  C. 3 excludes the operai agricoli from the whole article, so
from the surcharge; c. 29 lists the other exclusions
(:class:`~ccnl_engine.payroll.employment.inputs_fixed_term.NaspiExclusion`).

The rates and the exempt categories are data of the sector ruleset; the
contract facts come from the request.  A fact the surcharge depends on and
the request leaves unknown is named, and the rate charged meanwhile is the
one of a contract with no exclusion and no renewal.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ccnl_engine.payroll.employment.inputs_fixed_term import FixedTerm

if TYPE_CHECKING:
    from ccnl_engine.contract.employment.models_category import WorkerCategory
    from ccnl_engine.payroll.employment.inputs import Contract
    from ccnl_engine.tax.annual.models import YearRules

__all__ = ["NaspiSurcharge", "SurchargeReason", "naspi_surcharge"]

_ZERO = Decimal(0)
#: Public facts of :data:`~ccnl_engine.payroll.assurance.models_decision.PUBLIC_FACTS`.
_CATEGORY = "category"
_EXCLUSION = "naspi_exclusion"
_RENEWALS = "renewals"


class SurchargeReason(StrEnum):
    """Why the surcharge of a run is charged at its rate, or not at all.

    Attributes:
        NOT_FIXED_TERM: A permanent or apprenticeship contract (c. 29
            lett. c excludes apprentices).
        EXEMPT_CATEGORY: A worker category the sector ruleset exempts
            (c. 3: operai agricoli).
        EXCLUDED: An exclusion of c. 29 the contract falls in.
        CHARGED: Charged on the INPS base of the run.
    """

    NOT_FIXED_TERM = "not_fixed_term"
    EXEMPT_CATEGORY = "exempt_category"
    EXCLUDED = "excluded"
    CHARGED = "charged"


@dataclass(frozen=True, slots=True)
class NaspiSurcharge:
    """The NASpI surcharge of a run.

    Attributes:
        rate: Rate added to the employer INPS rate, zero when not charged.
        reason: Why the rate is what it is.
        renewals: Renewals counted in the rate.
        missing_fact: Public fact the surcharge depends on and the request
            leaves unknown, ``None`` when it is determined.
    """

    rate: Decimal
    reason: SurchargeReason
    renewals: int = 0
    missing_fact: str | None = None


_NOT_FIXED_TERM = NaspiSurcharge(_ZERO, SurchargeReason.NOT_FIXED_TERM)
_EXEMPT = NaspiSurcharge(_ZERO, SurchargeReason.EXEMPT_CATEGORY)
_EXCLUDED = NaspiSurcharge(_ZERO, SurchargeReason.EXCLUDED)


def _missing_fact(
    rules: YearRules,
    contract: FixedTerm,
    category: WorkerCategory | None,
    increment: Decimal,
) -> str | None:
    """Return the first unknown fact the surcharge of a run depends on.

    Returns:
        The worker category when the sector exempts some, the exclusion
        when the sector charges a surcharge, the renewals when they raise
        it; ``None`` when every fact it depends on is stated.
    """
    if rules.fixed_term_exempt_categories and category is None:
        return _CATEGORY
    if contract.naspi_exclusion is None and (
        rules.fixed_term_additional_rate or increment
    ):
        return _EXCLUSION
    if contract.renewals is None and increment:
        return _RENEWALS
    return None


def naspi_surcharge(
    rules: YearRules,
    contract: Contract,
    category: WorkerCategory | None,
    *,
    domestic: bool = False,
) -> NaspiSurcharge:
    """Return the NASpI surcharge of a run.

    Args:
        rules: Rules of the competence year of the run.
        contract: Contract of the employment.
        category: Worker category of the run, ``None`` when not known.
        domestic: The contract is domestic work, which never pays the
            renewal increase (c. 28, third period).

    Returns:
        The surcharge, with the fact it depends on when it is unknown.
    """
    if not isinstance(contract, FixedTerm):
        return _NOT_FIXED_TERM
    if category in rules.fixed_term_exempt_categories:
        return _EXEMPT
    exclusion = contract.naspi_exclusion
    if exclusion is not None and exclusion.excludes_surcharge:
        return _EXCLUDED
    no_increase = domestic or (
        exclusion is not None and exclusion.excludes_renewal_increase
    )
    increment = _ZERO if no_increase else rules.fixed_term_renewal_increment
    renewals = contract.renewals or 0
    return NaspiSurcharge(
        rate=rules.fixed_term_additional_rate + increment * renewals,
        reason=SurchargeReason.CHARGED,
        renewals=renewals if increment else 0,
        missing_fact=_missing_fact(rules, contract, category, increment),
    )
