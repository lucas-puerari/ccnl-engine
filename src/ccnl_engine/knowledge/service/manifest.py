"""The manifest of the knowledge bundle: the one index of its resources.

``knowledge/manifest.json`` lists every JSON resource of the bundle once,
with its path relative to ``ccnl_engine/knowledge``, its dataset, year and
scope.  The loaders find a resource here, never by globbing directories, so
a file the manifest does not list is not read, and a listed one that is
missing fails loudly.  In a wheel each resource is stored compressed under
the same path with ``.gz``
(:func:`~ccnl_engine.knowledge.service.bundled.read_bundled`).
"""

from __future__ import annotations

import functools
import importlib.resources
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.knowledge.service.bundled import read_bundled

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

__all__ = [
    "MANIFEST",
    "Resource",
    "read_resource",
    "resource_dir",
    "resources",
]

#: Name of the manifest, at the root of the knowledge package.
MANIFEST = "manifest.json"


@dataclass(frozen=True)
class Resource:
    """One resource the manifest lists.

    Attributes:
        path: Path relative to ``ccnl_engine/knowledge``.
        dataset: Dataset of the resource, e.g. ``taxation/annual``.
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
