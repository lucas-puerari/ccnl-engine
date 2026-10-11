"""Readers of the knowledge bundle: the manifest and the resources it lists.

``knowledge/manifest.json`` lists every JSON resource of the bundle once,
with its path relative to ``ccnl_engine/knowledge``, its dataset, year and
scope.  The loaders find a resource here, never by globbing directories, so
a file the manifest does not list is not read, and a listed one that is
missing fails loudly.  In a wheel each resource is stored compressed under
the same path with ``.gz``
(:func:`~ccnl_engine.knowledge.loaders.read_bundled`).
"""

from __future__ import annotations

import functools
import gzip
import importlib.resources
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


__all__ = [
    "MANIFEST",
    "Resource",
    "read_resource",
    "resource_dir",
    "resources",
]


def read_bundled(pkg: Traversable, filename: str) -> str:
    """Read a bundled data file, preferring the compressed variant when present.

    In installed wheels the data files are stored as ``<filename>.gz`` to
    reduce package size. In editable installs (development) the plain
    ``<filename>`` is used as a fallback.

    The caller receives the decoded content regardless of which variant is
    found. If the ``.gz`` file exists but is corrupt, ``gzip.BadGzipFile``
    propagates to the caller. If neither file exists, ``FileNotFoundError``
    propagates from the inner ``read_bytes()`` / ``read_text()`` call.

    Args:
        pkg: A :class:`~importlib.resources.abc.Traversable` pointing to the
            package data directory (e.g. the result of
            ``importlib.resources.files("ccnl_engine.knowledge")`` joined to
            the directory of a manifest resource).
        filename: The uncompressed filename to look up (e.g. ``"foo.json"``).
            The ``.gz`` variant is tried first; ``filename`` itself is the
            fallback.

    Returns:
        The file content decoded as UTF-8.
    """
    try:
        return gzip.decompress(pkg.joinpath(filename + ".gz").read_bytes()).decode(
            "utf-8"
        )
    except FileNotFoundError:
        return pkg.joinpath(filename).read_text(encoding="utf-8")


#: Name of the manifest, at the root of the knowledge package.
MANIFEST = "manifest.json"


@dataclass(frozen=True)
class Resource:
    """One resource the manifest lists.

    Attributes:
        path: Path relative to ``ccnl_engine/knowledge``.
        dataset: Dataset of the resource, e.g. ``sector``.
        year: Year of the resource, ``None`` when it has none.
        scope: Last dimension of the path (sector, slug, ...), ``None`` when
            the year is the last one.
    """

    path: str
    dataset: str
    year: int | None
    scope: str | None

    @property
    def name(self) -> str:
        """File name of the resource."""
        return self.path.rsplit("/", 1)[-1]


def _root() -> Traversable:
    return importlib.resources.files("ccnl_engine.knowledge")


@functools.cache
def _manifest() -> dict[str, Resource]:
    """Return the resources of the manifest, keyed by path.

    Returns:
        Every resource of the bundle.
    """
    raw = json.loads(read_bundled(_root(), MANIFEST))
    return {
        entry["path"]: Resource(
            entry["path"], entry["dataset"], entry["year"], entry["scope"]
        )
        for entry in raw["resources"]
    }


def resources(dataset: str) -> tuple[Resource, ...]:
    """Return the resources of ``dataset``, in path order.

    Returns:
        The resources the manifest lists for the dataset.
    """
    return tuple(r for path, r in sorted(_manifest().items()) if r.dataset == dataset)


def resource_dir(path: str) -> Traversable:
    """Return the directory that holds the resource at ``path``.

    Every resource sits in a dataset directory, so the path has one.

    Returns:
        The traversable directory, inside the package.
    """
    return _root().joinpath(*path.split("/")[:-1])


def read_resource(path: str) -> str:
    """Return the text of the resource at ``path``.

    Returns:
        The JSON text, from the plain or the compressed file.

    Raises:
        FileNotFoundError: When the manifest does not list ``path``.
    """
    if path not in _manifest():
        msg = f"the knowledge manifest lists no resource {path!r}"
        raise FileNotFoundError(msg)
    return read_bundled(resource_dir(path), path.rsplit("/", 1)[-1])


class BundledResourceStore:
    """Read JSON resources from a package data directory.

    Handles both the editable-install layout (``.json``) and the wheel layout
    (``.json.gz``), so callers never need to know which form is present.

    Args:
        pkg: A :class:`~importlib.resources.abc.Traversable` pointing to the
            package data directory, e.g. the result of
            a directory of the knowledge bundle, e.g.
            ``importlib.resources.files("ccnl_engine.knowledge")``.
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
