"""Fiscal edge-case tests: IVS ceiling, domestic INPS, addizionali."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.metadata.domain.rules import (
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Jurisdiction,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.provenance.domain.extraction import (
    ExtractionMethod,
    ExtractionTrace,
)
from ccnl_engine.engine.provenance.domain.source import (
    SourceDocument,
    SourceKind,
    SourceLocation,
)
from ccnl_engine.engine.surtax.domain.rules import (
    ComunaleEntry,
    RegionaleEntry,
    SurtaxBracket,
    SurtaxRules,
)
from tests.helpers import (
    make_domestic_year_rules,
    make_year_rules,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _FIXED_TERM,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        TaxSector,
    )
    from ccnl_engine.engine.payroll.domain.calculation import Calculation
    from ccnl_engine.engine.payroll.domain.payroll_result import (
        AnnualEstimate as PayrollResult,
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


def _rule_provenance(tag: str) -> RuleProvenance:
    """Build a RuleProvenance with a distinguishing document/section identity.

    Returns:
        A :class:`RuleProvenance` uniquely identified by ``tag``.
    """
    return RuleProvenance(
        location=SourceLocation(
            source_document=SourceDocument(
                document_id=f"doc-{tag}",
                title=f"Document {tag}",
                kind=SourceKind.TABELLA_RETRIBUTIVA,
                url="https://example.com",
            ),
            section=f"Tabella {tag}",
        ),
        extraction=ExtractionTrace(
            method=ExtractionMethod.MANUAL,
            extraction_timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            verification_status=VerificationStatus.UNVERIFIED,
            effective_from=date(2025, 1, 1),
        ),
        note=tag,
    )


class TestComputeIvsCeilingSplit:
    """compute() with ivs_ceiling_applies=True and RAL above massimale."""

    _CEILING = "122295.00"

    def _rules_with_ceiling(self) -> YearRules:
        return make_year_rules(
            inps={
                "employee_rate": "0.0919",
                "employee_ivs_rate": "0.0919",
                "employer_rate": "0.2898",
                "employer_ivs_rate": "0.2381",
                "ceiling": self._CEILING,
            }
        )

    def _scenario(
        self, ral: Decimal, *, ivs_ceiling_applies: bool
    ) -> AnnualEstimateInput:
        return _req(
            negotiated_ral=ral,
            ivs_ceiling_applies=ivs_ceiling_applies,
        )

    def test_below_ceiling_unchanged(self) -> None:
        """RAL below the massimale: ceiling split equals flat rate."""
        ral = _D("80000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r_capped = compute(self._scenario(ral, ivs_ceiling_applies=True)).result
        r_flat = compute(self._scenario(ral, ivs_ceiling_applies=False)).result
        assert (
            r_capped.contributions.inps_employee_annual
            == r_flat.contributions.inps_employee_annual
        )
        assert (
            r_capped.contributions.inps_employer_annual
            == r_flat.contributions.inps_employer_annual
        )

    def test_above_ceiling_ivs_capped_non_ivs_uncapped(self) -> None:
        """RAL above massimale: IVS portion capped, non-IVS applied to full base."""
        ral = _D("150000.00")
        ceiling = _D(self._CEILING)
        emp_rate = _D("0.0919")
        emp_ivs_rate = _D("0.0919")
        er_rate = _D("0.2898")
        er_ivs_rate = _D("0.2381")
        er_non_ivs = er_rate - er_ivs_rate
        emp_non_ivs = emp_rate - emp_ivs_rate
        expected_employee = money(ceiling * emp_ivs_rate + ral * emp_non_ivs)
        expected_employer = money(ceiling * er_ivs_rate + ral * er_non_ivs)

        _mock_rules[0] = self._rules_with_ceiling()
        r = compute(self._scenario(ral, ivs_ceiling_applies=True)).result
        assert r.contributions.inps_employee_annual == expected_employee
        assert r.contributions.inps_employer_annual == expected_employer

    def test_ceiling_flag_false_skips_split(self) -> None:
        """ivs_ceiling_applies=False: flat rate even when ceiling is configured."""
        ral = _D("150000.00")
        _mock_rules[0] = self._rules_with_ceiling()
        r = compute(self._scenario(ral, ivs_ceiling_applies=False)).result
        assert r.contributions.inps_employee_annual == _D("150000.00") * _D("0.0919")
        assert r.contributions.inps_employer_annual == _D("150000.00") * _D("0.2898")


# ---------------------------------------------------------------------------
# IRPEF floor
# ---------------------------------------------------------------------------


class TestComputeIrpefFloor:
    """Net = gross - inps when deduction exceeds gross IRPEF."""

    def test_irpef_net_floored_at_zero(self) -> None:
        """Low income: deduction > irpef_gross → irpef_net == 0."""
        r = estimate_annual(_req(negotiated_ral=_D("5000.00")), repo=_REPO).result

        assert r.taxes.irpef_net == _D("0.00")
        assert r.net_annual == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )


# ---------------------------------------------------------------------------
# Withholding exemption (non-sostituto d'imposta employers)
# ---------------------------------------------------------------------------


class TestComputeWithholdingExempt:
    """withholding_exempt=True: irpef_net zero, informational fields retained."""

    _EXEMPT_CCNL = _build_ccnl(**{"meta.withholding_exempt": True})

    def test_irpef_net_is_zero(self) -> None:
        """Exempt employer: irpef_net must be zero regardless of income."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.taxes.irpef_net == _D("0.00")

    def test_employer_withholds_irpef_flag_false(self) -> None:
        """Exempt employer: employer_withholds_irpef must be False."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.taxes.employer_withholds_irpef is False

    def test_net_annual_excludes_irpef(self) -> None:
        """Net = gross - INPS employee; IRPEF not deducted by employer."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.net_annual == (
            r.earnings.gross_annual - r.contributions.inps_employee_annual
        )

    def test_irpef_informational_fields_nonzero(self) -> None:
        """irpef_gross and work_income_deduction remain as informational."""
        _mock_ccnl[0] = self._EXEMPT_CCNL
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.taxes.irpef_gross > _D("0.00")
        assert r.taxes.work_income_deduction >= _D("0.00")

    def test_standard_ccnl_withholds_irpef(self) -> None:
        """Standard CCNL: employer_withholds_irpef must be True."""
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.taxes.employer_withholds_irpef is True


# ---------------------------------------------------------------------------
# Domestic flat-hour INPS model
# ---------------------------------------------------------------------------


_DOMESTIC_RULES = make_domestic_year_rules()
_DEFAULT_WEEKLY_HOURS: Decimal = _D("40")


class TestComputeDomesticInps:
    """Flat per-hour INPS model (rules.domestic_contributions is not None)."""

    def test_missing_weekly_hours_raises(self) -> None:
        """domestic_contributions set but weekly_hours=None must raise."""
        _mock_rules[0] = _DOMESTIC_RULES
        with pytest.raises(ValueError, match="weekly_hours is required"):
            estimate_annual(_req(), repo=_REPO)

    def test_hours_bracket_permanent(self) -> None:
        """weekly_hours > 24 → hours bracket; permanent uses base employer rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("40")), repo=_REPO).result

        annual_hours = _D("40") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("0.93") * annual_hours)

    def test_hours_bracket_fixed_term(self) -> None:
        """weekly_hours > 24 + FixedTerm → hours bracket fixed-term rate."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(
            _req(contract=_FIXED_TERM, weekly_hours=_D("40")), repo=_REPO
        ).result

        annual_hours = _D("40") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.31") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("1.01") * annual_hours)

    def test_wage_bracket_mid(self) -> None:
        """weekly_hours <= 24 → wage bracket selected by annualised hourly rate.

        Level 4, gross_monthly=1000, weekly_hours=20:
        hourly_rate = 1000 * 12 / (20 * 52) = 11.54 → bracket up_to=11.70.
        """
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("20")), repo=_REPO).result

        annual_hours = _D("20") * _D("52")
        assert r.contributions.inps_employee_annual == money(_D("0.48") * annual_hours)
        assert r.contributions.inps_employer_annual == money(_D("1.44") * annual_hours)

    def test_net_is_gross_minus_inps_minus_irpef(self) -> None:
        """Net = gross - INPS employee - irpef_net for domestic path."""
        _mock_rules[0] = _DOMESTIC_RULES
        r = estimate_annual(_req(weekly_hours=_D("40")), repo=_REPO).result
        assert r.net_annual == (
            r.earnings.gross_annual
            - r.contributions.inps_employee_annual
            - r.taxes.irpef_net
        )

    def test_no_ivs_ceiling_warning_for_domestic_contracts(self) -> None:
        """Domestic contracts must not emit a false IVS ceiling warning.

        The domestic model uses per-hour forfait rates; the IVS ceiling
        does not participate in that calculation.  Emitting the warning
        would produce a false confidence downgrade for a valid scenario.
        """
        _mock_rules[0] = _DOMESTIC_RULES
        # seniority_months=12 implies a clearly post-1996 hire: without the
        # guard, _ivs_ceiling_warning would emit "contributions are overstated".
        r = estimate_annual(
            _req(weekly_hours=_D("40"), seniority_months=12), repo=_REPO
        ).result
        ivs_warnings = [w for w in r.coverage.warnings if "overstated" in w]
        assert ivs_warnings == [], (
            f"Unexpected IVS warning on domestic contract: {r.coverage.warnings}"
        )


# ---------------------------------------------------------------------------
# Addizionale regionale e comunale
# ---------------------------------------------------------------------------

_FS = FiscalSimplification  # short alias for long assertion lines


class TestComputeAddizionali:
    """Tests for the addizionale regionale and comunale computation."""

    def _surtax_rules(self) -> SurtaxRules:
        """Build a minimal SurtaxRules with one region and one municipality.

        Returns:
            A SurtaxRules instance with TestRegione and X001 entries.
        """
        return SurtaxRules(
            year=2026,
            regionale={
                "TestRegione": RegionaleEntry(
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.0123")),)
                )
            },
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(10000),
                )
            },
        )

    def _result(
        self,
        *,
        regione: str | None = None,
        comune_belfiore: str | None = None,
        negotiated_ral: Decimal | None = None,
    ) -> PayrollResult:
        has_locality = regione is not None or comune_belfiore is not None
        if has_locality:
            _mock_surtax[0] = self._surtax_rules()
        return estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=(
                    Jurisdiction(regione=regione, comune_belfiore=comune_belfiore)
                    if has_locality
                    else None
                ),
                negotiated_ral=negotiated_ral,
            ),
            repo=_REPO,
        ).result

    def test_without_surtax_parameter_both_zero(self) -> None:
        """When no jurisdiction set (default), both addizionali are zero."""
        r = estimate_annual(_req(), repo=_REPO).result
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications

    def test_regione_only(self) -> None:
        """With regione set, addizionale regionale > 0; comunale still zero."""
        r = self._result(regione="TestRegione")
        assert r.taxes.addizionale_regionale_annual > Decimal(0)
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications

    def test_comune_only(self) -> None:
        """With comune_belfiore set, addizionale comunale > 0; regionale zero."""
        r = self._result(comune_belfiore="X001")
        assert r.taxes.addizionale_comunale_annual > Decimal(0)
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications

    def test_both_set_both_computed(self) -> None:
        """With both fields set, both surtaxes are computed; neither flag set."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        assert r.taxes.addizionale_regionale_annual > Decimal(0)
        assert r.taxes.addizionale_comunale_annual > Decimal(0)
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications

    def test_both_reduce_net_annual(self) -> None:
        """Net annual is reduced by the sum of both addizionali."""
        r = self._result(regione="TestRegione", comune_belfiore="X001")
        expected_net = (
            r.earnings.gross_annual
            - r.contributions.inps_employee_annual
            - r.taxes.irpef_net
            - r.taxes.addizionale_regionale_annual
            - r.taxes.addizionale_comunale_annual
            + r.taxes.trattamento_integrativo
        )
        assert r.net_annual == expected_net

    def test_unknown_regione_produces_zero(self) -> None:
        """Unknown region name → addizionale regionale is zero, no flag."""
        r = self._result(regione="RegioneSconosciuta")
        assert r.taxes.addizionale_regionale_annual == Decimal("0.00")
        # No flag: the caller passed a region, we just didn't find it
        assert _FS.NO_ADDIZIONALE_REGIONALE not in r.taxes.fiscal_simplifications

    def test_unknown_comune_produces_zero(self) -> None:
        """Unknown codice catastale → addizionale comunale zero, no flag."""
        r = self._result(comune_belfiore="Z999")
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")
        assert _FS.NO_ADDIZIONALE_COMUNALE not in r.taxes.fiscal_simplifications

    def test_soglia_exempts_low_income(self) -> None:
        """Income below the soglia yields zero comunal surtax."""
        tiny_ral = Decimal(9000)  # well below X001's soglia of 10000
        custom_surtax = SurtaxRules(
            year=2026,
            regionale={},
            comunale={
                "X001": ComunaleEntry(
                    nome="Test",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(10000),
                )
            },
        )
        _mock_surtax[0] = custom_surtax
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=tiny_ral,
                jurisdiction=Jurisdiction(comune_belfiore="X001"),
            ),
            repo=_REPO,
        ).result
        assert r.taxes.addizionale_comunale_annual == Decimal("0.00")

    def test_irpef_zero_suppresses_addizionali(self) -> None:
        """When IRPEF is fully offset by deductions, addizionali are zero.

        A low RAL causes work_income_deduction to exceed irpef_gross, leaving
        irpef_fiscal = 0. Even with a valid jurisdiction, both surtaxes must
        be zero and NO_ADDIZIONALE_* flags must be present.
        """
        _mock_surtax[0] = self._surtax_rules()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),
                jurisdiction=Jurisdiction(
                    regione="TestRegione", comune_belfiore="X001"
                ),
            ),
            repo=_REPO,
        ).result
        assert r.taxes.irpef_net == _D("0.00"), "irpef_net must be zero in no-tax area"
        assert r.taxes.addizionale_regionale_annual == _D("0.00")
        assert r.taxes.addizionale_comunale_annual == _D("0.00")
        assert _FS.NO_ADDIZIONALE_REGIONALE in r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_COMUNALE in r.taxes.fiscal_simplifications


class TestFiscalFlagsExclusivity:
    """Addizionale flags are mutually exclusive regardless of TI-rules presence.

    When ``YearRules.taxes.trattamento_integrativo`` is ``None`` (no TI data in the
    bundle), ``_compute_ti`` must NOT seed the flag set with
    ``ADDIZIONALE_*_UNKNOWN``.  ``_compute_addizionali`` must further ensure
    that ``NO_ADDIZIONALE_*`` and ``ADDIZIONALE_*_UNKNOWN`` are never
    simultaneously active for the same jurisdiction axis.
    """

    @staticmethod
    def _surtax() -> SurtaxRules:
        return SurtaxRules(
            year=2026,
            regionale={
                "KnownRegione": RegionaleEntry(
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.0123")),)
                )
            },
            comunale={
                "K001": ComunaleEntry(
                    nome="Known",
                    brackets=(SurtaxBracket(up_to=None, rate=Decimal("0.008")),),
                    exemption_threshold=Decimal(0),
                )
            },
        )

    def test_ti_absent_no_jurisdiction_no_unknown_flags(self) -> None:
        """TI absent, no jurisdiction: NO_ADDIZIONALE_* set, UNKNOWN flags absent.

        The standard _RULES mock has no trattamento_integrativo. When no
        jurisdiction is provided, both axes must carry NO_ADDIZIONALE_*, and
        ADDIZIONALE_*_UNKNOWN must be absent.
        """
        r = estimate_annual(_req(), repo=_REPO).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs

    def test_ti_absent_known_jurisdiction_no_flags(self) -> None:
        """TI absent, known jurisdiction: addizionale computed, no simplification.

        Neither NO_ADDIZIONALE_* nor ADDIZIONALE_*_UNKNOWN should be present
        when the jurisdiction is found in the bundle.
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="KnownRegione", comune_belfiore="K001"
                ),
            ),
            repo=_REPO,
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE not in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE not in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs

    def test_ti_absent_unknown_jurisdiction_unknown_flag_only(self) -> None:
        """TI absent, unknown jurisdiction: UNKNOWN set, NO_ADDIZIONALE_* absent.

        When a jurisdiction is provided but not found in the bundle, only
        ADDIZIONALE_*_UNKNOWN should be set; NO_ADDIZIONALE_* must be absent.
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            ),
            repo=_REPO,
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN in sfs
        assert _FS.NO_ADDIZIONALE_REGIONALE not in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE not in sfs

    def test_ti_absent_irpef_zero_unknown_jurisdiction_no_unknown_flags(
        self,
    ) -> None:
        """TI absent, irpef_due=0, unknown jurisdiction: NO_ADDIZIONALE_* only.

        When IRPEF is zero (no-tax area), addizionali are suppressed regardless
        of jurisdiction. The NO_ADDIZIONALE_* flags must be set and
        ADDIZIONALE_*_UNKNOWN must be absent (not a contradiction).
        """
        _mock_surtax[0] = self._surtax()
        r = estimate_annual(
            _req(
                as_of=date(2026, 1, 1),
                negotiated_ral=_D("8000"),  # below no-tax threshold
                jurisdiction=Jurisdiction(
                    regione="UnknownRegione", comune_belfiore="Z999"
                ),
            ),
            repo=_REPO,
        ).result
        sfs = r.taxes.fiscal_simplifications
        assert _FS.NO_ADDIZIONALE_REGIONALE in sfs
        assert _FS.NO_ADDIZIONALE_COMUNALE in sfs
        assert _FS.ADDIZIONALE_REGIONALE_UNKNOWN not in sfs
        assert _FS.ADDIZIONALE_COMUNALE_UNKNOWN not in sfs
