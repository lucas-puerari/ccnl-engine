"""What a :class:`~ccnl_engine.PeriodResult` reports beyond its amounts.

Assurance and blockers, decisions and issues, model limitations, capability
gaps, unresolved requirements, runs a year left out and the remittance lines.
"""

from __future__ import annotations

from ccnl_engine.assurance.models import (
    BlockerCode,
    CoverageStatus,
    EvidenceStatus,
    Payability,
    ResultAssurance,
    ResultBlocker,
    ResultTotal,
)
from ccnl_engine.capability.requirement.rules import UnresolvedRequirement
from ccnl_engine.capability.results import CapabilityGap, CapabilityScope
from ccnl_engine.decision.models import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.ledger.remittance.models import (
    RemittanceColumn,
    RemittanceLine,
)
from ccnl_engine.limitation.models import (
    LimitationStatus,
    ModelLimitation,
    MonetaryImpact,
)
from ccnl_engine.year.coverage.models import UncoveredRun

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
    "ResultTotal",
    "UncoveredRun",
    "UnresolvedRequirement",
]
