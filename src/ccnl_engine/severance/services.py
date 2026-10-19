"""Payable rules of the TFR accrual, its yearly revaluation and its settlement."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.capability.rule.services import Rule
    from ccnl_engine.severance.models import TfrRules
    from ccnl_engine.severance.revaluation.models import TfrRevaluationRules
    from ccnl_engine.severance.settlement.models import TfrSettlementRules

__all__ = [
    "revaluation_rule_name",
    "revaluation_rules",
    "settlement_rules",
    "tfr_rules",
]


def tfr_rules(name: str, tfr: TfrRules) -> tuple[Rule, ...]:
    """Return the accrual rule and the additional IVS deduction, when set.

    Returns:
        The accrual rule, then the L. 297/1982 deduction of the sector.
    """
    accrual: Rule = (f"{name}:tfr", tfr.provenance)
    if tfr.additional_ivs is None:
        return (accrual,)
    return accrual, (f"{name}:tfr.additional_ivs", tfr.additional_ivs.provenance)


def revaluation_rule_name(revaluation: TfrRevaluationRules | None, year: int) -> str:
    """Return the id of the ruleset of the revaluation of *year*.

    Returns:
        The id of the bundled revaluation ruleset, or
        ``tax/<year>/tfr-revaluation`` when the year has none.
    """
    if revaluation is None or revaluation.ruleset is None:
        return f"tax/{year}/tfr-revaluation"
    return revaluation.ruleset.id


def revaluation_rules(
    revaluation: TfrRevaluationRules | None, year: int
) -> tuple[Rule, ...]:
    """Return the rate, price index and substitute tax of the revaluation.

    Returns:
        The three rules of art. 2120 c. 4 c.c. and D.Lgs. 47/2000 art. 11;
        empty when the year has no revaluation rules.
    """
    if revaluation is None:
        return ()
    name = revaluation_rule_name(revaluation, year)
    return (
        (f"{name}:rate", revaluation.rate.provenance),
        (f"{name}:price_index", revaluation.price_index.provenance),
        (f"{name}:substitute_tax", revaluation.substitute_tax.provenance),
    )


def settlement_rules(settlement: TfrSettlementRules | None) -> tuple[Rule, ...]:
    """Return the separate taxation rules of the TFR settlement.

    Returns:
        The separate taxation, the reference income and the months of
        service of artt. 17 and 19 TUIR and art. 2120 c. 1 c.c.; empty when
        the year has no settlement rules.
    """
    if settlement is None:
        return ()
    name = (
        f"tax/{settlement.year}/tfr-settlement"
        if settlement.ruleset is None
        else settlement.ruleset.id
    )
    return (
        (f"{name}:separate_taxation", settlement.separate_taxation.provenance),
        (f"{name}:reference_income", settlement.reference_income.provenance),
        (f"{name}:service_period", settlement.service_period.provenance),
    )
