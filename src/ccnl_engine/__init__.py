"""ccnl_engine: Italian CCNL payroll computation library.

Public API
----------
The single entry point is :class:`PayrollEngine`.  Construct it with
:meth:`~PayrollEngine.bundled` and call
:meth:`~PayrollEngine.calculate_period` for one cedolino,
:meth:`~PayrollEngine.calculate_competence_year` for every run of a
competence year, :meth:`~PayrollEngine.calculate_tax_year` for every
payment cashed in a tax year and :meth:`~PayrollEngine.close_tax_year` to
open the next tax year.

The root holds the common path: the facade, the request and plan types and
what they need, the results the facade returns, every public error and
:data:`engine_version`.  Every other public name lives in exactly one of four
namespaces:

- :mod:`ccnl_engine.inputs`: facts beyond the common path (contract types,
  hours, seniority, family, tax facts, calendar, opening state and balances);
- :mod:`ccnl_engine.events`: work events of a period;
- :mod:`ccnl_engine.results`: assurance, blockers, decisions, limitations,
  capability gaps and remittance lines;
- :mod:`ccnl_engine.catalog`: bundled contracts, ruleset readiness and the
  capability catalog.

Usage::

    from datetime import date
    from ccnl_engine import (
        Employment, EmployerProfile, Headcount, PayrollEngine, PayrollRun,
        PeriodInput,
    )

    engine = PayrollEngine.bundled()
    result = engine.calculate_period(PeriodInput(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        employment=Employment(
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
        ),
        employer=EmployerProfile(headcount=Headcount(50)),
    ))
    print(result.is_payable, result.period_net)
    for blocker in result.blockers:
        print(blocker.code, blocker.feature, blocker.detail)

``PayrollEngine.bundled(mode="operational")`` also blocks payment from any
ruleset that is not ``production``; :meth:`~PayrollEngine.list_contracts` and
:meth:`~PayrollEngine.inspect_ruleset` report readiness before any run.
"""

from __future__ import annotations

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.payroll.application.year_result import (
    CompetenceYearResult,
    TaxYearResult,
)
from ccnl_engine.payroll.domain.competence_year_plan import CompetenceYearPlan
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment import Employment
from ccnl_engine.payroll.domain.inputs import PeriodFacts, PeriodInput
from ccnl_engine.payroll.domain.period import PeriodResult
from ccnl_engine.payroll.domain.run import PayrollRun
from ccnl_engine.payroll.domain.tax_year_plan import TaxYearPlan
from ccnl_engine.shared.domain.errors import (
    CcnlEngineError,
    DataIntegrityError,
    InvalidInputError,
    MissingRequiredFactError,
    MissingRuleError,
    OutOfScopeError,
    UnknownCcnlError,
    UnknownLevelError,
    UnsupportedTaxYearError,
)
from ccnl_engine.version import __version__ as engine_version

__all__ = [
    "CcnlEngineError",
    "CompetenceYearPlan",
    "CompetenceYearResult",
    "DataIntegrityError",
    "EmployerProfile",
    "Employment",
    "Headcount",
    "InvalidInputError",
    "MissingRequiredFactError",
    "MissingRuleError",
    "OutOfScopeError",
    "PayrollEngine",
    "PayrollRun",
    "PeriodFacts",
    "PeriodInput",
    "PeriodResult",
    "TaxYearPlan",
    "TaxYearResult",
    "UnknownCcnlError",
    "UnknownLevelError",
    "UnsupportedTaxYearError",
    "engine_version",
]
