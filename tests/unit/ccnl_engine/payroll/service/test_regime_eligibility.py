"""Unit tests for preferential regime eligibility and the amount split."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.engine.contract.domain.identity import TaxSector
from ccnl_engine.engine.tax.domain.preferential_regime import (
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
    sector_of_tax_sector,
)

_RINNOVO = load_variable_pay_rules(2026).rinnovo
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
) -> RegimeFacts:
    return RegimeFacts(prior_income=prior_income, sector=sector, waived=waived)


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
            required_sector=None, income_ceiling=None, income_reference_year=None
        )

        assessment = assess_regime(regime, _facts(None, sector=None), _AMOUNT, 2026)

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


class TestSectorOfTaxSector:
    """Employment sector implied by the CCNL tax sector."""

    @pytest.mark.parametrize(
        ("tax_sector", "sector"),
        [
            (TaxSector.PUBBLICA_AMMINISTRAZIONE.value, _PUBLIC),
            (TaxSector.TERZIARIO.value, _PRIVATE),
            (None, None),
        ],
    )
    def test_maps_ccnl_tax_sector(
        self, tax_sector: str | None, sector: EmploymentSector | None
    ) -> None:
        """Public administration is public, other sectors private."""
        assert sector_of_tax_sector(tax_sector) is sector
