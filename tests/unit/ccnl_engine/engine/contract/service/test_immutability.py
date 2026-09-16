"""Recursive immutability tests for the cached CCNL object graph.

Every collection exposed by the CCNL hierarchy must be transitively
read-only so that callers sharing the cached instance cannot alter
results for other callers.

The Commercio Confcommercio contract is used because it has non-empty
fixed_allowances, employer_funds, seniority amounts and work_rules data,
exercising all branches.  Metalmeccanico Federmeccanica is used for
coverage work_rules_features.
"""

import contextlib
import copy

import pytest
from pydantic import ValidationError

from ccnl_engine.engine.contract.domain.ccnl import CCNL
from ccnl_engine.engine.contract.service.loaders import load_ccnl
from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
from ccnl_engine.engine.primitives import FrozenDict

# Any exception class accepted as proof of immutability enforcement.
_IMMUTABLE = (TypeError, AttributeError, ValidationError)


@pytest.fixture(scope="module")
def commercio() -> CCNL:
    """Return the cached Commercio Confcommercio CCNL.

    Returns:
        The validated, cached CCNL instance.
    """
    return load_ccnl("commercio-confcommercio.json")


@pytest.fixture(scope="module")
def metalmeccanico() -> CCNL:
    """Return the cached Metalmeccanico Federmeccanica CCNL.

    Returns:
        The validated, cached CCNL instance.
    """
    return load_ccnl("metalmeccanico-federmeccanica.json")


class TestLevelCollections:
    """Level.fixed_allowances must be a read-only tuple."""

    def test_fixed_allowances_is_tuple(self, commercio: CCNL) -> None:
        """fixed_allowances is stored as an immutable tuple."""
        level = commercio.level_by_code("4")
        assert isinstance(level.fixed_allowances, tuple)

    def test_fixed_allowances_no_append(self, commercio: CCNL) -> None:
        """Appending to fixed_allowances raises AttributeError."""
        level = commercio.level_by_code("4")
        with pytest.raises(AttributeError):
            level.fixed_allowances.append(None)  # type: ignore[attr-defined]

    def test_fixed_allowances_no_clear(self, commercio: CCNL) -> None:
        """Clearing fixed_allowances raises AttributeError."""
        level = commercio.level_by_code("4")
        with pytest.raises(AttributeError):
            level.fixed_allowances.clear()  # type: ignore[attr-defined]

    def test_mutation_does_not_affect_cache(self, commercio: CCNL) -> None:
        """Reproduces the N02 attack: cached graph must be unaffected.

        Mutating one lookup must not change a subsequent lookup that
        shares the same cached object.
        """
        level = commercio.level_by_code("4")
        original_count = len(level.fixed_allowances)
        with contextlib.suppress(AttributeError):
            level.fixed_allowances.clear()  # type: ignore[attr-defined]
        assert len(commercio.level_by_code("4").fixed_allowances) == original_count


class TestParameterCollections:
    """CCNLParameters.employer_funds must be a read-only tuple."""

    def test_employer_funds_is_tuple(self, commercio: CCNL) -> None:
        """employer_funds is stored as an immutable tuple."""
        assert isinstance(commercio.parameters.employer_funds, tuple)

    def test_employer_funds_no_append(self, commercio: CCNL) -> None:
        """Appending to employer_funds raises AttributeError."""
        with pytest.raises(AttributeError):
            commercio.parameters.employer_funds.append(None)  # type: ignore[attr-defined]


class TestSeniorityMappings:
    """SeniorityIncrements dict fields must be FrozenDict."""

    def test_amount_by_level_is_frozen(self, commercio: CCNL) -> None:
        """amount_by_level is a FrozenDict."""
        si = commercio.parameters.seniority_increments
        assert isinstance(si.amount_by_level, FrozenDict)

    def test_amount_by_level_no_update(self, commercio: CCNL) -> None:
        """FrozenDict.update() raises TypeError."""
        si = commercio.parameters.seniority_increments
        with pytest.raises(_IMMUTABLE):
            si.amount_by_level.update({"FAKE": None})  # type: ignore[attr-defined]

    def test_amount_by_level_no_clear(self, commercio: CCNL) -> None:
        """FrozenDict.clear() raises TypeError."""
        si = commercio.parameters.seniority_increments
        with pytest.raises(_IMMUTABLE):
            si.amount_by_level.clear()  # type: ignore[attr-defined]

    def test_first_cadence_by_level_is_frozen(self, commercio: CCNL) -> None:
        """first_cadence_months_by_level is a FrozenDict."""
        si = commercio.parameters.seniority_increments
        assert isinstance(si.first_cadence_months_by_level, FrozenDict)

    def test_maximum_count_by_level_is_frozen(self, commercio: CCNL) -> None:
        """maximum_count_by_level is a FrozenDict."""
        si = commercio.parameters.seniority_increments
        assert isinstance(si.maximum_count_by_level, FrozenDict)


class TestCoverageMapping:
    """CCNLCoverage.work_rules_features must be a FrozenDict."""

    def test_work_rules_features_is_frozen(self, metalmeccanico: CCNL) -> None:
        """work_rules_features is a FrozenDict."""
        assert isinstance(metalmeccanico.coverage.work_rules_features, FrozenDict)

    def test_work_rules_features_no_update(self, metalmeccanico: CCNL) -> None:
        """FrozenDict.update() raises TypeError."""
        with pytest.raises(_IMMUTABLE):
            metalmeccanico.coverage.work_rules_features.update({})  # type: ignore[attr-defined]


class TestCoverageNotes:
    """CCNLCoverage.notes must be a read-only tuple."""

    def test_notes_is_tuple(self, commercio: CCNL) -> None:
        """Coverage notes are stored as an immutable tuple."""
        assert isinstance(commercio.coverage.notes, tuple)

    def test_notes_no_append(self, commercio: CCNL) -> None:
        """Appending to coverage notes raises AttributeError."""
        with pytest.raises(AttributeError):
            commercio.coverage.notes.append(None)  # type: ignore[attr-defined]


class TestMetaCollections:
    """CCNLMeta.signatories and .sources must be read-only tuples."""

    def test_signatories_is_tuple(self, commercio: CCNL) -> None:
        """Signatories are stored as an immutable tuple."""
        assert isinstance(commercio.meta.signatories, tuple)

    def test_signatories_no_append(self, commercio: CCNL) -> None:
        """Appending to signatories raises AttributeError."""
        with pytest.raises(AttributeError):
            commercio.meta.signatories.append("FAKE")  # type: ignore[attr-defined]

    def test_sources_is_tuple(self, commercio: CCNL) -> None:
        """Sources are stored as an immutable tuple."""
        assert isinstance(commercio.meta.sources, tuple)

    def test_sources_no_append(self, commercio: CCNL) -> None:
        """Appending to sources raises AttributeError."""
        with pytest.raises(AttributeError):
            commercio.meta.sources.append(None)  # type: ignore[attr-defined]


class TestProvenanceFrozen:
    """Provenance models must be frozen (raise on field assignment)."""

    def test_source_document_frozen(self, commercio: CCNL) -> None:
        """SourceDocument raises on attribute assignment."""
        doc = commercio.meta.sources[0]
        with pytest.raises(_IMMUTABLE):
            doc.title = "hacked"  # type: ignore[misc]

    def test_rule_provenance_frozen(self, commercio: CCNL) -> None:
        """RuleProvenance raises on attribute assignment."""
        level = commercio.level_by_code("4")
        if level.provenance is not None:
            with pytest.raises(_IMMUTABLE):
                level.provenance.note = "hacked"  # type: ignore[misc]

    def test_source_document_pages_is_tuple(self, commercio: CCNL) -> None:
        """SourceDocument.pages is stored as an immutable tuple."""
        doc = commercio.meta.sources[0]
        assert isinstance(doc.pages, tuple)


class TestOvertimeBandsImmutable:
    """TimeSupplements.overtime_bands and OvertimeBand.applies_to_kinds are tuples."""

    def test_overtime_bands_is_tuple(self, metalmeccanico: CCNL) -> None:
        """overtime_bands is stored as an immutable tuple."""
        wr = metalmeccanico.work_rules
        if wr is not None and wr.time_supplements is not None:
            assert isinstance(wr.time_supplements.overtime_bands, tuple)

    def test_applies_to_kinds_is_tuple(self, metalmeccanico: CCNL) -> None:
        """applies_to_kinds is stored as an immutable tuple on every band."""
        wr = metalmeccanico.work_rules
        if wr is not None and wr.time_supplements is not None:
            for band in wr.time_supplements.overtime_bands:
                assert isinstance(band.applies_to_kinds, tuple)


class TestSerializationRoundTrip:
    """CCNL must survive model_dump_json, deepcopy, and model_copy(deep=True).

    N15: MappingProxyType blocked both JSON serialisation and deepcopy.
    FrozenDict is a dict subclass and supports all three operations.
    """

    def test_model_dump_json(self, commercio: CCNL) -> None:
        """model_dump_json must not raise PydanticSerializationError."""
        payload = commercio.model_dump_json()
        assert len(payload) > 0

    def test_model_dump_json_roundtrip(self, commercio: CCNL) -> None:
        """model_validate_json of model_dump_json must produce an equal CCNL."""
        restored = CCNL.model_validate_json(commercio.model_dump_json())
        assert restored.meta.ccnl_id == commercio.meta.ccnl_id
        assert restored.meta.name == commercio.meta.name

    def test_deepcopy(self, commercio: CCNL) -> None:
        """copy.deepcopy must not raise TypeError."""
        cloned = copy.deepcopy(commercio)
        assert cloned.meta.ccnl_id == commercio.meta.ccnl_id

    def test_model_copy_deep(self, commercio: CCNL) -> None:
        """model_copy(deep=True) must not raise TypeError."""
        cloned = commercio.model_copy(deep=True)
        assert cloned.meta.ccnl_id == commercio.meta.ccnl_id

    def test_frozen_dict_blocks_mutation_after_deepcopy(self, commercio: CCNL) -> None:
        """FrozenDict in the deepcopy still blocks item assignment."""
        cloned = copy.deepcopy(commercio)
        si = cloned.parameters.seniority_increments
        with pytest.raises(_IMMUTABLE):
            si.amount_by_level.update({"FAKE": None})  # type: ignore[attr-defined]


class TestRulesetIdentityFrozen:
    """RulesetIdentity must be immutable (N02).

    Mutating the shared identity object corrupts audit records without
    affecting salaries; frozen=True makes the assignment fail immediately.
    """

    def test_version_mutation_blocked(self, metalmeccanico: CCNL) -> None:
        """Assigning to ruleset.version raises (frozen_instance or TypeError)."""
        assert metalmeccanico.ruleset is not None
        with pytest.raises(_IMMUTABLE):
            metalmeccanico.ruleset.version = "review-probe"  # type: ignore[misc]

    def test_ruleset_is_ruleset_identity(self, metalmeccanico: CCNL) -> None:
        """ccnl.ruleset is a RulesetIdentity instance."""
        assert isinstance(metalmeccanico.ruleset, RulesetIdentity)

    def test_cached_ruleset_unchanged_after_probe(self, metalmeccanico: CCNL) -> None:
        """A blocked assignment leaves the ruleset id@version intact."""
        assert metalmeccanico.ruleset is not None
        original = str(metalmeccanico.ruleset)
        with contextlib.suppress(*_IMMUTABLE):
            metalmeccanico.ruleset.version = "probe"  # type: ignore[misc]
        assert str(metalmeccanico.ruleset) == original
