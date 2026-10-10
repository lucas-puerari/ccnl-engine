"""JSON form of a period state: tagged values, versions, safe reading."""

from __future__ import annotations

import dataclasses
import importlib
import json
import pkgutil
import sys
import typing
from datetime import date
from decimal import Decimal
from enum import Enum
from types import UnionType

import pytest

import ccnl_engine.payroll.domain as payroll_domain
from ccnl_engine.payroll.domain.inps_base import InpsBaseYtd
from ccnl_engine.payroll.domain.period_state import PeriodState
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.sickness import SicknessEpisode
from ccnl_engine.payroll.domain.state_codec import (
    STATE_TYPES,
    period_state_from_json,
    period_state_to_json,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

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
    return period_state_from_json(text, **_VERSIONS)


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
        pytest.param(_payload(engine_version="0.1.0"), id="other-engine"),
        pytest.param(_payload(bundle_version="2025.1"), id="other-bundle"),
        pytest.param(_payload(engine_version=None), id="no-engine"),
        pytest.param(_with_state({"$type": "dict", "fields": {}}), id="foreign"),
        pytest.param(
            _with_state({
                "$type": "ccnl_engine.payroll.domain.period_state.PeriodState",
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


def test_writing_a_type_outside_the_registry_is_a_defect() -> None:
    """A state type the registry forgot fails loudly instead of being written."""

    @dataclasses.dataclass(frozen=True)
    class Stray:
        amount: Decimal

    with pytest.raises(TypeError, match="Stray"):
        period_state_to_json(Stray(Decimal(1)), **_VERSIONS)  # type: ignore[arg-type]


def _domain_types() -> dict[str, type]:
    names: dict[str, type] = {}
    for module in pkgutil.walk_packages(
        payroll_domain.__path__, f"{payroll_domain.__name__}."
    ):
        imported = importlib.import_module(module.name)
        names.update({k: v for k, v in vars(imported).items() if isinstance(v, type)})
    return names


def _inner(hint: object, names: dict[str, type]) -> list[object]:
    if typing.get_origin(hint) is not None or isinstance(hint, UnionType):
        return list(typing.get_args(hint))
    if isinstance(hint, typing.TypeAliasType):
        return [hint.__value__]
    if isinstance(hint, type) and dataclasses.is_dataclass(hint):
        own = vars(sys.modules[hint.__module__])
        hints = typing.get_type_hints(hint, localns={**names, **own})
        return [hints[f.name] for f in dataclasses.fields(hint) if f.init]
    return []


def _is_state_type(hint: object) -> bool:
    return isinstance(hint, type) and (
        issubclass(hint, Enum) or dataclasses.is_dataclass(hint)
    )


def _reachable(root: type, names: dict[str, type]) -> set[type]:
    found: set[type] = set()
    seen: set[int] = set()
    pending: list[object] = [root]
    while pending:
        hint = pending.pop()
        if id(hint) in seen:
            continue
        seen.add(id(hint))
        if _is_state_type(hint):
            found.add(typing.cast("type", hint))
        pending.extend(_inner(hint, names))
    return found


def test_the_registry_holds_every_type_of_a_state() -> None:
    """Each dataclass and enum a PeriodState can hold has a tag, and only those."""
    registered = set(STATE_TYPES.values())
    reachable = _reachable(PeriodState, _domain_types())
    difference = sorted(
        f"{c.__module__}.{c.__qualname__}" for c in registered ^ reachable
    )
    assert registered == reachable, difference
