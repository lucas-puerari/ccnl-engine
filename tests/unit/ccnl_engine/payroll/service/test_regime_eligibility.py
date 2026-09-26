"""Unit tests for preferential regime eligibility and the amount split."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.tax.domain.preferential_regime import (
    EmployerActivity,
    EmploymentSector,
    PreferentialTaxRegime,
)
from ccnl_engine.engine.tax.service.tax_optional_loaders import (
    load_variable_pay_rules,
)
from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.service.regime_eligibility import (
    RegimeEligibility,
    RegimeFacts,
    assess_regime,
)

_RULES = load_variable_pay_rules(2026)
_RINNOVO = _RULES.rinnovo
_WORK_TIME = _RULES.notte_festivi_turni
_SIGNED = date(2025, 3, 1)
_PRIVATE = EmploymentSector.PRIVATE
_PUBLIC = EmploymentSector.PUBLIC
_AMOUNT = Decimal(2_000)
_ELIGIBLE = RegimeEligibility.ELIGIBLE
_INELIGIBLE = RegimeEligibility.INELIGIBLE
_UNKNOWN = RegimeEligibility.UNKNOWN


def _regime(**update: object) -> PreferentialTaxRegime:
    return _RINNOVO.model_copy(update=update)


def _facts(
    prior_income: Decimal | None = Decimal(20_000),
    sector: EmploymentSector | None = _PRIVATE,
    waived: bool = False,
    signed_on: date | None = _SIGNED,
    activity: EmployerActivity | None = EmployerActivity.OTHER,
) -> RegimeFacts:
    return RegimeFacts(
        prior_income=prior_income,
        sector=sector,
        activity=activity,
        waived_regimes=frozenset({"rinnovo", "notte_festivi_turni"} if waived else ()),
        agreement_signed_on=signed_on,
    )


class TestAssessRegime:
    """Eligibility outcome, reason and split of the amount."""

    @pytest.mark.parametrize(
        ("facts", "eligibility", "reason"),
        [
            (_facts(), _ELIGIBLE, "requirements_met"),
            (_facts(Decimal(33_000)), _ELIGIBLE, "requirements_met"),
            (
                _facts(Decimal("33000.01")),
                _INELIGIBLE,
                "prior_income_above_ceiling",
            ),
            (_facts(sector=_PUBLIC), _INELIGIBLE, "sector_not_eligible"),
            (_facts(waived=True), _INELIGIBLE, "waived_by_worker"),
            (_facts(None), _UNKNOWN, "prior_income_unknown"),
            (_facts(sector=None), _UNKNOWN, "sector_unknown"),
            (_facts(None, sector=_PUBLIC), _INELIGIBLE, "sector_not_eligible"),
            (
                _facts(Decimal(100_000), sector=None),
                _INELIGIBLE,
                "prior_income_above_ceiling",
            ),
        ],
    )
    def test_eligibility_and_reason(
        self, facts: RegimeFacts, eligibility: RegimeEligibility, reason: str
    ) -> None:
        """Definite ineligibility wins over a missing fact; 33,000 is eligible."""
        assessment = assess_regime(_RINNOVO, facts, _AMOUNT, 2026)

        assert (assessment.eligibility, assessment.reason_code) == (
            eligibility,
            reason,
        )

    def test_eligible_amount_is_wholly_substitute(self) -> None:
        """Without a cap the whole eligible amount takes the substitute rate."""
        assessment = assess_regime(_RINNOVO, _facts(), _AMOUNT, 2026)

        assert (assessment.eligible_amount, assessment.ordinary_amount) == (
            _AMOUNT,
            Decimal(0),
        )

    @pytest.mark.parametrize(
        "facts", [_facts(Decimal(100_000)), _facts(None)], ids=["no", "unknown"]
    )
    def test_not_eligible_amount_is_wholly_ordinary(self, facts: RegimeFacts) -> None:
        """Ineligible and unknown amounts stay wholly ordinary."""
        assessment = assess_regime(_RINNOVO, facts, _AMOUNT, 2026)

        assert (assessment.eligible_amount, assessment.ordinary_amount) == (
            Decimal(0),
            _AMOUNT,
        )

    def test_outside_validity_years_is_ineligible(self) -> None:
        """A payment outside the validity years is ineligible."""
        assessment = assess_regime(_RINNOVO, _facts(), _AMOUNT, 2027)

        assert assessment.reason_code == "regime_not_in_force"

    def test_waiver_ignored_when_regime_is_not_waivable(self) -> None:
        """A waiver has no effect on a regime that cannot be renounced."""
        regime = _regime(waivable=False)

        assessment = assess_regime(regime, _facts(waived=True), _AMOUNT, 2026)

        assert assessment.eligibility is _ELIGIBLE

    def test_regime_without_requirements_is_eligible_on_unknown_facts(self) -> None:
        """Facts the regime does not require cannot make it unknown."""
        regime = _regime(
            required_sector=None,
            income_ceiling=None,
            income_reference_year=None,
            agreements_signed_from=None,
            agreements_signed_until=None,
        )
        facts = _facts(None, sector=None, signed_on=None, activity=None)

        assessment = assess_regime(regime, facts, _AMOUNT, 2026)

        assert assessment.eligibility is _ELIGIBLE

    @pytest.mark.parametrize(
        ("available", "eligible"),
        [
            (None, Decimal(1_500)),
            (Decimal(400), Decimal(400)),
            (Decimal(-1), Decimal(0)),
            (Decimal(5_000), _AMOUNT),
        ],
    )
    def test_annual_cap_splits_the_excess_to_ordinary(
        self, available: Decimal | None, eligible: Decimal
    ) -> None:
        """Only the amount within the available cap takes the substitute rate."""
        regime = _regime(annual_cap=Decimal(1_500))

        assessment = assess_regime(regime, _facts(), _AMOUNT, 2026, available)

        assert assessment.eligible_amount == eligible
        assert assessment.ordinary_amount == _AMOUNT - eligible


class TestAssessmentRecords:
    """Calculation decision and issue built from an assessment."""

    def test_eligible_decision_is_final_with_inputs(self) -> None:
        """An eligible decision is final and records its normalized inputs."""
        assessment = assess_regime(_RINNOVO, _facts(), _AMOUNT, 2026)

        decision = assessment.decision(Decimal("100.00"))

        assert decision.capability == "rinnovo_substitute_tax"
        assert decision.status is CalculationStatus.FINAL
        assert decision.reason_code == "requirements_met"
        assert decision.rule == "tax/variable-pay-rules/2026"
        assert decision.amount == Decimal("100.00")
        assert decision.source == _RINNOVO.source
        assert decision.inputs["prior_income"] == Decimal(20_000)
        assert decision.inputs["sector"] == "private"
        assert decision.inputs["waived"] == "false"
        assert assessment.issue() is None

    def test_unknown_decision_is_provisional_with_issue(self) -> None:
        """An unknown eligibility is provisional and raises an issue."""
        assessment = assess_regime(_RINNOVO, _facts(None, sector=None), _AMOUNT, 2026)

        decision = assessment.decision(Decimal(0))
        issue = assessment.issue()

        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.inputs["prior_income"] == "unknown"
        assert decision.inputs["sector"] == "unknown"
        assert issue is not None
        assert issue.code == "rinnovo_eligibility_unknown"
        assert issue.status is CalculationStatus.PROVISIONAL

    def test_decision_without_ruleset_uses_regime_and_year(self) -> None:
        """Without provenance the rule is the regime id at the tax year."""
        assessment = assess_regime(_regime(ruleset=None), _facts(), _AMOUNT, 2026)

        decision = assessment.decision(Decimal("100.00"))

        assert (decision.rule, decision.rule_version) == ("rinnovo", "2026")


class TestSigningWindow:
    """A renewal qualifies only when signed within the window of the regime."""

    @pytest.mark.parametrize(
        ("signed_on", "eligibility", "reason"),
        [
            (date(2024, 1, 1), _ELIGIBLE, "requirements_met"),
            (date(2026, 12, 31), _ELIGIBLE, "requirements_met"),
            (date(2023, 12, 31), _INELIGIBLE, "agreement_signed_outside_window"),
            (date(2027, 1, 1), _INELIGIBLE, "agreement_signed_outside_window"),
            (None, _UNKNOWN, "agreement_signing_date_unknown"),
        ],
    )
    def test_signing_date_against_window(
        self, signed_on: date | None, eligibility: RegimeEligibility, reason: str
    ) -> None:
        """Bounds are included; an unknown date makes the renewal unknown."""
        assessment = assess_regime(_RINNOVO, _facts(signed_on=signed_on), _AMOUNT, 2026)

        assert (assessment.eligibility, assessment.reason_code) == (
            eligibility,
            reason,
        )

    def test_signing_date_recorded_on_decision(self) -> None:
        """The decision records the signing date, or unknown."""
        known = assess_regime(_RINNOVO, _facts(), _AMOUNT, 2026)
        unknown = assess_regime(_RINNOVO, _facts(signed_on=None), _AMOUNT, 2026)

        assert known.decision(Decimal(0)).inputs["agreement_signed_on"] == (
            "2025-03-01"
        )
        assert unknown.decision(Decimal(0)).inputs["agreement_signed_on"] == ("unknown")

    def test_regime_without_window_ignores_the_date(self) -> None:
        """The work-time regime has no signing window."""
        assessment = assess_regime(
            _WORK_TIME, _facts(signed_on=None), _AMOUNT, 2026, Decimal(1_500)
        )

        assert assessment.eligibility is _ELIGIBLE
        assert "agreement_signed_on" not in assessment.decision(Decimal(0)).inputs


class TestEmployerActivity:
    """L. 199/2025 art. 1 c. 11 excludes the activities of c. 18."""

    @pytest.mark.parametrize(
        ("activity", "eligibility", "reason"),
        [
            (EmployerActivity.OTHER, _ELIGIBLE, "requirements_met"),
            (
                EmployerActivity.FOOD_AND_BEVERAGE_SERVICE,
                _INELIGIBLE,
                "employer_activity_excluded",
            ),
            (EmployerActivity.TOURISM, _INELIGIBLE, "employer_activity_excluded"),
            (
                EmployerActivity.THERMAL_ESTABLISHMENT,
                _INELIGIBLE,
                "employer_activity_excluded",
            ),
            (None, _UNKNOWN, "activity_unknown"),
        ],
    )
    def test_activity_against_exclusion(
        self,
        activity: EmployerActivity | None,
        eligibility: RegimeEligibility,
        reason: str,
    ) -> None:
        """An excluded activity is ineligible, an unknown one unknown."""
        assessment = assess_regime(
            _WORK_TIME, _facts(activity=activity), _AMOUNT, 2026, Decimal(1_500)
        )

        assert (assessment.eligibility, assessment.reason_code) == (
            eligibility,
            reason,
        )

    def test_activity_recorded_on_decision(self) -> None:
        """The decision records the activity, or unknown."""
        known = assess_regime(_WORK_TIME, _facts(), _AMOUNT, 2026)
        unknown = assess_regime(_WORK_TIME, _facts(activity=None), _AMOUNT, 2026)

        assert known.decision(Decimal(0)).inputs["employer_activity"] == "other"
        assert unknown.decision(Decimal(0)).inputs["employer_activity"] == "unknown"

    def test_renewal_regime_has_no_activity_exclusion(self) -> None:
        """An unknown activity does not affect the renewal regime."""
        assessment = assess_regime(_RINNOVO, _facts(activity=None), _AMOUNT, 2026)

        assert assessment.eligibility is _ELIGIBLE
        assert "employer_activity" not in assessment.decision(Decimal(0)).inputs
