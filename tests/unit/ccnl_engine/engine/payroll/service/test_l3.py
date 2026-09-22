"""L3 period-event tests: warnings, absences, leave, sickness, variable pay."""

from __future__ import annotations

from datetime import date
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
