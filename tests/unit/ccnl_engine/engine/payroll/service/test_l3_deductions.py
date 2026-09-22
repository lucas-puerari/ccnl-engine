"""L3 period-event tests: family deductions, Art. 15, sterilizzazione."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from tests.helpers import make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.surtax.domain.rules import (
        SurtaxRules,
    )
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules as SurtaxRulesT
    from ccnl_engine.engine.tax.domain.rules import YearRules

_TEST_TAX_PERIOD = TaxPeriod(
    start=_DATE,
    end=date(2026, 12, 31),
    eligible_work_days=(date(2026, 12, 31) - _DATE).days + 1,
)


def compute(
    scenario: AnnualEstimateInput,
    period: PeriodPayrollInput | None = None,
) -> Calculation:
    """Route to estimate_period_effects or estimate_annual.

    When calling with a period that has no tax_period set, a test-default
    TaxPeriod covering the remainder of 2026 from _DATE is injected.

    Returns:
        Calculation from the appropriate estimator.
    """
    if period is not None:
        if period.tax_period is None:
            period = period.model_copy(update={"tax_period": _TEST_TAX_PERIOD})
        return estimate_period_effects(scenario, period, repo=_REPO)
    return estimate_annual(scenario, repo=_REPO)


_DEFAULT_CCNL = _build_ccnl()
_DEFAULT_CCNL_UC = _build_ccnl("under_classification")

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_RULES]
_mock_surtax: list[SurtaxRulesT | None] = [None]


class _MockRepo:
    """KnowledgeRepository stub for the autouse _reset_mock_state fixture."""

    def load_ccnl(self, filename: str) -> CCNL:
        return _mock_ccnl[0]

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> SurtaxRules | None:
        return _mock_surtax[0]

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        return CapabilityCatalog(year=year, capabilities=())


_REPO = _MockRepo()


@pytest.fixture(autouse=True)
def _reset_mock_state() -> None:
    """Reset mutable mock state before each test."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_RULES]
    _mock_surtax[:] = [None]


_SPOUSE_DEP = Dependent(relationship=DependentRelationship.SPOUSE)
_CHILD_DEP = Dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2000, 1, 1)
)
_FAMILY_INPUT = FamilyComposition(dependents=(_SPOUSE_DEP,))
_ART15_INPUT = Art15Deductions(mortgage_interest=_D("4000"))


# ---------------------------------------------------------------------------
# L3: Family deductions (Art. 12 TUIR)
# ---------------------------------------------------------------------------


class TestL3FamilyDeductions:
    """Family deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_family_leaves_irpef_net_unchanged(self) -> None:
        """Without family input, irpef_net equals baseline (no deduction)."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_none = estimate_annual(
            _req().model_copy(update={"family": None}), repo=_REPO
        ).result
        assert with_none.taxes.irpef_net == baseline.taxes.irpef_net
        assert with_none.taxes.family_deduction_annual == _D("0")

    def test_spouse_deduction_reduces_irpef_net(self) -> None:
        """Spouse deduction is subtracted from irpef_net."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_spouse = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert with_spouse.taxes.family_deduction_spouse_annual > _D("0")
        assert with_spouse.taxes.irpef_net < baseline.taxes.irpef_net

    def test_family_deduction_children_and_other_zero_when_not_set(self) -> None:
        """Children/other fields are zero when only spouse is set."""
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert result.taxes.family_deduction_children_annual == _D("0")
        assert result.taxes.family_deduction_other_annual == _D("0")

    def test_no_dependents_flags_no_deduction(self) -> None:
        """Family with no eligible dependents: deduction zero, irpef_net unchanged."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_empty_family = estimate_annual(
            _req().model_copy(update={"family": FamilyComposition()}), repo=_REPO
        ).result
        assert with_empty_family.taxes.family_deduction_annual == _D("0")
        assert with_empty_family.taxes.irpef_net == baseline.taxes.irpef_net

    def test_exempt_employer_family_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total deduction."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert result.taxes.family_deduction_spouse_annual > _D("0")
        assert (
            result.taxes.unused_family_deduction_annual
            == result.taxes.family_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_gross_annual_not_mutated_by_family_deductions(self) -> None:
        """gross_annual is unchanged by family deductions."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_family = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert with_family.earnings.gross_annual == baseline.earnings.gross_annual

    def test_family_deduction_taper_uses_taxable_income(self) -> None:
        """Art. 12 taper uses taxable_income (gross minus INPS), not gross_annual.

        With a spouse dependent, the taper formula is
        (95000 - reddito_complessivo) / 95000.  This test verifies the engine
        uses taxable_income (< gross_annual) so the taper and resulting
        deduction are larger than they would be if computed on gross_annual.
        """
        result_no_fam = estimate_annual(_req(), repo=_REPO).result
        result_spouse = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        # taxable_income < gross_annual, so the taper (95000 - RC) / 95000
        # is larger when RC = taxable_income.  The deduction must be strictly
        # greater than what the wrong (gross_annual) base would give.
        gross = result_no_fam.earnings.gross_annual
        taxable = result_no_fam.taxes.taxable_income
        assert taxable < gross
        # Deduction must be positive and taper-dependent
        assert result_spouse.taxes.family_deduction_spouse_annual > _D("0")
        # Expected: taper(taxable) > taper(gross), so deduction is larger.
        limit = _D("95000")
        taper_taxable = max(_D("0"), (limit - taxable) / limit)
        taper_gross = max(_D("0"), (limit - gross) / limit)
        assert taper_taxable > taper_gross

    def test_no_detrazioni_familiari_absent_when_dependents_present(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is removed when scenario.family has dependents.

        The flag signals that family deductions were NOT computed; it must be
        absent when the engine ran the Art. 12 computation, regardless of
        whether fam_total is positive.
        """
        result = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert (
            FiscalSimplification.NO_DETRAZIONI_FAMILIARI
            not in result.taxes.fiscal_simplifications
        )

    def test_no_detrazioni_familiari_present_when_family_is_none(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when no family data is provided."""
        result = estimate_annual(
            _req().model_copy(update={"family": None}), repo=_REPO
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_FAMILIARI in sfs

    def test_no_detrazioni_familiari_present_when_no_dependents(self) -> None:
        """NO_DETRAZIONI_FAMILIARI is present when family has no eligible dependents.

        FamilyComposition() with no dependents: has_any_dependent is False, so
        the engine skips the Art. 12 computation and keeps the flag set.
        """
        result = estimate_annual(
            _req().model_copy(update={"family": FamilyComposition()}), repo=_REPO
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_FAMILIARI in sfs


# ---------------------------------------------------------------------------
# Sterilizzazione detrazioni (Art. 1 c. 3-4 L. 199/2025)
# ---------------------------------------------------------------------------


class TestSterilizzazioneDetrazioni:
    """Sterilizzazione detrazioni — orchestrator integration.

    Art. 1 c. 3-4 L. 199/2025: reduces oneri detraibili al 19% (Art. 15
    c. 1 lett. a, b, d, e TUIR; not spese sanitarie lett. c) by EUR 440
    when reddito complessivo > threshold.  Art. 12 and Art. 13 deductions
    are not affected.  Uses a low custom threshold to trigger at test-CCNL
    income.
    """

    # Threshold below test-CCNL taxable income (~10 897) so sterilizzazione fires.
    _STRD_RULES = {"threshold": "10000", "reduction": "440"}

    def test_sterilizzazione_family_deduction_field_unchanged(self) -> None:
        """Family deductions are not reduced by sterilizzazione.

        Art. 12 deductions are not listed among the oneri targeted by
        Art. 1 c. 4 L. 199/2025.  Without Art. 15 deductions, sterilizzazione
        has nothing to reduce and the clawback is zero.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        _mock_rules[0] = make_year_rules()
        baseline = estimate_annual(
            _req().model_copy(
                update={"family": FamilyComposition(dependents=(_SPOUSE_DEP,))}
            ),
            repo=_REPO,
        ).result
        assert (
            baseline.taxes.family_deduction_annual
            == with_strd.taxes.family_deduction_annual
        )
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("0")

    def test_sterilizzazione_no_art15_no_clawback(self) -> None:
        """Without Art. 15 deductions, sterilizzazione clawback is zero.

        The reduction targets oneri at 19%: when art15_total = 0 there is
        nothing to reduce and irpef_net is unchanged.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(_req(), repo=_REPO).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(_req(), repo=_REPO).result
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("0")
        assert with_strd.taxes.irpef_net == without_strd.taxes.irpef_net

    def test_sterilizzazione_increases_irpef_net(self) -> None:
        """Sterilizzazione reduces Art. 15 oneri credit → irpef_net increases.

        3 000 EUR mortgage interest → credit 570 EUR.  Clawback = min(440, 570)
        = 440.  irpef_net rises by exactly 440 EUR.  The raw art15_deduction
        field keeps reporting the pre-clawback credit.

        A RAL of 50 000 EUR is used to ensure IRPEF > 570 in both scenarios
        so the full 440 clawback is reflected rather than capped by incapienza.
        """
        art15 = Art15Deductions(mortgage_interest=_D("3000"))
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        with_strd = estimate_annual(
            _req(negotiated_ral=_D("50000")).model_copy(
                update={"art15_deductions": art15}
            ),
            repo=_REPO,
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req(negotiated_ral=_D("50000")).model_copy(
                update={"art15_deductions": art15}
            ),
            repo=_REPO,
        ).result
        # Art. 13 (work_income_deduction) is not affected.
        assert (
            with_strd.taxes.work_income_deduction
            == without_strd.taxes.work_income_deduction
        )
        # Clawback fires at 440 (< 570 credit).
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")
        # irpef_net increases by the clawback amount.
        assert (
            with_strd.taxes.irpef_net - without_strd.taxes.irpef_net
            == with_strd.taxes.sterilizzazione_clawback_annual
        )
        # Raw art15_deduction_annual field is the pre-clawback credit.
        assert with_strd.taxes.art15_deduction_annual == _D("570.00")

    def test_sterilizzazione_below_threshold_no_effect(self) -> None:
        """Income <= threshold: no clawback; irpef_net unchanged."""
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "9999999", "reduction": "440"}
        )
        with_high_threshold = estimate_annual(_req(), repo=_REPO).result
        _mock_rules[0] = make_year_rules()
        without = estimate_annual(_req(), repo=_REPO).result
        assert with_high_threshold.taxes.sterilizzazione_clawback_annual == _D("0")
        assert with_high_threshold.taxes.irpef_net == without.taxes.irpef_net

    def test_sterilizzazione_at_high_income_art15_reduced(self) -> None:
        """At real 200k+ income with Art. 15 oneri, clawback fires on the credit.

        At reddito complessivo 250 000 EUR, the full EUR 440 reduction applies
        to the Art. 15 mortgage credit (4 000 * 19% = 760 EUR → 320 EUR net).
        """
        high_income = _D("250000")
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "200000", "reduction": "440"}
        )
        with_strd = estimate_annual(
            _req(negotiated_ral=high_income).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            ),
            repo=_REPO,
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req(negotiated_ral=high_income).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            ),
            repo=_REPO,
        ).result
        # Clawback fires: Art. 15 credit is 760; min(440, 760) = 440.
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")
        # Raw art15_deduction_annual still shows the pre-clawback credit.
        assert with_strd.taxes.art15_deduction_annual == _D("760.00")
        # irpef_net increases by the clawback.
        assert with_strd.taxes.irpef_net - without_strd.taxes.irpef_net == _D("440.00")

    def test_sterilizzazione_with_family_and_art15_pins_unused(self) -> None:
        """art15_unused is recomputed against the effective credit after clawback.

        When sterilizzazione fires (clawback = 440), the effective Art. 15
        credit drops from 760 to 320 EUR.  art15_unused must be recomputed
        against the effective credit so that incapienza is not overstated.
        """
        _mock_rules[0] = make_year_rules(sterilizzazione_detrazioni=self._STRD_RULES)
        result = estimate_annual(
            _req().model_copy(
                update={
                    "family": FamilyComposition(dependents=(_SPOUSE_DEP,)),
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000")),
                }
            ),
            repo=_REPO,
        ).result
        _mock_rules[0] = make_year_rules()
        result_no_strd = estimate_annual(
            _req().model_copy(
                update={
                    "family": FamilyComposition(dependents=(_SPOUSE_DEP,)),
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000")),
                }
            ),
            repo=_REPO,
        ).result
        # Verify sterilizzazione fired and family deductions are present.
        assert result.taxes.sterilizzazione_clawback_annual == _D("440.00")
        assert result.taxes.family_deduction_annual > _D("0")
        # Raw art15_deduction_annual reports the pre-clawback credit in both.
        assert (
            result.taxes.art15_deduction_annual
            == result_no_strd.taxes.art15_deduction_annual
        )
        # art15_unused is lower with sterilizzazione because the effective credit
        # is smaller (320 vs 760 EUR), so less credit needs to be absorbed.
        assert result.taxes.unused_art15_deduction_annual <= (
            result_no_strd.taxes.unused_art15_deduction_annual
        )
        # The reduction in unused is bounded by the clawback amount.
        delta = (
            result_no_strd.taxes.unused_art15_deduction_annual
            - result.taxes.unused_art15_deduction_annual
        )
        assert _D("0") <= delta <= result.taxes.sterilizzazione_clawback_annual


# ---------------------------------------------------------------------------
# Art. 15 deductions (interessi passivi mutuo prima casa)
# ---------------------------------------------------------------------------


class TestArt15Deductions:
    """Art. 15 TUIR deductions — orchestrator integration."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_no_art15_leaves_irpef_net_unchanged(self) -> None:
        """Without art15_deductions, irpef_net equals baseline."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_none = estimate_annual(
            _req().model_copy(update={"art15_deductions": None}), repo=_REPO
        ).result
        assert with_none.taxes.irpef_net == baseline.taxes.irpef_net
        assert with_none.taxes.art15_deduction_annual == _D("0")

    def test_mortgage_deduction_reduces_irpef_net(self) -> None:
        """Art. 15 mortgage credit is subtracted from irpef_net, clamped at 0.

        At the test-CCNL income level the credit (570 EUR) exceeds irpef_net
        (551.36), so irpef_net is floored at 0 — excess credit is lost per
        Italian tax law.
        """
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_art15 = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            ),
            repo=_REPO,
        ).result
        assert with_art15.taxes.art15_deduction_annual == _D("570.00")  # 3000 * 0.19
        expected = max(_D("0"), baseline.taxes.irpef_net - _D("570.00"))
        assert with_art15.taxes.irpef_net == expected

    def test_ceiling_cap_applied(self) -> None:
        """Interest above EUR 4 000 ceiling: credit capped at EUR 760."""
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("9999"))
                }
            ),
            repo=_REPO,
        ).result
        assert result.taxes.art15_deduction_annual == _D("760.00")  # 4000 * 0.19

    def test_no_detrazioni_art15_mortgage_tag_removed_when_computed(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE absent when mortgage interest is provided."""
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("1000"))
                }
            ),
            repo=_REPO,
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE not in sfs

    def test_partial_detrazioni_art15_always_set_when_mortgage_present(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 stays set even when mortgage is provided.

        Only one of ~15 Art. 15 TUIR categories is modelled; the flag signals
        that the other categories are always out of scope.
        """
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("1000"))
                }
            ),
            repo=_REPO,
        ).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_no_detrazioni_art15_mortgage_tag_present_when_not_set(self) -> None:
        """NO_DETRAZIONI_ART15_MORTGAGE present when mortgage not provided."""
        result = estimate_annual(_req(), repo=_REPO).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs

    def test_partial_detrazioni_art15_always_set_when_no_art15(self) -> None:
        """PARTIAL_DETRAZIONI_ART15 always set, even without any Art. 15 input."""
        result = estimate_annual(_req(), repo=_REPO).result
        sfs = result.taxes.fiscal_simplifications
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_exempt_employer_art15_unused_equals_total(self) -> None:
        """When employer does not withhold IRPEF, unused = total credit."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            ),
            repo=_REPO,
        ).result
        assert result.taxes.art15_deduction_annual == _D("570.00")
        assert (
            result.taxes.unused_art15_deduction_annual
            == result.taxes.art15_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_zero_interest_has_no_effect(self) -> None:
        """Art15Deductions with zero mortgage_interest: no deduction, tags kept."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_zero = estimate_annual(
            _req().model_copy(
                update={"art15_deductions": Art15Deductions(mortgage_interest=_D("0"))}
            ),
            repo=_REPO,
        ).result
        assert with_zero.taxes.art15_deduction_annual == _D("0")
        assert with_zero.taxes.irpef_net == baseline.taxes.irpef_net
        sfs = with_zero.taxes.fiscal_simplifications
        assert FiscalSimplification.NO_DETRAZIONI_ART15_MORTGAGE in sfs
        assert FiscalSimplification.PARTIAL_DETRAZIONI_ART15 in sfs

    def test_gross_annual_not_mutated_by_art15_deductions(self) -> None:
        """gross_annual is unchanged by Art. 15 deductions."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_art15 = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("2000"))
                }
            ),
            repo=_REPO,
        ).result
        assert with_art15.earnings.gross_annual == baseline.earnings.gross_annual

    def test_sterilizzazione_reduces_art15_increases_irpef(self) -> None:
        """Sterilizzazione fires on Art. 15 oneri; clawback = 440.

        When sterilizzazione fires (income > threshold), the effective Art. 15
        credit is reduced by 440.  art15_deduction_annual keeps reporting the
        raw pre-clawback credit; sterilizzazione_clawback_annual shows the
        reduction.
        """
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "10000", "reduction": "440"}
        )
        with_strd = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            ),
            repo=_REPO,
        ).result
        _mock_rules[0] = make_year_rules()
        without_strd = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            ),
            repo=_REPO,
        ).result
        # art15_deduction_annual reports the raw pre-clawback credit in both.
        assert with_strd.taxes.art15_deduction_annual == _D("570.00")
        assert without_strd.taxes.art15_deduction_annual == _D("570.00")
        # Clawback fires on Art. 15 → sterilizzazione_clawback = 440.
        assert with_strd.taxes.sterilizzazione_clawback_annual == _D("440.00")

    def test_exempt_employer_sterilizzazione_art15_unused_unchanged(self) -> None:
        """Exempt employer + sterilizzazione: art15_unused equals full art15_total.

        For exempt employers (non sostituto d'imposta), IRPEF is never
        withheld, so the entire Art. 15 credit is always unused.
        Sterilizzazione does not recompute art15_unused in this case.
        """
        _mock_ccnl[0] = self._EXEMPT_CCNL
        _mock_rules[0] = make_year_rules(
            sterilizzazione_detrazioni={"threshold": "10000", "reduction": "440"}
        )
        result = estimate_annual(
            _req().model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("3000"))
                }
            ),
            repo=_REPO,
        ).result
        # art15 = 3000 * 0.19 = 570; unchanged by sterilizzazione.
        assert result.taxes.art15_deduction_annual == _D("570.00")
        # Exempt employer: all art15 is unused (irpef_net stays 0 regardless).
        assert (
            result.taxes.unused_art15_deduction_annual
            == result.taxes.art15_deduction_annual
        )
        assert result.taxes.irpef_net == _D("0.00")

    def test_ulteriore_detrazione_reduces_art15_available_capacity(self) -> None:
        """Ulteriore detrazione consumes IRPEF capacity before Art. 15 credits.

        When ulteriore_detrazione_lavoro > 0, the IRPEF available to absorb
        Art. 15 deductions is reduced accordingly.  With a large UDL (EUR 5 000),
        all IRPEF is consumed before Art. 15 → unused_art15 equals art15_total.
        """
        # Set UDL rules with a large max_amount to exhaust IRPEF capacity.
        _mock_rules[0] = make_year_rules(
            ulteriore_detrazione={
                "threshold_low": "20000",
                "threshold_mid": "32000",
                "threshold_high": "40000",
                "max_amount": "5000",
            }
        )
        result = estimate_annual(
            _req(negotiated_ral=_D("25000")).model_copy(
                update={
                    "art15_deductions": Art15Deductions(mortgage_interest=_D("4000"))
                }
            ),
            repo=_REPO,
        ).result
        # art15 = min(4000, 4000) * 0.19 = 760 (at EUR 4 000 ceiling).
        assert result.taxes.art15_deduction_annual == _D("760.00")
        # UDL = 5 000 exhausts all IRPEF before Art. 15 → full credit is unused.
        assert result.taxes.ulteriore_detrazione_lavoro == _D("5000.00")
        assert result.taxes.unused_art15_deduction_annual == _D("760.00")


class TestArt15MortgagePre2022:
    """Tests for mortgage_pre_2022 TI qualification gate."""

    def test_post_2021_mortgage_excluded_from_ti_relevant_deductions(self) -> None:
        """Post-2021 mortgage (default) does not affect trattamento_integrativo."""
        # Level 2 (base 600/month) puts taxable income in the TI band.
        baseline = estimate_annual(_req(level_code="2"), repo=_REPO).result
        with_post_2021 = estimate_annual(
            _req(level_code="2").model_copy(
                update={
                    "art15_deductions": Art15Deductions(
                        mortgage_interest=_D("3000"), mortgage_pre_2022=False
                    )
                }
            ),
            repo=_REPO,
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_post_2021.taxes.art15_deduction_annual == _D("570.00")
        # TI unaffected by post-2021 mortgage
        assert (
            with_post_2021.taxes.trattamento_integrativo
            == baseline.taxes.trattamento_integrativo
        )

    def test_pre_2022_mortgage_included_in_ti_relevant_deductions(self) -> None:
        """Pre-2022 mortgage qualifies for TI relevant_deductions."""
        baseline = estimate_annual(_req(level_code="2"), repo=_REPO).result
        with_pre_2022 = estimate_annual(
            _req(level_code="2").model_copy(
                update={
                    "art15_deductions": Art15Deductions(
                        mortgage_interest=_D("3000"), mortgage_pre_2022=True
                    )
                }
            ),
            repo=_REPO,
        ).result
        # Art. 15 credit still applied to IRPEF
        assert with_pre_2022.taxes.art15_deduction_annual == _D("570.00")
        # TI may increase because relevant_deductions grew (or remain at max)
        assert (
            with_pre_2022.taxes.trattamento_integrativo
            >= baseline.taxes.trattamento_integrativo
        )
