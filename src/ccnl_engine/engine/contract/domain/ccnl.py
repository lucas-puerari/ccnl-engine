"""CCNL domain models — re-export shim for backward compatibility.

All public names are now defined in their respective submodules:
  absence.py, compensation.py, identity.py, seniority.py,
  sickness.py, validation.py, working_time.py.
"""

from ccnl_engine.engine.contract.domain.absence import (
    AbsenceRules,
    DailyDivisorMethod,
)
from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.domain.compensation import (
    Allowance,
    CCNLParameters,
    EmployerFund,
    Level,
)
from ccnl_engine.engine.contract.domain.identity import (
    CCNL,
    CCNLCoverage,
    CCNLMeta,
    CCNLValidity,
    CCNLVerification,
    CCNLWorkRules,
    CoverageNote,
    CoverageStatus,
    NoteKind,
    TaxSector,
    WorkRuleFeature,
)
from ccnl_engine.engine.contract.domain.seniority import (
    SeniorityIncrements,
    SeniorityTier,
)
from ccnl_engine.engine.contract.domain.sickness import (
    SicknessRules,
    SicknessTier,
)
from ccnl_engine.engine.contract.domain.working_time import (
    LeaveEntitlementTier,
    LeaveRules,
    OvertimeBand,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)

__all__ = [
    "CCNL",
    "AbsenceRules",
    "Allowance",
    "CCNLCoverage",
    "CCNLMeta",
    "CCNLParameters",
    "CCNLValidity",
    "CCNLVerification",
    "CCNLWorkRules",
    "CoverageNote",
    "CoverageStatus",
    "DailyDivisorMethod",
    "EmployerFund",
    "LeaveEntitlementTier",
    "LeaveRules",
    "Level",
    "NoteKind",
    "OvertimeBand",
    "SeniorityIncrements",
    "SeniorityTier",
    "SicknessRules",
    "SicknessTier",
    "TaxSector",
    "TimeSupplementKind",
    "TimeSupplements",
    "WorkKind",
    "WorkRuleFeature",
    "WorkerCategory",
]
