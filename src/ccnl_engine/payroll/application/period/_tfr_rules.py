"""Payable rules of the TFR accrual and of its yearly revaluation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.period._rule_lookup import Rule
    from ccnl_engine.tax.severance.models import TfrRules
    from ccnl_engine.tax.severance.models_revaluation import TfrRevaluationRules

__all__ = ["revaluation_rule_name", "revaluation_rules", "tfr_rules"]


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
