"""The bundle version names the series and the content of the bundled data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import ccnl_engine
from ccnl_engine.bundle.facade import SERIES
from ccnl_engine.bundle.loaders import MANIFEST, bundle_version

_KNOWLEDGE = Path(ccnl_engine.__file__).parent / "knowledge"


def _digest(resources: list[object]) -> str:
    canonical = json.dumps(resources, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def test_the_version_is_the_series_and_the_manifest_digest() -> None:
    """Any change to a resource hash in the manifest changes the version."""
    resources = json.loads((_KNOWLEDGE / MANIFEST).read_text(encoding="utf-8"))[
        "resources"
    ]
    assert bundle_version() == f"{SERIES}+{_digest(resources)}"
    assert ccnl_engine.bundle_version == bundle_version()

    changed = [{**resources[0], "source_hash": "0" * 64}, *resources[1:]]
    assert _digest(changed) != _digest(resources)
