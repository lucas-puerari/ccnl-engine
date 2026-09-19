"""Variable pay handler: fringe benefits, welfare, bonus and PdR."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.variable_pay import (
    compute_bonus,
    compute_fringe_benefit,
    compute_welfare,
)
from ccnl_engine.engine.tax.service.loaders import load_variable_pay_rules

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario
    from ccnl_engine.engine.tax.domain.variable_pay import VariablePayRules

_ZERO = Decimal(0)


@dataclass(frozen=True)
class _VariablePayResult:
    fringe_benefit: Decimal
    fringe_benefit_threshold: Decimal
    fringe_benefit_taxable: Decimal
    welfare: Decimal
    bonus: Decimal
    bonus_pdr_flat_tax: Decimal
    bonus_ordinary_taxable: Decimal
    bonus_pdr_missing_prior_year: bool
    var_pay_rules: VariablePayRules | None


def _run_wr_variable_pay(
    scenario: PayrollScenario,
    year: int,
    wr_warnings: list[str],
) -> _VariablePayResult:
    """Run the work-rules variable-pay block (fringe benefits, welfare, bonus/PdR).

    Returns:
        :class:`_VariablePayResult` with zero amounts for unset inputs.
        ``var_pay_rules`` is ``None`` when no fringe-benefit or bonus/PdR
        input is present (rules were not loaded).
    """
    fb_input = scenario.fringe_benefit_input
    welfare_input = scenario.welfare_input
    bonus_input = scenario.bonus_input
    any_input = (
        fb_input is not None or welfare_input is not None or bonus_input is not None
    )
    # Load only when fringe-benefit or bonus/PdR computation is actually needed.
    rules_needed = fb_input is not None or bonus_input is not None

    if not any_input:
        return _VariablePayResult(
            fringe_benefit=_ZERO,
            fringe_benefit_threshold=_ZERO,
            fringe_benefit_taxable=_ZERO,
            welfare=_ZERO,
            bonus=_ZERO,
            bonus_pdr_flat_tax=_ZERO,
            bonus_ordinary_taxable=_ZERO,
            bonus_pdr_missing_prior_year=False,
            var_pay_rules=None,
        )

    fb_annual = _ZERO
    fb_threshold = _ZERO
    fb_taxable = _ZERO
    welfare_annual = _ZERO
    bonus_annual = _ZERO
    pdr_flat_tax = _ZERO
    bonus_ordinary = _ZERO
    pdr_missing_prior_year = False
    var_pay_rules: VariablePayRules | None

    if rules_needed:
        var_pay_rules = load_variable_pay_rules(year)
        if fb_input is not None:
            fb_annual, fb_threshold, fb_taxable = compute_fringe_benefit(
                fb_input, var_pay_rules.fringe_benefit
            )
        if bonus_input is not None:
            missing_prior = (
                bonus_input.eligible_for_pdr
                and bonus_input.prior_year_gross_annual is None
            )
            if missing_prior:
                pdr_missing_prior_year = True
                wr_warnings.append(
                    "bonus_input: prior_year_gross_annual required for PdR "
                    "regime verification — bonus treated as ordinary income"
                )
            bonus_annual, pdr_flat_tax, bonus_ordinary = compute_bonus(
                bonus_input, var_pay_rules.pdr, wr_warnings
            )
    else:
        var_pay_rules = None
    if welfare_input is not None:
        welfare_annual = compute_welfare(welfare_input)

    return _VariablePayResult(
        fringe_benefit=fb_annual,
        fringe_benefit_threshold=fb_threshold,
        fringe_benefit_taxable=fb_taxable,
        welfare=welfare_annual,
        bonus=bonus_annual,
        bonus_pdr_flat_tax=pdr_flat_tax,
        bonus_ordinary_taxable=bonus_ordinary,
        bonus_pdr_missing_prior_year=pdr_missing_prior_year,
        var_pay_rules=var_pay_rules,
    )
