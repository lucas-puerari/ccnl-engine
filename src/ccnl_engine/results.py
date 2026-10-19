"""What a :class:`~ccnl_engine.PeriodResult` reports beyond its amounts.

Assurance and blockers, decisions and issues, model limitations, capability
gaps, unresolved requirements, runs a year left out and the remittance lines;
:func:`result_to_json` writes a whole result as JSON.
:data:`PUBLIC_FACTS` maps the detail of a ``missing_fact`` blocker to the
public field that supplies it.
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
    PUBLIC_FACTS,
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
    DecisionOrigin,
)
from ccnl_engine.interchange.result.serializers import result_to_json
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
    "PUBLIC_FACTS",
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
    "result_to_json",
]
