"""Tests for Calculation / InputSnapshot provenance and reproducibility."""

import copy
import typing
from collections import UserDict
from datetime import date
from decimal import Decimal
from enum import Enum

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
from ccnl_engine.engine.payroll.domain.art15 import Art15Deductions
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    CalculationTrace,
    InputSnapshot,
    _deep_freeze,
    _dump,
    _load_by_hint,
    _load_dataclass,
    _load_union,
)
from ccnl_engine.engine.payroll.domain.employee import SeniorityByCount
from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.scenario import (
    Employee,
    Employer,
    Employment,
    PayrollScenario,
)
from ccnl_engine.engine.payroll.domain.supplements import OvertimeHours
from ccnl_engine.engine.payroll.service.assembly import _ruleset_versions
from ccnl_engine.engine.payroll.service.orchestrator import compute
from ccnl_engine.engine.primitives import FrozenDict
from tests.helpers import make_minimal_ccnl, make_year_rules
from tests.unit.ccnl_engine.engine.payroll.service.builders import (
    _CCNL_FILENAME,
    _req,
)

# ---------------------------------------------------------------------------
# Module-level mutable mock state (reset per-test by the autouse fixture)
# ---------------------------------------------------------------------------

_DEFAULT_CCNL = make_minimal_ccnl()
_DEFAULT_RULES = make_year_rules()

_mock_ccnl: list[CCNL] = [_DEFAULT_CCNL]
_mock_rules: list[object] = [_DEFAULT_RULES]


@pytest.fixture(autouse=True)
def _patch_loaders(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the three loaders in orchestrator and reset mock state."""
    _mock_ccnl[:] = [_DEFAULT_CCNL]
    _mock_rules[:] = [_DEFAULT_RULES]
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_ccnl",
        lambda _: _mock_ccnl[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_year_rules",
        lambda *_: _mock_rules[0],
    )
    monkeypatch.setattr(
        "ccnl_engine.engine.payroll.service.orchestrator.load_surtax_rules",
        lambda _: None,
    )


def _scenario() -> PayrollScenario:
    return PayrollScenario(
        employee=Employee(
            level_code="4",
            seniority=SeniorityByCount(2),
        ),
        employment=Employment(
            ccnl=_CCNL_FILENAME,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            calculation_date=date(2026, 6, 1),
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
        assert isinstance(recovered, PayrollScenario)
        assert snapshot.ccnl_id == "test"
        assert snapshot.year == 2026
        assert snapshot.uses_surtax is True

    def test_materialise_preserves_tax_year_override(self) -> None:
        """materialise() round-trips Optional[int] tax_year when non-None."""
        scenario = PayrollScenario(
            employee=Employee(level_code="4"),
            employment=Employment(
                ccnl=_CCNL_FILENAME,
                contract=Permanent(),
                employer=Employer(num_employees=50),
                calculation_date=date(2025, 11, 1),
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
        assert recovered.employment.calculation_date.year == 2025

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
        calc = compute(_req())
        assert isinstance(calc, Calculation)
        assert calc.engine_version == "0.5.1"
        assert calc.ruleset_version["ccnl"] == "test@2026.2"
        assert calc.ruleset_version["tax"] == "test/rules@2026.2"
        assert calc.ruleset_version["inps"] == "test/rules@2026.2"
        assert "surtax" not in calc.ruleset_version
        assert type(calc.result.net_annual) is Decimal

    def test_result_delegation(self) -> None:
        """Unknown attributes read through to the PayrollResult result."""
        calc = compute(_req())
        assert calc.net_annual == calc.result.net_annual
        assert calc.gross_annual == calc.result.gross_annual
        assert calc.level_code == calc.result.level_code

    def test_to_dict_from_dict_roundtrip(self) -> None:
        """to_dict/from_dict round-trips the full calculation."""
        calc = compute(_req())
        restored = Calculation.from_dict(calc.to_dict())
        assert restored == calc
        assert restored.engine_version == calc.engine_version
        assert restored.input_snapshot == calc.input_snapshot
        assert restored.result == calc.result

    def test_to_json_from_json_roundtrip(self) -> None:
        """to_json/from_json round-trips through a JSON string."""
        calc = compute(_req())
        restored = Calculation.from_json(calc.to_json())
        assert restored == calc

    def test_reproduce_identical_result(self) -> None:
        """reproduce() yields the identical result without external args."""
        calc = compute(_req())
        replayed = calc.reproduce()
        assert replayed.result == calc.result
        assert replayed.input_snapshot == calc.input_snapshot
        assert replayed.engine_version == calc.engine_version

    def test_reproduce_preserves_seniority_variant(self) -> None:
        """Union member type is preserved through snapshot/reproduce."""
        calc = compute(_req(seniority_count=2))
        replayed = calc.reproduce()
        assert isinstance(replayed.input_snapshot, InputSnapshot)
        # The materialised seniority should still be by-count.
        scenario = replayed.input_snapshot.materialise()
        assert isinstance(scenario.employee.seniority, SeniorityByCount)
        assert scenario.employee.seniority.value == 2

    def test_copy_deepcopy_snapshot(self) -> None:
        """copy.deepcopy on InputSnapshot must not raise TypeError."""
        calc = compute(_req())
        snapshot_copy = copy.deepcopy(calc.input_snapshot)
        assert snapshot_copy == calc.input_snapshot

    def test_copy_deepcopy_calculation(self) -> None:
        """copy.deepcopy on a full Calculation must not raise TypeError."""
        calc = compute(_req())
        calc_copy = copy.deepcopy(calc)
        assert calc_copy == calc
        assert calc_copy.result == calc.result

    def test_copy_shallow_snapshot(self) -> None:
        """copy.copy on InputSnapshot must not raise TypeError."""
        calc = compute(_req())
        snapshot_copy = copy.copy(calc.input_snapshot)
        assert snapshot_copy == calc.input_snapshot

    def test_ruleset_version_is_frozen(self) -> None:
        """ruleset_version must reject item assignment after construction."""
        calc = compute(_req())
        with pytest.raises(TypeError):
            calc.ruleset_version["ccnl"] = "tampered"  # type: ignore[index]

    def test_snapshot_scenario_is_frozen(self) -> None:
        """snapshot.scenario must reject item assignment after construction."""
        calc = compute(_req())
        with pytest.raises(TypeError):
            calc.input_snapshot.scenario["ccnl"] = "tampered"  # type: ignore[index]


class TestDumpLoadPrimitives:
    """Low-level serialisation helpers used by InputSnapshot."""

    def test_dump_rejects_unsupported_type(self) -> None:
        """_dump raises TypeError for a non-JSON-native object."""

        class NotMappable:
            pass

        with pytest.raises(TypeError, match="Cannot serialise"):
            _dump(NotMappable())

    def test_load_dataclass_missing_field_raises(self) -> None:
        """_load_dataclass raises ValueError on a missing required field."""
        with pytest.raises(ValueError, match="Missing field"):
            _load_dataclass(SeniorityByCount, {})

    def test_load_union_no_match_raises(self) -> None:
        """_load_union raises ValueError when no dataclass member matches."""
        with pytest.raises(ValueError, match="No union member matched"):
            _load_union([SeniorityByCount], {"unrelated": 1})

    def test_load_union_pydantic_member_failure(self) -> None:
        """_load_union tries pydantic members and raises when none accept."""
        with pytest.raises(ValueError, match="No union member matched"):
            _load_union([Permanent], {"type": "not-a-contract"})

    def test_load_union_tag_mismatch_falls_through(self) -> None:
        """A non-matching $type tag falls back to trial-loading."""
        loaded = _load_union(
            [SeniorityByCount],
            {"$type": "SomeOtherType", "value": 3},
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 3

    def test_load_union_non_string_tag_falls_through(self) -> None:
        """A non-string $type tag is ignored and trial-loading applies."""
        loaded = _load_union(
            [SeniorityByCount],
            {"$type": 5, "value": 4},
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 4

    def test_load_dataclass_non_dict_raises(self) -> None:
        """_load_dataclass raises TypeError when raw is not a mapping."""
        with pytest.raises(TypeError, match="Expected a mapping"):
            _load_dataclass(SeniorityByCount, "not-a-dict")

    def test_load_dataclass_unknown_field_raises(self) -> None:
        """_load_dataclass raises ValueError on an unrecognised field key."""
        with pytest.raises(ValueError, match="Unknown fields"):
            _load_dataclass(SeniorityByCount, {"value": 3, "bogus_field": 1})

    def test_load_dataclass_dtype_tag_is_exempt(self) -> None:
        """The $type discriminator key is not treated as an unknown field."""
        loaded = _load_dataclass(
            SeniorityByCount, {"$type": "SeniorityByCount", "value": 7}
        )
        assert isinstance(loaded, SeniorityByCount)
        assert loaded.value == 7

    def test_load_dataclass_migrates_mortgage_pre_1993_true(self) -> None:
        """mortgage_pre_1993=True is migrated to mortgage_pre_2022=True."""
        result = _load_dataclass(Art15Deductions, {"mortgage_pre_1993": True})
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is True

    def test_load_dataclass_migrates_mortgage_pre_1993_false_raises(self) -> None:
        """mortgage_pre_1993=False raises ValueError — the mapping is ambiguous."""
        with pytest.raises(ValueError, match="ambiguous"):
            _load_dataclass(Art15Deductions, {"mortgage_pre_1993": False})

    def test_load_dataclass_both_old_and_new_key_drops_old(self) -> None:
        """Both old and new key present: old is dropped, new wins."""
        result = _load_dataclass(
            Art15Deductions,
            {"mortgage_pre_1993": True, "mortgage_pre_2022": False},
        )
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is False  # new key wins

    def test_load_dataclass_art15_no_old_key_skips_rename(self) -> None:
        """Art15Deductions without the old key loads normally, using default."""
        result = _load_dataclass(Art15Deductions, {"mortgage_interest": "500"})
        assert isinstance(result, Art15Deductions)
        assert result.mortgage_pre_2022 is False


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
        assert loaded == (SeniorityByCount(1),)

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


class TestLoadDataclassCompat:
    """_load_dataclass skips fields with defaults when absent from the dict."""

    def test_missing_defaulted_field_is_skipped(self) -> None:
        """A dict missing a field with a default does not raise."""
        # OvertimeHours has all fields defaulted to zero; an empty dict should
        # reconstruct the instance using the defaults.
        result = _load_dataclass(OvertimeHours, {})
        assert result == OvertimeHours()

    def test_partial_dict_uses_defaults_for_absent_fields(self) -> None:
        """Only provided fields are set; absent defaulted fields use defaults."""
        result = _load_dataclass(OvertimeHours, {"weekday_hours": "5"})
        assert isinstance(result, OvertimeHours)
        assert result.weekday_hours == Decimal(5)
        assert result.night_hours == Decimal(0)


class TestR2R19R20Fixes:
    """Tests for Literal replay (R2), snapshot alias (R19), deepcopy (R20)."""

    def test_literal_valid_value_returned(self) -> None:
        """_load_by_hint returns a valid Literal value unchanged."""
        hint: type = typing.Literal["impiegato", "operaio"]  # type: ignore[assignment]
        assert _load_by_hint(hint, "impiegato") == "impiegato"

    def test_literal_invalid_value_raises(self) -> None:
        """_load_by_hint rejects a value not in the Literal union."""
        hint: type = typing.Literal["impiegato", "operaio"]  # type: ignore[assignment]
        with pytest.raises(ValueError, match="expected one of"):
            _load_by_hint(hint, "supervisore")

    def test_getattr_missing_result_raises_attribute_error(self) -> None:
        """__getattr__ raises AttributeError when result is uninitialised."""
        calc = object.__new__(Calculation)
        with pytest.raises(AttributeError):
            _ = calc.net_annual


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
        calc = compute(_req())
        with pytest.raises(TypeError):
            calc.ruleset_version["ccnl"] = "tampered"  # type: ignore[index]

    def test_from_dict_without_trace_key_uses_empty_trace(self) -> None:
        """from_dict() succeeds and returns empty trace when 'trace' key is absent."""
        calc = compute(_req())
        d = calc.to_dict()
        d.pop("trace")
        restored = Calculation.from_dict(d)
        assert restored.trace == CalculationTrace(steps=())
        assert restored.result == calc.result

    def test_reproduce_stable_after_to_dict_mutation(self) -> None:
        """reproduce() is stable even if to_dict() output is mutated."""
        calc = compute(_req())
        original_net = calc.result.net_annual
        d = calc.to_dict()
        # Tamper with the serialised copy — must not affect reproduce().
        d["input_snapshot"]["scenario"]["employee"]["level_code"] = "1"  # type: ignore[index]
        replayed = calc.reproduce()
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


class TestCoerceScalarStrictPrimitives:
    """_load_by_hint rejects wrong primitive types for bool/int/str."""

    def test_bool_string_false_rejected(self) -> None:
        """String 'false' for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, "false")

    def test_bool_string_true_rejected(self) -> None:
        """String 'true' for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, "true")

    def test_bool_int_zero_rejected(self) -> None:
        """Integer 0 for a bool hint raises TypeError."""
        with pytest.raises(TypeError, match="expected bool"):
            _load_by_hint(bool, 0)

    def test_bool_valid_passes(self) -> None:
        """True/False pass through unchanged for a bool hint."""
        assert _load_by_hint(bool, True) is True
        assert _load_by_hint(bool, False) is False

    def test_int_string_rejected(self) -> None:
        """String '42' for an int hint raises TypeError."""
        with pytest.raises(TypeError, match="expected int"):
            _load_by_hint(int, "42")

    def test_int_bool_rejected(self) -> None:
        """Bool True for an int hint raises TypeError (bool subclass guard)."""
        with pytest.raises(TypeError, match="expected int"):
            _load_by_hint(int, True)

    def test_int_valid_passes(self) -> None:
        """A plain int passes through unchanged."""
        assert _load_by_hint(int, 2026) == 2026

    def test_str_int_rejected(self) -> None:
        """Integer 42 for a str hint raises TypeError."""
        with pytest.raises(TypeError, match="expected str"):
            _load_by_hint(str, 42)

    def test_str_valid_passes(self) -> None:
        """A plain str passes through unchanged."""
        assert _load_by_hint(str, "hello") == "hello"


class TestNestedBoolValidation:
    """materialise() rejects string values for nested bool scenario fields."""

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

    def test_ivs_ceiling_applies_string_false_raises(self) -> None:
        """String 'false' for ivs_ceiling_applies raises TypeError on materialise."""
        snap = self._snapshot_with_bool_field("ivs_ceiling_applies", "false")
        with pytest.raises(TypeError, match="expected bool"):
            snap.materialise()

    def test_ivs_ceiling_applies_int_zero_raises(self) -> None:
        """Integer 0 for ivs_ceiling_applies raises TypeError on materialise."""
        snap = self._snapshot_with_bool_field("ivs_ceiling_applies", 0)
        with pytest.raises(TypeError, match="expected bool"):
            snap.materialise()

    def test_replay_identity(self) -> None:
        """A round-tripped snapshot reproduces the same net_annual."""
        calc = compute(_req())
        original_net = calc.result.net_annual
        restored = Calculation.from_dict(calc.to_dict())
        replayed = restored.reproduce()
        assert replayed.result.net_annual == original_net


class TestCalculationFromDictStrictValidation:
    """Calculation.from_dict rejects wrong types for version fields."""

    def test_engine_version_int_rejected(self) -> None:
        """Integer engine_version raises TypeError."""
        calc = compute(_req())
        d = calc.to_dict()
        d["engine_version"] = 5
        with pytest.raises(TypeError, match="engine_version"):
            Calculation.from_dict(d)

    def test_ruleset_version_int_value_rejected(self) -> None:
        """Integer value in ruleset_version raises TypeError."""
        calc = compute(_req())
        d = calc.to_dict()
        d["ruleset_version"] = {"ccnl": 42}
        with pytest.raises(TypeError, match="ruleset_version"):
            Calculation.from_dict(d)
