"""Hatchling build hook: compress JSON data files into .json.gz for the wheel.

Only active for standard wheel builds (not editable installs or sdists).
Each .json file in the two data directories is compressed with gzip (level 9,
mtime=0 for reproducibility) and injected into the wheel via force_include.
The plain .json files are excluded from the wheel by the pyproject.toml
exclude list, so the wheel carries only the compressed variant.
"""

from __future__ import annotations

import gzip
import pathlib
import tempfile
from typing import Any

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

# Pairs of (package-relative dist prefix, source directory relative to project root).
_DATA_DIRS: list[tuple[str, str]] = [
    ("ccnl_engine/contracts/data", "src/ccnl_engine/contracts/data"),
    ("ccnl_engine/tax/data", "src/ccnl_engine/tax/data"),
    ("ccnl_engine/surtax/data", "src/ccnl_engine/surtax/data"),
]


class CustomBuildHook(BuildHookInterface[BuilderConfig]):
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

        for dist_prefix, src_rel in _DATA_DIRS:
            src_dir = root / src_rel
            for json_file in sorted(src_dir.glob("*.json")):
                compressed = gzip.compress(
                    json_file.read_bytes(), compresslevel=9, mtime=0
                )
                out_name = json_file.name + ".gz"
                out_path = tmp / dist_prefix / out_name
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_bytes(compressed)
                build_data["force_include"][str(out_path)] = f"{dist_prefix}/{out_name}"
