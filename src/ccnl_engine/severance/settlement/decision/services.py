"""The decisions and the issues of a TFR settlement."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.employment.fact.inputs import PublicEndOfService
from ccnl_engine.provenance.source.rule.models import RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.period.context.services import RunContext
    from ccnl_engine.provenance.source.models import SourceLocation
    from ccnl_engine.severance.settlement.services import TfrSettlement

from ccnl_engine.severance.settlement.gap.models import _Gap

#: Capability of the TFR settlement, as the events name it.
CAPABILITY = "termination_tfr"
_KIND = "tfr_settlement_item"
_ZERO = Decimal(0)
_MONTHS = 12
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Months of service up to which a fixed term takes the art. 19 c. 1-ter deduction.
_SHORT_FIXED_TERM = 24
_FINAL = CalculationStatus.FINAL
_INCOMPLETE = CalculationStatus.INCOMPLETE


def _location(provenance: RuleProvenance | None) -> SourceLocation | None:
    return provenance.location if isinstance(provenance, RuleProvenance) else None


def _ruleset_name(ctx: RunContext) -> str:
    rules = ctx.contract.year_rules
    settlement = rules.tfr_settlement
    if settlement is None or settlement.ruleset is None:
        return f"tax/{rules.year}/tfr-settlement"
    return settlement.ruleset.id


def _payout_decision(ctx: RunContext, settlement: TfrSettlement) -> CalculationDecision:
    """Return the decision of the TFR due.

    Returns:
        A final ``tfr_due`` decision, an incomplete ``revaluation_pending``
        one when the revaluation of the year is left out, or an incomplete
        one with the reason of the gap.
    """
    rules = ctx.contract.year_rules
    tax_name = rules.ruleset.id if rules.ruleset else f"tax/{rules.year}"
    gap = settlement.payout_gap
    if gap is not None:
        status, reason = _INCOMPLETE, gap.reason
    elif settlement.revaluation_pending:
        status, reason = _INCOMPLETE, "revaluation_pending"
    else:
        status, reason = _FINAL, "tfr_due"
    return CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code=reason,
        rule=f"{tax_name}:tfr",
        rule_version=str(rules.year)
        if rules.ruleset is None
        else rules.ruleset.version,
        inputs=settlement.inputs,
        source=_location(rules.tfr.provenance),
        amount=settlement.payout,
    )


def _tax_decision(ctx: RunContext, settlement: TfrSettlement) -> CalculationDecision:
    """Return the decision of the separate tax of the TFR.

    Returns:
        A final ``average_rate`` (or ``caller_rate``) decision with the
        tax, or an incomplete one with the reason of the gap.
    """
    rules = ctx.contract.year_rules.tfr_settlement
    gap = settlement.tax_gap or settlement.payout_gap
    if gap is not None:
        status, reason = _INCOMPLETE, gap.reason
    else:
        status = _FINAL
        reason = "average_rate" if settlement.caller_rate is None else "caller_rate"
    return CalculationDecision(
        capability=CAPABILITY,
        status=status,
        reason_code=reason,
        rule=f"{_ruleset_name(ctx)}:reference_income",
        rule_version=(
            str(ctx.contract.year_rules.year)
            if rules is None or rules.ruleset is None
            else rules.ruleset.version
        ),
        inputs=settlement.inputs,
        source=None if rules is None else _location(rules.reference_income.provenance),
        amount=settlement.tax,
    )


def _issue(gap: _Gap) -> CalculationIssue:
    return CalculationIssue(
        code=f"tfr_settlement_{gap.reason}",
        message=f"{CAPABILITY}: {gap.message}",
        status=_INCOMPLETE,
        fact=gap.fact,
        capability=CAPABILITY,
    )


def _issues(settlement: TfrSettlement) -> tuple[CalculationIssue, ...]:
    gaps = (settlement.payout_gap, settlement.tax_gap)
    issues = [_issue(gap) for gap in gaps if gap is not None]
    if settlement.revaluation_pending:
        issues.append(
            CalculationIssue(
                code="tfr_settlement_revaluation_pending",
                message=(
                    f"{CAPABILITY}: the revaluation of the TFR fund for the "
                    "termination year (art. 2120 c. 5 c.c.) is not computed and "
                    "is left out of the TFR paid; the separate tax does not "
                    "depend on it"
                ),
                status=_INCOMPLETE,
                capability=CAPABILITY,
            )
        )
    return tuple(issues)
