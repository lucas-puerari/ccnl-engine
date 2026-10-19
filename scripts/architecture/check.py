"""Enforce the dependency tiers of the concepts and the size of a module.

Two gates over ``src/ccnl_engine``:

- Import gate: every module belongs to the concept of its first path
  segment (``sickness/day/rules.py`` to ``sickness``, ``api.py`` to
  ``api``), and every concept to the tier the "Dependency tiers" table of
  ``docs/engine/architecture-contract.md`` gives it (norms, computation,
  orchestration).  A runtime import of a higher tier fails unless the
  exception table of that section lists the module pair; a listed pair no
  longer imported fails too.  Imports under ``if TYPE_CHECKING:`` do not
  count, imports inside a function do.  A concept missing from the table,
  and an import of the package root, fail.  The package root
  ``__init__.py`` holds the public namespace and is not checked.
- Size gate: a module holds at most 300 physical lines.  The longer modules
  are listed in ``baseline.json`` with their length; a listed module that
  grows, a new module over the limit and a listed module that is gone or
  fits fail.

The script uses the standard library only, so CI can run it without
installing the project.

Usage::

    python scripts/architecture/check.py
    python scripts/architecture/check.py --update-baseline

``--update-baseline`` rewrites the baseline from the tree, to record a
module that shrank; it refuses a module that grew or is new.

Exit codes:
    0   All checks pass.
    1   One or more checks fail.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ccnl_engine"
CONTRACT = ROOT / "docs" / "engine" / "architecture-contract.md"
BASELINE = Path(__file__).resolve().with_name("baseline.json")

PACKAGE = "ccnl_engine"
MAX_LINES = 300
TIERS = ("norms", "computation", "orchestration")
_SECTION = "## Dependency tiers"
_CODE = re.compile(r"`([^`]+)`")


@dataclass(frozen=True, slots=True)
class Contract:
    """The tier of each concept and the upward imports allowed by module.

    Attributes:
        tiers: Rank of each concept, ``0`` for norms up to ``2`` for
            orchestration.
        exceptions: Allowed upward imports as (importer, imported) paths
            relative to the package, such as ``seniority/services.py``.
    """

    tiers: Mapping[str, int]
    exceptions: frozenset[tuple[str, str]]


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_contract(text: str) -> Contract:
    """Read the tier table and the exception table of the contract page.

    Returns:
        The contract of the "Dependency tiers" section.

    Raises:
        ValueError: The section or its tier table is missing.
    """
    start = text.find(_SECTION)
    if start < 0:
        msg = f"no {_SECTION!r} section in the architecture contract"
        raise ValueError(msg)
    end = text.find("\n## ", start + len(_SECTION))
    tiers: dict[str, int] = {}
    exceptions: set[tuple[str, str]] = set()
    for line in text[start : end if end >= 0 else None].splitlines():
        if not line.startswith("|"):
            continue
        cells = _cells(line)
        if cells[0] in TIERS:
            rank = TIERS.index(cells[0])
            tiers.update(dict.fromkeys(_CODE.findall(cells[1]), rank))
        elif len(cells) >= 2 and cells[0].endswith(".py`"):
            exceptions.add((cells[0].strip("`"), cells[1].strip("`")))
    if not tiers:
        msg = "no tier table in the architecture contract"
        raise ValueError(msg)
    return Contract(tiers=tiers, exceptions=frozenset(exceptions))


def _is_type_checking(test: ast.expr) -> bool:
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def runtime_imports(node: ast.AST) -> Iterator[ast.Import | ast.ImportFrom]:
    """Yield the imports below ``node`` that run, skipping TYPE_CHECKING blocks.

    Yields:
        Each ``import`` and ``from ... import`` statement that runs.
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Import | ast.ImportFrom):
            yield child
        elif isinstance(child, ast.If) and _is_type_checking(child.test):
            yield from runtime_imports(ast.Module(body=child.orelse, type_ignores=[]))
        else:
            yield from runtime_imports(child)


def _targets(module: tuple[str, ...], node: ast.Import | ast.ImportFrom) -> list[str]:
    """Resolve the modules an import names.

    Returns:
        The imported modules as absolute dotted names.
    """
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if node.level == 0:
        return [node.module or ""]
    package = [PACKAGE, *module[:-1]]
    base = package[: len(package) + 1 - node.level]
    return [".".join([*base, *(node.module.split(".") if node.module else [])])]


def _path(target: str) -> str:
    """Map a dotted module of the package to its path.

    Returns:
        The path relative to the package, such as ``seniority/services.py``.
    """
    return "/".join(target.split(".")[1:]) + ".py"


def _edge_error(
    importer: str, concept: str, target: str, contract: Contract
) -> str | None:
    """Judge the import of ``target`` by ``importer`` of ``concept``.

    Returns:
        Why the import breaks the tiers, or ``None`` when it keeps them.
    """
    parts = target.split(".")
    if len(parts) == 1:
        return f"{importer}: imports the package root {PACKAGE}"
    rank = contract.tiers.get(parts[1])
    if rank is None:
        return f"{importer}: imports {parts[1]}, a concept with no tier"
    own = contract.tiers[concept]
    if rank <= own:
        return None
    return (
        f"{importer}: imports {_path(target)} of tier {TIERS[rank]} from tier "
        f"{TIERS[own]}, an upward import the contract does not list"
    )


def _module_edges(
    path: Path, source: Path, contract: Contract
) -> tuple[list[str], set[tuple[str, str]]]:
    """Check the runtime imports of one module against the tiers.

    Returns:
        The errors of the module, and the listed exceptions it uses.
    """
    relative = path.relative_to(source)
    importer = relative.as_posix()
    module = relative.with_suffix("").parts
    if module[0] not in contract.tiers:
        return [f"{importer}: concept {module[0]} has no tier"], set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    errors: list[str] = []
    used: set[tuple[str, str]] = set()
    for node in runtime_imports(tree):
        for target in _targets(module, node):
            if target.split(".")[0] != PACKAGE:
                continue
            edge = (importer, _path(target))
            error = _edge_error(importer, module[0], target, contract)
            if error is not None and edge in contract.exceptions:
                used.add(edge)
            elif error is not None:
                errors.append(error)
    return errors, used


def upward_edges(
    source: Path, contract: Contract
) -> tuple[list[str], set[tuple[str, str]]]:
    """Check every module of ``source`` but the package root.

    Returns:
        The errors, and the listed exceptions the tree still uses.
    """
    errors: list[str] = []
    used: set[tuple[str, str]] = set()
    for path in sorted(source.rglob("*.py")):
        if path == source / "__init__.py":
            continue
        found, edges = _module_edges(path, source, contract)
        errors.extend(found)
        used |= edges
    return errors, used


def check_imports(source: Path, contract_text: str) -> list[str]:
    """Return every import of ``source`` that breaks the dependency tiers.

    Returns:
        One message per upward import the contract does not list, per
        concept without a tier and per listed exception no longer imported.
    """
    contract = read_contract(contract_text)
    errors, used = upward_edges(source, contract)
    errors.extend(
        f"{importer}: the contract lists an upward import of {imported} "
        "that no longer exists"
        for importer, imported in sorted(contract.exceptions - used)
    )
    return errors


def oversize(source: Path) -> dict[str, int]:
    """Return the modules of ``source`` longer than the limit, with their length.

    Returns:
        Physical lines by path relative to the repository root.
    """
    found: dict[str, int] = {}
    for path in sorted(source.rglob("*.py")):
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > MAX_LINES:
            found[path.relative_to(source.parents[1]).as_posix()] = lines
    return found


def _growth(current: Mapping[str, int], baseline: Mapping[str, int]) -> list[str]:
    """Compare the oversize modules with the baseline.

    Returns:
        One message per oversize module that is new or longer than listed.
    """
    errors: list[str] = []
    for module, lines in current.items():
        allowed = baseline.get(module)
        if allowed is None:
            errors.append(f"{module}: {lines} lines, over the limit of {MAX_LINES}")
        elif lines > allowed:
            errors.append(f"{module}: {lines} lines, grew from {allowed}")
    return errors


def check_sizes(source: Path, baseline: Mapping[str, int]) -> list[str]:
    """Return every module of ``source`` that breaks the size ratchet.

    Returns:
        One message per new oversize module, per listed module that grew
        and per listed module that is gone or fits.
    """
    current = oversize(source)
    return _growth(current, baseline) + [
        f"{module}: listed in the baseline but gone or within {MAX_LINES} lines"
        for module in sorted(set(baseline) - set(current))
    ]


def load_baseline(path: Path) -> dict[str, int]:
    """Read the size baseline.

    Returns:
        The allowed length of each oversize module.
    """
    data: dict[str, int] = json.loads(path.read_text(encoding="utf-8"))
    return data


def update_baseline(source: Path, path: Path) -> list[str]:
    """Rewrite the baseline from ``source`` unless a module grew or is new.

    Returns:
        The modules that grew or are new; the baseline is left untouched
        when there is any.
    """
    current = oversize(source)
    errors = _growth(current, load_baseline(path))
    if not errors:
        path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Run both gates, or rewrite the baseline.

    Returns:
        The exit code: ``0`` when every check passes, ``1`` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args(argv)
    if args.update_baseline:
        errors = update_baseline(SOURCE, BASELINE)
    else:
        errors = check_imports(SOURCE, CONTRACT.read_text(encoding="utf-8"))
        errors += check_sizes(SOURCE, load_baseline(BASELINE))
    for error in errors:
        print(error)
    if errors:
        return 1
    print("Architecture check passed: dependency tiers and module sizes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
