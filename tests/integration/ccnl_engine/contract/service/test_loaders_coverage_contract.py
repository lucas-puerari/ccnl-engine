"""Coverage of the bundled CCNLs: the aggregate agrees with its features.

``coverage.work_rules`` summarizes the thirteen work-rule features of
``coverage.work_rules_features``; a feature left out counts as
``not_implemented``, as in the capability matrix.  The contracts index reads
the aggregate and the matrix reads the features: when they disagree the two
pages contradict each other.
"""

from __future__ import annotations

import importlib.resources

import pytest

from ccnl_engine.contract.domain.identity import CoverageStatus, WorkRuleFeature
from ccnl_engine.contract.service.loaders import load_ccnl

_FILENAMES = sorted(
    entry.name
    for entry in importlib.resources.files("ccnl_engine.knowledge.ccnl.data").iterdir()
    if entry.name.endswith(".json")
)


def test_bundle_is_not_empty() -> None:
    """A packaging mistake must not make the contract below vacuous."""
    assert _FILENAMES


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="work rules declared implemented while their features are not",
)
def test_implemented_work_rules_have_every_feature_implemented() -> None:
    """No CCNL declares work rules implemented with a feature not implemented.

    Today 111 of the 125 bundled CCNLs do.
    """
    contradicting = []
    for filename in _FILENAMES:
        coverage = load_ccnl(filename).coverage
        features = coverage.work_rules_features
        missing = [
            feature.value
            for feature in WorkRuleFeature
            if features.get(feature, CoverageStatus.NOT_IMPLEMENTED)
            is CoverageStatus.NOT_IMPLEMENTED
        ]
        if coverage.work_rules is CoverageStatus.IMPLEMENTED and missing:
            contradicting.append(f"{filename}: {', '.join(missing)}")

    assert contradicting == []
