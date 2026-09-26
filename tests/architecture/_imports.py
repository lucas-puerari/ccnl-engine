"""Static import analysis of the ``ccnl_engine`` package.

Sources are parsed with :mod:`ast` and never imported, so the analysis sees
the code as written and cannot be influenced by import-time side effects.
Imports under ``if TYPE_CHECKING:`` are ignored: they do not run.

Every module is placed on a layer:

- ``root``: the package root ``ccnl_engine/__init__.py``, the public API;
- ``api``: the ``ccnl_engine.api`` capability;
- ``application``, ``service``, ``domain``: ``ccnl_engine.<capability>.<layer>``;
- ``metadata``: ``ccnl_engine.version`` and the ``ccnl_engine.knowledge`` data
  bundle outside its ``service`` layer (version strings and resource anchors);
- ``package``: a capability ``__init__.py``, which must stay import free.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from pathlib import Path

ROOT_PACKAGE = "ccnl_engine"
LAYERS: frozenset[str] = frozenset({"application", "service", "domain"})

#: Layers each layer may import at runtime.  Same-layer imports inside one
#: capability are always allowed; cross-capability rules are checked apart.
ALLOWED_LAYERS: Mapping[str, frozenset[str]] = {
    "root": frozenset({
        "root",
        "api",
        "application",
        "service",
        "domain",
        "metadata",
    }),
    "api": frozenset({"api", "application", "metadata"}),
    "application": frozenset({"application", "service", "domain", "metadata"}),
    "service": frozenset({"service", "domain", "metadata"}),
    "domain": frozenset({"domain"}),
    "metadata": frozenset(),
    "package": frozenset(),
}

_SHARED_CAPABILITY = "shared"
_METADATA_MODULES = frozenset({f"{ROOT_PACKAGE}.version"})
_DATA_CAPABILITY = "knowledge"


@dataclass(frozen=True)
class Module:
    """A parsed source module.

    Attributes:
        name: Dotted module name, e.g. ``ccnl_engine.api.facade``.
        path: Source path relative to the directory holding the package.
        is_package: True for an ``__init__.py``.
        tree: Parsed module body.
    """

    name: str
    path: str
    is_package: bool
    tree: ast.Module


@dataclass(frozen=True)
class Import:
    """A runtime import of a ``ccnl_engine`` module.

    Attributes:
        importer: Module holding the import statement.
        target: Absolute dotted name of the imported module.
        lineno: Line of the import statement.
    """

    importer: Module
    target: str
    lineno: int

    def describe(self) -> str:
        """Return ``path:line -> target`` for failure messages.

        Returns:
            A one-line human-readable description of the import.
        """
        return f"{self.importer.path}:{self.lineno} -> {self.target}"


@dataclass(frozen=True)
class Location:
    """Capability and layer of a module.

    Attributes:
        capability: Capability name, empty for the package root and version.
        layer: One of the keys of :data:`ALLOWED_LAYERS`.
    """

    capability: str
    layer: str

    @property
    def node(self) -> str:
        """The ``<capability>.<layer>`` node name used for cycles.

        Returns:
            The node name, or the bare layer when there is no capability.
        """
        if not self.capability or self.capability == self.layer:
            return self.layer
        return f"{self.capability}.{self.layer}"


def parse_sources(sources: Mapping[str, str]) -> dict[str, Module]:
    """Parse ``{relative path: source}`` into modules keyed by dotted name.

    Paths are relative to the directory holding ``ccnl_engine``, for example
    ``ccnl_engine/api/facade.py``.

    Returns:
        The parsed modules keyed by dotted module name.
    """
    modules: dict[str, Module] = {}
    for path, source in sources.items():
        parts = path.removesuffix(".py").split("/")
        is_package = parts[-1] == "__init__"
        if is_package:
            parts = parts[:-1]
        name = ".".join(parts)
        modules[name] = Module(name, path, is_package, ast.parse(source, path))
    return modules


def read_package(src: Path) -> dict[str, Module]:
    """Parse every ``.py`` file of ``ccnl_engine`` under *src*.

    Returns:
        The parsed modules keyed by dotted module name.
    """
    return parse_sources({
        path.relative_to(src).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted((src / ROOT_PACKAGE).rglob("*.py"))
        if not any(part.startswith(".") for part in path.relative_to(src).parts)
    })


def locate(name: str) -> Location | None:
    """Return the capability and layer of the ``ccnl_engine`` module *name*.

    Returns:
        The location, or None when the module fits no layer.
    """
    if name == ROOT_PACKAGE:
        return Location("", "root")
    if name in _METADATA_MODULES:
        return Location("", "metadata")
    capability, *rest = name.split(".")[1:]
    if capability == "api":
        layer: str | None = "api"
    elif rest and rest[0] in LAYERS:
        layer = rest[0]
    elif capability == _DATA_CAPABILITY:
        layer = "metadata"
    else:
        layer = None if rest else "package"
    return None if layer is None else Location(capability, layer)


def _is_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def runtime_nodes(tree: ast.Module) -> Iterator[ast.AST]:
    """Yield every node that runs outside ``if TYPE_CHECKING:`` bodies.

    The ``else`` branch of such a guard runs at runtime and is yielded.

    Yields:
        AST nodes in depth-first order.
    """
    stack: list[ast.AST] = [tree]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, ast.If) and _is_type_checking(node.test):
            stack.extend(reversed(node.orelse))
            continue
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _in_package(name: str) -> bool:
    return name == ROOT_PACKAGE or name.startswith(f"{ROOT_PACKAGE}.")


def _resolve_from(module: Module, node: ast.ImportFrom) -> str:
    if not node.level:
        return node.module or ""
    base = module.name.split(".")
    if not module.is_package:
        base = base[:-1]
    base = base[: len(base) - (node.level - 1)]
    return ".".join([*base, *([node.module] if node.module else [])])


def _targets(
    module: Module, node: ast.AST, known: Mapping[str, Module]
) -> Iterator[str]:
    if isinstance(node, ast.Import):
        yield from (alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        base = _resolve_from(module, node)
        for alias in node.names:
            submodule = f"{base}.{alias.name}"
            yield submodule if submodule in known else base


def runtime_imports(modules: Mapping[str, Module]) -> list[Import]:
    """Return every runtime import of a ``ccnl_engine`` module.

    ``from package import submodule`` resolves to the submodule when it is
    one of *modules*.  Relative imports are made absolute.

    Returns:
        The imports, in module and source order, without duplicates.
    """
    found: list[Import] = []
    for module in modules.values():
        seen: set[tuple[str, int]] = set()
        for node in runtime_nodes(module.tree):
            for target in _targets(module, node, modules):
                key = (target, getattr(node, "lineno", 0))
                if _in_package(target) and key not in seen:
                    seen.add(key)
                    found.append(Import(module, target, key[1]))
    return found


def unclassified(modules: Mapping[str, Module]) -> list[str]:
    """Return modules, and imported modules, that fit no layer.

    Returns:
        Sorted module paths or import descriptions.
    """
    bad = {m.path for m in modules.values() if locate(m.name) is None}
    bad.update(
        imp.describe() for imp in runtime_imports(modules) if locate(imp.target) is None
    )
    return sorted(bad)


def layer_violations(modules: Mapping[str, Module]) -> list[str]:
    """Return imports that break :data:`ALLOWED_LAYERS`.

    Returns:
        Sorted descriptions of the offending imports.
    """
    bad: list[str] = []
    for imp in runtime_imports(modules):
        source, target = locate(imp.importer.name), locate(imp.target)
        if source is None or target is None:
            continue
        if target.layer not in ALLOWED_LAYERS[source.layer]:
            bad.append(f"{imp.describe()} ({source.layer} -> {target.layer})")
    return sorted(bad)


def _allowlisted(
    capability: str, target: str, allowlist: Mapping[tuple[str, str], str]
) -> tuple[str, str] | None:
    for key in allowlist:
        owner, prefix = key
        if owner == capability and (
            target == prefix or target.startswith(f"{prefix}.")
        ):
            return key
    return None


def foreign_domain_imports(
    modules: Mapping[str, Module],
) -> list[tuple[Import, str]]:
    """Return domain imports of another capability's domain.

    ``shared.domain`` is not foreign: it holds the shared primitives.

    Returns:
        Each import with the importing capability.
    """
    found: list[tuple[Import, str]] = []
    for imp in runtime_imports(modules):
        source, target = locate(imp.importer.name), locate(imp.target)
        if (
            source is not None
            and target is not None
            and source.layer == target.layer == "domain"
            and target.capability not in {source.capability, _SHARED_CAPABILITY}
        ):
            found.append((imp, source.capability))
    return found


def domain_coupling_violations(
    modules: Mapping[str, Module], allowlist: Mapping[tuple[str, str], str]
) -> list[str]:
    """Return foreign domain imports that no allowlist entry covers.

    An entry ``(capability, target)`` covers imports of *target* or of any of
    its submodules from the domain of *capability*.

    Returns:
        Sorted descriptions of the uncovered imports.
    """
    return sorted(
        imp.describe()
        for imp, capability in foreign_domain_imports(modules)
        if _allowlisted(capability, imp.target, allowlist) is None
    )


def stale_allowlist_entries(
    modules: Mapping[str, Module], allowlist: Mapping[tuple[str, str], str]
) -> list[tuple[str, str]]:
    """Return allowlist entries that no import uses any more.

    Returns:
        The unused entries, sorted.
    """
    used = {
        _allowlisted(capability, imp.target, allowlist)
        for imp, capability in foreign_domain_imports(modules)
    }
    return sorted(key for key in allowlist if key not in used)


def layer_graph(modules: Mapping[str, Module]) -> dict[str, set[str]]:
    """Return the runtime import graph over ``<capability>.<layer>`` nodes.

    Returns:
        Adjacency sets; edges within one node are dropped.
    """
    graph: dict[str, set[str]] = {}
    for imp in runtime_imports(modules):
        source, target = locate(imp.importer.name), locate(imp.target)
        if source is None or target is None or source.node == target.node:
            continue
        graph.setdefault(source.node, set()).add(target.node)
        graph.setdefault(target.node, set())
    return graph


def cycles(graph: Mapping[str, set[str]]) -> list[list[str]]:
    """Return the strongly connected components with more than one node.

    Returns:
        Each cycle as a sorted node list; the list itself is sorted.
    """
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    found: list[list[str]] = []

    def pop_component(root: str) -> list[str]:
        component = stack[stack.index(root) :]
        del stack[stack.index(root) :]
        return sorted(component)

    def visit(node: str) -> None:
        index[node] = low[node] = len(index)
        stack.append(node)
        for succ in sorted(graph.get(node, set())):
            if succ not in index:
                visit(succ)
                low[node] = min(low[node], low[succ])
            elif succ in stack:
                low[node] = min(low[node], index[succ])
        if low[node] == index[node] and len(component := pop_component(node)) > 1:
            found.append(component)

    for node in sorted(graph):
        if node not in index:
            visit(node)
    return sorted(found)


_IO_MODULES = ("importlib.resources", "pathlib")
_IO_METHODS = frozenset({"read_text", "read_bytes", "open"})


def _io_import(node: ast.AST) -> str | None:
    names: list[str] = []
    if isinstance(node, ast.Import):
        names = [alias.name for alias in node.names]
    elif isinstance(node, ast.ImportFrom) and not node.level:
        base = node.module or ""
        names = [base, *(f"{base}.{alias.name}" for alias in node.names)]
    for name in names:
        for io_module in _IO_MODULES:
            if name == io_module or name.startswith(f"{io_module}."):
                return f"imports {io_module}"
    return None


def _io_call(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Name) and func.id == "open":
        return "calls open()"
    if isinstance(func, ast.Attribute):
        if func.attr in _IO_METHODS:
            return f"calls .{func.attr}()"
        if (
            func.attr == "load"
            and isinstance(func.value, ast.Name)
            and func.value.id == "json"
        ):
            return "calls json.load()"
    return None


def domain_io_violations(modules: Mapping[str, Module]) -> list[str]:
    """Return I/O performed by domain modules.

    Flags imports of ``importlib.resources`` and ``pathlib``, calls to
    ``open()`` and ``json.load()``, and ``.read_text()``, ``.read_bytes()``
    or ``.open()`` calls.

    Returns:
        Sorted ``path:line: reason`` descriptions.
    """
    bad: list[str] = []
    for module in modules.values():
        location = locate(module.name)
        if location is None or location.layer != "domain":
            continue
        for node in runtime_nodes(module.tree):
            reason = _io_import(node) or _io_call(node)
            if reason is not None:
                line = getattr(node, "lineno", 0)
                bad.append(f"{module.path}:{line}: {reason}")
    return sorted(bad)
