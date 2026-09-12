"""Tests for Calculation / InputSnapshot provenance and reproducibility."""

import typing
from datetime import date
from decimal import Decimal
from enum import Enum

import pytest

from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
from ccnl_engine.engine.payroll.domain.calculation import (
    Calculation,
    InputSnapshot,
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
from ccnl_engine.engine.payroll.service.audit import _ruleset_versions
from ccnl_engine.engine.payroll.service.orchestrator import compute
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


class TestCalculation:
    """Calculation carries provenance and reproduces an identical result."""

    def test_compute_returns_calculation(self) -> None:
        """Compute returns a Calculation with engine version and rulesets."""
        calc = compute(_req())
        assert isinstance(calc, Calculation)
        assert calc.engine_version == "0.5.1"
        assert calc.ruleset_version["ccnl"] == "test@2026.2"
        assert calc.ruleset_version["tax"] == "tax/2026/terziario@2026.2"
        assert "inps" not in calc.ruleset_version
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
        """_load_dataclass raises TypeError when raw is not a dict."""
        with pytest.raises(TypeError, match="Expected dict"):
            _load_dataclass(SeniorityByCount, "not-a-dict")


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

    def test_load_by_hint_pydantic_model_validate(self) -> None:
        """Pydantic hints are validated via model_validate."""
        assert isinstance(_load_by_hint(Permanent, {"type": "permanent"}), Permanent)

    def test_ruleset_fallback_ids(self) -> None:
        """Rulesets without a block fall back to knowledge-version ids."""
        ccnl = make_minimal_ccnl()
        rules = make_year_rules()
        versions = _ruleset_versions(ccnl, rules, surtax=None)
        assert versions["ccnl"] == "test@2026.2"
        assert versions["tax"] == "tax/2026/terziario@2026.2"
        assert "inps" not in versions
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
