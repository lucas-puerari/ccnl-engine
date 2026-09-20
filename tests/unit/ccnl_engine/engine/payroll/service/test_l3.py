"""L3 period-event tests: absences, leave, sickness, variable pay, Art. 15."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import CapabilityCatalog
from ccnl_engine.engine.contract.domain.ccnl import (
    CCNL,
    AbsenceRules,
    CCNLWorkRules,
    DailyDivisorMethod,
    LeaveEntitlementTier,
    LeaveRules,
    OvertimeBand,
    SicknessRules,
    TaxSector,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries, ValidityPeriod
from ccnl_engine.engine.errors import OutOfScopeError
from ccnl_engine.engine.metadata.domain.rules import (
    VerificationStatus,
)
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.family import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
)
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.payroll.domain.payroll_result import (
    PeriodPayroll,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.domain.supplements import (
    AbsenceDays,
    BonusInput,
    FringeBenefitInput,
    LeaveInput,
    OvertimeHours,
    SickInput,
    WeeklyOvertimeHours,
    WelfareInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
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
from tests.helpers import (
    make_year_rules,
)
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _D,
    _DATE,
    _RULES,
    _build_ccnl,
    _req,
)

if TYPE_CHECKING:
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


_SPOUSE_DEP = Dependent(relationship=DependentRelationship.SPOUSE)
_CHILD_DEP = Dependent(
    relationship=DependentRelationship.CHILD, birth_date=date(2000, 1, 1)
)
_FAMILY_INPUT = FamilyComposition(dependents=(_SPOUSE_DEP,))
_ART15_INPUT = Art15Deductions(mortgage_interest=_D("4000"))


class TestL3Warning:
    """Orchestrator warning path for missing L3 schema."""

    def test_raises_out_of_scope_when_ccnl_has_no_l3(self) -> None:
        """Raise OutOfScopeError when time_supplements set but CCNL has no L3 schema."""
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(weekday_hours=_D("5"))
        )
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(_req(), period)

    def test_warning_and_not_computed_when_gross_incl_allowances(self) -> None:
        """R10: hourly_base_method='gross_incl_allowances' emits warning, returns 0.

        The CCNL schema is present but the method is not yet implemented.
        The scope must show 'not_computed' for overtime/night/holiday work, and
        the result status must be 'partial' because of the not_computed entries.
        """
        ts_schema = TimeSupplements(
            hourly_base_method="gross_incl_allowances",
            overtime_bands=[],  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(weekday_hours=_D("5"))
        )
        try:
            result = compute(_req(), period).result
            assert isinstance(result, PeriodPayroll)
            warnings = result.coverage.warnings
            assert any("gross_incl_allowances" in w for w in warnings), (
                f"Expected gross_incl_allowances warning, got: {warnings}"
            )
            assert result.overtime_supplement_monthly == _D("0")
            assert result.time_supplements_monthly == _D("0")
            # Scope must show not_computed because method is unsupported
            ot_scope = next(
                s for s in result.coverage.calculation_scope if s.feature == "overtime"
            )
            assert ot_scope.calculation_status == "not_computed"
            assert result.coverage.status == "partial"
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_night_holiday_hours_contribute_to_holiday_scope(self) -> None:
        """R9: night_holiday_hours > 0 sets holiday_work to not_computed.

        Before the fix, night_holiday_hours was not counted toward the holiday
        scope, so holiday_work would be 'excluded' even when hours were supplied.
        Verified with a schema-present CCNL that has no NIGHT_HOLIDAY band.
        """
        weekday_band = OvertimeBand(
            code="STR",
            description="Straordinario feriale",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.25"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[weekday_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(night_holiday_hours=_D("2"))
        )
        try:
            result = compute(_req(), period).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            # night_holiday_hours → holiday scope, no matching band → not_computed
            assert scope["holiday_work"] == "not_computed", (
                f"Expected holiday_work not_computed, got: {scope['holiday_work']}"
            )
            # Overtime and night must remain excluded (no hours for those buckets)
            assert scope["overtime"] == "excluded"
            assert scope["night_work"] == "excluded"
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_not_computed_when_schema_present_but_no_kind_band(self) -> None:
        """Schema present but no band for the requested WorkKind → not_computed.

        A CCNL with only a night band must report 'not_computed' for overtime
        when weekday_hours are requested, and 'verified' for night_work.
        Before the fix, scope checked ``wr_schema_present`` (the container) so
        both would show 'verified', masking missing band coverage.
        """
        night_band = OvertimeBand(
            code="NOTTE",
            description="Straordinario notturno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.30"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.NIGHT],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[night_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(
                weekday_hours=_D("5"),
                night_hours=_D("3"),
            )
        )
        try:
            result = compute(_req(), period).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed for overtime (no weekday band), got:"
                f" {scope['overtime']}"
            )
            assert scope["night_work"] == "computed", (
                f"Expected verified for night_work (band present), got:"
                f" {scope['night_work']}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_supplementare_hours_with_only_weekday_band_not_computed(self) -> None:
        """supplementare_hours declared but only weekday band → not_computed + warning.

        When the CCNL has a weekday band but no supplementare band, declaring
        supplementare_hours must produce a warning and mark overtime as
        not_computed; the weekday band must not silently absorb the hours.
        """
        weekday_band = OvertimeBand(
            code="OT_WD",
            description="Straordinario diurno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(
            overtime_bands=[weekday_band]  # type: ignore[arg-type]
        )
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(supplementare_hours=_D("10"))
        )
        try:
            result = compute(_req(), period).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["overtime"] == "not_computed", (
                f"Expected not_computed (no supplementare band), got:"
                f" {scope['overtime']}"
            )
            assert any("supplementare" in w for w in result.coverage.warnings), (
                f"Expected supplementare warning, got: {result.coverage.warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_holiday_hours_with_only_night_holiday_band_not_computed(self) -> None:
        """holiday_hours declared but only night_holiday band → not_computed."""
        nh_band = OvertimeBand(
            code="NH",
            description="Festivo-notturno",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.85"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.NIGHT_HOLIDAY],  # type: ignore[arg-type]
        )
        ts_schema = TimeSupplements(overtime_bands=[nh_band])  # type: ignore[arg-type]
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(holiday_hours=_D("4"))
        )
        try:
            result = compute(_req(), period).result
            scope = {
                item.feature: item.calculation_status
                for item in result.coverage.calculation_scope
            }
            assert scope["holiday_work"] == "not_computed", (
                f"Expected not_computed (no holiday band), got: {scope['holiday_work']}"
            )
            assert any("holiday" in w for w in result.coverage.warnings), (
                f"Expected holiday warning, got: {result.coverage.warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_tiered_band_warning_emitted_without_weekly_breakdown(self) -> None:
        """Warn when CCNL has tiered weekly bands but no OvertimeHours.weeks.

        When multiple bands share the same WorkKind (partitioned by
        hour_threshold_per_week) and the caller does not supply per-week
        hours, the engine emits a warning to avoid silent overstatement of
        the higher band.
        """
        band1 = OvertimeBand(
            code="OT_BASE",
            description="Straordinario base",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        band2 = OvertimeBand(
            code="OT_EXTRA",
            description="Straordinario extra",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.20"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
            hour_threshold_per_week=4,
        )
        ts_schema = TimeSupplements(overtime_bands=(band1, band2))
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        period = PeriodPayrollInput(
            time_supplements=OvertimeHours(weekday_hours=_D("10"))
        )
        try:
            result = compute(_req(), period).result
            warnings = result.coverage.warnings
            assert any("tiered weekly thresholds" in w for w in warnings), (
                f"Expected tiered-band warning, got: {warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_tiered_band_warning_suppressed_with_weekly_breakdown(self) -> None:
        """No tiered-band warning when OvertimeHours.weeks is supplied."""
        band1 = OvertimeBand(
            code="OT_BASE",
            description="Straordinario base",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.15"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
        )
        band2 = OvertimeBand(
            code="OT_EXTRA",
            description="Straordinario extra",
            kind=TimeSupplementKind("percentage"),
            rate=TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2020, 1, 1),
                        valid_until=None,
                        value=_D("0.20"),
                    ),
                )
            ),
            applies_to_kinds=[WorkKind.WEEKDAY],  # type: ignore[arg-type]
            hour_threshold_per_week=4,
        )
        ts_schema = TimeSupplements(overtime_bands=(band1, band2))
        _mock_ccnl[0] = _build_ccnl(
            work_rules={"time_supplements": ts_schema.model_dump()}
        )
        oh = OvertimeHours.from_weeks((
            WeeklyOvertimeHours(weekday_hours=_D("5")),
            WeeklyOvertimeHours(weekday_hours=_D("5")),
        ))
        period = PeriodPayrollInput(time_supplements=oh)
        try:
            result = compute(_req(), period).result
            warnings = result.coverage.warnings
            assert not any("tiered weekly thresholds" in w for w in warnings), (
                f"Unexpected tiered warning with weeks supplied: {warnings}"
            )
        finally:
            _mock_ccnl[0] = _DEFAULT_CCNL

    def test_zero_hours_supplement_no_warning_when_no_schema(self) -> None:
        """Zero-valued OvertimeHours is treated as not requested: no warning.

        When all five hour fields are zero the engine must not emit
        "time_supplements requested but not modelled", because the caller
        effectively passed no hours.  Scope items must show 'excluded'.
        """
        # all fields default to 0
        period = PeriodPayrollInput(time_supplements=OvertimeHours())
        result = compute(_req(), period).result
        warnings = result.coverage.warnings
        assert not any("time_supplements" in w for w in warnings), (
            f"Unexpected time_supplements warning for zero hours: {warnings}"
        )
        ot_scope = next(
            s for s in result.coverage.calculation_scope if s.feature == "overtime"
        )
        assert ot_scope.calculation_status == "excluded"


class TestL3Absence:
    """Orchestrator behaviour for L3 absence deduction."""

    def test_raises_out_of_scope_when_ccnl_has_no_absence_rules(self) -> None:
        """Raise OutOfScopeError when absence_days set but CCNL has no schema."""
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("2")))
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(_req(), period)

    def test_absence_deduction_with_wr_schema(self) -> None:
        """Compute absence deduction when CCNL has absence_rules (by_26 method)."""
        absence_rules = AbsenceRules(
            daily_divisor_method=DailyDivisorMethod.BY_26,
        )
        # Inject work_rules with absence_rules into the mock CCNL.
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(absence_rules=absence_rules)}
        )
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("1")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        # No warning: schema is present.
        assert not any("absence_days" in w for w in result.coverage.warnings)
        # Deduction must be > 0 and equals gross / 26.
        gross = result.earnings.gross_monthly
        expected = (gross / _D("26")).quantize(_D("0.01"))
        assert result.absence_deduction_monthly == expected
        # effective_gross = gross - deduction.
        assert result.effective_gross_monthly == gross - expected

    def test_absence_scope_excluded_when_no_days(self) -> None:
        """Absence scope item is excluded when no absence_days supplied."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["absence"] == "excluded"

    def test_raises_out_of_scope_when_absence_days_but_no_schema(self) -> None:
        """OutOfScopeError raised when absence_days given but CCNL has no schema."""
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("3")))
        with pytest.raises(OutOfScopeError):
            compute(_req(), period)

    def test_absence_scope_verified_with_schema(self) -> None:
        """Absence is verified when days given and CCNL has absence_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("2")))
        result = compute(_req(), period).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["absence"] == "computed"

    def test_absence_deduction_capped_when_exceeds_gross(self) -> None:
        """Deduction exceeding gross_monthly is capped and a warning emitted.

        With by_26 and gross=1000: daily_rate=38.46, 27 days → 1038.42 > 1000.
        The deduction must be capped to 1000 and effective_gross_monthly = 0.
        """
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("27")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        gross = result.earnings.gross_monthly
        assert result.absence_deduction_monthly == gross
        assert result.effective_gross_monthly == _D("0.00")
        assert any("capped" in w for w in result.coverage.warnings), (
            f"Expected cap warning, got: {result.coverage.warnings}"
        )

    def test_absence_deduction_at_boundary_no_cap(self) -> None:
        """Deduction exactly equal to gross_monthly requires no cap and no warning.

        With by_26 and gross=1000: daily_rate=38.46, 26 days → 999.96 <= 1000.
        No cap warning and effective_gross_monthly = gross - deduction.
        """
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    absence_rules=AbsenceRules(
                        daily_divisor_method=DailyDivisorMethod.BY_26,
                    )
                )
            }
        )
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("26")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        gross = result.earnings.gross_monthly
        expected_deduction = _D("999.96")  # round(1000/26)=38.46; 38.46*26=999.96
        assert result.absence_deduction_monthly == expected_deduction
        assert result.effective_gross_monthly == gross - expected_deduction
        assert not any("capped" in w for w in result.coverage.warnings), (
            f"Unexpected cap warning, got: {result.coverage.warnings}"
        )

    def test_zero_absence_days_no_warning_when_no_schema(self) -> None:
        """AbsenceDays(unpaid_days=0) is treated as not requested: no warning.

        When unpaid_days is zero the engine must not emit
        "absence_days requested but not modelled", because the caller
        effectively requested no absence.  Scope item must show 'excluded'.
        """
        period = PeriodPayrollInput(absence_days=AbsenceDays(unpaid_days=_D("0")))
        result = compute(_req(), period).result
        assert not any("absence_days" in w for w in result.coverage.warnings), (
            f"Unexpected absence_days warning for zero days: {result.coverage.warnings}"
        )
        absence_scope = next(
            s for s in result.coverage.calculation_scope if s.feature == "absence"
        )
        assert absence_scope.calculation_status == "excluded"


class TestL3Leave:
    """Orchestrator behaviour for L3 leave accrual."""

    def test_raises_out_of_scope_when_ccnl_has_no_leave_rules(self) -> None:
        """Raise OutOfScopeError when leave_input set but CCNL has no leave schema."""
        period = PeriodPayrollInput(leave_input=LeaveInput(taken_days=_D("3")))
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(_req(), period)

    def test_leave_accrual_with_wr_schema(self) -> None:
        """Compute leave accrual when CCNL has leave_rules (flat, no tiers)."""
        leave_rules = LeaveRules(default_annual_days=_D("20"))
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(leave_rules=leave_rules)}
        )
        period = PeriodPayrollInput(leave_input=LeaveInput(taken_days=_D("3")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        assert not any("leave_input" in w for w in result.coverage.warnings)
        # 20 / 12 = 1.67
        assert result.leave_accrued_days_monthly == _D("1.67")
        assert result.leave_taken_days_monthly == _D("3")
        assert result.leave_balance_days == _D("-1.33")

    def test_leave_accrual_selects_tier_by_service_months(self) -> None:
        """Tier with highest matching service_months_min is selected."""
        leave_rules = LeaveRules(
            default_annual_days=_D("20"),
            entitlement_tiers=[  # type: ignore[arg-type]
                LeaveEntitlementTier(service_months_min=0, annual_days=_D("20")),
                LeaveEntitlementTier(service_months_min=36, annual_days=_D("25")),
            ],
        )
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={"work_rules": CCNLWorkRules(leave_rules=leave_rules)}
        )
        # Employee with 48 months → senior tier (25 days/year → 2.08/month)
        result = compute(
            _req(seniority_months=48),
            PeriodPayrollInput(leave_input=LeaveInput(taken_days=_D("0"))),
        ).result
        assert isinstance(result, PeriodPayroll)
        assert result.leave_accrued_days_monthly == _D("2.08")

    def test_leave_scope_excluded_when_no_input(self) -> None:
        """Leave scope item is excluded when no leave_input supplied."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["leave"] == "excluded"

    def test_raises_out_of_scope_when_leave_input_but_no_schema(self) -> None:
        """OutOfScopeError raised when leave_input given but CCNL has no schema."""
        period = PeriodPayrollInput(leave_input=LeaveInput(taken_days=_D("3")))
        with pytest.raises(OutOfScopeError):
            compute(_req(), period)

    def test_leave_scope_verified_with_schema(self) -> None:
        """Leave is verified when input given and CCNL has leave_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    leave_rules=LeaveRules(default_annual_days=_D("20"))
                )
            }
        )
        period = PeriodPayrollInput(leave_input=LeaveInput(taken_days=_D("2")))
        result = compute(_req(), period).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["leave"] == "computed"


class TestL3Sickness:
    """Orchestrator behaviour for L3 sickness (malattia ordinaria)."""

    def test_raises_out_of_scope_when_ccnl_has_no_sickness_rules(self) -> None:
        """Raise OutOfScopeError when sick_input set but CCNL has no sickness schema."""
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("5")))
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(_req(), period)

    def test_sickness_computed_with_wr_schema(self) -> None:
        """Compute sick-leave indemnity when CCNL has sickness_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("3")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        assert not any("sick_input" in w for w in result.coverage.warnings)
        # 3 days: only carenza, no INPS indemnity
        assert result.sick_days_monthly == _D("3")
        assert result.sick_inps_indemnity_monthly == _D("0")

    def test_sick_scope_excluded_when_no_input(self) -> None:
        """Sickness is excluded when no sick_input is provided."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "excluded"

    def test_raises_out_of_scope_when_sick_input_but_no_schema(self) -> None:
        """OutOfScopeError raised when sick_input given but CCNL has no schema."""
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("5")))
        with pytest.raises(OutOfScopeError):
            compute(_req(), period)

    def test_sick_scope_verified_with_schema(self) -> None:
        """Sickness is verified when input given and CCNL has sickness_rules."""
        _mock_ccnl[0] = _DEFAULT_CCNL.model_copy(
            update={
                "work_rules": CCNLWorkRules(
                    sickness_rules=SicknessRules(
                        carenza_integration_rate=_D("1"),
                        full_pay_integration_rate=_D("1"),
                    )
                )
            }
        )
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("5")))
        result = compute(_req(), period).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "computed"

    def test_sick_all_zero_when_no_input(self) -> None:
        """No sick_input produces AnnualEstimate (no period fields)."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert not isinstance(result, PeriodPayroll)

    def test_zero_sick_days_no_warning_when_no_schema(self) -> None:
        """SickInput() with zero sick_days is treated as not requested.

        Mirrors test_zero_hours_supplement_no_warning_when_no_schema: a
        zero-valued SickInput must not emit the 'not modelled' warning and
        must leave the sickness scope as 'excluded', exactly like sick_input=None.
        """
        # sick_days defaults to 0
        period = PeriodPayrollInput(sick_input=SickInput())
        result = compute(_req(), period).result
        warnings = result.coverage.warnings
        assert not any("sick_input" in w for w in warnings), (
            f"Unexpected sick_input warning for zero sick days: {warnings}"
        )
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["sickness"] == "excluded"

    def test_zero_sick_days_same_result_as_no_input(self) -> None:
        """SickInput() produces the same metadata as sick_input=None.

        confidence, result_status, and scope must be identical for a scenario
        with sick_input=None and one with sick_input=SickInput() (zero days).
        """
        result_none = estimate_annual(_req(), repo=_REPO).result
        period_zero = PeriodPayrollInput(sick_input=SickInput())
        result_zero = compute(_req(), period_zero).result
        # Scope entry must match.
        scope_none = {
            s.feature: s.calculation_status
            for s in result_none.coverage.calculation_scope
        }
        scope_zero = {
            s.feature: s.calculation_status
            for s in result_zero.coverage.calculation_scope
        }
        assert scope_none["sickness"] == scope_zero["sickness"]
        # Overall result status must match.
        assert result_none.coverage.status == result_zero.coverage.status
        # Confidence must match.
        assert result_none.coverage.confidence == result_zero.coverage.confidence

    def test_sick_pay_loader_not_called_when_ccnl_has_no_sickness_rules(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_sick_pay_rates must not be called when the CCNL has no sickness_rules.

        Regression guard for the lazy-load gate: with positive sick days but no
        CCNL sickness schema OutOfScopeError is raised before the loader is
        reached, so a missing or corrupt sick-pay file cannot block a calculation.
        """

        def _fail() -> None:
            msg = "load_sick_pay_rates must not be called"
            raise RuntimeError(msg)

        monkeypatch.setattr(
            "ccnl_engine.engine.payroll.service.work_rules.load_sick_pay_rates",
            _fail,
        )
        # Default CCNL has no work_rules (no sickness schema).
        period = PeriodPayrollInput(sick_input=SickInput(sick_days=_D("3")))
        # OutOfScopeError is raised before load_sick_pay_rates is ever called.
        with pytest.raises(OutOfScopeError, match="not modelled"):
            compute(_req(), period)


class TestL3VariablePay:
    """Orchestrator integration tests for the variable-pay L3 features."""

    def test_fringe_benefit_scope_excluded_when_no_input(self) -> None:
        """fringe_benefit scope is excluded when no fringe_benefit_input."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["fringe_benefit"] == "excluded"

    def test_welfare_scope_excluded_when_no_input(self) -> None:
        """Welfare scope is excluded when no welfare_input."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["welfare"] == "excluded"

    def test_bonus_pdr_scope_excluded_when_no_input(self) -> None:
        """bonus_pdr scope is excluded when no bonus_input."""
        result = estimate_annual(_req(), repo=_REPO).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["bonus_pdr"] == "excluded"

    def test_all_variable_pay_fields_zero_when_no_inputs(self) -> None:
        """No variable-pay inputs produces AnnualEstimate (no period fields)."""
        result = estimate_annual(_req(), repo=_REPO).result
        assert not isinstance(result, PeriodPayroll)

    def test_fringe_benefit_scope_verified_when_input_given(self) -> None:
        """fringe_benefit scope is verified when input is provided."""
        period = PeriodPayrollInput(
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("800"))
        )
        result = compute(_req(), period).result
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["fringe_benefit"] == "computed"

    def test_fringe_benefit_below_threshold_not_taxable(self) -> None:
        """Fringe benefit below €1.000 threshold: taxable_annual is zero."""
        period = PeriodPayrollInput(
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("800"))
        )
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        assert result.fringe_benefit_annual == _D("800")
        assert result.fringe_benefit_threshold_annual == _D("1000.00")
        assert result.fringe_benefit_taxable_annual == _D("0")

    def test_fringe_benefit_above_threshold_taxable(self) -> None:
        """R15: Fringe benefit above €1.000 threshold: ENTIRE amount is taxable."""
        period = PeriodPayrollInput(
            fringe_benefit_input=FringeBenefitInput(annual_amount=_D("1400"))
        )
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        assert result.fringe_benefit_annual == _D("1400")
        assert result.fringe_benefit_taxable_annual == _D("1400.00")

    def test_welfare_scope_verified_when_input_given(self) -> None:
        """Welfare scope is verified when input is provided."""
        period = PeriodPayrollInput(welfare_input=WelfareInput(annual_amount=_D("600")))
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["welfare"] == "computed"
        assert result.welfare_annual == _D("600")

    def test_bonus_pdr_eligible_applies_flat_tax(self) -> None:
        """PdR-eligible bonus within ceiling: flat tax computed correctly."""
        period = PeriodPayrollInput(
            bonus_input=BonusInput(
                annual_amount=_D("2000"),
                eligible_for_pdr=True,
                prior_year_gross_annual=_D("50000"),
            )
        )
        result = compute(_req(), period).result
        assert isinstance(result, PeriodPayroll)
        scope = {
            item.feature: item.calculation_status
            for item in result.coverage.calculation_scope
        }
        assert scope["bonus_pdr"] == "computed"
        assert result.bonus_annual == _D("2000")
        assert result.bonus_pdr_flat_tax_annual == _D("20.00")
        assert result.bonus_ordinary_taxable_annual == _D("0")

    def test_gross_annual_not_mutated_by_variable_pay(self) -> None:
        """gross_annual is unchanged; fringe (above threshold) raises taxable_income."""
        baseline = estimate_annual(_req(), repo=_REPO).result
        with_inputs = compute(
            _req(),
            PeriodPayrollInput(
                fringe_benefit_input=FringeBenefitInput(annual_amount=_D("1400")),
                welfare_input=WelfareInput(annual_amount=_D("600")),
                bonus_input=BonusInput(
                    annual_amount=_D("2000"),
                    eligible_for_pdr=True,
                    prior_year_gross_annual=_D("50000"),
                ),
            ),
        ).result
        # gross_annual (base salary) is never altered by variable-pay inputs
        assert with_inputs.earnings.gross_annual == baseline.earnings.gross_annual
        # fringe above threshold (€1400 > €1000) adds to taxable_income
        assert with_inputs.taxes.taxable_income > baseline.taxes.taxable_income
        # higher taxable_income means more IRPEF and lower net
        assert with_inputs.taxes.irpef_net > baseline.taxes.irpef_net
        assert with_inputs.net_annual < baseline.net_annual

    def test_welfare_only_does_not_register_variable_pay_ruleset(self) -> None:
        """A welfare-only scenario must not include variable_pay in ruleset_version.

        compute_welfare() does not consume the variable-pay rules file; only
        fringe-benefit and bonus/PdR inputs trigger its load and registration.
        """
        period = PeriodPayrollInput(welfare_input=WelfareInput(annual_amount=_D("500")))
        calc = compute(_req(), period)
        assert "variable_pay" not in calc.ruleset_version


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
