"""Names of files and directories: directory = domain, file = technical role.

- a module under ``src/ccnl_engine`` is named after a role
  (:data:`SOURCE_ROLES`), at the package root also after a public module
  (:data:`ROOT_MODULES`); ``__init__.py`` is a package marker;
- a test module is ``test_<name>.py`` where ``<name>`` is a name a mirrored
  module may have; its helpers are ``conftest.py``, ``builders.py``,
  ``oracles.py`` and ``support.py``.  The tests of a module that need more
  than one file sit in a directory named after the module
  (``catalog/loaders/``), where a test takes the name of its behaviour;
- a script is named after an action (:data:`SCRIPT_ACTIONS`) or a role;
- the demo holds its entry point ``app.py`` only;
- a directory holding Python modules is named after a domain listed in the
  "Directory names" section of ``docs/domain/glossary.md``, or after a root
  of the tree (:data:`STRUCTURAL_DIRECTORIES`); right below the package root
  (``src/ccnl_engine`` and its mirror under each test category) only a
  concept of that section's "Concepts" paragraph.  Under ``tests`` a
  directory may also be named after a module it tests.

Directories without Python modules (knowledge data, test fixtures) are not
named by this rule: their names identify resources.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path, PurePath

#: Technical roles a module is named after.
SOURCE_ROLES: Final = frozenset({
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
})
#: Public modules at the package root besides the roles.
ROOT_MODULES: Final = frozenset({"api", "events", "errors", "version"})
#: Actions a script is named after.
SCRIPT_ACTIONS: Final = frozenset({
    "check",
    "build",
    "generate",
    "update",
    "diff",
    "assign",
    "demote",
    "report",
    "test",
})
#: Helper modules of the test suite.
TEST_HELPERS: Final = frozenset({"conftest", "builders", "oracles", "support"})
#: Entry points of the demo.
DEMO_ENTRIES: Final = frozenset({"app"})
#: Roots of the trees, named by the layout and not by a domain.
STRUCTURAL_DIRECTORIES: Final = frozenset({
    "src",
    "ccnl_engine",
    "tests",
    "unit",
    "integration",
    "knowledge",
    "scripts",
    "demo",
})
GLOSSARY: Final = "docs/domain/glossary.md"
_SECTION: Final = "## Directory names"
_CONCEPTS: Final = "**Concepts**"
_NAME: Final = re.compile(r"`([a-z0-9_]+)`")
_PACKAGE: Final = "ccnl_engine"


@dataclass(frozen=True)
class Vocabulary:
    """Directory names the glossary admits.

    Attributes:
        concepts: Names admitted right below the package root.
        names: Every admitted name, concepts included.
    """

    concepts: frozenset[str]
    names: frozenset[str]


_TESTED: Final = SOURCE_ROLES | ROOT_MODULES | SCRIPT_ACTIONS | DEMO_ENTRIES


def vocabulary(root: Path) -> Vocabulary:
    """Return the directory names the glossary of *root* lists.

    Returns:
        The backticked names of the "Directory names" section, those of its
        "Concepts" paragraph apart; empty when the glossary or the section
        is missing.
    """
    path = root / GLOSSARY
    if not path.is_file():
        return Vocabulary(frozenset(), frozenset())
    names: set[str] = set()
    concepts: set[str] = set()
    inside = in_concepts = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip() == _SECTION
        elif inside:
            in_concepts = line.startswith(_CONCEPTS) or (in_concepts and bool(line))
            found = _NAME.findall(line)
            names.update(found)
            if in_concepts:
                concepts.update(found)
    return Vocabulary(frozenset(concepts), frozenset(names))


def file_offends(rel: PurePath) -> bool:
    """Return whether the Python module *rel* breaks the naming rule.

    Args:
        rel: Path relative to the repository root, under ``src``, ``tests``,
            ``scripts`` or ``demo``.

    Returns:
        True when the file name is not one its tree allows.
    """
    stem, top = rel.stem, rel.parts[0]
    if top == "src":
        at_root = len(rel.parts) == 3
        allowed = SOURCE_ROLES | ROOT_MODULES if at_root else SOURCE_ROLES
        return stem not in allowed | {"__init__"}
    if top == "tests":
        return stem not in TEST_HELPERS and not _test_name(rel)
    if top == "scripts":
        return stem not in SCRIPT_ACTIONS | SOURCE_ROLES
    return stem not in DEMO_ENTRIES


def _test_name(rel: PurePath) -> bool:
    """Return whether *rel* is a test the naming rule admits.

    Returns:
        True for ``test_<module name>.py``, or for any ``test_*.py`` in the
        directory of the tests of one module.
    """
    if not rel.stem.startswith("test_"):
        return False
    return rel.parent.name in _TESTED or rel.stem[len("test_") :] in _TESTED


def directory_offends(rel: PurePath, words: Vocabulary) -> bool:
    """Return whether a directory holding modules breaks the naming rule.

    Args:
        rel: Directory relative to the repository root.
        words: The admitted names.

    Returns:
        True when a directory right below a package root is not a concept,
        or another directory is neither an admitted name nor a root.
    """
    if rel.parts[0] == "tests" and rel.name in _TESTED:
        return False
    if rel.parent.name == _PACKAGE:
        return rel.name not in words.concepts
    return rel.name not in words.names | STRUCTURAL_DIRECTORIES
