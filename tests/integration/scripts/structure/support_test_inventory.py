"""Inventory of the test suite: exact duplicates and owners per capability.

A test is an exact duplicate of another when its body, docstring aside, its
decorators, its arguments and the class it sits in are the same, and every
imported name it uses comes from the same module.  Two tests calling a
``main`` imported from different scripts are therefore distinct.

The owner of a test is the source module it exercises:

- a test that mirrors a module, as checked by ``test_test_layout``, owns it;
- a knowledge or public API test, which mirrors no module, owns the modules
  defining the public names it imports, the facade aside, since every such
  test goes through it.

Run ``python -m tests.integration.scripts.structure.support_test_inventory``
for the report: the tests of each capability per level, and the modules
tested at more than one level, the place to check that each level asserts
something different.
"""

from __future__ import annotations

import ast
import importlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

_TESTS = Path(__file__).parents[3]
_SRC = _TESTS.parent / "src" / "ccnl_engine"
_LEVELS = ("knowledge", "unit", "integration")
_FACADE = "api"
_NONE = "(facade or tooling only)"

__all__ = ["TestFunction", "collect", "exact_duplicates", "report"]


@dataclass(frozen=True)
class TestFunction:
    """One test function or method and what makes it identical to another."""

    __test__ = False  # not a pytest class

    path: str
    name: str
    key: str


def _imported_names(tree: ast.Module) -> dict[str, str]:
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                names[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names[alias.asname or alias.name] = alias.name
    return names


class _Qualify(ast.NodeTransformer):
    """Replace each imported name with the dotted path it was imported from."""

    def __init__(self, names: dict[str, str]) -> None:
        self._names = names

    def visit_Name(self, node: ast.Name) -> ast.Name:
        return ast.Name(id=self._names.get(node.id, node.id), ctx=node.ctx)


def _key(
    node: ast.FunctionDef | ast.AsyncFunctionDef, context: str, q: _Qualify
) -> str:
    body = node.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
    ):
        body = body[1:]
    parts: list[ast.AST] = [*body, *node.decorator_list, node.args]
    # The tree is parsed for this key only: qualifying it in place is safe.
    return context + "|".join(ast.dump(q.visit(part)) for part in parts)


def _scopes(
    tree: ast.Module,
) -> list[tuple[str, str, list[ast.stmt]]]:
    """Return the module and each class as (prefix, context, members).

    Returns:
        The module scope first, then one scope per top-level class.
    """
    scopes: list[tuple[str, str, list[ast.stmt]]] = [("", "", tree.body)]
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            fields = [s for s in node.body if not isinstance(s, ast.FunctionDef)]
            context = ast.dump(ast.Module(body=fields, type_ignores=[]))
            scopes.append((f"{node.name}.", context, node.body))
    return scopes


def _functions(path: Path, tests: Path) -> list[TestFunction]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    qualify = _Qualify(_imported_names(tree))
    rel = path.relative_to(tests).as_posix()
    return [
        TestFunction(rel, prefix + member.name, _key(member, context, qualify))
        for prefix, context, members in _scopes(tree)
        for member in members
        if isinstance(member, ast.FunctionDef | ast.AsyncFunctionDef)
        and member.name.startswith("test")
    ]


def collect(tests: Path = _TESTS) -> list[TestFunction]:
    """Return every test function under *tests*.

    Returns:
        The tests, in path order.
    """
    files = sorted(tests.rglob("test_*.py"))
    return [fn for path in files for fn in _functions(path, tests)]


def exact_duplicates(functions: list[TestFunction]) -> list[tuple[str, ...]]:
    """Return the groups of tests that are exact duplicates of each other.

    Returns:
        Sorted groups of ``path::name``, each with two or more tests.
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for fn in functions:
        groups[fn.key].append(f"{fn.path}::{fn.name}")
    return sorted(tuple(g) for g in groups.values() if len(g) > 1)


def _mirrored(rel: Path, src: Path) -> str | None:
    directory = src.joinpath(*rel.parts[1:-1])
    stem = rel.stem.removeprefix("test_")
    if not directory.is_dir():
        return None
    names = sorted(
        (p.stem.lstrip("_") for p in directory.iterdir() if p.name != "__init__.py"),
        key=len,
        reverse=True,
    )
    for name in names:
        if stem == name or stem.startswith(f"{name}_"):
            return ".".join((*rel.parts[1:-1], name))
    return None


def _public_owners(path: Path) -> set[str]:
    owners: set[str] = set()
    for dotted in _imported_names(ast.parse(path.read_text(encoding="utf-8"))).values():
        module, _, name = dotted.rpartition(".")
        if not module.startswith("ccnl_engine"):
            continue
        defined = getattr(importlib.import_module(module), name, None)
        origin = getattr(defined, "__module__", "") or ""
        if origin.startswith("ccnl_engine."):
            owners.add(_strip_private(origin.removeprefix("ccnl_engine.")))
    return owners - {_FACADE}


def _strip_private(module: str) -> str:
    return ".".join(part.lstrip("_") for part in module.split("."))


def _owners(path: Path, tests: Path, src: Path) -> tuple[str, set[str]]:
    rel = path.relative_to(tests)
    level = rel.parts[0]
    inner = rel.relative_to(rel.parts[0])
    if level not in _LEVELS or inner.parts[0] != "ccnl_engine":
        return level, set()
    owner = _mirrored(inner, src)
    if owner is not None:
        return level, {_strip_private(owner)}
    return level, _public_owners(path)


def _related(a: str, b: str) -> bool:
    return a == b or a.startswith(f"{b}.") or b.startswith(f"{a}.")


def _shared(levels: dict[str, set[str]]) -> dict[str, tuple[str, ...]]:
    """Return the modules tested at more than one level, with those levels.

    A package and the modules inside it count as one frontier.

    Returns:
        The levels of each module, in level order, for two levels or more.
    """
    shared: dict[str, tuple[str, ...]] = {}
    for module in sorted(levels):
        seen = set().union(*(s for m, s in levels.items() if _related(m, module)))
        if len(seen) > 1:
            shared[module] = tuple(lv for lv in _LEVELS if lv in seen)
    return shared


def report(tests: Path = _TESTS, src: Path = _SRC) -> str:
    """Return the Markdown report of the tests per capability and level.

    Returns:
        A table of the tests owning each capability per level, then the
        modules tested at more than one level.
    """
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    levels: dict[str, set[str]] = defaultdict(set)
    for fn in collect(tests):
        level, owners = _owners(tests / fn.path, tests, src)
        for capability in {owner.split(".")[0] for owner in owners} or {_NONE}:
            counts[capability][level] += 1
        for owner in owners:
            levels[owner].add(level)
    lines = ["| Capability | knowledge | unit | integration |", "|---|---|---|---|"]
    lines += [
        f"| {cap} | " + " | ".join(str(counts[cap][lv]) for lv in _LEVELS) + " |"
        for cap in sorted(counts)
    ]
    lines += ["", "Modules tested at more than one level:", ""]
    shared = _shared(levels)
    lines += [f"- `{m}`: {', '.join(lv)}" for m, lv in shared.items()] or ["- none"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(report(), end="")  # noqa: T201 - command-line report
