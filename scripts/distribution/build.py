"""Hatchling build hook: compress JSON data files into .json.gz for the wheel.

Only active for standard wheel builds (not editable installs or sdists).
The knowledge manifest and every resource it lists are compressed with
gzip (level 9, mtime=0 for reproducibility) and injected into the wheel via
force_include, under the same path with ``.gz``.
The plain .json files are excluded from the wheel by the pyproject.toml
exclude list, so the wheel carries only the compressed variant.
"""

from __future__ import annotations

import gzip
import json
import pathlib
import tempfile
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

#: The knowledge bundle: every resource its manifest lists, and the manifest.
_KNOWLEDGE = "ccnl_engine/knowledge"
_MANIFEST = "manifest.json"


def _knowledge_files(root: pathlib.Path) -> list[str]:
    """Return the knowledge files the wheel carries, relative to the bundle.

    Returns:
        The manifest and every resource it lists.
    """
    manifest = root / "src" / _KNOWLEDGE / _MANIFEST
    resources = json.loads(manifest.read_text(encoding="utf-8"))["resources"]
    return [_MANIFEST, *(entry["path"] for entry in resources)]


class CustomBuildHook(BuildHookInterface):  # type: ignore[type-arg]
    """Compress bundled JSON data files into .json.gz during wheel builds."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """Inject compressed data files into the wheel artifact.

        Skips editable installs (version == "editable") and non-wheel targets
        so that development installs continue to read the plain .json files.

        Args:
            version: The hatchling build version string (``"standard"`` for a
                regular wheel, ``"editable"`` for an editable install).
            build_data: Mutable dict of build metadata; ``force_include`` maps
                absolute local paths to their destination paths inside the wheel.
        """
        if self.target_name != "wheel" or version != "standard":
            return

        root = pathlib.Path(self.root)
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="ccnl-gz-"))

        for rel in _knowledge_files(root):
            source = root / "src" / _KNOWLEDGE / rel
            compressed = gzip.compress(source.read_bytes(), compresslevel=9, mtime=0)
            out_path = tmp / _KNOWLEDGE / f"{rel}.gz"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(compressed)
            build_data["force_include"][str(out_path)] = f"{_KNOWLEDGE}/{rel}.gz"
