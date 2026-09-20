"""Tax rule models for a single fiscal year.

Re-exports all public names from the split modules for backwards compatibility.
"""

from __future__ import annotations

from ccnl_engine.engine.tax.domain.contribution_rules import (
    ApprenticeRates,
    ApprenticeRawRates,
    DomesticInpsHoursBracket,
    DomesticInpsRates,
    DomesticInpsWageBracket,
    InpsEmployeeTier,
    InpsEmployerTier,
    InpsRates,
    InpsRawRates,
)
from ccnl_engine.engine.tax.domain.credit_rules import (
    SommaEsenteBand,
    SommaEsenteRules,
    TrattamentoIntegrativoRules,
    UlterioreDetrazioneRules,
)
from ccnl_engine.engine.tax.domain.irpef_rules import (
    DeductionBreakpoint,
    IrpefBracket,
    SterilizzazioneDetrazioniRules,
    WorkDeductionRules,
)
from ccnl_engine.engine.tax.domain.ruleset import YearRules, YearRulesRaw
from ccnl_engine.engine.tax.domain.tfr_rules import TfrRules

__all__ = [
    "ApprenticeRates",
    "ApprenticeRawRates",
    "DeductionBreakpoint",
    "DomesticInpsHoursBracket",
    "DomesticInpsRates",
    "DomesticInpsWageBracket",
    "InpsEmployeeTier",
    "InpsEmployerTier",
    "InpsRates",
    "InpsRawRates",
    "IrpefBracket",
    "SommaEsenteBand",
    "SommaEsenteRules",
    "SterilizzazioneDetrazioniRules",
    "TfrRules",
    "TrattamentoIntegrativoRules",
    "UlterioreDetrazioneRules",
    "WorkDeductionRules",
    "YearRules",
    "YearRulesRaw",
]
