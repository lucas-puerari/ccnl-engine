"""Map every tracked file to its path in the architecture contract.

The contract (``docs/engine/architecture-contract.md``) fixes the target
trees of ``src``, ``tests``, ``demo`` and ``scripts``. This script builds the
inventory ``current path -> target`` for every file ``git ls-files`` lists
under those four roots, from ``inventory_rules.json``:

- ``overrides`` map one path to its target and win over every rule;
- ``rules`` are tried in order and the first whose ``pattern`` matches
  applies. A rule with ``target`` formats it with the named groups of the
  match; a rule with ``mirror`` maps a unit or integration test through the
  module it mirrors (``test_z.py`` or ``test_z_<suffix>.py`` for module
  ``z`` or ``_z``, as ``tests/architecture/test_test_layout.py`` reads it)
  into the ``mirror`` category, renamed after the target module.

A target is a path, or ``{"dissolve": <dir>}`` for a package marker
``__init__.py`` that holds only a docstring and becomes part of the
namespace package ``<dir>``. An ``__init__.py`` with code needs a file
target, so no re-export is lost.

``--check`` fails on an unmapped path, a duplicate target, a target that
breaks the contract (underscore basename, technical directory, depth, role
names, tree) and on drift between the rules and ``inventory.json``.

The script uses the standard library only.

Usage::

    python scripts/structure/inventory.py            # rewrite the inventory
    python scripts/structure/inventory.py --check    # fail on drift or a bad target
    python scripts/structure/inventory.py --summary  # counts per target area

Exit codes:
    0   The inventory is written, or matches the rules and the contract.
    1   The check fails.
    2   The rules, the inventory or the git listing cannot be read.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess  # noqa: S404
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

from pathlib import Path

ROOT: Final = Path(__file__).resolve().parents[2]
RULES: Final = Path(__file__).with_name("inventory_rules.json")
INVENTORY: Final = Path(__file__).with_name("inventory.json")

#: Roots whose tracked files the inventory covers.
TRACKED_ROOTS: Final = ("src", "tests", "demo", "scripts")
#: The only file of the target trees whose name starts with an underscore.
ROOT_INIT: Final = "src/ccnl_engine/__init__.py"
PACKAGE: Final = "src/ccnl_engine"
#: Directory names that name a technical layer, never a domain.
TECHNICAL_DIRS: Final = frozenset({
    "domain",
    "application",
    "service",
    "handlers",
    "fixtures",
    "data",
})
#: Technical roles of a production module; ``<role>_<suffix>.py`` splits one.
ROLES: Final = (
    "models",
    "types",
    "inputs",
    "requests",
    "results",
    "policies",
    "rules",
    "services",
    "handlers",
    "ports",
    "repositories",
    "loaders",
    "serializers",
    "validators",
    "facade",
)
#: Modules of the package root; ``<name>_<suffix>.py`` splits one.
ROOT_MODULES: Final = (
    "api",
    "inputs",
    "results",
    "events",
    "catalog",
    "errors",
    "primitives",
    "validation",
    "version",
)
_SUFFIX: Final = "(?:_[a-z0-9]+)*"
ROLE_NAME: Final = re.compile(rf"^(?:{'|'.join(ROLES)}){_SUFFIX}\.py$")
ROOT_NAME: Final = re.compile(rf"^(?:{'|'.join(ROOT_MODULES)}){_SUFFIX}\.py$")
#: Python modules a test tree may hold besides tests.
TEST_NAME: Final = re.compile(
    rf"^(?:test_[a-z0-9_]+|conftest|(?:builders|oracles|support){_SUFFIX})\.py$"
)
#: Directories of the target production tree, relative to ``src/ccnl_engine``.
SOURCE_TREE: Final = frozenset({
    "",
    "contract",
    *(
        f"contract/{name}"
        for name in (
            "identity",
            "employment",
            "compensation",
            "working_time",
            "absence",
            "sickness",
            "seniority",
            "fund",
            "catalog",
        )
    ),
    "payroll",
    *(
        f"payroll/{name}"
        for name in (
            "period",
            "year",
            "employment",
            "event",
            "amount",
            "contribution",
            "taxation",
            "withholding",
            "sickness",
            "family",
            "termination",
            "accrual",
            "ledger",
            "assurance",
            "capability",
            "state",
        )
    ),
    "tax",
    *(
        f"tax/{name}"
        for name in (
            "income",
            "surtax",
            "contribution",
            "pension",
            "sickness",
            "severance",
            "family",
            "regime",
            "annual",
        )
    ),
    "knowledge",
    "knowledge/capability",
    "knowledge/limitation",
    "provenance",
    "provenance/ruleset",
    "provenance/source",
    "comparison",
    "comparison/ruleset",
})
#: First-level datasets of the knowledge tree.
KNOWLEDGE_DOMAINS: Final = frozenset({
    "contract",
    "taxation",
    "surtax",
    "social_security",
    "policy",
    "capability",
    "limitation",
})
SCRIPT_DOMAINS: Final = frozenset({
    "structure",
    "provenance",
    "knowledge",
    "documentation",
    "quality",
    "distribution",
})
DEMO_DIRS: Final = frozenset({"localization", "release"})
TEST_CATEGORIES: Final = frozenset({"knowledge", "unit", "integration"})
TEST_TOP_FILES: Final = frozenset({"conftest.py", "README.md"})
#: Code root mirrored by each test root.
MIRROR_ROOTS: Final[Mapping[str, str]] = {
    "ccnl_engine": PACKAGE,
    "demo": "demo",
    "scripts": "scripts",
}
#: Directories under the package root before a module.
MAX_SOURCE_DEPTH: Final = 3
#: Directories under ``tests`` before a file.
MAX_TEST_DEPTH: Final = 5

#: A target path, or ``{"dissolve": <dir>}`` for a package marker.
Entry = str | dict[str, str]


@dataclass(frozen=True)
class Rule:
    """One ordered mapping rule of the rules file."""

    pattern: re.Pattern[str]
    target: str | None = None
    mirror: str | None = None


@dataclass(frozen=True)
class Rules:
    """Ordered rules and per-file overrides."""

    rules: tuple[Rule, ...]
    overrides: Mapping[str, Entry]


def _entry(value: object, where: str) -> Entry:
    if isinstance(value, str):
        return value
    if (
        isinstance(value, dict)
        and set(value) == {"dissolve"}
        and isinstance(value["dissolve"], str)
    ):
        return {"dissolve": value["dissolve"]}
    msg = f"{where}: expected a path or {{'dissolve': <dir>}}"
    raise ValueError(msg)


def _rule(raw: object, index: int) -> Rule:
    if not isinstance(raw, dict) or not isinstance(raw.get("pattern"), str):
        msg = f"rule {index}: expected an object with a string 'pattern'"
        raise ValueError(msg)  # noqa: TRY004
    target, mirror = raw.get("target"), raw.get("mirror")
    if (target is None) == (mirror is None):
        msg = f"rule {index}: give exactly one of 'target' and 'mirror'"
        raise ValueError(msg)
    if not isinstance(target or mirror, str):
        msg = f"rule {index}: 'target' and 'mirror' are strings"
        raise ValueError(msg)  # noqa: TRY004
    return Rule(re.compile(raw["pattern"]), target, mirror)


def load_rules(path: Path) -> Rules:
    """Read and validate the rules file.

    Returns:
        The ordered rules and the overrides.

    Raises:
        ValueError: if the file does not hold valid rules and overrides.
    """
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path}: expected a JSON object"
        raise ValueError(msg)  # noqa: TRY004
    rules, overrides = data.get("rules"), data.get("overrides")
    if not isinstance(rules, list) or not isinstance(overrides, dict):
        msg = f"{path}: expected a 'rules' list and an 'overrides' object"
        raise ValueError(msg)  # noqa: TRY004
    return Rules(
        tuple(_rule(raw, index) for index, raw in enumerate(rules)),
        {key: _entry(value, key) for key, value in overrides.items()},
    )


def git_environment() -> dict[str, str]:
    """Return the environment without the ``GIT_*`` variables.

    A git hook exports ``GIT_DIR`` and ``GIT_INDEX_FILE``; left in place they
    would point a git command run for another directory at the repository
    of the hook.

    Returns:
        A copy of ``os.environ`` without the variables git reads to locate a
        repository.
    """
    return {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }


def tracked_files(root: Path) -> list[str]:
    """Return the files git tracks under :data:`TRACKED_ROOTS` of *root*.

    Returns:
        Repository-relative POSIX paths, sorted.
    """
    out = subprocess.run(  # noqa: S603
        ["git", "ls-files", "--", *TRACKED_ROOTS],  # noqa: S607
        cwd=root,
        env=git_environment(),
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(line for line in out.stdout.splitlines() if line)


def _parent(path: str) -> str:
    return str(PurePosixPath(path).parent)


def _children(files: Iterable[str]) -> dict[str, list[str]]:
    """Group *files* by their parent directory.

    Returns:
        The files of each directory.
    """
    grouped: dict[str, list[str]] = {}
    for path in files:
        grouped.setdefault(_parent(path), []).append(path)
    return grouped


def _module_names(directory: str, children: Mapping[str, list[str]]) -> dict[str, str]:
    """Return the modules and packages of *directory*, underscore-stripped.

    Returns:
        Each mirrored name with the path that maps it: the module itself, or
        the ``__init__.py`` of a package.
    """
    names: dict[str, str] = {}
    for path in children.get(directory, []):
        pure = PurePosixPath(path)
        if pure.suffix == ".py" and pure.name != "__init__.py":
            names[pure.stem.lstrip("_")] = path
    prefix = f"{directory}/"
    for parent, paths in children.items():
        init = f"{parent}/__init__.py"
        if _parent(parent) == directory and init in paths:
            names[parent.removeprefix(prefix).lstrip("_")] = init
    return names


def _mirrored(stem: str, names: Mapping[str, str]) -> tuple[str, str] | None:
    """Return the name *stem* mirrors and its path, the longest match first.

    Returns:
        ``(name, path)``, or ``None`` when no module or package matches.
    """
    matches = [name for name in names if stem == name or stem.startswith(f"{name}_")]
    if not matches:
        return None
    name = max(matches, key=len)
    return name, names[name]


def _below(path: str, root: str) -> str | None:
    """Return *path* relative to *root* with a leading slash, or ``None``.

    Returns:
        ``""`` for *root* itself, ``"/a/b"`` below it, ``None`` outside it.
    """
    if path == root:
        return ""
    if path.startswith(f"{root}/"):
        return path.removeprefix(root)
    return None


@dataclass(frozen=True)
class Mirror:
    """A unit or integration test resolved through the module it mirrors."""

    category: str
    root: str
    path: str

    def target(
        self, mapping: Mapping[str, Entry], children: Mapping[str, list[str]]
    ) -> Entry | None:
        """Return the target of the test, or ``None`` when nothing mirrors it.

        Returns:
            A test path in the target tree, or a dissolve entry for a
            package marker.
        """
        code_root = MIRROR_ROOTS[self.root]
        test_root = f"tests/{self.category}/{self.root}"
        directory = _parent(f"{code_root}/{self.path}")
        name = PurePosixPath(self.path).name
        if name == "__init__.py":
            entry = mapping.get(f"{directory}/__init__.py")
            if entry is None:
                return None
            where = entry["dissolve"] if isinstance(entry, dict) else _parent(entry)
            below = _below(where, code_root)
            return None if below is None else {"dissolve": f"{test_root}{below}"}
        stem = PurePosixPath(name).stem.removeprefix("test_")
        found = _mirrored(stem, _module_names(directory, children))
        if not name.startswith("test_") or found is None:
            return None
        matched, source = found
        entry = mapping.get(source)
        if entry is None:
            return None
        if isinstance(entry, dict):
            below = _below(entry["dissolve"], code_root)
            new_name = name
        else:
            below = _below(_parent(entry), code_root)
            new_name = f"test_{PurePosixPath(entry).stem}{stem[len(matched) :]}.py"
        return None if below is None else f"{test_root}{below}/{new_name}"


def _match(path: str, rules: Rules) -> Entry | Mirror | None:
    if path in rules.overrides:
        return rules.overrides[path]
    for rule in rules.rules:
        found = rule.pattern.fullmatch(path)
        if found is None:
            continue
        if rule.target is not None:
            return rule.target.format(**found.groupdict())
        groups = found.groupdict()
        return Mirror(
            category=(rule.mirror or "").format(**groups),
            root=groups["root"],
            path=groups["path"],
        )
    return None


def build(files: Sequence[str], rules: Rules) -> tuple[dict[str, Entry], list[str]]:
    """Map every file in *files* with *rules*.

    Overrides and target rules resolve first; mirrored tests resolve after,
    through the mapping of the code they mirror.

    Returns:
        The inventory sorted by path, and the paths no rule maps.
    """
    mapping: dict[str, Entry] = {}
    mirrors: dict[str, Mirror] = {}
    unmapped: list[str] = []
    for path in files:
        found = _match(path, rules)
        if isinstance(found, Mirror):
            mirrors[path] = found
        elif found is None:
            unmapped.append(path)
        else:
            mapping[path] = found
    children = _children(files)
    for path, mirror in mirrors.items():
        target = mirror.target(mapping, children)
        if target is None:
            unmapped.append(path)
        else:
            mapping[path] = target
    return dict(sorted(mapping.items())), sorted(unmapped)


# ---------------------------------------------------------------------------
# Contract checks
# ---------------------------------------------------------------------------


def _tree(targets: Iterable[str], root: str) -> set[str]:
    """Return every directory under *root* holding or above a target.

    Returns:
        Directories relative to *root*, ``""`` for *root* itself.
    """
    tree: set[str] = set()
    for target in targets:
        below = _below(_parent(target), root)
        if below is None:
            continue
        parts = below.strip("/").split("/") if below else []
        tree.update("/".join(parts[:depth]) for depth in range(len(parts) + 1))
    return tree


def _common_problems(target: str) -> list[str]:
    pure = PurePosixPath(target)
    problems = [
        f"technical directory {part!r}"
        for part in pure.parts[:-1]
        if part in TECHNICAL_DIRS
    ]
    if pure.name.startswith("_") and target != ROOT_INIT and not _is_marker(target):
        problems.append("basename starts with an underscore")
    return problems


def _is_marker(target: str) -> bool:
    """Return whether *target* is a package marker of a source directory.

    Source directories keep a docstring-only ``__init__.py`` so that the
    documentation tooling sees them as packages; check_structure.py checks
    that a marker holds no code.

    Returns:
        True for an ``__init__.py`` under ``src/ccnl_engine``.
    """
    return target.startswith(f"{PACKAGE}/") and target.endswith("/__init__.py")


#: The index of the knowledge bundle, at its root.
KNOWLEDGE_MANIFEST = PurePosixPath("knowledge/manifest.json")


def _resource_problems(pure: PurePosixPath) -> list[str]:
    if pure == KNOWLEDGE_MANIFEST:
        return []
    domain = pure.parts[1] if len(pure.parts) > 2 else ""
    if pure.parts[0] != "knowledge" or domain not in KNOWLEDGE_DOMAINS:
        return ["resource outside a knowledge dataset"]
    return []


def _module_problems(pure: PurePosixPath) -> list[str]:
    directory = "/".join(pure.parts[:-1])
    if len(pure.parts) - 1 > MAX_SOURCE_DEPTH:
        return [f"{len(pure.parts) - 1} directories under the package"]
    if directory not in SOURCE_TREE:
        return [f"directory {directory!r} not in the target tree"]
    naming = ROLE_NAME if directory else ROOT_NAME
    if pure.name == "__init__.py" or naming.match(pure.name):
        return []
    return ["name is not a technical role"]


def _source_problems(target: str) -> list[str]:
    below = _below(target, PACKAGE)
    if below is None:
        return ["outside src/ccnl_engine"]
    pure = PurePosixPath(below.lstrip("/"))
    if target == ROOT_INIT or below == "/py.typed":
        return []
    if pure.suffix == ".json":
        return _resource_problems(pure)
    if pure.suffix != ".py":
        return ["unexpected file type in the package"]
    return _module_problems(pure)


def _test_problems(target: str, trees: Mapping[str, set[str]]) -> list[str]:
    parts = PurePosixPath(target).parts[1:]
    if len(parts) == 1:
        return [] if parts[0] in TEST_TOP_FILES else ["file at the top of tests"]
    if parts[0] not in TEST_CATEGORIES:
        return [f"category {parts[0]!r} not in {sorted(TEST_CATEGORIES)}"]
    if len(parts) < 3 or parts[1] not in MIRROR_ROOTS:
        return [f"mirror root not in {sorted(MIRROR_ROOTS)}"]
    if len(parts) - 1 > MAX_TEST_DEPTH:
        return [f"{len(parts) - 1} directories under tests"]
    return _mirror_problems(parts[2:], trees[parts[1]])


def _mirror_problems(parts: tuple[str, ...], tree: set[str]) -> list[str]:
    """Return how a file below a test mirror root breaks the mirror.

    A module sits in a directory of the code tree; a resource sits in one, or
    in a dataset directory right below one.

    Returns:
        One reason, or nothing for a conforming file.
    """
    directory = "/".join(parts[:-1])
    if not parts[-1].endswith(".py"):
        if directory not in tree and "/".join(parts[:-2]) not in tree:
            return [f"resource directory {directory!r} sits under no code directory"]
        return []
    if directory not in tree:
        return [f"directory {directory!r} mirrors no code directory"]
    if not TEST_NAME.match(parts[-1]):
        return ["not a test, conftest, builder, oracle or support module"]
    return []


def _tooling_problems(target: str) -> list[str]:
    parts = PurePosixPath(target).parts
    allowed = SCRIPT_DOMAINS if parts[0] == "scripts" else DEMO_DIRS
    if len(parts) > 3:
        return ["more than one directory level"]
    if len(parts) == 3 and parts[1] not in allowed:
        return [f"directory {parts[1]!r} not in {sorted(allowed)}"]
    if parts[0] == "scripts" and len(parts) == 2:
        return ["script outside an operational domain"]
    return []


def target_problems(target: str, trees: Mapping[str, set[str]]) -> list[str]:
    """Return how *target* breaks the contract.

    Returns:
        One reason per broken rule; empty for a conforming target.
    """
    problems = _common_problems(target)
    top = PurePosixPath(target).parts[0]
    if top == "src":
        problems += _source_problems(target)
    elif top == "tests":
        problems += _test_problems(target, trees)
    elif top in {"scripts", "demo"}:
        problems += _tooling_problems(target)
    else:
        problems.append(f"root {top!r} not in {list(TRACKED_ROOTS)}")
    return problems


def code_free(source: str) -> bool:
    """Return whether *source* holds only docstrings and future imports.

    Returns:
        ``True`` for a package marker that can dissolve.
    """
    return all(
        (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant))
        or (isinstance(node, ast.ImportFrom) and node.module == "__future__")
        for node in ast.parse(source).body
    )


def _dissolve_problems(path: str, where: str, root: Path, dirs: set[str]) -> list[str]:
    if PurePosixPath(path).name != "__init__.py":
        return ["only a package marker can dissolve"]
    if not code_free((root / path).read_text(encoding="utf-8")):
        return ["holds code: give it a file target"]
    return [] if where in dirs else [f"dissolves into {where!r}, not a target dir"]


def check_mapping(mapping: Mapping[str, Entry], root: Path) -> list[str]:
    """Check every target of *mapping* against the contract.

    Returns:
        One ``path: reason`` line per problem, sorted.
    """
    files = [entry for entry in mapping.values() if isinstance(entry, str)]
    trees = {name: _tree(files, code) for name, code in MIRROR_ROOTS.items()}
    dirs = {
        str(parent)
        for target in files
        for parent in PurePosixPath(target).parents
        if str(parent) != "."
    }
    problems = [
        f"{target}: target of {count} paths"
        for target, count in Counter(files).items()
        if count > 1
    ]
    for path, entry in mapping.items():
        if isinstance(entry, dict):
            reasons = _dissolve_problems(path, entry["dissolve"], root, dirs)
        else:
            reasons = target_problems(entry, trees)
        problems += [f"{path}: {reason}" for reason in reasons]
    return sorted(problems)


# ---------------------------------------------------------------------------
# Inventory file and command line
# ---------------------------------------------------------------------------


def render(mapping: Mapping[str, Entry]) -> str:
    """Return the inventory file content for *mapping*.

    Returns:
        Indented JSON with a trailing newline.
    """
    document = {
        "description": (
            "Current path -> target path of every tracked file under src, "
            "tests, demo and scripts. Generated by "
            "scripts/structure/inventory.py from inventory_rules.json; "
            "do not edit by hand."
        ),
        "files": dict(mapping),
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def summary(mapping: Mapping[str, Entry]) -> list[str]:
    """Count the file targets per area and per payroll subdomain.

    Returns:
        One ``area: count`` line per area, sorted.
    """
    counts: Counter[str] = Counter()
    for entry in mapping.values():
        if isinstance(entry, dict):
            counts["dissolved package markers"] += 1
            continue
        parts = PurePosixPath(entry).parts
        depth = 3 if parts[:3] == ("src", "ccnl_engine", "payroll") else 2
        counts["/".join(parts[: min(depth + 1, len(parts) - 1)])] += 1
    return [f"{area}: {count}" for area, count in sorted(counts.items())]


def run(
    root: Path, rules_path: Path, inventory: Path, *, check: bool
) -> tuple[dict[str, Entry], list[str]]:
    """Build the inventory and write it, or compare it with *inventory*.

    Returns:
        The inventory, and the problems found: empty when the inventory is
        written or matches.
    """
    mapping, unmapped = build(tracked_files(root), load_rules(rules_path))
    problems = [f"{path}: no rule maps it" for path in unmapped]
    problems += check_mapping(mapping, root)
    content = render(mapping)
    if not check:
        inventory.write_text(content, encoding="utf-8")
    elif not inventory.is_file() or inventory.read_text(encoding="utf-8") != content:
        problems.append(
            f"{inventory.name} is out of date: run "
            "uv run python scripts/structure/inventory.py"
        )
    return mapping, problems


def main(argv: Sequence[str] | None = None) -> int:
    """Run the inventory build or check.

    Returns:
        The process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--rules", type=Path, default=RULES)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    parser.add_argument("--check", action="store_true", help="fail on drift")
    parser.add_argument(
        "--summary", action="store_true", help="check and print counts per area"
    )
    args = parser.parse_args(argv)
    try:
        mapping, problems = run(
            args.root,
            args.rules,
            args.inventory,
            check=args.check or args.summary,
        )
    except (OSError, SyntaxError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.summary:
        print("\n".join(summary(mapping)))
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    print(f"layout inventory: {len(mapping)} paths, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
