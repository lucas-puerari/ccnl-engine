"""Enforce structural size limits with a shrink-only baseline of exceptions.

Rules and hard limits:

- ``production_file_lines``: physical lines of a module under
  ``src/ccnl_engine`` (300);
- ``test_file_lines``: physical lines of a module under ``tests`` (500);
- ``function_lines``: effective lines of a function or method (60);
- ``class_lines``: effective lines of a class (150), declarative classes
  exempt;
- ``public_methods``: methods of a class whose name has no leading
  underscore (15);
- ``source_depth``: directories under ``src/ccnl_engine`` before a module
  (3), ``data`` resource directories exempt;
- ``underscore_files``: files under ``src``, ``tests``, ``scripts`` and
  ``demo`` whose name starts with an underscore (0), the package root
  ``src/ccnl_engine/__init__.py`` exempt: every new ``__init__.py`` or
  ``_module.py`` fails;
- ``technical_directories``: directories under the same roots named after a
  technical layer (``domain``, ``application``, ``service``, ``handlers``,
  ``fixtures``, ``data``) instead of a domain (0);
- ``markdown_lines``: physical lines of a hand-written Markdown page (600):
  the top-level pages and those under ``docs``. The audit notes
  ``REVIEW.md`` and ``TODO.md`` are excluded, and so are the generated
  pages under ``docs/contracts`` and the built site under ``docs/_build``:
  the generators validate those pages against their sources with
  ``--check``.

Effective lines are lines holding code, from the ``def`` or ``class`` line to
the end of the body: blank lines, comment-only lines and docstrings do not
count. Function and class rules apply to ``src``, ``tests`` and ``scripts``.
The layout rules skip hidden directories, ``__pycache__`` and the gitignored
demo build output (``demo/_build``, ``demo/wheels``); each offender is
recorded with the value 1, so the baseline lists them one by one.

A class is declarative when every method defined in its body is a pydantic
validator or serializer, so models, dataclasses, enums and constant holders
without behaviour are measured by their methods only.

Current offenders are listed in ``structure_baseline.json`` with their
measured value. The check fails when a new offender appears, when an
offender grows past its baseline value, or when a baseline entry no longer
offends and must be removed. The baseline can only shrink.

Every rule also has a target at about 80% of its limit (``TARGETS``). The
target is a report, never a failure: the check prints how many entries sit
above each target, and ``--targets`` lists them.

The script uses the standard library only.

Usage::

    python scripts/ci/check_structure.py
    python scripts/ci/check_structure.py --targets
    python scripts/ci/check_structure.py --write-baseline

Exit codes:
    0   The tree matches the limits and the baseline.
    1   A limit or baseline check fails.
    2   The tree or the baseline cannot be read.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence

ROOT: Final = Path(__file__).resolve().parents[2]
BASELINE: Final = Path(__file__).with_name("structure_baseline.json")

PACKAGE: Final = Path("src") / "ccnl_engine"
TESTS: Final = Path("tests")
MEASURED: Final = (Path("src"), TESTS, Path("scripts"))
RESOURCE_DIRS: Final = frozenset({"data"})
#: Roots of the layout rules: underscore files and technical directories.
LAYOUT_ROOTS: Final = (Path("src"), TESTS, Path("scripts"), Path("demo"))
#: Gitignored build output of the demo, outside the layout rules.
GENERATED_DIRS: Final = frozenset({Path("demo") / "_build", Path("demo") / "wheels"})
#: The single file whose name may start with an underscore.
ROOT_INIT: Final = PACKAGE / "__init__.py"
#: Directory names of a technical layer; the contract names directories
#: after domains only (docs/engine/architecture-contract.md).
TECHNICAL_DIRS: Final = frozenset({
    "domain",
    "application",
    "service",
    "handlers",
    "fixtures",
    "data",
})
DOCS: Final = Path("docs")
#: Top-level audit notes, outside the Markdown limit.
EXCLUDED_MARKDOWN: Final = frozenset({"REVIEW.md", "TODO.md"})
#: Directories under ``docs`` written by tools, not by hand.
GENERATED_DOCS: Final = frozenset({"_build", "contracts"})
DECLARATIVE_DECORATORS: Final = frozenset({
    "field_validator",
    "model_validator",
    "field_serializer",
    "model_serializer",
    "validator",
    "root_validator",
})
_NON_CODE_TOKENS: Final = frozenset({
    tokenize.COMMENT,
    tokenize.NL,
    tokenize.NEWLINE,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.ENCODING,
    tokenize.ENDMARKER,
})

#: Hard limit per rule.
LIMITS: Final[dict[str, int]] = {
    "production_file_lines": 300,
    "test_file_lines": 500,
    "function_lines": 60,
    "class_lines": 150,
    "public_methods": 15,
    "source_depth": 3,
    "underscore_files": 0,
    "technical_directories": 0,
    "markdown_lines": 600,
}

#: Non-blocking target per rule, about 80% of the hard limit.
TARGETS: Final[dict[str, int]] = {
    "production_file_lines": 240,
    "test_file_lines": 400,
    "function_lines": 40,
    "class_lines": 100,
    "public_methods": 10,
    "source_depth": 3,
    "underscore_files": 0,
    "technical_directories": 0,
    "markdown_lines": 450,
}

#: Offending values per rule, keyed by ``path`` or ``path::qualname``.
Measurements = dict[str, dict[str, int]]

_Definition = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
_DEFINITION_TYPES: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
_DOCUMENTED_TYPES: Final = (
    ast.Module,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
)


@dataclass
class Report:
    """Outcome of comparing measured offenders with the baseline."""

    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _skipped(part: str) -> bool:
    return part.startswith(".") or part == "__pycache__"


def python_files(root: Path, top: Path) -> list[Path]:
    """Return the ``.py`` files under ``root / top``, skipping cache dirs.

    Returns:
        Paths relative to *root*, sorted.
    """
    base = root / top
    return sorted(
        path.relative_to(root)
        for path in base.rglob("*.py")
        if not any(_skipped(part) for part in path.relative_to(base).parts)
    )


def _outside_layout(rel: Path) -> bool:
    return any(_skipped(part) for part in rel.parts) or any(
        generated == rel or generated in rel.parents for generated in GENERATED_DIRS
    )


def layout_offenders(root: Path) -> tuple[list[Path], list[Path]]:
    """Return the underscore files and technical directories of *root*.

    Hidden directories, ``__pycache__`` and :data:`GENERATED_DIRS` are
    skipped; :data:`ROOT_INIT` is not an offender.

    Returns:
        Files whose name starts with an underscore and directories named in
        :data:`TECHNICAL_DIRS`, both relative to *root* and sorted.
    """
    files: list[Path] = []
    dirs: list[Path] = []
    for top in LAYOUT_ROOTS:
        for path in (root / top).rglob("*"):
            rel = path.relative_to(root)
            if _outside_layout(rel):
                continue
            if path.is_dir():
                if path.name in TECHNICAL_DIRS:
                    dirs.append(rel)
            elif path.name.startswith("_") and rel != ROOT_INIT:
                files.append(rel)
    return sorted(files), sorted(dirs)


def markdown_files(root: Path) -> list[Path]:
    """Return the hand-written Markdown pages of the repository at *root*.

    Returns:
        Top-level pages except the audit notes, and the pages under
        ``docs`` outside generated and hidden directories; relative to
        *root*, sorted.
    """
    top = [
        path.relative_to(root)
        for path in root.glob("*.md")
        if path.name not in EXCLUDED_MARKDOWN
    ]
    docs = root / DOCS
    pages = [
        path.relative_to(root)
        for path in docs.rglob("*.md")
        if not any(_skipped(part) for part in path.relative_to(docs).parts)
        and path.relative_to(docs).parts[0] not in GENERATED_DOCS
    ]
    return sorted(top + pages)


def code_lines(source: str) -> set[int]:
    """Return the line numbers holding at least one code token.

    Returns:
        Line numbers, a multi-line token counting on every line it spans.
    """
    lines: set[int] = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in _NON_CODE_TOKENS:
            lines.update(range(token.start[0], token.end[0] + 1))
    return lines


def docstring_lines(tree: ast.Module) -> set[int]:
    """Return the lines of every module, class and function docstring.

    Returns:
        Line numbers covered by docstring expressions.
    """
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, _DOCUMENTED_TYPES):
            continue
        first = node.body[0] if node.body else None
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            lines.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return lines


def _definitions(node: ast.AST, prefix: str) -> Iterator[tuple[str, _Definition]]:
    """Yield every function and class below *node* with its dotted qualname.

    Yields:
        ``(qualname, node)`` pairs, nested definitions included.
    """
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _DEFINITION_TYPES):
            name = f"{prefix}{child.name}"
            yield name, child
            yield from _definitions(child, f"{name}.")
        else:
            yield from _definitions(child, prefix)


def _decorator_name(node: ast.expr) -> str:
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _methods(cls: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in cls.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def is_declarative(cls: ast.ClassDef) -> bool:
    """Return whether every method of *cls* is a validator or serializer.

    Returns:
        ``True`` for classes whose body declares data only.
    """
    return all(
        any(
            _decorator_name(decorator) in DECLARATIVE_DECORATORS
            for decorator in method.decorator_list
        )
        for method in _methods(cls)
    )


def public_methods(cls: ast.ClassDef) -> int:
    """Return the number of methods of *cls* without a leading underscore.

    Returns:
        The count of public methods defined directly in the class body.
    """
    return sum(1 for method in _methods(cls) if not method.name.startswith("_"))


def _record(
    found: Measurements,
    rule: str,
    key: str,
    value: int,
    thresholds: Mapping[str, int] = LIMITS,
) -> None:
    if value > thresholds[rule]:
        bucket = found.setdefault(rule, {})
        bucket[key] = max(value, bucket.get(key, 0))


def measure_source(
    path: str,
    source: str,
    found: Measurements,
    thresholds: Mapping[str, int] = LIMITS,
) -> None:
    """Record the function and class offenders of one module into *found*.

    Values above *thresholds*, the hard limits by default, are recorded.
    """
    tree = ast.parse(source, filename=path)
    effective = code_lines(source) - docstring_lines(tree)
    for qualname, node in _definitions(tree, ""):
        span = range(node.lineno, (node.end_lineno or node.lineno) + 1)
        lines = len(effective.intersection(span))
        key = f"{path}::{qualname}"
        if not isinstance(node, ast.ClassDef):
            _record(found, "function_lines", key, lines, thresholds)
            continue
        _record(found, "public_methods", key, public_methods(node), thresholds)
        if not is_declarative(node):
            _record(found, "class_lines", key, lines, thresholds)


def _physical_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def measure_tree(root: Path, thresholds: Mapping[str, int] = LIMITS) -> Measurements:
    """Measure every rule on the repository at *root*.

    Returns:
        The values above *thresholds* per rule, the hard limits by default;
        rules without such values are omitted.
    """
    found: Measurements = {}
    for rel in python_files(root, PACKAGE):
        key = rel.as_posix()
        lines = _physical_lines(root / rel)
        _record(found, "production_file_lines", key, lines, thresholds)
        dirs = rel.relative_to(PACKAGE).parts[:-1]
        if not RESOURCE_DIRS.intersection(dirs):
            _record(found, "source_depth", key, len(dirs), thresholds)
    for rel in python_files(root, TESTS):
        lines = _physical_lines(root / rel)
        _record(found, "test_file_lines", rel.as_posix(), lines, thresholds)
    underscore, technical = layout_offenders(root)
    for rel in underscore:
        _record(found, "underscore_files", rel.as_posix(), 1, thresholds)
    for rel in technical:
        _record(found, "technical_directories", rel.as_posix(), 1, thresholds)
    for rel in markdown_files(root):
        lines = _physical_lines(root / rel)
        _record(found, "markdown_lines", rel.as_posix(), lines, thresholds)
    for top in MEASURED:
        for rel in python_files(root, top):
            text = (root / rel).read_text(encoding="utf-8")
            measure_source(rel.as_posix(), text, found, thresholds)
    return found


def load_baseline(path: Path) -> Measurements:
    """Read and validate the baseline file.

    Returns:
        The baseline entries per rule.

    Raises:
        ValueError: if the file does not map known rules to integer values.
    """
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path}: expected a JSON object"
        raise ValueError(msg)  # noqa: TRY004
    baseline: Measurements = {}
    for rule, entries in data.items():
        if rule not in LIMITS:
            msg = f"{path}: unknown rule {rule!r}"
            raise ValueError(msg)
        if not isinstance(entries, dict) or not all(
            isinstance(value, int) for value in entries.values()
        ):
            msg = f"{path}: {rule!r} must map keys to integers"
            raise ValueError(msg)
        baseline[rule] = dict(entries)
    return baseline


def compare(found: Measurements, baseline: Measurements) -> Report:
    """Compare measured offenders with the baseline.

    Returns:
        Problems that fail the check and notes on offenders that improved.
    """
    report = Report()
    for rule, limit in LIMITS.items():
        current = found.get(rule, {})
        allowed = baseline.get(rule, {})
        for key, value in sorted(current.items()):
            ceiling = allowed.get(key)
            if ceiling is None:
                report.problems.append(f"{rule}: {key} is {value} (limit {limit})")
            elif value > ceiling:
                report.problems.append(
                    f"{rule}: {key} grew to {value} (baseline {ceiling})"
                )
            elif value < ceiling:
                report.notes.append(
                    f"{rule}: {key} improved to {value}, lower its baseline"
                )
        for key in sorted(allowed.keys() - current.keys()):
            report.problems.append(
                f"{rule}: {key} is within the limit, remove it from the baseline"
            )
    return report


def check(root: Path, baseline_path: Path) -> Report:
    """Measure *root* and compare it with the baseline at *baseline_path*.

    Returns:
        The comparison report.
    """
    return compare(measure_tree(root), load_baseline(baseline_path))


def write_baseline(root: Path, baseline_path: Path) -> Measurements:
    """Write the current offenders of *root* to *baseline_path*.

    Returns:
        The written entries.
    """
    found = measure_tree(root)
    ordered = {rule: dict(sorted(found[rule].items())) for rule in sorted(found)}
    baseline_path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
    return ordered


def target_report(above: Measurements) -> list[str]:
    """Describe the entries above their target, rule by rule.

    Returns:
        One line per entry, sorted by rule order and key.
    """
    return [
        f"{rule}: {key} is {value} (target {target})"
        for rule, target in TARGETS.items()
        for key, value in sorted(above.get(rule, {}).items())
    ]


def _target_summary(above: Measurements) -> str:
    counts = ", ".join(f"{rule} {len(above.get(rule, {}))}" for rule in TARGETS)
    return f"above the 80% targets (not blocking): {counts}"


def _summary(baseline: Measurements) -> str:
    counts = ", ".join(f"{rule} {len(baseline.get(rule, {}))}" for rule in LIMITS)
    return f"structure baseline entries: {counts}"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the structural check.

    Returns:
        The process exit code.
    """
    parser = argparse.ArgumentParser(
        description="Enforce structural size limits with a shrink-only baseline."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="record the current offenders; review that no entry was added",
    )
    parser.add_argument(
        "--targets",
        action="store_true",
        help="list every entry above its 80%% target; never fails the check",
    )
    args = parser.parse_args(argv)
    try:
        if args.write_baseline:
            print(_summary(write_baseline(args.root, args.baseline)))
            return 0
        baseline = load_baseline(args.baseline)
        report = compare(measure_tree(args.root), baseline)
        above = measure_tree(args.root, TARGETS)
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for note in report.notes:
        print(f"note: {note}")
    for problem in report.problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if args.targets:
        for line in target_report(above):
            print(f"target: {line}")
    print(_summary(baseline))
    print(_target_summary(above))
    return 1 if report.problems else 0


if __name__ == "__main__":
    sys.exit(main())
