"""Revaluation of the TFR fund at 31 December, through the period calculation.

Art. 2120 c. 4 c.c. (Normattiva, in force from 11-4-1991,
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262~art2120)
revalues the TFR, "con esclusione della quota maturata nell'anno", at 31
December by 1.5% plus 75% of the yearly increase of the ISTAT FOI index;
c. 5 revalues a fraction of the year at termination.  D.Lgs. 47/2000 art.
11 cc. 3-4 (text in force until 31-12-2026) taxes the revaluation at 17%
and charges the tax to the fund.  ISTAT has not published the December
2026 index: the final branch runs on rules patched with a hypothetical one.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine.contract.domain.identity import TaxSector
from ccnl_engine.inputs import TfrFundBalance
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.tax.domain.ruleset import YearRules
    from ccnl_engine.tax.domain.tfr_revaluation import TfrRevaluationRules

_FUND = TfrFundBalance(2025, Decimal("10000.00"))
_HIRED_2020 = EmploymentPeriod(date(2020, 1, 1))
_BUNDLED = BundledKnowledgeRepository()


class _Repository(BundledKnowledgeRepository):
    """Bundled rules with the revaluation of the year replaced."""

    def __init__(self, revaluation: TfrRevaluationRules | None) -> None:
        self._revaluation = revaluation

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        rules = super().load_year_rules(year, sector, num_employees)
        return rules.model_copy(update={"tfr_revaluation": self._revaluation})


def _bundled_rules() -> TfrRevaluationRules:
    rules = _BUNDLED.load_year_rules(2026, TaxSector.INDUSTRIA, 50).tfr_revaluation
    assert rules is not None
    return rules


def _with_december(december: str, **update: object) -> _Repository:
    """Return the bundled 2026 rules with a hypothetical December index.

    Returns:
        A repository serving them, with ``update`` applied to the rules.
    """
    rules = _bundled_rules()
    index = rules.price_index.model_copy(update={"december": Decimal(december)})
    return _Repository(rules.model_copy(update={"price_index": index, **update}))


def _run(
    month: int = 12,
    *,
    repo: BundledKnowledgeRepository = _BUNDLED,
    kind: RunKind = RunKind.REGULAR,
    **kwargs: object,
) -> PeriodResult:
    kwargs.setdefault("employment_period", _HIRED_2020)
    return calculate_period(
        PeriodCalculationRequest(
            period_id=PeriodId(year=2026, month=month),
            payment_date=date(2026, month, 27),
            ccnl_slug="metalmeccanico-federmeccanica.json",
            level_code="C3",
            employer=EmployerProfile(headcount=Headcount(50)),
            seniority=new_hire(),
            tfr_treasury_fund=False,
            run=PayrollRun(run_kind=kind, month=month, year=2026),
            **kwargs,  # type: ignore[arg-type]
        ),
        repo=repo,
    )


def _decisions(result: PeriodResult) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.capability == "tfr_revaluation"]


def _decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = _decisions(result)
    return decision


def _codes(result: PeriodResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_a_month_before_december_does_not_revalue() -> None:
    """The fund is revalued at 31 December only."""
    assert _decisions(_run(3, tfr_fund=_FUND)) == []


def test_revalued_fund_with_a_december_index() -> None:
    """10,000.00 revalued with a hypothetical December 2026 index of 103.7.

    Increase: 103.7 x 1.214 / 121.5 - 1 = 125.8918 / 121.5 - 1 =
    0.03614650206; rate: 0.015 + 0.75 x 0.03614650206 = 0.04210987654;
    revaluation: 10,000.00 x 0.04210987654 = 421.0987654 -> 421.10;
    substitute tax: 17% x 421.10 = 71.587 -> 71.59; net to the fund:
    421.10 - 71.59 = 349.51.
    """
    result = _run(repo=_with_december("103.7"), tfr_fund=_FUND)
    decision = _decision(result)
    assert decision.status is CalculationStatus.FINAL
    assert decision.reason_code == "revalued"
    assert decision.amount == Decimal("421.10")
    assert decision.inputs["substitute_tax"] == Decimal("71.59")
    assert decision.inputs["net_revaluation"] == Decimal("349.51")
    assert decision.rule == "tax/2026/tfr-revaluation:rate"
    assert decision.source is not None
    assert "tax/2026/tfr-revaluation" in {r.identity.id for r in result.rulesets}
    assert "tfr_revaluation" not in {e.pay_item_kind for e in result.ledger_entries}


def test_revaluation_does_not_change_the_pay_of_the_run() -> None:
    """The fund grows; net pay and employer cost of December do not."""
    revalued = _run(repo=_with_december("103.7"), tfr_fund=_FUND)
    empty = _run(tfr_fund=TfrFundBalance(2025, Decimal("0.00")))
    assert revalued.period_net == empty.period_net
    assert revalued.period_employer_cost == empty.period_employer_cost


def test_unpublished_december_index_is_not_computed() -> None:
    """The bundle has no December 2026 index: incomplete, never final."""
    result = _run(tfr_fund=_FUND)
    decision = _decision(result)
    assert decision.status is CalculationStatus.INCOMPLETE
    assert decision.reason_code == "price_index_not_published"
    assert decision.amount is None
    assert decision.inputs["fund"] == Decimal("10000.00")
    assert not result.is_payable


@pytest.mark.parametrize(
    "repo",
    [_Repository(None), _with_december("103.7", year=2025)],
    ids=["no_rules", "rules_of_another_year"],
)
def test_rules_missing_for_the_year_are_not_computed(
    repo: BundledKnowledgeRepository,
) -> None:
    """Without the rules of the year the rate is unknown."""
    decision = _decision(_run(repo=repo, tfr_fund=_FUND))
    assert decision.reason_code == "price_index_not_published"
    assert decision.rule == "tax/2026/tfr-revaluation:rate"


def test_rules_without_identity_name_the_year() -> None:
    """A table without its ruleset block names the rule after the year."""
    decision = _decision(
        _run(repo=_with_december("103.7", ruleset=None), tfr_fund=_FUND)
    )
    assert decision.rule == "tax/2026/tfr-revaluation:rate"
    assert decision.rule_version == "2026"


def test_negative_rate_is_not_computed() -> None:
    """95 x 1.214 / 121.5 - 1 = -0.0508; 0.015 + 0.75 x -0.0508 < 0."""
    decision = _decision(_run(repo=_with_december("95"), tfr_fund=_FUND))
    assert decision.reason_code == "negative_rate"
    assert decision.status is CalculationStatus.INCOMPLETE
    assert Decimal(str(decision.inputs["rate"])) < 0


def test_hire_in_the_year_has_nothing_to_revalue() -> None:
    """Employed from 2026: no fund at 31 December 2025, no fact needed."""
    result = _run(employment_period=EmploymentPeriod(date(2026, 1, 1)))
    decision = _decision(result)
    assert decision.status is CalculationStatus.FINAL
    assert decision.reason_code == "no_opening_fund"
    assert decision.amount == Decimal(0)
    assert decision.inputs["fund"] == Decimal("0.00")
    assert "tfr_fund_unknown" not in _codes(result)
    assert "tfr_revaluation" not in {g.feature for g in result.capability_report.gaps}
    assert "tfr_revaluation" not in result.capability_report.rule_sources


def test_empty_fund_has_nothing_to_revalue() -> None:
    """A stated zero balance is revalued to zero, final."""
    decision = _decision(_run(tfr_fund=TfrFundBalance(2025, Decimal("0.00"))))
    assert (decision.reason_code, decision.amount) == ("no_opening_fund", Decimal(0))


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    [
        ({}, "required_fact_missing"),
        ({"employment_period": None}, "required_fact_missing"),
        (
            {"tfr_fund": TfrFundBalance(2024, Decimal("10000.00"))},
            "fund_of_another_year",
        ),
    ],
    ids=["hired_before_the_year", "employment_not_tracked", "fund_of_2024"],
)
def test_fund_of_the_year_not_stated_is_a_missing_fact(
    kwargs: dict[str, Any], reason: str
) -> None:
    """The fund at 31 December 2025 is required: a missing_fact blocker."""
    result = _run(**kwargs)
    decision = _decision(result)
    assert (decision.status, decision.reason_code) == (
        CalculationStatus.INCOMPLETE,
        reason,
    )
    assert "tfr_fund_unknown" in _codes(result)
    assert ("missing_fact", "tfr_fund") in {
        (b.code.value, b.detail) for b in result.blockers
    }


@pytest.mark.parametrize(
    ("month", "kind", "ended_on"),
    [
        (5, RunKind.REGULAR, date(2026, 5, 20)),
        (5, RunKind.TERMINATION, date(2026, 5, 20)),
        (12, RunKind.REGULAR, date(2026, 12, 15)),
        (5, RunKind.TERMINATION, None),
    ],
    ids=["regular_last_month", "termination_run", "ends_mid_december", "no_end"],
)
def test_termination_before_year_end_is_not_computed(
    month: int, kind: RunKind, ended_on: date | None
) -> None:
    """The revaluation of a fraction of the year (c. 5) is not computed."""
    period = EmploymentPeriod(date(2020, 1, 1), ended_on)
    decision = _decision(
        _run(month, kind=kind, employment_period=period, tfr_fund=_FUND)
    )
    assert decision.inputs["moment"] == "termination"
    assert decision.reason_code == "termination_not_computed"
    assert decision.status is CalculationStatus.INCOMPLETE


def test_employment_ending_on_31_december_is_revalued_once() -> None:
    """The December run revalues the year; the termination run does not."""
    period = EmploymentPeriod(date(2020, 1, 1), date(2026, 12, 31))
    repo = _with_december("103.7")
    regular = _run(repo=repo, employment_period=period, tfr_fund=_FUND)
    termination = _run(
        repo=repo, kind=RunKind.TERMINATION, employment_period=period, tfr_fund=_FUND
    )
    assert _decision(regular).inputs["moment"] == "year_end"
    assert _decision(regular).amount == Decimal("421.10")
    assert _decisions(termination) == []


def test_not_computed_revaluation_is_unresolved() -> None:
    """An incomplete decision traces the capability unresolved."""
    result = _run(tfr_fund=_FUND)
    gaps = {gap.feature: gap.kind.value for gap in result.capability_report.gaps}
    assert gaps["tfr_revaluation"] == "unresolved"
