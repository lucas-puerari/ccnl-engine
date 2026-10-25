"""The knowledge port of the engine and the models it returns.

A :class:`~ccnl_engine.PayrollEngine` reads every rule through a
:class:`KnowledgeRepository`; pass your own to
``PayrollEngine(repository=...)`` to add CCNL files or a year the bundle
does not hold, without a fork.  :class:`BundledKnowledgeRepository` is the
one the package ships; a custom repository can wrap it and override what
it changes.  The port also returns ``ContractSummary`` and ``TaxSector``
(:mod:`ccnl_engine.catalog`), ``CapabilityCatalog`` and ``ModelLimitation``
(:mod:`ccnl_engine.results`).  Below the facade every service receives
the repository it is given: none falls back to the bundled data.
"""

from __future__ import annotations

from ccnl_engine.absence.insured.models import InsuredAbsenceRates
from ccnl_engine.agreement.facade import CCNL
from ccnl_engine.family.models import FamilyDeductionRules
from ccnl_engine.pay_item.policies import PolicyResolver
from ccnl_engine.period.ports import KnowledgeRepository
from ccnl_engine.period.repositories import BundledKnowledgeRepository
from ccnl_engine.period.services import bundled_policies
from ccnl_engine.sector.models import YearRules
from ccnl_engine.sickness.indemnity.models import InpsSickPayRates
from ccnl_engine.surtax.models import SurtaxRules
from ccnl_engine.variable_pay.models import VariablePayRules

__all__ = [
    "CCNL",
    "BundledKnowledgeRepository",
    "FamilyDeductionRules",
    "InpsSickPayRates",
    "InsuredAbsenceRates",
    "KnowledgeRepository",
    "PolicyResolver",
    "SurtaxRules",
    "VariablePayRules",
    "YearRules",
    "bundled_policies",
]
