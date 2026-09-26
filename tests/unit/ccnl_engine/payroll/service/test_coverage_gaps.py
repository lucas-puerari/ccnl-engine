"""Coverage gap tests for payroll service / domain modules."""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from ccnl_engine.api.facade import PayrollEngine
from ccnl_engine.engine.contract.domain.category import WorkerCategory
from ccnl_engine.engine.contract.domain.compensation import Allowance
from ccnl_engine.engine.contract.domain.identity._ccnl import CCNL
from ccnl_engine.engine.contract.domain.seniority import (
    SeniorityIncrements,
    SeniorityTier,
)
from ccnl_engine.engine.contract.domain.validity import TimeSeries
from ccnl_engine.engine.contract.domain.working_time import (
    OvertimeBand,
    TimeSupplementKind,
    TimeSupplements,
    WorkKind,
)
from ccnl_engine.engine.errors import InvalidInputError, OutOfScopeError
from ccnl_engine.engine.tax.service.tax_optional_loaders import load_sick_pay_rates
from ccnl_engine.payroll.domain.employment import Apprentice
from ccnl_engine.payroll.domain.pay_items._policy import (
    PayItemPolicy,
    PolicyDecision,
)
from ccnl_engine.payroll.domain.treatments import (
    ContributionTreatment,
    CostTreatment,
    TaxTreatment,
    TfrTreatment,
)
from ccnl_engine.payroll.service.apprenticeship import (
    _apprentice_chain,
    _find_period_index,
    _select_track,
)
from ccnl_engine.payroll.service.chain import _allowance_active
from ccnl_engine.payroll.service.rounding import money
from ccnl_engine.payroll.service.seniority import (
    _count_from_tiers,
    _resolve_seniority_count,
    _resolve_tier_amount,
    _seniority_amount,
    seniority_first_cadence,
    seniority_maximum,
)
from ccnl_engine.payroll.service.types import MonthlyPayChain
from tests.helpers import TEST_PROV, _series, make_ccnl_dict, make_minimal_ccnl

_AS_OF = date(2026, 6, 1)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _time_series(value: str) -> TimeSeries:
    """Build a single-period TimeSeries for the given value.

    Returns:
        A :class:`TimeSeries` valid from 2020-01-01 with no end date.
    """
    return TimeSeries.model_validate(_series(value))


def _allowance(
    *,
    code: str = "EDR",
    monthly: str = "10.00",
    role: str | None = None,
    apprenticeship_pct_relevant: bool = True,
    service_months_threshold: int | None = None,
) -> Allowance:
    """Build a minimal :class:`Allowance` for testing.

    Returns:
        A frozen :class:`Allowance` with the given parameters.
    """
    return Allowance(
        code=code,
        description=code,
        monthly=_time_series(monthly),
        role=role,
        apprenticeship_pct_relevant=apprenticeship_pct_relevant,
        service_months_threshold=service_months_threshold,
        provenance=None,
    )


def _policy_decision() -> PolicyDecision:
    """Build a minimal :class:`PolicyDecision` for testing.

    Returns:
        A :class:`PolicyDecision` with ordinary tax treatment.
    """
    return PolicyDecision(
        policy_id="test/pol",
        policy_version="1.0",
        effective_from=date(2020, 1, 1),
        effective_until=None,
        tax_treatment=TaxTreatment.ORDINARY,
        contribution_treatment=ContributionTreatment.INCLUDED,
        tfr_treatment=TfrTreatment.INCLUDED,
        cost_treatment=CostTreatment.EMPLOYEE_CASH,
        legal_basis="Test",
    )


def _policy(
    *,
    kinds: tuple[str, ...] = ("base_salary",),
    from_: date = date(2020, 1, 1),
    until: date | None = None,
) -> PayItemPolicy:
    """Build a minimal :class:`PayItemPolicy` for testing.

    Returns:
        A :class:`PayItemPolicy` covering the given kinds and period.
    """
    return PayItemPolicy(
        policy_id="test/pol",
        policy_version="1.0",
        applies_to_kinds=kinds,
        effective_from=from_,
        effective_until=until,
        default_decision=_policy_decision(),
    )


def _flat_increments(
    *,
    cadence: int = 24,
    maximum: int = 5,
    amount: str = "10.00",
    excluded_categories: tuple[str, ...] = (),
    apprentice_amount: str | None = None,
    first_cadence_months: int | None = None,
    first_cadence_months_by_category: dict[str, int] | None = None,
    amount_by_level_by_category: dict[str, dict[str, str]] | None = None,
    maximum_count_by_category: dict[str, int] | None = None,
) -> SeniorityIncrements:
    """Build a flat-mode :class:`SeniorityIncrements` for testing.

    Returns:
        A :class:`SeniorityIncrements` with the given parameters.
    """
    raw: dict[str, Any] = {
        "cadence_months": cadence,
        "maximum_count": maximum,
        "amount_by_level": {"L1": _series(amount)},
        "provenance": TEST_PROV,
        "excluded_categories": list(excluded_categories),
    }
    if apprentice_amount is not None:
        raw["apprentice_amount"] = _series(apprentice_amount)
    if first_cadence_months is not None:
        raw["first_cadence_months"] = first_cadence_months
    if first_cadence_months_by_category:
        raw["first_cadence_months_by_category"] = first_cadence_months_by_category
    if amount_by_level_by_category:
        raw["amount_by_level_by_category"] = {
            cat: {code: _series(v) for code, v in levels.items()}
            for cat, levels in amount_by_level_by_category.items()
        }
    if maximum_count_by_category:
        raw["maximum_count_by_category"] = maximum_count_by_category
    return SeniorityIncrements.model_validate(raw)


def _tiered_increments() -> SeniorityIncrements:
    """Build a two-tier :class:`SeniorityIncrements` for testing.

    Returns:
        A :class:`SeniorityIncrements` with 3 increments at 24-month cadence
        then 2 at 48-month cadence.
    """
    return SeniorityIncrements.model_validate({
        "cadence_months": 24,
        "maximum_count": 5,
        "amount_by_level": {},
        "tiers": [
            {
                "cadence_months": 24,
                "maximum_count": 3,
                "amount_by_level": {"L1": _series("10.00")},
                "provenance": TEST_PROV,
            },
            {
                "cadence_months": 48,
                "maximum_count": 2,
                "amount_by_level": {"L1": _series("15.00")},
                "provenance": TEST_PROV,
            },
        ],
        "provenance": TEST_PROV,
    })


def _ccnl_two_tracks_same_level() -> CCNL:
    """Build a CCNL with two percentage tracks both covering level 4.

    Returns:
        A :class:`CCNL` instance with ambiguous apprenticeship tracks.
    """
    raw = make_ccnl_dict(app_type="percentage")
    second_track = copy.deepcopy(raw["apprenticeship"][0])
    second_track["name"] = "alternative"
    raw["apprenticeship"].append(second_track)
    return CCNL.model_validate(raw)


class TestPayItemPolicyResolve:
    """PayItemPolicy.resolve() out-of-scope branches."""

    def test_kind_not_in_applies_to_kinds_returns_none(self) -> None:
        """resolve() returns None when the kind is not in applies_to_kinds."""
        pol = _policy(kinds=("base_salary",))
        assert pol.resolve("bonus", date(2025, 1, 1)) is None

    def test_as_of_before_effective_from_returns_none(self) -> None:
        """resolve() returns None when as_of is before effective_from."""
        pol = _policy(from_=date(2025, 1, 1))
        assert pol.resolve("base_salary", date(2020, 6, 1)) is None

    def test_as_of_after_effective_until_returns_none(self) -> None:
        """resolve() returns None when as_of is after effective_until."""
        pol = _policy(until=date(2024, 12, 31))
        assert pol.resolve("base_salary", date(2025, 6, 1)) is None

    def test_in_scope_returns_decision(self) -> None:
        """resolve() returns the default_decision when kind and date are in scope."""
        pol = _policy(from_=date(2020, 1, 1), until=date(2030, 12, 31))
        assert pol.resolve("base_salary", _AS_OF) is not None


class TestAllowanceActive:
    """_allowance_active branching logic."""

    def test_role_not_in_roles_returns_false(self) -> None:
        """Returns False when the allowance has a role not present in roles."""
        a = _allowance(role="manager")
        assert _allowance_active(a, frozenset({"driver"}), None) is False

    def test_no_role_no_threshold_returns_true(self) -> None:
        """Returns True when role is None and threshold is None."""
        a = _allowance(role=None, service_months_threshold=None)
        assert _allowance_active(a, frozenset(), None) is True

    def test_threshold_met(self) -> None:
        """Returns True when seniority_months >= service_months_threshold."""
        a = _allowance(service_months_threshold=12)
        assert _allowance_active(a, frozenset(), 24) is True

    def test_threshold_not_met(self) -> None:
        """Returns False when seniority_months < service_months_threshold."""
        a = _allowance(service_months_threshold=24)
        assert _allowance_active(a, frozenset(), 12) is False


# ---------------------------------------------------------------------------
# MonthlyPayChain
# ---------------------------------------------------------------------------


class TestMonthlyPayChain:
    """MonthlyPayChain.scaled_selective, scaled, for_extra_month, allowances_total."""

    def test_scaled_selective_non_relevant_allowance_uses_base_factor(self) -> None:
        """scaled_selective: base_factor only for apprenticeship-exempt allowances."""
        a_relevant = _allowance(
            code="BASE", apprenticeship_pct_relevant=True, monthly="100.00"
        )
        a_exempt = _allowance(
            code="EDR", apprenticeship_pct_relevant=False, monthly="50.00"
        )
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("0.00"),
            allowances=(
                (a_relevant, Decimal("100.00")),
                (a_exempt, Decimal("50.00")),
            ),
        )
        base_factor = Decimal("0.5")
        apprenticeship_pct = Decimal("0.8")
        result = chain.scaled_selective(base_factor, apprenticeship_pct)
        combined = base_factor * apprenticeship_pct
        assert result.allowances[0][1] == Decimal("100.00") * combined
        assert result.allowances[1][1] == Decimal("50.00") * base_factor

    def test_scaled_applies_factor_to_all_components(self) -> None:
        """scaled() multiplies base, seniority, and all allowances by factor."""
        a = _allowance(monthly="100.00")
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("50.00"),
            allowances=((a, Decimal("100.00")),),
        )
        result = chain.scaled(Decimal("0.5"))
        assert result.base == Decimal("500.00")
        assert result.seniority == Decimal("25.00")
        assert result.allowances[0][1] == Decimal("50.00")

    def test_for_extra_month_filters_by_months_per_year(self) -> None:
        """for_extra_month excludes allowances paid fewer than threshold times/year."""
        a_all = _allowance(code="ALL", monthly="10.00")
        a_12 = Allowance(
            code="A12",
            description="A12",
            monthly=_time_series("10.00"),
            months_per_year=12,
        )
        a_14 = Allowance(
            code="A14",
            description="A14",
            monthly=_time_series("10.00"),
            months_per_year=14,
        )
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("0.00"),
            allowances=(
                (a_all, Decimal("10.00")),
                (a_12, Decimal("10.00")),
                (a_14, Decimal("10.00")),
            ),
        )
        result = chain.for_extra_month(13)
        codes = {a.code for a, _ in result.allowances}
        assert "ALL" in codes
        assert "A12" not in codes
        assert "A14" in codes

    def test_allowances_total_sums_all_values(self) -> None:
        """allowances_total returns the rounded sum of all allowance amounts."""
        a1 = _allowance(code="A1", monthly="10.00")
        a2 = _allowance(code="A2", monthly="20.00")
        chain = MonthlyPayChain(
            base=Decimal("1000.00"),
            seniority=Decimal("0.00"),
            allowances=((a1, Decimal("10.00")), (a2, Decimal("20.00"))),
        )
        assert chain.allowances_total == Decimal("30.00")


class TestCountFromTiers:
    """_count_from_tiers multi-tier counting."""

    def test_single_tier_basic(self) -> None:
        """Single tier correctly counts increments and caps at maximum_count."""
        tier = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 5,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        assert _count_from_tiers((tier,), 48) == 2
        assert _count_from_tiers((tier,), 0) == 0
        assert _count_from_tiers((tier,), 120) == 5

    def test_multi_tier_boundary(self) -> None:
        """Multi-tier count correctly crosses tier boundaries."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        t2 = SeniorityTier.model_validate({
            "cadence_months": 48,
            "maximum_count": 2,
            "amount_by_level": {"L1": _series("15.00")},
            "provenance": TEST_PROV,
        })
        assert _count_from_tiers((t1, t2), 72 + 48) == 4
        assert _count_from_tiers((t1, t2), 72) == 3


class TestResolveTierAmount:
    """_resolve_tier_amount month-based, count-based, and error paths."""

    def test_month_based_single_tier(self) -> None:
        """Month-based dispatch returns correct amount for a single tier."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        result = _resolve_tier_amount((t1,), "L1", _AS_OF, seniority_months=48)
        assert result == Decimal("20.00")

    def test_month_based_loop_no_break(self) -> None:
        """Loop exits normally (no break) when months exactly fill a tier."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        result = _resolve_tier_amount((t1,), "L1", _AS_OF, seniority_months=72)
        assert result == Decimal("30.00")

    def test_count_based_all_tiers_consumed_no_break(self) -> None:
        """count_override consuming all tiers exits the loop without break."""
        inc = _tiered_increments()
        result = _resolve_tier_amount(inc.tiers, "L1", _AS_OF, count_override=5)
        assert result == Decimal("60.00")

    def test_both_none_raises(self) -> None:
        """Raises InvalidInputError when both month/count inputs are None."""
        t1 = SeniorityTier.model_validate({
            "cadence_months": 24,
            "maximum_count": 3,
            "amount_by_level": {"L1": _series("10.00")},
            "provenance": TEST_PROV,
        })
        with pytest.raises(InvalidInputError, match="seniority_months is required"):
            _resolve_tier_amount((t1,), "L1", _AS_OF)


class TestSeniorityLookups:
    """seniority_first_cadence and seniority_maximum override paths."""

    def test_first_cadence_category_override(self) -> None:
        """Category override takes precedence over per-level and global values."""
        inc = _flat_increments(
            cadence=24,
            first_cadence_months=36,
            first_cadence_months_by_category={"operaio": 24},
        )
        assert (
            seniority_first_cadence(inc, "L1", worker_category=WorkerCategory.OPERAIO)
            == 24
        )
        assert (
            seniority_first_cadence(inc, "L1", worker_category=WorkerCategory.IMPIEGATO)
            == 36
        )

    def test_maximum_category_override(self) -> None:
        """Category override to maximum_count_by_category takes precedence."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            maximum_count_by_category={"operaio": 3},
        )
        assert seniority_maximum(inc, "L1", worker_category=WorkerCategory.OPERAIO) == 3
        assert (
            seniority_maximum(inc, "L1", worker_category=WorkerCategory.IMPIEGATO) == 5
        )


class TestResolveSeniorityCount:
    """_resolve_seniority_count edge cases."""

    def test_exceeds_maximum_raises(self) -> None:
        """Raises InvalidInputError when seniority_count > maximum."""
        inc = _flat_increments(cadence=24, maximum=3)
        with pytest.raises(InvalidInputError, match="exceeds the maximum"):
            _resolve_seniority_count(
                inc, "L1", seniority_count=10, seniority_months=None
            )

    def test_excluded_category_returns_zero(self) -> None:
        """Excluded category returns 0 regardless of months elapsed."""
        inc = _flat_increments(cadence=24, maximum=5, excluded_categories=("operaio",))
        count = _resolve_seniority_count(
            inc,
            "L1",
            seniority_count=None,
            seniority_months=72,
            worker_category=WorkerCategory.OPERAIO,
        )
        assert count == 0

    def test_tiered_increments_uses_count_from_tiers(self) -> None:
        """Tiered mode dispatches to _count_from_tiers."""
        inc = _tiered_increments()
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=None, seniority_months=48
        )
        assert count == 2

    def test_below_first_cadence_returns_zero(self) -> None:
        """seniority_months below first_cadence yields count=0."""
        inc = _flat_increments(cadence=24, maximum=5, first_cadence_months=36)
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=None, seniority_months=24
        )
        assert count == 0

    def test_count_within_max_returns_count(self) -> None:
        """seniority_count within maximum is returned unchanged."""
        inc = _flat_increments(cadence=24, maximum=5)
        count = _resolve_seniority_count(
            inc, "L1", seniority_count=3, seniority_months=None
        )
        assert count == 3


class TestSeniorityAmount:
    """_seniority_amount paths: excluded category, apprentice, tiered, category."""

    def test_excluded_category_returns_zero(self) -> None:
        """Excluded category yields zero seniority amount."""
        inc = _flat_increments(cadence=24, maximum=5, excluded_categories=("operaio",))
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal(0)

    def test_apprentice_uses_apprentice_amount(self) -> None:
        """Apprentices use apprentice_amount * count."""
        inc = _flat_increments(cadence=24, maximum=5, apprentice_amount="5.00")
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=True,
            seniority_months=None,
        )
        assert result == Decimal("10.00")

    def test_apprentice_no_apprentice_amount_returns_zero(self) -> None:
        """Apprentices return zero when apprentice_amount is None."""
        inc = _flat_increments(cadence=24, maximum=5)
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=True,
            seniority_months=None,
        )
        assert result == Decimal(0)

    def test_category_specific_amounts(self) -> None:
        """Category-specific amount table takes precedence over level table."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            amount="10.00",
            amount_by_level_by_category={"operaio": {"L1": "7.00"}},
            maximum_count_by_category={"operaio": 5},
        )
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("21.00")

    def test_category_no_level_override_falls_through_to_level(self) -> None:
        """Category present but no override for this level falls to amount_by_level."""
        inc = _flat_increments(
            cadence=24,
            maximum=5,
            amount="10.00",
            amount_by_level_by_category={"operaio": {"L2": "7.00"}},
            maximum_count_by_category={"operaio": 5},
        )
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=WorkerCategory.OPERAIO,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("20.00")

    def test_tiered_uses_months(self) -> None:
        """Tiered mode uses seniority_months when provided."""
        inc = _tiered_increments()
        result = _seniority_amount(
            inc,
            "L1",
            count=3,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=72,
        )
        assert result == Decimal("30.00")

    def test_tiered_falls_back_to_count(self) -> None:
        """Tiered mode uses count when seniority_months is None."""
        inc = _tiered_increments()
        result = _seniority_amount(
            inc,
            "L1",
            count=2,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal("20.00")

    def test_level_not_in_amounts_returns_zero(self) -> None:
        """Unknown level code with no entry in amount_by_level returns zero."""
        inc = _flat_increments(cadence=24, maximum=5, amount="10.00")
        result = _seniority_amount(
            inc,
            "UNKNOWN_LEVEL",
            count=3,
            as_of=_AS_OF,
            worker_category=None,
            is_apprentice=False,
            seniority_months=None,
        )
        assert result == Decimal(0)


class TestFindPeriodIndex:
    """_find_period_index error paths."""

    def test_no_period_covers_months_elapsed_raises(self) -> None:
        """Raises OutOfScopeError when no period covers months_elapsed."""

        class _P:
            months_from: int = 0
            months_until: int | None = 12

        with pytest.raises(OutOfScopeError, match="no apprenticeship period"):
            _find_period_index([_P()], 24)

    def test_empty_periods_raises(self) -> None:
        """Raises OutOfScopeError when periods list is empty."""
        with pytest.raises(OutOfScopeError, match="no apprenticeship period"):
            _find_period_index([], 0)


class TestSelectTrack:
    """_select_track error and success paths."""

    def test_explicit_named_track_returns_track(self) -> None:
        """Named track matching the level is returned directly."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track="standard")
        track = _select_track(ccnl, level, employment)
        assert track.name == "standard"

    def test_explicit_wrong_level_raises(self) -> None:
        """Named track not covering the destination level raises OutOfScopeError."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level_2 = ccnl.level_by_code("2")
        employment = Apprentice(months_elapsed=0, track="standard")
        with pytest.raises(OutOfScopeError, match="does not cover destination level"):
            _select_track(ccnl, level_2, employment)

    def test_no_track_for_level_raises(self) -> None:
        """Level with no applicable track raises OutOfScopeError."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level_2 = ccnl.level_by_code("2")
        employment = Apprentice(months_elapsed=0, track=None)
        with pytest.raises(OutOfScopeError, match="has no apprenticeship track"):
            _select_track(ccnl, level_2, employment)

    def test_ambiguous_tracks_raises(self) -> None:
        """Level with multiple tracks raises OutOfScopeError when track is None."""
        ccnl = _ccnl_two_tracks_same_level()
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        with pytest.raises(
            OutOfScopeError, match="covered by several apprenticeship tracks"
        ):
            _select_track(ccnl, level, employment)


class TestApprenticeChain:
    """_apprentice_chain underclass and percentage track paths."""

    def test_underclass_track(self) -> None:
        """Under-classification track sets pct=None and code to pay level."""
        ccnl = make_minimal_ccnl(app_type="under_classification")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, pct, code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        assert pct is None
        assert code is not None
        assert chain.base > Decimal(0)

    def test_underclass_midpoint_to_destination(self) -> None:
        """midpoint_to_destination=True sets base to average of pay and dest level."""
        raw = make_ccnl_dict(app_type="under_classification")
        raw["apprenticeship"][0]["periods"][0]["midpoint_to_destination"] = True
        ccnl = CCNL.model_validate(raw)
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, _pct, _code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        pay_level = ccnl.level_by_code("3")
        dest_base = level.base_salary.value_at(_AS_OF)
        pay_base = pay_level.base_salary.value_at(_AS_OF)
        expected = money((pay_base + dest_base) / Decimal(2))
        assert chain.base == expected

    def test_percentage_track(self) -> None:
        """Percentage track sets pct to the period percentage and code=None."""
        ccnl = make_minimal_ccnl(app_type="percentage")
        level = ccnl.level_by_code("4")
        employment = Apprentice(months_elapsed=0, track=None)
        chain, pct, code = _apprentice_chain(
            ccnl,
            level,
            employment,
            count=0,
            roles=frozenset(),
            as_of=_AS_OF,
        )
        assert pct is not None
        assert code is None
        assert chain.base > Decimal(0)


class TestMiscCoverageGaps:
    """Remaining coverage gaps in primitives, facade, and loaders."""

    def test_payroll_engine_bundled(self) -> None:
        """PayrollEngine.bundled() returns a live engine instance."""
        engine = PayrollEngine.bundled()
        assert engine is not None

    def test_load_sick_pay_rates_returns_valid_rates(self) -> None:
        """load_sick_pay_rates() loads the bundled sick-pay JSON without error."""
        rates = load_sick_pay_rates()
        assert rates.carenza_days >= 0

    def test_overtime_band_collision_raises(self) -> None:
        """Two unconditional bands for the same WorkKind raise ValueError."""
        band_a = OvertimeBand(
            code="A",
            description="Band A",
            kind=TimeSupplementKind.PERCENTAGE,
            rate=_time_series("0.25"),
            applies_to_kinds=(WorkKind.WEEKDAY,),
        )
        band_b = OvertimeBand(
            code="B",
            description="Band B",
            kind=TimeSupplementKind.PERCENTAGE,
            rate=_time_series("0.30"),
            applies_to_kinds=(WorkKind.WEEKDAY,),
        )
        with pytest.raises(ValueError, match="Ambiguous OvertimeBand collisions"):
            TimeSupplements(
                hourly_base_method="minimo_tabellare",
                overtime_bands=(band_a, band_b),
            )
