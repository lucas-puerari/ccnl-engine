"""Capability registry entries: implementation, handler and applicability."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ccnl_engine.payroll.domain.assurance import EvidenceStatus
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityApplicability,
    CapabilityCatalog,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)

_NATIVE = CapabilityImplementation.NATIVE
_UNSUPPORTED = CapabilityImplementation.UNSUPPORTED


def entry(
    feature: str = "irpef",
    implementation: CapabilityImplementation = _NATIVE,
    applies_when: CapabilityApplicability = CapabilityApplicability.ALWAYS,
    handler: CapabilityHandler | None = CapabilityHandler.PIPELINE,
) -> CapabilityEntry:
    """Return a registry entry of the net layer.

    Returns:
        The entry.
    """
    return CapabilityEntry(
        feature, CapabilityLayer.NET, implementation, applies_when, handler
    )


class TestImplementation:
    """Implementations are ordered from native to unsupported."""

    def test_worst(self) -> None:
        """The worst of several implementations is the last in order."""
        partial = CapabilityImplementation.PARTIAL
        assert CapabilityImplementation.worst((_NATIVE, partial)) is partial
        assert CapabilityImplementation.worst(list(CapabilityImplementation)) is (
            _UNSUPPORTED
        )

    def test_worst_of_nothing_is_native(self) -> None:
        """An empty layer has nothing missing."""
        assert CapabilityImplementation.worst(()) is _NATIVE


class TestEntry:
    """An entry is consistent with its handler and its predicate."""

    def test_defaults(self) -> None:
        """Evidence defaults to derived; text fields to empty."""
        native = entry()
        assert native.evidence is EvidenceStatus.DERIVED
        assert not native.description
        assert native.variants == ()
        assert native.required_facts == ()

    def test_frozen(self) -> None:
        """Assigning to a field raises FrozenInstanceError."""
        with pytest.raises(FrozenInstanceError):
            entry().feature = "g"  # type: ignore[misc]

    def test_unsupported_without_handler(self) -> None:
        """An unsupported capability has no handler."""
        unsupported = entry(
            "inail", _UNSUPPORTED, CapabilityApplicability.OUTSIDE_INPUT, None
        )
        assert unsupported.handler is None

    def test_unsupported_with_handler_is_rejected(self) -> None:
        """A handler would claim a decision the engine does not take."""
        with pytest.raises(ValueError, match="unsupported capability has no handler"):
            entry("inail", _UNSUPPORTED)

    def test_implemented_without_handler_is_rejected(self) -> None:
        """A computed capability needs a handler that decides it."""
        with pytest.raises(ValueError, match="every other one has one"):
            entry(handler=None)

    @pytest.mark.parametrize(
        ("applies_when", "handler"),
        [
            (CapabilityApplicability.ALWAYS, CapabilityHandler.DECISION),
            (CapabilityApplicability.DECIDED, CapabilityHandler.EVENT),
            (CapabilityApplicability.EVENT, CapabilityHandler.PIPELINE),
        ],
    )
    def test_predicate_needs_its_handler(
        self, applies_when: CapabilityApplicability, handler: CapabilityHandler
    ) -> None:
        """The predicate reads the trace of the handler kind it names."""
        with pytest.raises(ValueError, match="is decided by"):
            entry(applies_when=applies_when, handler=handler)

    def test_termination_predicate_takes_any_handler(self) -> None:
        """A run fact does not depend on the handler kind."""
        closing = entry(
            applies_when=CapabilityApplicability.TERMINATION_RUN,
            handler=CapabilityHandler.EVENT,
        )
        assert closing.handler is CapabilityHandler.EVENT


class TestCatalog:
    """The catalog holds one entry per feature."""

    def test_by_feature(self) -> None:
        """Lookup by feature returns the entry or None."""
        catalog = CapabilityCatalog(2026, (entry(),))
        assert catalog.by_feature("irpef") == entry()
        assert catalog.by_feature("unknown") is None

    def test_duplicate_features_are_rejected(self) -> None:
        """Two entries for one feature would contradict each other."""
        with pytest.raises(ValueError, match=r"duplicate features \['irpef'\]"):
            CapabilityCatalog(2026, (entry(), entry()))

    def test_implemented_leaves_out_unsupported(self) -> None:
        """Only the capabilities the engine computes need a handler."""
        unsupported = entry(
            "inail", _UNSUPPORTED, CapabilityApplicability.OUTSIDE_INPUT, None
        )
        catalog = CapabilityCatalog(2026, (entry(), unsupported))
        assert catalog.implemented() == (entry(),)
