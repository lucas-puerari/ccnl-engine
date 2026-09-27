"""Payroll taxes of an employer that is not a withholding agent.

Only the sostituti d'imposta listed by art. 23 c. 1 D.P.R. 600/1973 (in
force until 31 December 2026) and, from 1 January 2027, by art. 33 c. 1 of
the testo unico of D.Lgs. 33/2025 (art. 243 as amended by D.L. 200/2025
art. 4) withhold IRPEF on employment income.  A household employer (datore
di lavoro domestico) is not among them, so on its payslips:

- no IRPEF is withheld and no conguaglio is run;
- no regional or municipal surtax is withheld: both are determined and
  withheld by the sostituti of art. 23 (D.Lgs. 446/1997 art. 50 c. 4,
  D.Lgs. 360/1998 art. 1 c. 5);
- no trattamento integrativo is paid: the sostituti of art. 23 recognize it
  (D.L. 3/2020 art. 1 c. 3);
- no somma esente and no ulteriore detrazione are recognized: the sostituti
  of art. 23 recognize them (L. 207/2024 art. 1 c. 7);
- no substitute tax is withheld: the regimes are applied by the withholding
  agent.

The worker declares the income personally.  Each skipped capability records
a final decision with reason :data:`NOT_WITHHOLDING_AGENT` and a nil amount.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.service.withholding_law import (
    WithholdingTopic,
    withholding_rule,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "NOT_WITHHOLDING_AGENT",
    "PAYROLL_TAX_CAPABILITIES",
    "not_withholding_agent_decision",
    "not_withholding_agent_decisions",
]

#: Reason code of every capability a non-withholding employer skips.
NOT_WITHHOLDING_AGENT = "not_withholding_agent"

#: Capabilities only a withholding agent computes on the payslip.
PAYROLL_TAX_CAPABILITIES = (
    "irpef",
    "family_deductions",
    "ulteriore_detrazione_lavoro",
    "trattamento_integrativo",
    "somma_esente",
    "addizionale_regionale",
    "addizionale_comunale",
)

_ZERO = Decimal(0)


def not_withholding_agent_decision(
    capability: str,
    tax_year: int,
    inputs: Mapping[str, Decimal | str] | None = None,
) -> CalculationDecision:
    """Return the decision that ``capability`` does not apply to the employer.

    Args:
        capability: Catalog feature the employer does not compute.
        tax_year: Tax year of the run, the rule version.
        inputs: Inputs to record, e.g. the amount left to ordinary income.

    Returns:
        A final decision with reason :data:`NOT_WITHHOLDING_AGENT` and a
        nil amount.
    """
    law = withholding_rule(WithholdingTopic.AGENTS, tax_year)
    return CalculationDecision(
        capability=capability,
        status=CalculationStatus.FINAL,
        reason_code=NOT_WITHHOLDING_AGENT,
        rule=law.rule,
        rule_version=str(tax_year),
        inputs=inputs or {},
        source=law.source,
        amount=_ZERO,
    )


def not_withholding_agent_decisions(tax_year: int) -> tuple[CalculationDecision, ...]:
    """Return one decision per payroll tax capability the employer skips.

    Returns:
        The decisions of :data:`PAYROLL_TAX_CAPABILITIES`, in order.
    """
    return tuple(
        not_withholding_agent_decision(c, tax_year) for c in PAYROLL_TAX_CAPABILITIES
    )
