"""Every default of a public input field is classified.

A field of a public input type that has a default is either the fact
(``absence_is_fact``) or stands for a fact the caller has not stated
(``requires_fact``); see :mod:`ccnl_engine.payroll.domain.input_defaults`.
A new defaulted field without a classification, or a classification of a
field that no longer has a default, fails here.  The ``requires_fact``
fields honoured by a requirement are exactly the applicability facts of the
capability registry, and the facts an issue reports are ``reported``.
Every ``requires_fact`` field has a pair of requests, stated and left to its
default (:mod:`tests.fixtures.default_cases`).
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect

import ccnl_engine
from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.payroll.domain.decisions import PUBLIC_FACTS
from ccnl_engine.payroll.domain.input_defaults.model import (
    DefaultPolicy,
    FactEnforcement,
)
from ccnl_engine.payroll.domain.input_defaults.registry import INPUT_DEFAULTS
from tests.fixtures.default_cases import DEFAULT_CASES, NAMES_NOT_SHOWN, NOT_EXERCISED

#: Namespaces whose types a caller builds a request from.
_INPUT_NAMESPACES = ("ccnl_engine", "ccnl_engine.inputs", "ccnl_engine.events")
#: Root names that are not input types: the facade and the results.
_NOT_INPUTS = frozenset({
    "PayrollEngine",
    "PeriodResult",
    "CompetenceYearResult",
    "TaxYearResult",
})
_CATALOG = load_capability_catalog(2026)


def _input_types() -> dict[str, type]:
    types: dict[str, type] = {}
    for namespace in _INPUT_NAMESPACES:
        module = importlib.import_module(namespace)
        types.update(
            (name, obj)
            for name in module.__all__
            if name not in _NOT_INPUTS
            and inspect.isclass(obj := getattr(module, name))
            and dataclasses.is_dataclass(obj)
        )
    return types


def _has_default(field: dataclasses.Field[object]) -> bool:
    return field.init and (
        field.default is not dataclasses.MISSING
        or field.default_factory is not dataclasses.MISSING
    )


def _defaulted_fields() -> set[str]:
    return {
        f"{name}.{field.name}"
        for name, cls in _input_types().items()
        for field in dataclasses.fields(cls)
        if _has_default(field)
    }


def test_the_scan_sees_the_request_types() -> None:
    """The scan is not vacuous: it finds the residence of PeriodFacts."""
    assert "PeriodFacts.regione" in _defaulted_fields()
    assert {"PeriodResult.run", "PeriodResult.mode"}.isdisjoint(_defaulted_fields())
    assert all(hasattr(ccnl_engine, name) for name in _NOT_INPUTS)


def test_every_defaulted_public_field_is_classified() -> None:
    """A defaulted field of a public input type has a classification."""
    assert sorted(_defaulted_fields() - set(INPUT_DEFAULTS)) == []


def test_every_classification_names_a_defaulted_public_field() -> None:
    """No classification outlives its field or its default."""
    assert sorted(set(INPUT_DEFAULTS) - _defaulted_fields()) == []


def test_a_required_fact_names_a_capability_of_the_registry() -> None:
    """The capability a ``requires_fact`` field feeds is in the registry."""
    features = {entry.feature for entry in _CATALOG.capabilities}
    unknown = {
        name: default.capability
        for name, default in INPUT_DEFAULTS.items()
        if default.policy is DefaultPolicy.REQUIRES_FACT
        and default.capability not in features
    }
    assert unknown == {}


def test_requirements_are_the_applicability_facts_of_the_registry() -> None:
    """A field is honoured by a requirement exactly when the registry says so."""
    declared = {
        (default.capability, default.fact)
        for default in INPUT_DEFAULTS.values()
        if default.enforcement is FactEnforcement.REQUIREMENT
    }
    registry = {
        (entry.feature, fact)
        for entry in _CATALOG.capabilities
        for fact in entry.applicability_facts
    }
    assert declared == registry


def test_a_fact_an_issue_names_is_reported() -> None:
    """The fields a ``missing_fact`` issue names are ``reported``."""
    enforcement = {
        path: INPUT_DEFAULTS[path].enforcement for path in PUBLIC_FACTS.values()
    }
    assert set(enforcement.values()) == {FactEnforcement.REPORTED}


def _required_fields(*enforcements: FactEnforcement) -> set[str]:
    return {
        name
        for name, default in INPUT_DEFAULTS.items()
        if default.policy is DefaultPolicy.REQUIRES_FACT
        and (not enforcements or default.enforcement in enforcements)
    }


def test_every_required_fact_has_a_default_case() -> None:
    """Each ``requires_fact`` field is run stated and left to its default.

    The cases feed the metamorphic test of
    ``tests/acceptance/public_api/test_default_facts.py``: the true fact
    never has more blockers than its default.  A field without a case
    states why.
    """
    covered = set(DEFAULT_CASES) | set(NOT_EXERCISED)
    assert set(DEFAULT_CASES).isdisjoint(NOT_EXERCISED)
    assert sorted(covered ^ _required_fields()) == []


def test_a_blocking_default_shows_its_blocker() -> None:
    """A field honoured by a blocker has a case where the default shows it."""
    blocking = _required_fields(FactEnforcement.REPORTED, FactEnforcement.REQUIREMENT)
    shown = {
        name
        for name, cases in DEFAULT_CASES.items()
        if any(case.names is not None for case in cases)
    }
    expected = blocking - set(NOT_EXERCISED) - set(NAMES_NOT_SHOWN)
    assert sorted(expected - shown) == []
    assert set(NAMES_NOT_SHOWN) <= blocking - shown
