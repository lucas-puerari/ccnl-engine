"""Extra-month ratei counted with the CCNL accrual rule, or the default.

Hired on 16 June 2026, June has 15 employed days (16 to 30).  Under the
engine default (at least 15 days) June counts and the tredicesima accrues
7 months (June to December); under "more than 15 days" June does not count
and it accrues 6.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.contract.catalog.loaders import load_ccnl
from ccnl_engine.contract.compensation.models import (
    AccrualComparison,
    ExtraMonthAccrualRule,
)
from ccnl_engine.payroll.accrual.models import ExtraMonthAccrual
from ccnl_engine.payroll.accrual.models_extra_month_schedule import ExtraMonthKind
from ccnl_engine.payroll.accrual.services_decision import REASON_CODE
from ccnl_engine.payroll.accrual.services_extra_month import run_schedule
from ccnl_engine.payroll.accrual.services_rule import (
    MISSING_ACCRUAL_PROVENANCE,
    month_accrual_rule,
)
from ccnl_engine.payroll.assurance.models_decision import CalculationStatus
from ccnl_engine.payroll.assurance.services_rule_source import MISSING_SOURCE_CODE
from ccnl_engine.payroll.employment.inputs_employer import EmployerProfile, Headcount
from ccnl_engine.payroll.employment.inputs_fact import EmploymentPeriod
from ccnl_engine.payroll.period.models_payroll import PeriodId
from ccnl_engine.payroll.period.models_run import PayrollRun
from ccnl_engine.payroll.period.repositories import (
    BundledKnowledgeRepository,
)
from ccnl_engine.payroll.period.requests import PeriodCalculationRequest
from ccnl_engine.payroll.period.services import calculate_period
from ccnl_engine.payroll.year.models_calendar import WorkCalendar
from ccnl_engine.provenance.source.models import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.provenance.source.models_chain import ProvenanceStatus, RuleProvenance
from tests.fixtures.withholding import calendar_schedule

if TYPE_CHECKING:
    from ccnl_engine.contract.identity.facade import CCNL
    from ccnl_engine.payroll.period.results import PeriodResult

_YEAR = 2026
_SLUG = "commercio-confcommercio.json"
_HIRED = EmploymentPeriod(date(_YEAR, 6, 16))
_SOURCE = RuleProvenance(
    status=ProvenanceStatus.DERIVED,
    location=SourceLocation(
        source_document=SourceDocument(
            document_id="ccnl-test", title="CCNL test", kind=SourceKind.ASSOCIAZIONE
        ),
        section="Art. 1, Tredicesima mensilità",
    ),
)
_MORE_THAN = ExtraMonthAccrualRule(
    min_days=15, comparison=AccrualComparison.MORE_THAN, provenance=_SOURCE
)


def _with_rule(rule: ExtraMonthAccrualRule | None) -> CCNL:
    ccnl = load_ccnl(_SLUG)
    params = ccnl.parameters.model_copy(update={"accrual_rule": rule})
    return ccnl.model_copy(update={"parameters": params})


class _Repo(BundledKnowledgeRepository):
    """Bundled data with the accrual rule of the CCNL replaced."""

    def __init__(self, rule: ExtraMonthAccrualRule | None) -> None:
        self._ccnl = _with_rule(rule)

    def load_ccnl(self, filename: str) -> CCNL:
        """Return the CCNL with the replaced rule.

        Returns:
            The CCNL of the test.
        """
        assert filename == _SLUG
        return self._ccnl


def _tredicesima(
    rule: ExtraMonthAccrualRule | None, employment: EmploymentPeriod | None
) -> PeriodResult:
    calendar = WorkCalendar.from_additional_months(_YEAR, 14)
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=12),
        payment_date=date(_YEAR, 12, 18),
        ccnl_slug=_SLUG,
        level_code="4",
        run=PayrollRun.thirteenth(_YEAR, 12),
        employment_period=employment,
        withholding_schedule=calendar_schedule(calendar),
    )
    return calculate_period(request, repo=_Repo(rule))


def _ratei(result: PeriodResult) -> dict[str, object]:
    (decision,) = (d for d in result.decisions if d.reason_code == REASON_CODE)
    return dict(decision.inputs)


def test_ccnl_without_the_clause_uses_the_default_as_missing() -> None:
    """No clause: at least 15 days, rule id of the CCNL, provenance missing."""
    rule = month_accrual_rule(_with_rule(None))
    assert (rule.min_days, rule.comparison) == (15, AccrualComparison.AT_LEAST)
    assert rule.rule == "ccnl/commercio-confcommercio:parameters.accrual_rule"
    assert rule.provenance is MISSING_ACCRUAL_PROVENANCE


def test_ccnl_clause_sets_threshold_and_source() -> None:
    """A stored clause gives the threshold, comparison and its record."""
    rule = month_accrual_rule(_with_rule(_MORE_THAN))
    assert (rule.min_days, rule.comparison) == (15, AccrualComparison.MORE_THAN)
    assert rule.provenance is _SOURCE
    assert "Tredicesima" in rule.source


def test_default_counts_a_fifteen_day_month() -> None:
    """At least 15 days: June counts, 7 ratei, and the rule is unsourced."""
    result = _tredicesima(None, _HIRED)
    ratei = _ratei(result)
    assert (ratei["months"], ratei["partial_months"]) == ("7", "1")
    assert (ratei["comparison"], ratei["rule_origin"]) == ("at_least", "engine_default")
    codes = [i.code for i in result.issues]
    assert MISSING_SOURCE_CODE in codes
    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert result.is_payable is False


def test_more_than_fifteen_days_leaves_the_month_out() -> None:
    """More than 15 days: June does not count, 6 ratei, from the CCNL clause."""
    default = _tredicesima(None, _HIRED)
    result = _tredicesima(_MORE_THAN, _HIRED)
    ratei = _ratei(result)
    assert (ratei["months"], ratei["fraction"]) == ("6", Decimal(6) / 12)
    assert (ratei["comparison"], ratei["rule_origin"]) == ("more_than", "ccnl")
    assert MISSING_SOURCE_CODE not in [i.code for i in result.issues]
    assert result.period_gross < default.period_gross


def test_whole_months_do_not_read_the_threshold() -> None:
    """A full-year worker accrues 12 whole months: no unsourced rule is read."""
    result = _tredicesima(None, None)
    assert _ratei(result)["partial_months"] == "0"
    assert MISSING_SOURCE_CODE not in [i.code for i in result.issues]


def test_accrual_built_by_the_caller_is_reported_as_request() -> None:
    """An accrual passed on the request keeps the rule the caller built."""
    schedule = run_schedule(ExtraMonthKind.THIRTEENTH, 12, Decimal(1))
    accrual = ExtraMonthAccrual.of(schedule, _YEAR, _HIRED)
    calendar = WorkCalendar.from_additional_months(_YEAR, 14)
    request = PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=_YEAR, month=12),
        payment_date=date(_YEAR, 12, 18),
        ccnl_slug=_SLUG,
        level_code="4",
        run=PayrollRun.thirteenth(_YEAR, 12),
        extra_month_accrual=accrual,
        withholding_schedule=calendar_schedule(calendar),
    )
    result = calculate_period(request)
    assert _ratei(result)["rule_origin"] == "request"
    assert MISSING_SOURCE_CODE not in [i.code for i in result.issues]
