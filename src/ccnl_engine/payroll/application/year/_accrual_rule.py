"""The month-qualification rule of a CCNL's extra-month ratei.

The rule comes from ``parameters.accrual_rule`` when the bundle holds the
signed clause.  Without it the engine default applies (a month counts with
at least 15 accruing days) and the rule carries a ``missing`` provenance
record: a run whose rateo depends on the threshold, because a month of its
window accrued for part of its days, reports the rule as unsourced.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.accrual import (
    DEFAULT_MONTH_ACCRUAL_RULE,
    MonthAccrualRule,
)
from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL

__all__ = ["MISSING_ACCRUAL_PROVENANCE", "accrual_rule_id", "month_accrual_rule"]

#: Provenance of the engine default applied for a CCNL without the clause.
MISSING_ACCRUAL_PROVENANCE = RuleProvenance(
    status=ProvenanceStatus.MISSING,
    note=(
        "No signed CCNL text in the bundle states when a fraction of a month "
        "counts for the extra-month ratei; the engine default (at least 15 "
        "days) applies."
    ),
)


def accrual_rule_id(ccnl: CCNL) -> str:
    """Return the identifier of the accrual rule of ``ccnl``.

    Returns:
        ``<ruleset id>:parameters.accrual_rule``.
    """
    name = f"ccnl/{ccnl.meta.ccnl_id}" if ccnl.ruleset is None else ccnl.ruleset.id
    return f"{name}:parameters.accrual_rule"


def month_accrual_rule(ccnl: CCNL) -> MonthAccrualRule:
    """Return the rule the ratei of ``ccnl`` are counted with.

    Returns:
        The CCNL clause with its provenance, or the engine default with a
        ``missing`` provenance when the bundle has no clause.
    """
    stored = ccnl.parameters.accrual_rule
    if stored is None:
        return MonthAccrualRule(
            min_days=DEFAULT_MONTH_ACCRUAL_RULE.min_days,
            source=DEFAULT_MONTH_ACCRUAL_RULE.source,
            comparison=DEFAULT_MONTH_ACCRUAL_RULE.comparison,
            rule=accrual_rule_id(ccnl),
            provenance=MISSING_ACCRUAL_PROVENANCE,
        )
    location = stored.provenance.location
    section = None if location is None else location.section
    return MonthAccrualRule(
        min_days=stored.min_days,
        source=f"CCNL {ccnl.meta.name}: {section or 'accrual clause'}",
        comparison=stored.comparison,
        rule=accrual_rule_id(ccnl),
        provenance=stored.provenance,
    )
