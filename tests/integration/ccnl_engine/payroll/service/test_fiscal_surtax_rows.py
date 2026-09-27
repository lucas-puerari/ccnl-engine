"""Surtax decisions of rows with provisions: dependents, exemptions, carried rates."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.payroll.domain.decisions import CalculationStatus
from ccnl_engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome, compute_surtax
from ccnl_engine.payroll.service.surtax_table import (
    DEPENDENT_PROVISIONS_ISSUE,
    PRIOR_YEAR_RATES_ISSUE,
    SPECIFIC_EXEMPTIONS_ISSUE,
    regional_surtax_amount,
)
from ccnl_engine.shared.domain.primitives import Bracket
from ccnl_engine.tax.domain.surtax_rules import (
    ComunaleEntry,
    RegionalDeduction,
    RegionaleEntry,
    SurtaxRules,
    WholeIncomeRate,
)

_D = Decimal
_FLAT = (Bracket(up_to=None, rate=_D("0.01")),)
_CHILD = Dependent(relationship=DependentRelationship.CHILD)
_SPOUSE = Dependent(relationship=DependentRelationship.SPOUSE)
_DISABLED_PARENT = Dependent(
    relationship=DependentRelationship.ASCENDANT, disabled=True
)


def _rules() -> SurtaxRules:
    return SurtaxRules(
        year=2026,
        regionale={
            "Veneto": RegionaleEntry(
                brackets=_FLAT, dependent_provisions="0.9% with a disabled member"
            ),
            "Provincia Autonoma di Trento": RegionaleEntry(
                brackets=_FLAT,
                exemption_threshold=_D("30000"),
                dependent_provisions="246 euro per child",
            ),
            "Provincia Autonoma di Bolzano": RegionaleEntry(
                brackets=_FLAT,
                deductions=(RegionalDeduction(amount=_D("500")),),
                dependent_provisions="340 euro per child",
            ),
        },
        comunale={
            "A001": ComunaleEntry(nome="Carried", brackets=_FLAT, rates_year=2025),
            "A002": ComunaleEntry(
                nome="Specific",
                brackets=_FLAT,
                specific_exemptions=("Esenzione per lavoro dipendente fino a 12.000",),
            ),
            "A003": ComunaleEntry(
                nome="Both",
                brackets=_FLAT,
                rates_year=2025,
                specific_exemptions=("Esenzione per pensioni fino a 8.000",),
            ),
            "A004": ComunaleEntry(
                nome="Zero",
                brackets=(Bracket(up_to=None, rate=_D(0)),),
                specific_exemptions=("Esenzione per pensioni fino a 8.000",),
            ),
            "A005": ComunaleEntry(nome="Current", brackets=_FLAT, rates_year=2026),
        },
    )


def _compute(
    regione: str | None,
    comune: str | None = None,
    family: FamilyComposition | None = None,
    income: str = "40000",
) -> SurtaxOutcome:
    return compute_surtax(
        _D(income),
        _rules(),
        regione=regione,
        comune_belfiore=comune,
        irpef_due=_D(1),
        family_composition=family,
    )


class TestDependentProvisions:
    """A regional row with provisions for dependents the engine does not apply."""

    @pytest.mark.parametrize(
        "family",
        [
            None,
            FamilyComposition(),
            FamilyComposition(dependents=(_SPOUSE,)),
        ],
    )
    def test_without_child_or_disability_the_row_is_final(
        self, family: FamilyComposition | None
    ) -> None:
        """No declared child or disabled dependent: the provisions cannot apply."""
        outcome = _compute("IT-34", family=family)

        (decision,) = outcome.decisions
        assert decision.reason_code == "table_applied"
        assert decision.status is CalculationStatus.FINAL
        assert decision.amount == _D("400.00")
        assert outcome.issues == ()

    @pytest.mark.parametrize("dependent", [_CHILD, _DISABLED_PARENT])
    def test_child_or_disabled_dependent_makes_it_provisional(
        self, dependent: Dependent
    ) -> None:
        """40,000 x 1% = 400.00 without the provisions, provisional."""
        family = FamilyComposition(dependents=(_SPOUSE, dependent))
        outcome = _compute("IT-34", family=family)

        (decision,) = outcome.decisions
        assert decision.reason_code == "dependent_provisions_not_applied"
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.amount == _D("400.00")
        (issue,) = outcome.issues
        assert issue.code == DEPENDENT_PROVISIONS_ISSUE
        assert issue.status is CalculationStatus.PROVISIONAL
        assert "0.9% with a disabled member" in issue.message

    def test_exempt_income_is_final_even_with_children(self) -> None:
        """Up to the exemption threshold nothing is due: nothing to lower."""
        family = FamilyComposition(dependents=(_CHILD,))
        outcome = _compute("IT-TN", family=family, income="30000")

        (decision,) = outcome.decisions
        assert decision.reason_code == "below_exemption_threshold"
        assert decision.amount == 0
        assert outcome.issues == ()

    def test_surtax_cancelled_by_deductions_is_final(self) -> None:
        """40,000 x 1% = 400 less a 500 euro deduction: 0, nothing to lower."""
        family = FamilyComposition(dependents=(_CHILD,))
        outcome = _compute("IT-BZ", family=family)

        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == ("table_applied", _D(0))
        assert decision.status is CalculationStatus.FINAL


class TestMunicipalProvisions:
    """Municipal rows with carried rates or category-specific exemptions."""

    def test_rates_of_the_year_before_are_provisional(self) -> None:
        """No 2026 delibera: 2025 rates, 40,000 x 1% = 400.00, provisional."""
        outcome = _compute(None, "A001")

        (decision,) = outcome.decisions
        assert decision.reason_code == "prior_year_rates_applied"
        assert decision.inputs["rates_year"] == "2025"
        assert decision.amount == _D("400.00")
        (issue,) = outcome.issues
        assert issue.code == PRIOR_YEAR_RATES_ISSUE
        assert "rates of 2025" in issue.message

    def test_rates_of_the_tax_year_are_final(self) -> None:
        """A row whose rates year is the tax year is applied as final."""
        outcome = _compute(None, "A005")

        (decision,) = outcome.decisions
        assert decision.reason_code == "table_applied"
        assert decision.status is CalculationStatus.FINAL

    def test_specific_exemptions_are_provisional(self) -> None:
        """Exemptions for a category of income are quoted, not applied."""
        outcome = _compute(None, "A002")

        (decision,) = outcome.decisions
        assert decision.reason_code == "specific_exemptions_not_applied"
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.amount == _D("400.00")
        (issue,) = outcome.issues
        assert issue.code == SPECIFIC_EXEMPTIONS_ISSUE
        assert "lavoro dipendente fino a 12.000" in issue.message

    def test_carried_rates_with_specific_exemptions_raise_both_issues(self) -> None:
        """The carried rates decide the reason; both issues are listed."""
        outcome = _compute(None, "A003")

        (decision,) = outcome.decisions
        assert decision.reason_code == "prior_year_rates_applied"
        assert [i.code for i in outcome.issues] == [
            PRIOR_YEAR_RATES_ISSUE,
            SPECIFIC_EXEMPTIONS_ISSUE,
        ]

    def test_zero_rate_needs_no_exemption(self) -> None:
        """A zero surtax cannot be lowered by an exemption: final."""
        outcome = _compute(None, "A004")

        (decision,) = outcome.decisions
        assert (decision.reason_code, decision.amount) == ("table_applied", _D(0))
        assert outcome.issues == ()


class TestRegionalAmount:
    """Whole-income rate and income-only deductions of one regional row."""

    _ROW = RegionaleEntry(
        brackets=(
            Bracket(up_to=_D("15000"), rate=_D("0.01")),
            Bracket(up_to=None, rate=_D("0.02")),
        ),
        whole_income_rate=WholeIncomeRate(income_up_to=_D("20000"), rate=_D("0.01")),
        deductions=(
            RegionalDeduction(
                amount=_D("60"), income_above=_D("20000"), income_up_to=_D("25000")
            ),
            RegionalDeduction(
                amount=_D("100"), income_above=_D("30000"), phase_in=_D("10000")
            ),
        ),
    )

    @pytest.mark.parametrize(
        ("income", "expected"),
        [
            # Whole income at 1%: 20,000 x 1% = 200.00.
            ("20000", "200.00"),
            # Brackets: 150.00 + 5,000.01 x 2% (100.0002) = 250.00, less 60.
            ("20000.01", "190.00"),
            # 150.00 + 10,000 x 2% = 350.00, less 60: 290.00.
            ("25000", "290.00"),
            # 150.00 + 10,000.01 x 2% = 350.00; no deduction: 350.00.
            ("25000.01", "350.00"),
            # 150.00 + 15,000 x 2% = 450.00 at the start of the phase-in.
            ("30000", "450.00"),
            # 150.00 + 20,000 x 2% = 550.00 less 100 x 5,000 / 10,000 = 50.
            ("35000", "500.00"),
            # 150.00 + 35,000 x 2% = 850.00 less the full 100.
            ("50000", "750.00"),
        ],
    )
    def test_amount(self, income: str, expected: str) -> None:
        """Band edges of the whole-income rate and of each deduction."""
        assert regional_surtax_amount(_D(income), self._ROW) == _D(expected)


def test_deduction_band_must_not_be_empty() -> None:
    """A deduction whose upper limit is not above its lower limit is rejected."""
    with pytest.raises(ValueError, match="income_up_to must exceed income_above"):
        RegionalDeduction(
            amount=_D("60"), income_above=_D("30000"), income_up_to=_D("30000")
        )
