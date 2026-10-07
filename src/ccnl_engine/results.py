"""What a :class:`~ccnl_engine.PeriodResult` reports beyond its amounts.

Assurance and blockers, decisions and issues, model limitations, capability
gaps, unresolved requirements and the remittance lines.
"""

from __future__ import annotations

from ccnl_engine.payroll.domain.assurance import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
)
from ccnl_engine.payroll.domain.capability_report import CapabilityGap, CapabilityScope
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.payroll.domain.ledger import AccountKind
from ccnl_engine.payroll.domain.remittance import RemittanceColumn, RemittanceLine
from ccnl_engine.payroll.domain.requirements import UnresolvedRequirement
from ccnl_engine.shared.domain.limitation import (
    LimitationStatus,
    ModelLimitation,
    MonetaryImpact,
)

__all__ = [
    "AccountKind",
    "BlockerCode",
    "CalculationDecision",
    "CalculationIssue",
    "CalculationStatus",
    "CapabilityGap",
    "CapabilityScope",
    "CoverageStatus",
    "DecisionOrigin",
    "EvidenceStatus",
    "LimitationStatus",
    "ModelLimitation",
    "MonetaryImpact",
    "Payability",
    "RemittanceColumn",
    "RemittanceLine",
    "ResultAssurance",
    "ResultBlocker",
    "UnresolvedRequirement",
]
