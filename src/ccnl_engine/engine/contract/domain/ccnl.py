"""CCNL domain models — re-export shim for backward compatibility.

All public names are now defined in their respective submodules:
  absence.py, compensation.py, identity.py, seniority.py,
  sickness.py, validation.py, working_time.py.
"""

from ccnl_engine.engine.contract.domain.absence import (
    AbsenceRules,
    DailyDivisorMethod,
)
from ccnl_engine.engine.contract.domain.compensation import (
    AgreementKind,
    Allowance,
    CCNLParameters,
    EmployerFund,
    Level,
    SupplementaryAllowance,
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
    LevelCategory,
    SeniorityIncrements,
    SeniorityTier,
)
from ccnl_engine.engine.contract.domain.sickness import (
    SicknessRules,
    SicknessTier,
)
from ccnl_engine.engine.contract.domain.validation import (
    _assert_level_provenance,
    _assert_unique,
    _check_category_level_codes,
    _check_flat_level_codes,
    _check_salary_ordering_at_date,
    _check_tier_level_codes,
    _coerce_legacy_extraction,
    _coerce_legacy_source,
    _collect_transition_dates,
    _legacy_source_kind,
    _slugify_url,
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
    "AgreementKind",
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
    "LevelCategory",
    "NoteKind",
    "OvertimeBand",
    "SeniorityIncrements",
    "SeniorityTier",
    "SicknessRules",
    "SicknessTier",
    "SupplementaryAllowance",
    "TaxSector",
    "TimeSupplementKind",
    "TimeSupplements",
    "WorkKind",
    "WorkRuleFeature",
    "_assert_level_provenance",
    "_assert_unique",
    "_check_category_level_codes",
    "_check_flat_level_codes",
    "_check_salary_ordering_at_date",
    "_check_tier_level_codes",
    "_coerce_legacy_extraction",
    "_coerce_legacy_source",
    "_collect_transition_dates",
    "_legacy_source_kind",
    "_slugify_url",
]
