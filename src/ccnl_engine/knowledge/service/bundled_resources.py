"""BundledResourceStore: unified JSON listing and reading for package data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.knowledge.service.bundled import read_bundled

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


class BundledResourceStore:
    """Read JSON resources from a package data directory.

    Handles both the editable-install layout (``.json``) and the wheel layout
    (``.json.gz``), so callers never need to know which form is present.

    Args:
        pkg: A :class:`~importlib.resources.abc.Traversable` pointing to the
            package data directory, e.g. the result of
            ``importlib.resources.files("ccnl_engine.knowledge.ccnl.data")``.
    """

    def __init__(self, pkg: Traversable) -> None:
        """Initialise the store bound to *pkg*."""
        self._pkg = pkg

    def list_json(self) -> list[str]:
        """Return a sorted list of available JSON filenames.

        Both ``.json`` (editable install) and ``.json.gz`` (wheel) entries are
        included; compressed entries are normalised to their ``.json`` name.
        When both forms exist for the same file, the name appears once.

        Returns:
            Sorted list of ``.json`` filenames present in the package.
        """
        seen: set[str] = set()
        for resource in self._pkg.iterdir():
            name = resource.name
            if name.endswith(".json.gz"):
                seen.add(name[:-3])
            elif name.endswith(".json"):
                seen.add(name)
        return sorted(seen)

    def read_json(self, filename: str) -> str:
        """Read a JSON file, preferring the compressed variant when available.

        Args:
            filename: The ``.json`` filename to read (without ``.gz`` suffix).

        Returns:
            File content decoded as UTF-8.
        """
        return read_bundled(self._pkg, filename)
