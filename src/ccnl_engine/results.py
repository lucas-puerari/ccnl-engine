"""What a :class:`~ccnl_engine.PeriodResult` reports beyond its amounts.

Assurance and blockers, decisions and issues, model limitations, capability
gaps, unresolved requirements, runs a year left out and the remittance lines.
"""

from __future__ import annotations

from ccnl_engine.knowledge.limitation.models import (
    LimitationStatus,
    ModelLimitation,
    MonetaryImpact,
)
from ccnl_engine.payroll.assurance.models import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
)
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.payroll.capability.results import CapabilityGap, CapabilityScope
from ccnl_engine.payroll.capability.rules_requirement import UnresolvedRequirement
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.ledger.models_remittance import (
    RemittanceColumn,
    RemittanceLine,
)
from ccnl_engine.payroll.year.models_uncovered_run import UncoveredRun

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
    "UncoveredRun",
    "UnresolvedRequirement",
]
