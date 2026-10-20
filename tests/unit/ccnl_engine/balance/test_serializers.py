"""JSON form of a period state: tagged values, versions, safe reading."""

from __future__ import annotations

import dataclasses
import json
import typing
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.balance import serializers
from ccnl_engine.balance.models import PeriodState
from ccnl_engine.balance.serializers import (
    FIRST_SCHEMA_VERSION,
    STATE_MIGRATIONS,
    STATE_TYPES,
    migrate_state,
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.contribution.base.models import InpsBaseYtd
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.run.models import PayrollRunId, RunKind
from ccnl_engine.sickness.models import SicknessEpisode
from tests.unit.ccnl_engine import support

_VERSIONS = {"engine_version": "1.0.0", "bundle_version": "2026.1"}


def _state() -> PeriodState:
    zero = PeriodState.zero()
    accrual = zero.accrual.__class__(
        competence_runs=(PayrollRunId(2026, 1, RunKind.REGULAR),),
        inps_bases=(InpsBaseYtd(2026, Decimal("2158.26"), Decimal(0)),),
        sickness_episodes=(SicknessEpisode("A", date(2026, 1, 5), date(2026, 1, 9)),),
        sickness_known_from=date(2026, 1, 1),
    )
    return PeriodState(accrual=accrual, cash=zero.cash, history_known=False)


def _write(state: PeriodState) -> str:
    return period_state_to_json(state, **_VERSIONS)


def _read(text: str) -> PeriodState:
    return period_state_from_json(text)


@pytest.mark.parametrize("state", [PeriodState.zero(), _state()], ids=["zero", "full"])
def test_a_state_reads_back_equal(state: PeriodState) -> None:
    """Decimals, dates, enums, tuples and nested states survive the round trip."""
    assert _read(_write(state)) == state


def test_the_json_carries_the_versions_that_wrote_it() -> None:
    """Schema, engine and bundle versions are written next to the state."""
    payload = json.loads(_write(PeriodState.zero()))
    assert payload["schema_version"] == PeriodState.SCHEMA_VERSION
    assert payload["engine_version"] == "1.0.0"
    assert payload["bundle_version"] == "2026.1"


def test_a_type_is_tagged_by_its_registered_name() -> None:
    """The tag does not depend on the module that defines the class."""
    payload = json.loads(_write(_state()))
    assert payload["state"]["$type"] == "PeriodState"


def _payload(**changes: object) -> str:
    payload = json.loads(_write(_state()))
    payload.update(changes)
    return json.dumps(payload)


@pytest.mark.parametrize(
    "versions",
    [
        pytest.param({"engine_version": "0.1.0"}, id="other-engine"),
        pytest.param({"bundle_version": "2025.1"}, id="other-bundle"),
        pytest.param(
            {"engine_version": "0.1.0", "bundle_version": "2025.1"}, id="both"
        ),
    ],
)
def test_a_state_of_another_engine_or_bundle_reads_back(
    versions: dict[str, str],
) -> None:
    """Only the schema is checked: the other versions stay in the text for audit."""
    assert _read(_payload(**versions)) == _state()


def test_the_migrations_cover_every_schema_since_the_first() -> None:
    """A schema bump without the step from the previous version fails here."""
    assert set(STATE_MIGRATIONS) == set(
        range(FIRST_SCHEMA_VERSION, PeriodState.SCHEMA_VERSION)
    )


def test_the_migrations_apply_in_order_up_to_the_target() -> None:
    """Each step reads the tree of its version and writes that of the next."""
    steps = {
        1: lambda tree: [*typing.cast("list[int]", tree), 2],
        2: lambda tree: [*typing.cast("list[int]", tree), 3],
    }

    assert migrate_state([1], 1, migrations=steps, target=3) == [1, 2, 3]
    assert migrate_state([3], 3, migrations=steps, target=3) == [3]


def test_a_missing_migration_is_a_defect_of_the_registry() -> None:
    """A gap in the steps raises instead of decoding a tree of another schema."""
    with pytest.raises(LookupError):
        migrate_state([1], 1, migrations={}, target=2)


def _with_state(state: object) -> str:
    return _payload(state=state)


_RUN = {"$type": "PayrollRunId", "fields": {"year": 2026, "month": 1}}


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("not json", id="not-json"),
        pytest.param("[" * 100_000, id="too-deep"),
        pytest.param("[1]", id="not-an-object"),
        pytest.param(_payload(schema_version=1), id="old-schema"),
        pytest.param(
            _payload(schema_version=PeriodState.SCHEMA_VERSION + 1), id="future-schema"
        ),
        pytest.param(_payload(schema_version="14"), id="schema-a-string"),
        pytest.param(_payload(schema_version=True), id="schema-a-bool"),
        pytest.param(_payload(schema_version=None), id="no-schema"),
        pytest.param(_payload(engine_version=None), id="no-engine"),
        pytest.param(_payload(bundle_version=2025), id="bundle-not-a-string"),
        pytest.param(_with_state({"$type": "dict", "fields": {}}), id="foreign"),
        pytest.param(
            _with_state({
                "$type": "ccnl_engine.balance.models.PeriodState",
                "fields": {},
            }),
            id="module-path",
        ),
        pytest.param(
            _with_state({"$type": "RunKind", "fields": {}}), id="enum-as-type"
        ),
        pytest.param(
            _with_state({"$enum": "PayrollRunId", "value": 1}), id="type-as-enum"
        ),
        pytest.param(_with_state({"$type": 1, "fields": {}}), id="tag-not-a-string"),
        pytest.param(_with_state({"$type": "PeriodState"}), id="no-fields"),
        pytest.param(
            _with_state({"$type": "PeriodState", "fields": []}), id="fields-a-list"
        ),
        pytest.param(
            _with_state({"$type": "PeriodState", "fields": {"nope": 1}}),
            id="unknown-field",
        ),
        pytest.param(_with_state({"$enum": "RunKind"}), id="no-value"),
        pytest.param(
            _with_state({"$enum": "RunKind", "value": "nope"}), id="bad-enum-value"
        ),
        pytest.param(_with_state({"$decimal": 1}), id="decimal-not-text"),
        pytest.param(_with_state({"$decimal": "one"}), id="decimal-malformed"),
        pytest.param(_with_state({"$date": "2026-13-01"}), id="date-malformed"),
        pytest.param(_with_state({"$tuple": {}}), id="tuple-not-a-list"),
        pytest.param(_with_state({"$decimal": "1", "x": 1}), id="extra-key"),
        pytest.param(_with_state([1]), id="bare-list"),
        pytest.param(_with_state({"x": 1}), id="untagged"),
        pytest.param(_with_state({"$decimal": "1"}), id="not-a-state"),
        pytest.param(_with_state(_RUN), id="constructor-rejects"),
    ],
)
def test_a_text_that_is_not_a_current_state_is_invalid_input(text: str) -> None:
    """Every malformed or foreign payload is an InvalidInputError, nothing else."""
    with pytest.raises(InvalidInputError):
        _read(text)


def test_a_tree_a_migration_rejects_is_invalid_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stored tree too malformed for a migration step is rejected input."""

    def rejecting(_tree: object, _version: int) -> object:
        msg = "no accrual"
        raise KeyError(msg)

    monkeypatch.setattr(serializers, "migrate_state", rejecting)
    with pytest.raises(InvalidInputError, match="cannot be migrated"):
        _read(_write(_state()))


def test_writing_a_type_outside_the_registry_is_a_defect() -> None:
    """A state type the registry forgot fails loudly instead of being written."""

    @dataclasses.dataclass(frozen=True)
    class Stray:
        amount: Decimal

    with pytest.raises(TypeError, match="Stray"):
        period_state_to_json(Stray(Decimal(1)), **_VERSIONS)  # type: ignore[arg-type]


def test_the_registry_holds_every_type_of_a_state() -> None:
    """Each dataclass and enum a PeriodState can hold has a tag, and only those."""
    registered = set(STATE_TYPES.values())
    reachable = support.reachable((PeriodState,), support.domain_types())
    difference = sorted(
        f"{c.__module__}.{c.__qualname__}" for c in registered ^ reachable
    )
    assert registered == reachable, difference
