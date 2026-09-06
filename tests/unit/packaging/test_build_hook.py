"""Tests that the build hook data-directory paths point to real directories.

The build hook (packaging/build_hook.py) lists source directories whose JSON
files it compresses into .json.gz for the wheel.  A typo in any of those
paths silently produces an empty wheel — no data files are found, no error is
raised — which breaks all runtime data access without any test failure.

These tests guard against that class of bug by asserting that every source
directory listed in _DATA_DIRS exists on disk and contains at least one JSON
file.

The build hook is parsed with ast rather than imported so that hatchling (a
build-only dependency) need not be installed in the test environment.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_BUILD_HOOK = _PROJECT_ROOT / "packaging" / "build_hook.py"


def _extract_data_dirs() -> list[tuple[str, str]]:
    """Parse _DATA_DIRS from build_hook.py without importing it.

    Returns:
        List of (dist_prefix, src_rel) tuples, same as _DATA_DIRS.

    Raises:
        AssertionError: If _DATA_DIRS cannot be found in the build hook.
    """
    tree = ast.parse(_BUILD_HOOK.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        # _DATA_DIRS uses a type annotation so it is an AnnAssign, not Assign.
        if not (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "_DATA_DIRS"
            and isinstance(node.value, ast.List)
        ):
            continue
        pairs: list[tuple[str, str]] = []
        for elt in node.value.elts:
            if not isinstance(elt, ast.Tuple) or len(elt.elts) != 2:
                continue
            a, b = elt.elts
            if isinstance(a, ast.Constant) and isinstance(b, ast.Constant):
                pairs.append((str(a.value), str(b.value)))
        return pairs
    msg = "_DATA_DIRS not found in build_hook.py"
    raise AssertionError(msg)


_DATA_DIRS = _extract_data_dirs()


@pytest.mark.parametrize(
    ("dist_prefix", "src_rel"),
    _DATA_DIRS,
    ids=[src for _, src in _DATA_DIRS],
)
class TestBuildHookDataDirs:
    """Each entry in _DATA_DIRS must point to a real, populated directory."""

    def test_source_dir_exists(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory listed in the build hook must exist."""
        src_dir = _PROJECT_ROOT / src_rel
        assert src_dir.is_dir(), (
            f"Build hook source directory not found: {src_rel!r}. "
            "Check the _DATA_DIRS entries in packaging/build_hook.py."
        )

    def test_source_dir_has_json_files(self, dist_prefix: str, src_rel: str) -> None:
        """The source directory must contain at least one .json file."""
        src_dir = _PROJECT_ROOT / src_rel
        json_files = list(src_dir.glob("*.json"))
        assert len(json_files) > 0, (
            f"No .json files found in {src_rel!r}. "
            "The wheel would be built without any data files."
        )
