"""Tests for Calculation / InputSnapshot provenance and reproducibility."""

from __future__ import annotations

import copy
import dataclasses
import typing
from collections import UserDict
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.engine.capability_catalog import (
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityStatus,
)
from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector

if TYPE_CHECKING:
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules
from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
)
from ccnl_engine.engine.payroll.domain.components import (
    CalculationStatus,
    ScopeItem,
)
from ccnl_engine.engine.payroll.domain.employee import SeniorityByCount
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.engine.payroll.domain.pay_items import (
    BaseSalaryEarning,
    CompetencePeriod,
)
from ccnl_engine.engine.payroll.domain.payroll_result import PeriodPayroll
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
    TaxPeriod,
)
from ccnl_engine.engine.payroll.domain.supplements import FringeBenefitInput
from ccnl_engine.engine.payroll.service.assembly import _ruleset_versions
from ccnl_engine.engine.payroll.service.orchestrator import (
    estimate_annual,
    estimate_period_effects,
)
from ccnl_engine.engine.primitives import FrozenDict
from ccnl_engine.engine.serialization.dataclass_codec import (
    _deep_freeze,
    _dump,
    _load_by_hint,
    _load_union,
)
from ccnl_engine.engine.serialization.envelope import reproduce
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _CCNL_FILENAME,
    _req,
)

compute = estimate_annual

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[YearRules] = [_DEFAULT_RULES]


class _MockRepo:
    """KnowledgeRepository stub for the autouse _reset_mock_state fixture."""

    def load_ccnl(self, filename: str) -> CCNL:
        return _mock_ccnl[0]

    def load_year_rules(
        self, year: int, sector: TaxSector, num_employees: int
    ) -> YearRules:
        return _mock_rules[0]

    def load_surtax_rules(self, year: int) -> SurtaxRules | None:
        return None

    def load_capability_catalog(self, year: int) -> CapabilityCatalog:
        return CapabilityCatalog(year=year, capabilities=())


_REPO = _MockRepo()


@pytest.fixture(autouse=True)
def _reset_mock_state() -> None:
    """Reset mutable mock state before each test."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_DEFAULT_RULES]


def _scenario() -> _InternalScenario:
    return _InternalScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByCount(value=2),
        ),
        employment=Employment(
            ccnl=_CCNL_FILENAME,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 6, 1),
        ),
    )


class TestInputSnapshot:
    """InputSnapshot captures and materialises raw inputs losslessly."""

    def test_capture_and_materialise(self) -> None:
        """capture()->materialise() rebuilds the same PayrollScenario."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=True,
        )
        recovered = snapshot.materialise()
        assert isinstance(recovered, _InternalScenario)
        assert snapshot.ccnl_id == "test"
        assert snapshot.year == 2026
        assert snapshot.uses_surtax is True

    def test_materialise_preserves_tax_year_override(self) -> None:
        """materialise() round-trips Optional[int] tax_year when non-None."""
        scenario = _InternalScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl=_CCNL_FILENAME,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                as_of=date(2025, 11, 1),
                tax_year=2026,
            ),
        )
        snapshot = InputSnapshot.capture(
            scenario=scenario,
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        recovered = snapshot.materialise()
        assert recovered.employment.tax_year == 2026
        assert recovered.employment.as_of.year == 2025

    def test_roundtrip_dict_json(self) -> None:
        """to_dict/from_dict and to_json/from_json round-trip."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        assert InputSnapshot.from_dict(snapshot.to_dict()) == snapshot
        assert InputSnapshot.from_json(snapshot.to_json()) == snapshot

    def test_missing_key_raises(self) -> None:
        """from_dict raises KeyError when a required key is absent."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        data = snapshot.to_dict()
        data.pop("year")
        with pytest.raises(KeyError):
            InputSnapshot.from_dict(data)


class TestInputSnapshotStrictDeserialisation:
    """from_dict rejects coercions and extra keys."""

    def _base(self) -> dict[str, object]:
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        return snapshot.to_dict()

    def test_uses_surtax_string_false_rejected(self) -> None:
        """'false' string for uses_surtax must raise TypeError, not be coerced."""
        data = self._base()
        data["uses_surtax"] = "false"
        with pytest.raises(TypeError, match="uses_surtax"):
            InputSnapshot.from_dict(data)

    def test_uses_surtax_string_true_rejected(self) -> None:
        """'true' string for uses_surtax must raise TypeError, not be coerced."""
        data = self._base()
        data["uses_surtax"] = "true"
        with pytest.raises(TypeError, match="uses_surtax"):
            InputSnapshot.from_dict(data)

    def test_uses_surtax_int_zero_rejected(self) -> None:
        """Integer 0 for uses_surtax must raise TypeError."""
        data = self._base()
        data["uses_surtax"] = 0
        with pytest.raises(TypeError, match="uses_surtax"):
            InputSnapshot.from_dict(data)

    def test_uses_surtax_int_one_rejected(self) -> None:
        """Integer 1 for uses_surtax must raise TypeError."""
        data = self._base()
        data["uses_surtax"] = 1
        with pytest.raises(TypeError, match="uses_surtax"):
            InputSnapshot.from_dict(data)

    def test_ccnl_id_int_rejected(self) -> None:
        """Integer ccnl_id must raise TypeError, not be silently str()d."""
        data = self._base()
        data["ccnl_id"] = 42
        with pytest.raises(TypeError, match="ccnl_id"):
            InputSnapshot.from_dict(data)

    def test_year_string_rejected(self) -> None:
        """String year must raise TypeError, not be coerced via int(str(...))."""
        data = self._base()
        data["year"] = "2026"
        with pytest.raises(TypeError, match="year"):
            InputSnapshot.from_dict(data)

    def test_year_bool_rejected(self) -> None:
        """Bool True for year must raise TypeError (bool is subclass of int)."""
        data = self._base()
        data["year"] = True
        with pytest.raises(TypeError, match="year"):
            InputSnapshot.from_dict(data)

    def test_scenario_non_dict_rejected(self) -> None:
        """A non-dict scenario must raise TypeError."""
        data = self._base()
        data["scenario"] = "not_a_dict"
        with pytest.raises(TypeError, match="scenario"):
            InputSnapshot.from_dict(data)

    def test_extra_key_rejected(self) -> None:
        """Extra keys not produced by to_dict must raise TypeError."""
        data = self._base()
        data["extra_field"] = "unexpected"
        with pytest.raises(TypeError, match="unexpected keys"):
            InputSnapshot.from_dict(data)


class TestCalculation:
    """Calculation carries provenance and reproduces an identical result."""

    def test_compute_returns_calculation(self) -> None:
        """Compute returns a Calculation with engine version and rulesets."""
        calc = estimate_annual(_req(), repo=_REPO)
        assert isinstance(calc, Calculation)
        assert calc.engine_version == "0.5.1"
        assert calc.ruleset_version["ccnl"] == "test@2026.2"
        assert calc.ruleset_version["tax"] == "test/rules@2026.2"
        assert calc.ruleset_version["inps"] == "test/rules@2026.2"
        assert "surtax" not in calc.ruleset_version

    def test_compute_exposes_ruleset_verification(self) -> None:
        """Compute populates ruleset_verification with VerificationStatus values."""
        calc = estimate_annual(_req(), repo=_REPO)
        # The test CCNL has no ruleset identity; tax/inps have verified identities.
        assert calc.ruleset_verification["ccnl"] == "unverified"
        assert calc.ruleset_verification["tax"] == "verified"
        assert calc.ruleset_verification["inps"] == "verified"
        assert "surtax_regional" not in calc.ruleset_verification

    def test_ruleset_verification_is_frozen(self) -> None:
        """ruleset_verification must reject item assignment after construction."""
        calc = estimate_annual(_req(), repo=_REPO)
        with pytest.raises(TypeError):
            calc.ruleset_verification["ccnl"] = "tampered"  # type: ignore[index]

    def test_to_dict_includes_ruleset_verification(self) -> None:
        """to_dict() includes ruleset_verification when non-empty."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        assert "ruleset_verification" in d
        rv = d["ruleset_verification"]
        assert isinstance(rv, dict)
        assert rv["tax"] == "verified"

    def test_to_dict_omits_ruleset_verification_when_empty(self) -> None:
        """to_dict() omits ruleset_verification when the mapping is empty."""
        calc = estimate_annual(_req(), repo=_REPO)
        calc_no_ver = Calculation(
            engine_version=calc.engine_version,
            ruleset_version=calc.ruleset_version,
            input_snapshot=calc.input_snapshot,
            result=calc.result,
            trace=calc.trace,
        )
        d = calc_no_ver.to_dict()
        assert "ruleset_verification" not in d

    def test_from_dict_restores_ruleset_verification(self) -> None:
        """from_dict() restores ruleset_verification from the dict."""
        calc = estimate_annual(_req(), repo=_REPO)
        restored = Calculation.from_dict(calc.to_dict())
        assert restored.ruleset_verification == calc.ruleset_verification

    def test_from_dict_absent_ruleset_verification_gives_empty(self) -> None:
        """from_dict() with no ruleset_verification key gives an empty mapping."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d.pop("ruleset_verification", None)
        restored = Calculation.from_dict(d)
        assert len(restored.ruleset_verification) == 0
        assert type(calc.result.net_annual) is Decimal

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """to_dict/from_dict round-trips the full calculation."""
        calc = estimate_annual(_req(), repo=_REPO)
        restored = Calculation.from_dict(calc.to_dict())
        assert restored == calc
        assert restored.engine_version == calc.engine_version
        assert restored.input_snapshot == calc.input_snapshot
        assert restored.result == calc.result

    def test_to_json_from_json_roundtrip(self) -> None:
        """to_json/from_json round-trips through a JSON string."""
        calc = estimate_annual(_req(), repo=_REPO)
        restored = Calculation.from_json(calc.to_json())
        assert restored == calc

    def test_reproduce_identical_result(self) -> None:
        """reproduce(, repo=_REPO) yields the identical result without external args."""
        calc = estimate_annual(_req(), repo=_REPO)
        replayed = reproduce(calc, repo=_REPO)
        assert replayed.result == calc.result
        assert replayed.input_snapshot == calc.input_snapshot
        assert replayed.engine_version == calc.engine_version

    def test_reproduce_preserves_seniority_variant(self) -> None:
        """Union member type is preserved through snapshot/reproduce."""
        calc = estimate_annual(_req(seniority_count=2), repo=_REPO)
        replayed = reproduce(calc, repo=_REPO)
        assert isinstance(replayed.input_snapshot, InputSnapshot)
        # The materialised seniority should still be by-count.
        scenario = replayed.input_snapshot.materialise()
        assert isinstance(scenario.employee.seniority, SeniorityByCount)
        assert scenario.employee.seniority.value == 2

    def test_reproduce_raises_on_engine_version_drift(self) -> None:
        """Reproduce raises ValueError when engine_version does not match."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["engine_version"] = "0.0.0"
        stale = Calculation.from_dict(d)
        with pytest.raises(ValueError, match="version drift"):
            reproduce(stale, repo=_REPO)

    def test_reproduce_allow_drift_flag_suppresses_error(self) -> None:
        """reproduce(allow_version_drift=True, repo=_REPO) succeeds despite mismatch."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["engine_version"] = "0.0.0"
        stale = Calculation.from_dict(d)
        replayed = reproduce(stale, allow_version_drift=True, repo=_REPO)
        assert replayed.result.net_annual == calc.result.net_annual

    def test_reproduce_raises_on_ruleset_version_drift(self) -> None:
        """Reproduce raises ValueError when a ruleset identity does not match."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["ruleset_version"] = {"ccnl": "old@0", "tax": "old@0"}
        stale = Calculation.from_dict(d)
        with pytest.raises(ValueError, match="version drift"):
            reproduce(stale, repo=_REPO)

    def test_copy_deepcopy_snapshot(self) -> None:
        """copy.deepcopy on InputSnapshot must not raise TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        snapshot_copy = copy.deepcopy(calc.input_snapshot)
        assert snapshot_copy == calc.input_snapshot

    def test_copy_deepcopy_calculation(self) -> None:
        """copy.deepcopy on a full Calculation must not raise TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        calc_copy = copy.deepcopy(calc)
        assert calc_copy == calc
        assert calc_copy.result == calc.result

    def test_copy_shallow_snapshot(self) -> None:
        """copy.copy on InputSnapshot must not raise TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        snapshot_copy = copy.copy(calc.input_snapshot)
        assert snapshot_copy == calc.input_snapshot

    def test_ruleset_version_is_frozen(self) -> None:
        """ruleset_version must reject item assignment after construction."""
        calc = estimate_annual(_req(), repo=_REPO)
        with pytest.raises(TypeError):
            calc.ruleset_version["ccnl"] = "tampered"  # type: ignore[index]

    def test_snapshot_scenario_is_frozen(self) -> None:
        """snapshot.scenario must reject item assignment after construction."""
        calc = estimate_annual(_req(), repo=_REPO)
        with pytest.raises(TypeError):
            calc.input_snapshot.scenario["ccnl"] = "tampered"  # type: ignore[index]


class TestDumpLoadBranches:
    """Direct coverage of the remaining _dump/_load_by_hint branches."""

    def test_dump_enum_serialises_value(self) -> None:
        """Enum members dump to their value."""

        class _Plain(Enum):
            A = 1

        assert _dump(_Plain.A) == 1  # plain Enum hits the .value path
        assert _dump(TaxSector.TERZIARIO) == "terziario"

    def test_load_union_non_dict_raw_falls_through(self) -> None:
        """A non-dict raw value is tried against every union member."""
        with pytest.raises(ValueError, match="No union member matched"):
            _load_union([str, SeniorityByCount], "not-a-dict")

    def test_load_by_hint_coerces_enum(self) -> None:
        """_load_by_hint reconstructs an Enum member from a string value."""
        assert _load_by_hint(TaxSector, "terziario") is TaxSector.TERZIARIO

    def test_load_by_hint_unwraps_annotated(self) -> None:
        """An Annotated hint is unwrapped before reconstruction."""
        hint = typing.Annotated[SeniorityByCount, object()]
        loaded = _load_by_hint(hint, {"$type": "SeniorityByCount", "value": 7})
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 7

    def test_load_by_hint_tuple(self) -> None:
        """A tuple hint builds a tuple of loaded elements."""
        data = [{"$type": "SeniorityByCount", "value": 1}]
        loaded = _load_by_hint(tuple[SeniorityByCount, ...], data)
        assert isinstance(loaded, tuple)
        assert loaded == (SeniorityByCount(value=1),)

    def test_load_by_hint_list(self) -> None:
        """A list hint builds a list of loaded elements."""
        loaded = _load_by_hint(list[int], [1, 2])
        assert loaded == [1, 2]

    def test_load_by_hint_scalar_pass_through(self) -> None:
        """A plain scalar hint returns the raw JSON-native value."""
        assert _load_by_hint(int, 42) == 42
        assert _load_by_hint(str, "x") == "x"

    def test_load_by_hint_unknown_type_falls_through(self) -> None:
        """A hint not in any explicit branch returns raw unchanged (fallback)."""
        raw = b"blob"
        assert _load_by_hint(bytes, raw) is raw

    def test_load_by_hint_pydantic_model_validate(self) -> None:
        """Pydantic hints are validated via model_validate."""
        assert isinstance(_load_by_hint(Permanent, {"type": "permanent"}), Permanent)

    def test_ruleset_fallback_ids(self) -> None:
        """Rulesets without a block fall back to knowledge-version ids."""
        ccnl = make_minimal_ccnl()
        # Pass ruleset=None so the fallback path is exercised.
        rules = make_year_rules(ruleset=None, inps_ruleset=None)
        versions = _ruleset_versions(ccnl, rules, surtax=None)
        assert versions["ccnl"] == "test@2026.2"
        assert versions["tax"] == "tax/2026/terziario@2026.2"
        # Standard percentage model without inps_ruleset emits a fallback entry.
        assert versions["inps"] == "inps/2026/terziario@2026.2"
        assert "surtax" not in versions

    def test_ruleset_verifications_fallback_when_no_inps_ruleset(self) -> None:
        """Falls back to 'unverified' for inps when inps_ruleset is absent."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules(ruleset=None, inps_ruleset=None)
        req = _req()
        _mock_ccnl[:] = [ccnl]
        _mock_rules[:] = [rules]
        calc = compute(req, repo=_REPO)
        assert calc.ruleset_verification["inps"] == "unverified"


class TestDeepImmutability:
    """InputSnapshot.scenario and Calculation.ruleset_version are deeply frozen."""

    def test_snapshot_scenario_top_level_is_immutable(self) -> None:
        """Assigning a top-level key on scenario raises TypeError."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        with pytest.raises(TypeError):
            snapshot.scenario["injected"] = "x"  # type: ignore[index]

    def test_snapshot_scenario_nested_dict_is_immutable(self) -> None:
        """Mutating a nested dict inside scenario raises TypeError."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        nested = snapshot.scenario["employee"]
        with pytest.raises(TypeError):
            nested["level_code"] = "tampered"  # type: ignore[index]

    def test_snapshot_to_dict_returns_mutable_copy(self) -> None:
        """to_dict() returns a plain, mutable dict that does not alias scenario."""
        snapshot = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        d = snapshot.to_dict()
        scenario_copy = d["scenario"]
        assert isinstance(scenario_copy, dict)
        # Mutating the returned copy must not affect the frozen snapshot.
        scenario_copy["injected"] = "x"
        assert "injected" not in snapshot.scenario

    def test_ruleset_version_is_immutable(self) -> None:
        """Assigning a key on ruleset_version raises TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        with pytest.raises(TypeError):
            calc.ruleset_version["ccnl"] = "tampered"  # type: ignore[index]

    def test_from_dict_without_trace_key_uses_empty_trace(self) -> None:
        """from_dict() succeeds and returns empty trace when 'trace' key is absent."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d.pop("trace")
        restored = Calculation.from_dict(d)
        assert restored.trace == CalculationTrace(steps=())
        assert restored.result == calc.result

    def test_reproduce_stable_after_to_dict_mutation(self) -> None:
        """reproduce(, repo=_REPO) is stable even if to_dict() output is mutated."""
        calc = estimate_annual(_req(), repo=_REPO)
        original_net = calc.result.net_annual
        d = calc.to_dict()
        # Tamper with the serialised copy — must not affect reproduce(, repo=_REPO).
        d["input_snapshot"]["scenario"]["employee"]["level_code"] = "1"  # type: ignore[index]
        replayed = reproduce(calc, repo=_REPO)
        assert replayed.result.net_annual == original_net

    def test_deep_freeze_user_dict_produces_frozen_dict(self) -> None:
        """_deep_freeze converts UserDict (and nested ones) to FrozenDict."""
        ud: UserDict[str, object] = UserDict({"a": 1, "nested": UserDict({"b": 2})})
        result = _deep_freeze(ud)
        assert isinstance(result, FrozenDict)
        nested = result["nested"]
        assert isinstance(nested, FrozenDict)
        assert nested["b"] == 2

    def test_input_snapshot_user_dict_not_aliased(self) -> None:
        """Mutating a UserDict passed as scenario after construction is a no-op."""
        source: UserDict[str, object] = UserDict({"key": "value"})
        snap = InputSnapshot(
            ccnl_id="test",
            tax_sector="terziario",
            year=2026,
            uses_surtax=False,
            scenario=source,
        )
        source["injected"] = "mutated"
        assert "injected" not in snap.scenario


class TestNestedBoolValidation:
    """materialise() behaviour for nested bool scenario fields.

    Pydantic coerces common bool representations (string "false", integer 0)
    to the Python bool type, so materialise() succeeds for those inputs.
    """

    def _snapshot_with_bool_field(self, field: str, value: object) -> InputSnapshot:
        """Capture a snapshot and tamper with a nested employee bool field.

        Returns:
            A new :class:`InputSnapshot` with the given field overridden.
        """
        snap = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        d = snap.to_dict()
        scenario_raw = typing.cast("dict[str, object]", d["scenario"])
        employee_raw = typing.cast("dict[str, object]", scenario_raw["employee"])
        employee_dict = dict(employee_raw)
        employee_dict[field] = value
        scenario_dict = dict(scenario_raw)
        scenario_dict["employee"] = employee_dict
        d["scenario"] = scenario_dict
        return InputSnapshot.from_dict(d)

    def test_ivs_ceiling_applies_string_false_coerced(self) -> None:
        """String 'false' for ivs_ceiling_applies is coerced to False by Pydantic."""
        snap = self._snapshot_with_bool_field("ivs_ceiling_applies", "false")
        scenario = snap.materialise()
        assert scenario.employee.ivs_ceiling_applies is False

    def test_ivs_ceiling_applies_int_zero_coerced(self) -> None:
        """Integer 0 for ivs_ceiling_applies is coerced to False by Pydantic."""
        snap = self._snapshot_with_bool_field("ivs_ceiling_applies", 0)
        scenario = snap.materialise()
        assert scenario.employee.ivs_ceiling_applies is False

    def test_replay_identity(self) -> None:
        """A round-tripped snapshot reproduces the same net_annual."""
        calc = estimate_annual(_req(), repo=_REPO)
        original_net = calc.result.net_annual
        restored = Calculation.from_dict(calc.to_dict())
        replayed = reproduce(restored, repo=_REPO)
        assert replayed.result.net_annual == original_net


class TestCollectionHintGuard:
    """_load_by_hint rejects strings/dicts for collection hints."""

    def test_frozenset_hint_string_rejected(self) -> None:
        """A string is rejected for a frozenset hint."""
        with pytest.raises(TypeError, match="expected a sequence"):
            _load_by_hint(frozenset[str], "quadro")

    def test_list_hint_string_rejected(self) -> None:
        """A string is rejected for a list hint."""
        with pytest.raises(TypeError, match="expected a sequence"):
            _load_by_hint(list[str], "quadro")

    def test_tuple_hint_string_rejected(self) -> None:
        """A string is rejected for a tuple hint."""
        with pytest.raises(TypeError, match="expected a sequence"):
            _load_by_hint(tuple[str, ...], "quadro")

    def test_snapshot_string_roles_rejected(self) -> None:
        """A snapshot with roles as string raises instead of silently exploding."""
        snap = InputSnapshot.capture(
            scenario=_scenario(),
            ccnl_id="test",
            tax_sector=TaxSector.TERZIARIO,
            year=2026,
            uses_surtax=False,
        )
        d = snap.to_dict()
        scenario_d = dict(typing.cast("dict[str, object]", d["scenario"]))
        employee_d = dict(typing.cast("dict[str, object]", scenario_d["employee"]))
        employee_d["roles"] = "quadro"
        scenario_d["employee"] = employee_d
        d["scenario"] = scenario_d
        tampered = InputSnapshot.from_dict(d)
        with pytest.raises((TypeError, ValueError)):
            tampered.materialise()


class TestCalculationFromDictStrictValidation:
    """Calculation.from_dict rejects wrong types for version fields."""

    def test_engine_version_int_rejected(self) -> None:
        """Integer engine_version raises TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["engine_version"] = 5
        with pytest.raises(TypeError, match="engine_version"):
            Calculation.from_dict(d)

    def test_ruleset_version_int_value_rejected(self) -> None:
        """Integer value in ruleset_version raises TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["ruleset_version"] = {"ccnl": 42}
        with pytest.raises(TypeError, match="ruleset_version"):
            Calculation.from_dict(d)

    def test_ruleset_verification_int_value_rejected(self) -> None:
        """Integer value in ruleset_verification raises TypeError."""
        calc = estimate_annual(_req(), repo=_REPO)
        d = calc.to_dict()
        d["ruleset_verification"] = {"ccnl": 42}
        with pytest.raises(TypeError, match="ruleset_verification"):
            Calculation.from_dict(d)


def _annual_scenario() -> AnnualEstimateInput:
    return AnnualEstimateInput(
        employee=Employee(level_code="4"),
        employment=Employment(
            ccnl=_CCNL_FILENAME,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=date(2026, 6, 1),
        ),
    )


class TestResultFromDictPeriodPayroll:
    """_result_from_dict dispatches to PeriodPayroll when pay_period key present."""

    def test_calculation_roundtrip_with_period_gives_period_payroll(self) -> None:
        """Calculation.from_dict on a period result produces PeriodPayroll."""
        calc = estimate_period_effects(
            _annual_scenario(),
            PeriodPayrollInput(
                tax_period=TaxPeriod(
                    start=date(2026, 1, 1),
                    end=date(2026, 12, 31),
                    eligible_work_days=365,
                ),
                fringe_benefit_input=FringeBenefitInput(annual_amount=Decimal(300)),
            ),
            repo=_REPO,
        )
        assert isinstance(calc.result, PeriodPayroll)
        raw = calc.to_dict()
        restored = Calculation.from_dict(raw)
        assert isinstance(restored.result, PeriodPayroll)
        assert restored.result.net_annual == calc.result.net_annual


class TestCheckCapabilityGaps:
    """Calculation.check_capability_gaps delegates to the catalog."""

    def test_check_capability_gaps_returns_empty_for_empty_catalog(self) -> None:
        """check_capability_gaps returns () when the catalog has no entries."""
        calc = estimate_annual(_req(), repo=_REPO)
        catalog = CapabilityCatalog(year=2026, capabilities=())
        assert calc.check_capability_gaps(catalog) == ()

    def test_check_capability_gaps_no_gap_when_feature_computed(self) -> None:
        """check_capability_gaps returns () when a computed feature matches declared."""
        calc = estimate_annual(_req(), repo=_REPO)
        catalog = CapabilityCatalog(
            year=2026,
            capabilities=(
                CapabilityEntry(
                    feature="base_salary", status=CapabilityStatus.COMPUTED
                ),
            ),
        )
        gaps = calc.check_capability_gaps(catalog)
        assert gaps == ()

    def test_check_capability_gaps_reports_not_computed_feature(self) -> None:
        """check_capability_gaps returns a gap for a not-computed declared feature."""
        calc = estimate_annual(_req(), repo=_REPO)
        # Inject a scope item with not_computed status to exercise the gap path.
        extra = ScopeItem(
            feature="some_feature", calculation_status=CalculationStatus.NOT_COMPUTED
        )
        existing_scope = calc.result.coverage.calculation_scope
        patched_coverage = dataclasses.replace(
            calc.result.coverage,
            calculation_scope=(*existing_scope, extra),
        )
        patched_result = dataclasses.replace(calc.result, coverage=patched_coverage)
        patched_calc = dataclasses.replace(calc, result=patched_result)
        catalog = CapabilityCatalog(
            year=2026,
            capabilities=(
                CapabilityEntry(
                    feature="some_feature",
                    status=CapabilityStatus.COMPUTED,
                ),
            ),
        )
        gaps = patched_calc.check_capability_gaps(catalog)
        assert len(gaps) == 1
        assert gaps[0].feature == "some_feature"
        assert gaps[0].declared == CapabilityStatus.COMPUTED
        assert gaps[0].observed == "not_computed"

    def test_check_capability_gaps_ignores_not_applicable_entries(self) -> None:
        """check_capability_gaps ignores entries with NOT_APPLICABLE status."""
        calc = estimate_annual(_req(), repo=_REPO)
        catalog = CapabilityCatalog(
            year=2026,
            capabilities=(
                CapabilityEntry(
                    feature="nonexistent_feature",
                    status=CapabilityStatus.NOT_APPLICABLE,
                ),
            ),
        )
        assert calc.check_capability_gaps(catalog) == ()


class TestCalculationAuditRoundTrip:
    """ledger_entries and pay_items survive a to_dict/from_dict round-trip."""

    def _base_calc(self) -> Calculation:
        return estimate_annual(_req(), repo=_REPO)

    def _ledger_entry(self) -> LedgerEntry:
        return LedgerEntry(
            entry_id="e1",
            competence_period=CompetencePeriod(year=2026, month=1),
            payment_date=date(2026, 1, 31),
            pay_item_id="pi1",
            pay_item_kind="base_salary_earning",
            account=AccountKind.CASH_EARNINGS,
            amount=Decimal("1500.00"),
            source_item_id="pi1",
            policy_decision_id="pd1",
        )

    def _pay_item(self) -> BaseSalaryEarning:
        return BaseSalaryEarning(
            item_id="pi1",
            competence_period=CompetencePeriod(year=2026, month=1),
            payment_date=date(2026, 1, 31),
            quantity=Decimal(1),
            amount=Decimal("1500.00"),
        )

    def test_ledger_entries_survive_round_trip(self) -> None:
        """ledger_entries are preserved through to_dict/from_dict."""
        base = self._base_calc()
        entry = self._ledger_entry()
        calc = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            ledger_entries=(entry,),
        )
        restored = Calculation.from_dict(calc.to_dict())
        assert len(restored.ledger_entries) == 1
        assert restored.ledger_entries[0] == entry

    def test_pay_items_survive_round_trip(self) -> None:
        """pay_items are preserved through to_dict/from_dict."""
        base = self._base_calc()
        item = self._pay_item()
        calc = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            pay_items=(item,),
        )
        restored = Calculation.from_dict(calc.to_dict())
        assert len(restored.pay_items) == 1
        assert restored.pay_items[0] == item

    def test_source_item_id_and_policy_decision_id_preserved(self) -> None:
        """source_item_id and policy_decision_id on LedgerEntry survive round-trip."""
        base = self._base_calc()
        entry = self._ledger_entry()
        calc = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            ledger_entries=(entry,),
        )
        restored = Calculation.from_dict(calc.to_dict())
        r = restored.ledger_entries[0]
        assert r.source_item_id == "pi1"
        assert r.policy_decision_id == "pd1"

    def test_equality_includes_ledger_entries(self) -> None:
        """Two Calculations differing only in ledger_entries are not equal."""
        base = self._base_calc()
        entry = self._ledger_entry()
        with_entry = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            ledger_entries=(entry,),
        )
        without_entry = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
        )
        assert with_entry != without_entry

    def test_equality_includes_pay_items(self) -> None:
        """Two Calculations differing only in pay_items are not equal."""
        base = self._base_calc()
        item = self._pay_item()
        with_item = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            pay_items=(item,),
        )
        without_item = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
        )
        assert with_item != without_item

    def test_empty_ledger_and_pay_items_omitted_from_dict(self) -> None:
        """to_dict omits ledger_entries/pay_items when both are empty."""
        base = self._base_calc()
        calc = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
        )
        d = calc.to_dict()
        assert "ledger_entries" not in d
        assert "pay_items" not in d

    def test_round_trip_json_preserves_audit_artifacts(self) -> None:
        """to_json/from_json preserves ledger_entries and pay_items."""
        base = self._base_calc()
        calc = Calculation(
            engine_version=base.engine_version,
            ruleset_version=base.ruleset_version,
            input_snapshot=base.input_snapshot,
            result=base.result,
            trace=base.trace,
            ledger_entries=(self._ledger_entry(),),
            pay_items=(self._pay_item(),),
        )
        restored = Calculation.from_json(calc.to_json())
        assert restored == calc


class TestInternalScenarioValidation:
    """_InternalScenario rejects negative override amounts."""

    def test_negative_prior_irpef_raises(self) -> None:
        """Negative prior_period_irpef_withheld is rejected by _InternalScenario."""
        with pytest.raises(Exception, match="prior_period_irpef_withheld"):
            _InternalScenario(
                employee=Employee(level_code="4"),
                employment=Employment(
                    ccnl=_CCNL_FILENAME,
                    contract=Permanent(),
                    employer=Employer(num_employees=50),
                    as_of=date(2026, 6, 1),
                ),
                prior_period_irpef_withheld=Decimal(-1),
            )
