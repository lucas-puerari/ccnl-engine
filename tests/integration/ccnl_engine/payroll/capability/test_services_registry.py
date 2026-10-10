"""The registry binds every computed capability to a handler the trace shows.

The bundled registry holds; each synthetic registry breaks one rule and is
rejected before any report is built from it.
"""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch

import pytest

from ccnl_engine.errors import DataIntegrityError
from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
)
from ccnl_engine.payroll.capability.results import CaseFacts
from ccnl_engine.payroll.capability.services_registry import (
    capability_report,
    registry_errors,
    validate_registry,
)
from ccnl_engine.payroll.capability.services_trace import (
    HANDLERS,
    build_traces,
)
from ccnl_engine.payroll.event.handlers_registry import _HANDLER_REGISTRY
from ccnl_engine.payroll.period.services_caller_rule import (
    CALLER_SUPPLIED_CAPABILITIES,
)

_BUNDLED = load_capability_catalog(2026)
_IMPL = CapabilityImplementation


def _with(feature: str, **changes: object) -> CapabilityCatalog:
    """Return the bundled registry with one entry changed.

    Returns:
        The changed registry.
    """
    entries = tuple(
        replace(e, **changes) if e.feature == feature else e  # type: ignore[arg-type]
        for e in _BUNDLED.capabilities
    )
    return CapabilityCatalog(_BUNDLED.year, entries)


def _without(feature: str) -> CapabilityCatalog:
    return CapabilityCatalog(
        _BUNDLED.year, tuple(e for e in _BUNDLED.capabilities if e.feature != feature)
    )


def test_bundled_registry_holds() -> None:
    """Every rule holds for the 2026 registry."""
    assert registry_errors(_BUNDLED) == []
    validate_registry(_BUNDLED)


def test_every_implemented_capability_is_traced() -> None:
    """Each computed capability has a trace in every run, even an empty one."""
    traced = {trace.feature for trace in build_traces((), frozenset())}
    implemented = {entry.feature for entry in _BUNDLED.implemented()}
    assert implemented == set(HANDLERS)
    assert implemented <= traced


def test_caller_supplied_matches_the_caller_rules() -> None:
    """The registry says caller_supplied where the handler takes caller values."""
    declared = {
        e.feature
        for e in _BUNDLED.capabilities
        if e.implementation is _IMPL.CALLER_SUPPLIED
    }
    assert declared == CALLER_SUPPLIED_CAPABILITIES - {"sickness"}


@pytest.mark.parametrize(
    ("catalog", "message"),
    [
        (
            _with(
                "overtime",
                handler=CapabilityHandler.DECISION,
                applies_when=CapabilityApplicability.DECIDED,
            ),
            "overtime: caller_supplied without a registered decision handler",
        ),
        (
            _without("irpef"),
            "irpef: handler registered without an implemented registry entry",
        ),
        (
            _with("welfare", implementation=_IMPL.CALLER_SUPPLIED),
            "welfare: declared caller_supplied but takes no caller value",
        ),
        (
            _with("absence", implementation=_IMPL.NATIVE),
            "absence: takes caller values in place of a rule but is native",
        ),
        (
            _with(
                "addizionale_regionale",
                required_facts=("facts.residence",),
                applicability_facts=("facts.residence",),
            ),
            (
                "addizionale_regionale: applicability fact facts.residence has "
                "no request reader"
            ),
        ),
    ],
)
def test_contradictions_are_listed(catalog: CapabilityCatalog, message: str) -> None:
    """A registry that contradicts the handlers lists each contradiction."""
    assert message in registry_errors(catalog)


def test_untraced_capability_is_rejected() -> None:
    """A computed capability no handler traces cannot be observed in a run."""
    ghost = CapabilityEntry(
        "ghost",
        _BUNDLED.capabilities[0].layer,
        _IMPL.NATIVE,
        CapabilityApplicability.TERMINATION_RUN,
        CapabilityHandler.PIPELINE,
    )
    catalog = CapabilityCatalog(_BUNDLED.year, (*_BUNDLED.capabilities, ghost))
    errors = registry_errors(catalog)
    assert "ghost: handler not observable in the run trace" in errors
    with pytest.raises(DataIntegrityError, match="ghost: native without a registered"):
        capability_report(catalog, (), frozenset(), CaseFacts(), 2026)


class _UntracedEvent:
    """An event type a handler would post without any trace."""


def test_untraced_event_handler_is_rejected() -> None:
    """An event handler without a traced capability posts unobserved amounts."""
    handler = _HANDLER_REGISTRY[next(iter(_HANDLER_REGISTRY))]
    with patch.dict(_HANDLER_REGISTRY, {_UntracedEvent: handler}):
        errors = registry_errors(_BUNDLED)
    assert errors == ["_UntracedEvent: event handler not observable in the run trace"]
