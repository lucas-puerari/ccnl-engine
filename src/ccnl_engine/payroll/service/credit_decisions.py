"""Calculation decisions recording the outcome of an IRPEF credit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus

if TYPE_CHECKING:
    from collections.abc import Mapping
    from decimal import Decimal

    from ccnl_engine.engine.tax.domain.rules import YearRules
    from ccnl_engine.payroll.service.irpef_credits import CreditOutcome


def credit_decision(
    capability: str,
    rule: str,
    rules: YearRules,
    outcome: CreditOutcome,
    inputs: Mapping[str, Decimal | str],
) -> CalculationDecision:
    """Return the final decision recording one credit outcome.

    Args:
        capability: Catalog feature of the credit, e.g.
            ``"trattamento_integrativo"``.
        rule: Identifier of the rule applied, e.g. ``"dl3-2020-art1"``.
        rules: Year rules the credit was computed with; their ruleset
            version, or the year when none is recorded, is the rule version.
        outcome: Annual amount and reason code of the credit.
        inputs: Normalized inputs the credit was computed from.

    Returns:
        A final decision whose amount is the annual credit of ``outcome``,
        zero when the credit is not due.
    """
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL,
        reason_code=outcome.reason_code,
        rule=rule,
        rule_version=(
            str(rules.year) if rules.ruleset is None else rules.ruleset.version
        ),
        inputs=inputs,
        amount=outcome.amount,
    )
