"""Sickness episodes paid by the runs of the months they touch.

Metalmeccanico C3 operaio (INPS sector industria, so INPS covers the
worker): 2158.26 EUR a month, daily quota by 26 = 83.01 EUR, CCNL
integration and carenza at 100%, comporto 180 days.  INPS: carenza days
1-3, 50% on days 4-20, 66.66% on days 21-180.  Every amount below is
computed by hand from those rules, amounts rounded half up to the cent.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.contract.domain.category import WorkerCategory
from ccnl_engine.contract.service.loaders import load_ccnl
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.employer import EmployerProfile, Headcount
from ccnl_engine.payroll.domain.employment_facts import EmploymentPeriod
from ccnl_engine.payroll.domain.events import SickLeaveEvent
from ccnl_engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.payroll.domain.period_request import PeriodCalculationRequest
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun, RunKind
from ccnl_engine.payroll.service.bundled_knowledge_repository import (
    BundledKnowledgeRepository,
)
from ccnl_engine.provenance.domain.chain import ProvenanceStatus, RuleProvenance
from ccnl_engine.shared.domain.errors import InvalidInputError
from tests.fixtures.seniority import new_hire
from tests.fixtures.sickness_episode import sickness_episode

if TYPE_CHECKING:
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.payroll.domain.decisions import CalculationDecision
    from ccnl_engine.payroll.domain.period import PeriodResult
    from ccnl_engine.tax.domain.sick_pay import InpsSickPayRates

_FEB_TO_MAR = sickness_episode("2026-02-20", date(2026, 2, 20), date(2026, 3, 13))
_MARCH = sickness_episode("2026-03-09", date(2026, 3, 9), date(2026, 3, 13))


def _req(
    month: int,
    *events: object,
    opening: PeriodState | None = None,
    slug: str = "metalmeccanico-federmeccanica.json",
    level: str = "C3",
    category: WorkerCategory | None = WorkerCategory.OPERAIO,
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(50)),
        period_id=PeriodId(year=2026, month=month),
        payment_date=date(2026, month, 27),
        ccnl_slug=slug,
        level_code=level,
        seniority=new_hire(),
        opening_state=opening or PeriodState.zero(),
        events=events,  # type: ignore[arg-type]
        category=category,
    )


def _sick(result: PeriodResult) -> dict[str, Decimal]:
    return {
        item.item_id.rsplit("_", 1)[1]: item.amount
        for item in result.pay_items
        if "_evt" in item.item_id
    }


def _decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = (d for d in result.decisions if d.capability == "sickness")
    return decision


class TestMultiPeriodEpisode:
    """One episode from Friday 20 February to Friday 13 March 2026."""

    def test_february_pays_carenza_and_the_first_band(self) -> None:
        """20-22 Feb carenza (2 payable days), 23-28 Feb INPS 50% (6 days).

        Carenza 2158.26 * 2 / 26 = 166.02; band 2158.26 * 6 / 26 = 498.06,
        INPS 249.03 and employer 249.03; deduction 664.08.
        """
        result = calculate_period(_req(2, _FEB_TO_MAR))
        assert _sick(result) == {
            "abs": Decimal("664.08"),
            "inps": Decimal("249.03"),
            "intg": Decimal("249.03"),
            "crnz": Decimal("166.02"),
        }
        assert result.closing_state.accrual.sickness_episodes == (
            _FEB_TO_MAR.through(date(2026, 2, 28)),
        )

    def test_march_continues_the_day_count(self) -> None:
        """1-11 Mar are days 10-20 (9 payable), 12-13 Mar days 21-22.

        9 days: 747.09, INPS 373.545 -> 373.55, employer 373.54; 2 days:
        166.02, INPS 166.02 * 0.6666 = 110.67, employer 55.35.
        """
        february = calculate_period(_req(2, _FEB_TO_MAR))
        march = calculate_period(_req(3, _FEB_TO_MAR, opening=february.closing_state))
        assert _sick(march) == {
            "abs": Decimal("913.11"),
            "inps": Decimal("484.22"),
            "intg": Decimal("428.89"),
        }
        decision = _decision(march)
        assert decision.reason_code == "sickness_episode_paid"
        assert decision.amount == Decimal("913.11")
        assert "sickness_inps_daily_base" in {lim.id for lim in march.limitations}

    def test_inps_indemnity_stays_out_of_the_contribution_base(self) -> None:
        """The INPS base is the monthly pay less the INPS share."""
        result = calculate_period(_req(2, _FEB_TO_MAR))
        assert result.closing_state.accrual.inps_base(2026).own == (
            Decimal("2158.26") - Decimal("249.03")
        )


class TestHireMonth:
    """Hired on Wednesday 4 March 2026: 24 of 26 payable days."""

    def test_sick_days_use_the_same_quota_as_the_hire(self) -> None:
        """9-11 Mar carenza 249.03; 12-13 Mar 166.02, INPS 83.01 + 83.01."""
        request = replace(
            _req(3, _MARCH),
            employment_period=EmploymentPeriod(started_on=date(2026, 3, 4)),
        )
        result = calculate_period(request)
        assert _sick(result) == {
            "abs": Decimal("415.05"),
            "inps": Decimal("83.01"),
            "intg": Decimal("83.01"),
            "crnz": Decimal("249.03"),
        }
        base = sum(
            i.amount for i in result.pay_items if i.kind == "base_salary_earning"
        )
        assert base == Decimal("1992.24")

    def test_days_before_the_hire_are_rejected(self) -> None:
        """An episode before the first employed day cannot be paid."""
        request = replace(
            _req(3, _MARCH),
            employment_period=EmploymentPeriod(started_on=date(2026, 3, 16)),
        )
        with pytest.raises(InvalidInputError, match="within the employment"):
            calculate_period(request)


class TestRejectedRuns:
    """Only the run that posts the monthly pay pays sick days."""

    def test_adjustment_run_rejects_an_episode(self) -> None:
        """An adjustment run posts no monthly pay."""
        run = PayrollRun(run_kind=RunKind.ADJUSTMENT, month=3, year=2026)
        with pytest.raises(InvalidInputError, match="posts the monthly pay"):
            calculate_period(replace(_req(3, _MARCH), run=run))

    def test_episode_passed_twice_is_rejected(self) -> None:
        """The same episode twice in one run would pay its days twice."""
        with pytest.raises(InvalidInputError, match="already paid through"):
            calculate_period(_req(3, _MARCH, _MARCH))

    def test_episode_outside_the_period_is_rejected(self) -> None:
        """An April episode does not touch March."""
        april = sickness_episode("a", date(2026, 4, 1), date(2026, 4, 3))
        with pytest.raises(InvalidInputError, match="does not touch period"):
            calculate_period(_req(3, april))


class TestMissingRulesAndFacts:
    """A missing rule posts nothing; a missing fact is provisional."""

    def test_ccnl_without_sickness_rule_is_incomplete(self) -> None:
        """Tabacco APTI defines no sickness rule."""
        result = calculate_period(
            _req(3, _MARCH, slug="tabacco-apti.json", level="2", category=None)
        )
        assert _sick(result) == {}
        decision = _decision(result)
        assert decision.reason_code == "sickness_rule_missing"
        assert decision.amount is None

    def test_ccnl_without_daily_quota_is_incomplete(self) -> None:
        """Without the absence rule there is no daily quota."""

        class _NoAbsence(BundledKnowledgeRepository):
            def load_ccnl(self, filename: str) -> CCNL:
                ccnl = load_ccnl(filename)
                assert ccnl.work_rules is not None
                rules = ccnl.work_rules.model_copy(update={"absence_rules": None})
                return ccnl.model_copy(update={"work_rules": rules})

        result = calculate_period(_req(3, _MARCH), repo=_NoAbsence())
        assert _decision(result).reason_code == "sickness_daily_quota_missing"
        assert _sick(result) == {}

    def test_unknown_category_names_the_fact(self) -> None:
        """C3 does not fix the category: INPS cover is unknown."""
        result = calculate_period(_req(3, _MARCH, category=None))
        issue = next(
            i for i in result.issues if i.code == "sickness_inps_cover_unknown"
        )
        assert issue.fact == "category"
        assert _sick(result)["intg"] == Decimal("166.02")

    def test_days_past_the_comporto_are_left_out(self) -> None:
        """From 1 January, every July day is past the 180-day comporto."""
        long = sickness_episode("a", date(2026, 1, 1), date(2026, 7, 31))
        result = calculate_period(_req(7, long))
        assert _decision(result).reason_code == "sickness_beyond_comporto"
        assert _sick(result) == {}


def test_hourly_quota_counts_hours() -> None:
    """Dirigenza sanitaria: by_hourly, 7.6 hours a day.

    Carenza 9-11 March: 3 * 7.6 = 22.8 hours; 12-13 March: 15.2 hours.
    """
    result = calculate_period(
        _req(
            3,
            _MARCH,
            slug="dirigenza-sanitaria-medico-veterinaria-aran.json",
            level="DIRIGENTE",
            category=None,
        )
    )
    inputs = _decision(result).inputs
    assert inputs["divisor_method"] == "by_hourly"
    assert inputs["inps_cover"] == "false"
    segments = str(inputs["segments"])
    assert "carenza:index=1:units=22.8:" in segments
    assert "indemnified:index=4:units=15.2:" in segments


def test_hourly_quota_without_daily_hours_is_missing() -> None:
    """A by_hourly rule without the hours of a day sets no quota."""

    class _NoHours(BundledKnowledgeRepository):
        def load_ccnl(self, filename: str) -> CCNL:
            ccnl = load_ccnl(filename)
            assert ccnl.work_rules is not None
            assert ccnl.work_rules.absence_rules is not None
            absence = ccnl.work_rules.absence_rules.model_copy(
                update={"daily_hours": None}
            )
            rules = ccnl.work_rules.model_copy(update={"absence_rules": absence})
            return ccnl.model_copy(update={"work_rules": rules})

    request = _req(
        3,
        _MARCH,
        slug="dirigenza-sanitaria-medico-veterinaria-aran.json",
        level="DIRIGENTE",
        category=None,
    )
    result = calculate_period(request, repo=_NoHours())
    assert _decision(result).reason_code == "sickness_daily_quota_missing"


def test_earlier_episode_outside_the_chain_is_a_limitation() -> None:
    """A March relapse chain after an unrelated January episode."""
    january = sickness_episode("j", date(2026, 1, 12), date(2026, 1, 14))
    february = sickness_episode("f", date(2026, 2, 2), date(2026, 2, 4))
    state = replace(
        PeriodState.zero(),
        accrual=replace(
            PeriodState.zero().accrual, sickness_episodes=(january, february)
        ),
    )
    relapse = sickness_episode("m", date(2026, 3, 2), date(2026, 3, 3), "f")
    result = calculate_period(_req(3, relapse, opening=state))
    assert "sickness_cumulation_window" in {lim.id for lim in result.limitations}


def test_sick_pay_override_is_not_payable() -> None:
    """An amount the caller computed overrides the engine and blocks."""
    override = SickLeaveEvent(date(2026, 3, 9), Decimal("100.00"))
    result = calculate_period(_req(3, override))
    assert (BlockerCode.CALLER_SUPPLIED_RULE, "sickness") in {
        (b.code, b.feature) for b in result.blockers
    }
    assert not result.is_payable


def test_indemnity_bands_report_their_provenance() -> None:
    """The INPS bands record reaches the evidence of the sickness capability."""

    class _AssumedBands(BundledKnowledgeRepository):
        def load_sick_pay_rates(self) -> InpsSickPayRates:
            rates = super().load_sick_pay_rates()
            record = RuleProvenance(status=ProvenanceStatus.ASSUMED)
            return rates.model_copy(update={"bands_provenance": record})

    bundled = calculate_period(_req(3, _MARCH))
    result = calculate_period(_req(3, _MARCH), repo=_AssumedBands())
    sources = result.capability_report.rule_sources
    assert (
        bundled.capability_report.rule_sources["sickness"] is ProvenanceStatus.DERIVED
    )
    assert sources["sickness"] is ProvenanceStatus.ASSUMED
